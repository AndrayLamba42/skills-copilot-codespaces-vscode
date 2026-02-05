"""
Industry Position Module
=========================
Evaluates where a firm sits within its industry using industry-level
benchmark data and the firm's own metrics.  Produces positioning
assessments: leader / contender / laggard / niche.
"""

from __future__ import annotations

from typing import Any

from analysis.config import INDUSTRY_VARIABLES, MICRO_VARIABLES, get_score_label
from analysis.micro.firm_metrics import FirmMetrics


class IndustryPosition:
    """Assess a firm's competitive position within its industry."""

    # Positioning thresholds (market-share based, in %)
    LEADER_THRESHOLD = 20.0
    CONTENDER_THRESHOLD = 10.0
    NICHE_CEILING = 3.0

    def __init__(
        self,
        firm: FirmMetrics,
        industry_data: dict[str, Any],
    ):
        """
        Parameters
        ----------
        firm : FirmMetrics
            The firm being evaluated.
        industry_data : dict
            Key-value pairs matching INDUSTRY_VARIABLES keys, providing
            aggregate industry benchmarks.
        """
        self.firm = firm
        self.industry = self._validate(industry_data)

    @staticmethod
    def _validate(data: dict[str, Any]) -> dict[str, Any]:
        validated: dict[str, Any] = {}
        for key in INDUSTRY_VARIABLES:
            validated[key] = data.get(key)
        return validated

    # ------------------------------------------------------------------
    # Positioning classification
    # ------------------------------------------------------------------
    def classify_position(self) -> str:
        """
        Return one of: 'leader', 'contender', 'laggard', 'niche',
        'unclassified' based on market share and margins relative
        to industry averages.
        """
        share = self.firm.get("market_share")
        if share is None:
            return "unclassified"
        if share >= self.LEADER_THRESHOLD:
            return "leader"
        if share >= self.CONTENDER_THRESHOLD:
            return "contender"
        if share <= self.NICHE_CEILING:
            return "niche"
        return "laggard"

    # ------------------------------------------------------------------
    # Firm-vs-industry metric comparison
    # ------------------------------------------------------------------
    def compare_growth(self) -> dict[str, Any]:
        """Compare firm revenue growth vs industry revenue growth."""
        firm_growth = self.firm.get("revenue_growth_yoy")
        ind_growth = self.industry.get("industry_revenue_growth")
        if firm_growth is None or ind_growth is None:
            return {"assessment": "no_data"}
        delta = firm_growth - ind_growth
        if delta > 2:
            assessment = "outperforming_industry"
        elif delta < -2:
            assessment = "underperforming_industry"
        else:
            assessment = "in_line_with_industry"
        return {
            "firm_growth": firm_growth,
            "industry_growth": ind_growth,
            "delta_pp": round(delta, 2),
            "assessment": assessment,
        }

    def compare_margins(self) -> dict[str, Any]:
        """Compare firm operating margin vs industry average."""
        firm_margin = self.firm.get("operating_margin")
        ind_margin = self.industry.get("industry_avg_operating_margin")
        if firm_margin is None or ind_margin is None:
            return {"assessment": "no_data"}
        delta = firm_margin - ind_margin
        if delta > 3:
            assessment = "margin_leader"
        elif delta < -3:
            assessment = "margin_laggard"
        else:
            assessment = "margin_parity"
        return {
            "firm_margin": firm_margin,
            "industry_avg_margin": ind_margin,
            "delta_pp": round(delta, 2),
            "assessment": assessment,
        }

    def compare_valuation(self) -> dict[str, Any]:
        """Compare firm P/E vs industry average P/E."""
        firm_pe = self.firm.get("pe_ratio")
        ind_pe = self.industry.get("industry_avg_pe")
        if firm_pe is None or ind_pe is None:
            return {"assessment": "no_data"}
        ratio = firm_pe / ind_pe if ind_pe != 0 else None
        if ratio is None:
            assessment = "no_data"
        elif ratio > 1.20:
            assessment = "premium_valued"
        elif ratio < 0.80:
            assessment = "discount_valued"
        else:
            assessment = "fairly_valued"
        return {
            "firm_pe": firm_pe,
            "industry_avg_pe": ind_pe,
            "pe_ratio_vs_industry": round(ratio, 2) if ratio else None,
            "assessment": assessment,
        }

    # ------------------------------------------------------------------
    # Industry structure summary
    # ------------------------------------------------------------------
    def industry_structure_summary(self) -> dict[str, Any]:
        """Summarise the competitive structure of the industry."""
        return {
            "total_addressable_market": self.industry.get(
                "industry_total_market_size"
            ),
            "hhi": self.industry.get("industry_hhi"),
            "major_competitors": self.industry.get(
                "industry_num_major_competitors"
            ),
            "entry_barrier": self.industry.get("industry_entry_barrier_score"),
            "regulatory_risk": self.industry.get(
                "industry_regulatory_risk_score"
            ),
            "tech_disruption_risk": self.industry.get(
                "industry_tech_disruption_score"
            ),
            "concentration": self._classify_concentration(),
        }

    def _classify_concentration(self) -> str:
        hhi = self.industry.get("industry_hhi")
        if hhi is None:
            return "unknown"
        if hhi < 1500:
            return "competitive"
        if hhi < 2500:
            return "moderately_concentrated"
        return "highly_concentrated"

    # ------------------------------------------------------------------
    # Composite industry-position score
    # ------------------------------------------------------------------
    def composite_score(self) -> dict:
        """
        Combine growth, margin, and valuation comparisons plus market
        share into a 0-100 score for firm-within-industry positioning.
        """
        sub_scores: list[tuple[float, float]] = []  # (score, weight)

        # Market share component (35%)
        share = self.firm.get("market_share")
        if share is not None:
            # Normalise: 0 % → 0, ≥ 40 % → 100
            s = min(100, max(0, (share / 40) * 100))
            sub_scores.append((s, 0.35))

        # Growth comparison component (25%)
        gc = self.compare_growth()
        if gc.get("delta_pp") is not None:
            # +10 pp → 100, -10 pp → 0
            s = min(100, max(0, ((gc["delta_pp"] + 10) / 20) * 100))
            sub_scores.append((s, 0.25))

        # Margin comparison component (25%)
        mc = self.compare_margins()
        if mc.get("delta_pp") is not None:
            s = min(100, max(0, ((mc["delta_pp"] + 10) / 20) * 100))
            sub_scores.append((s, 0.25))

        # Valuation premium component (15%)
        vc = self.compare_valuation()
        if vc.get("pe_ratio_vs_industry") is not None:
            # Being premium-valued indicates market confidence
            ratio = vc["pe_ratio_vs_industry"]
            s = min(100, max(0, (ratio / 2.0) * 100))
            sub_scores.append((s, 0.15))

        if not sub_scores:
            return {"score": None, "label": "Unrated"}

        total_w = sum(w for _, w in sub_scores)
        weighted = sum(s * w for s, w in sub_scores) / total_w
        return {
            "score": round(weighted, 1),
            "label": get_score_label(weighted),
            "position": self.classify_position(),
            "components_used": len(sub_scores),
        }

    # ------------------------------------------------------------------
    # Full comparison bundle
    # ------------------------------------------------------------------
    def full_comparison(self) -> dict:
        """Return the complete set of firm-vs-industry comparisons."""
        return {
            "firm": self.firm.firm_name,
            "ticker": self.firm.ticker,
            "industry": self.firm.industry,
            "position": self.classify_position(),
            "growth": self.compare_growth(),
            "margins": self.compare_margins(),
            "valuation": self.compare_valuation(),
            "industry_structure": self.industry_structure_summary(),
            "composite": self.composite_score(),
        }

    def __repr__(self) -> str:
        cs = self.composite_score()
        return (f"<IndustryPosition {self.firm.ticker} "
                f"position={self.classify_position()} "
                f"score={cs['score']}>")
