"""
Global Comparison Module
=========================
Provides structured US-vs-Global macro environment comparison, producing
directional assessments ("US outperforms", "US underperforms", "neutral")
for each variable, along with aggregate scoring by category.
"""

from __future__ import annotations

from typing import Any

from analysis.config import MACRO_VARIABLES, get_score_label
from analysis.macro.indicators import MacroIndicators


class GlobalComparison:
    """Compare the US macro backdrop against the global economy."""

    def __init__(self, indicators: MacroIndicators):
        self.indicators = indicators

    # ------------------------------------------------------------------
    # Per-variable assessment
    # ------------------------------------------------------------------
    def assess_variable(self, variable: str) -> dict[str, Any]:
        """
        For a single macro variable, return a dict with:
          - us_value, global_value, spread
          - direction (from config)
          - assessment: "us_outperforms" | "us_underperforms" | "neutral" | "no_data"
        """
        meta = MACRO_VARIABLES.get(variable)
        if meta is None:
            return {"error": f"Unknown variable: {variable}"}

        us_val = self.indicators.get_us(variable)
        gl_val = self.indicators.get_global(variable)
        spread = self.indicators.get_spread(variable)

        if us_val is None or gl_val is None:
            assessment = "no_data"
        elif meta["direction"] == "higher_better":
            assessment = "us_outperforms" if spread > 0 else (
                "us_underperforms" if spread < 0 else "neutral"
            )
        elif meta["direction"] == "lower_better":
            assessment = "us_outperforms" if spread < 0 else (
                "us_underperforms" if spread > 0 else "neutral"
            )
        else:
            assessment = "neutral"

        return {
            "variable": variable,
            "label": meta["label"],
            "us_value": us_val,
            "global_value": gl_val,
            "spread": spread,
            "unit": meta["unit"],
            "direction": meta["direction"],
            "assessment": assessment,
        }

    def assess_all(self) -> list[dict[str, Any]]:
        """Run assessment on every macro variable."""
        return [self.assess_variable(v) for v in MACRO_VARIABLES]

    # ------------------------------------------------------------------
    # Category-level scoring
    # ------------------------------------------------------------------
    def category_scores(self) -> dict[str, dict]:
        """
        For each macro category compute:
          - count of variables where US outperforms / underperforms / neutral
          - a simple 0-100 score: (outperforms / assessable) * 100
        """
        buckets: dict[str, dict] = {}
        for result in self.assess_all():
            cat = MACRO_VARIABLES[result["variable"]]["category"]
            if cat not in buckets:
                buckets[cat] = {
                    "us_outperforms": 0,
                    "us_underperforms": 0,
                    "neutral": 0,
                    "no_data": 0,
                }
            buckets[cat][result["assessment"]] += 1

        scored: dict[str, dict] = {}
        for cat, counts in buckets.items():
            assessable = counts["us_outperforms"] + counts["us_underperforms"]
            if assessable > 0:
                score = (counts["us_outperforms"] / assessable) * 100
            else:
                score = 50.0  # default when all neutral or no data
            scored[cat] = {
                **counts,
                "score": round(score, 1),
                "label": get_score_label(score),
            }
        return scored

    def composite_score(self) -> dict:
        """
        Weighted composite score across all categories.
        Weights are equal across categories here; the engine module
        can apply custom weighting.
        """
        cat_scores = self.category_scores()
        if not cat_scores:
            return {"score": None, "label": "Unrated"}
        total = sum(c["score"] for c in cat_scores.values())
        avg = total / len(cat_scores)
        return {
            "score": round(avg, 1),
            "label": get_score_label(avg),
            "category_detail": cat_scores,
        }

    # ------------------------------------------------------------------
    # Narrative helpers
    # ------------------------------------------------------------------
    def strengths_and_weaknesses(self) -> dict[str, list[str]]:
        """Identify US relative strengths and weaknesses."""
        strengths: list[str] = []
        weaknesses: list[str] = []
        for result in self.assess_all():
            if result["assessment"] == "us_outperforms":
                strengths.append(result["label"])
            elif result["assessment"] == "us_underperforms":
                weaknesses.append(result["label"])
        return {"us_strengths": strengths, "us_weaknesses": weaknesses}

    def __repr__(self) -> str:
        cs = self.composite_score()
        return f"<GlobalComparison score={cs['score']} ({cs['label']})>"
