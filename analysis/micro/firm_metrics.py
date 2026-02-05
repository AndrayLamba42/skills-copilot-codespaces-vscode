"""
Firm Metrics Module
====================
Holds, validates, and exposes a single firm's financial and operational
metrics.  These micro-level data points form the basis for all
firm-vs-industry and firm-vs-economy comparisons.
"""

from __future__ import annotations

from typing import Any

from analysis.config import MICRO_VARIABLES, get_score_label


class FirmMetrics:
    """Financial and operational metrics for a single company."""

    def __init__(
        self,
        firm_name: str,
        ticker: str,
        industry: str,
        data: dict[str, Any],
        fiscal_year: str | None = None,
    ):
        """
        Parameters
        ----------
        firm_name : str
            Full legal / common name of the company.
        ticker : str
            Stock ticker symbol.
        industry : str
            Industry classification (free-form or SIC / NAICS).
        data : dict
            Key-value pairs whose keys match MICRO_VARIABLES keys.
        fiscal_year : str, optional
            Fiscal year / period the data represents.
        """
        self.firm_name = firm_name
        self.ticker = ticker
        self.industry = industry
        self.fiscal_year = fiscal_year
        self.data = self._validate(data)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    @staticmethod
    def _validate(data: dict[str, Any]) -> dict[str, Any]:
        validated: dict[str, Any] = {}
        for key in MICRO_VARIABLES:
            validated[key] = data.get(key)  # None for missing
        unknown = set(data) - set(MICRO_VARIABLES)
        if unknown:
            print(f"[FirmMetrics] Warning – unknown keys ignored: {unknown}")
        return validated

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------
    def get(self, variable: str) -> Any:
        return self.data.get(variable)

    def available_variables(self) -> list[str]:
        return [k for k, v in self.data.items() if v is not None]

    def missing_variables(self) -> list[str]:
        return [k for k, v in self.data.items() if v is None]

    # ------------------------------------------------------------------
    # Category summaries
    # ------------------------------------------------------------------
    def by_category(self) -> dict[str, dict]:
        """Group metrics by their config category, with metadata."""
        cats: dict[str, dict] = {}
        for key, meta in MICRO_VARIABLES.items():
            cat = meta["category"]
            if cat not in cats:
                cats[cat] = {"variables": {}}
            cats[cat]["variables"][key] = {
                "label": meta["label"],
                "value": self.data.get(key),
                "unit": meta["unit"],
                "direction": meta["direction"],
            }
        return cats

    # ------------------------------------------------------------------
    # Profitability snapshot
    # ------------------------------------------------------------------
    def profitability_snapshot(self) -> dict[str, Any]:
        """Quick profitability overview."""
        return {
            "revenue": self.get("revenue"),
            "revenue_growth_yoy": self.get("revenue_growth_yoy"),
            "gross_margin": self.get("gross_margin"),
            "operating_margin": self.get("operating_margin"),
            "net_margin": self.get("net_margin"),
            "roe": self.get("roe"),
            "roa": self.get("roa"),
        }

    # ------------------------------------------------------------------
    # Valuation snapshot
    # ------------------------------------------------------------------
    def valuation_snapshot(self) -> dict[str, Any]:
        return {
            "market_cap": self.get("market_cap"),
            "pe_ratio": self.get("pe_ratio"),
            "ev_to_ebitda": self.get("ev_to_ebitda"),
            "price_to_book": self.get("price_to_book"),
        }

    # ------------------------------------------------------------------
    # Simple internal score (firm-only, no comparison)
    # ------------------------------------------------------------------
    def standalone_score(self) -> dict:
        """
        Produce a naive 0-100 standalone health score using only the
        directional hints in config.  This does NOT compare against
        industry or economy — it's meant as a quick internal gauge.

        Scoring heuristic per metric (only for 'higher_better' /
        'lower_better'):
          - Assign 100 if the value exceeds a generous benchmark,
            0 if it's zero or negative (for higher_better).
          - For simplicity, normalise against these rough baselines.
        """
        baselines_higher = {
            "revenue_growth_yoy": 20,
            "gross_margin": 60,
            "operating_margin": 25,
            "net_margin": 20,
            "roe": 25,
            "roa": 12,
            "market_share": 30,
            "market_share_delta_yoy": 3,
            "current_ratio": 2.5,
            "asset_turnover": 1.5,
            "rd_to_revenue": 15,
        }
        baselines_lower = {
            "debt_to_equity": 2.0,
        }

        scores: list[float] = []
        weights: list[float] = []

        for key, meta in MICRO_VARIABLES.items():
            val = self.data.get(key)
            if val is None:
                continue
            w = meta["weight"]

            if meta["direction"] == "higher_better" and key in baselines_higher:
                baseline = baselines_higher[key]
                s = min(100, max(0, (val / baseline) * 100))
                scores.append(s)
                weights.append(w)
            elif meta["direction"] == "lower_better" and key in baselines_lower:
                baseline = baselines_lower[key]
                s = min(100, max(0, ((baseline - val) / baseline) * 100))
                scores.append(s)
                weights.append(w)

        if not scores:
            return {"score": None, "label": "Unrated"}

        total_w = sum(weights)
        weighted = sum(s * w for s, w in zip(scores, weights)) / total_w
        return {
            "score": round(weighted, 1),
            "label": get_score_label(weighted),
            "metrics_scored": len(scores),
        }

    def __repr__(self) -> str:
        avail = len(self.available_variables())
        total = len(MICRO_VARIABLES)
        return (f"<FirmMetrics {self.ticker} ({self.firm_name}) "
                f"{avail}/{total} metrics>")
