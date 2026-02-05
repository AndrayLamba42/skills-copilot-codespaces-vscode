"""
Composite Scorer
=================
Takes the output of FirmEconomyComparator and produces a single
composite scorecard that rates the firm's position relative to
the economy on a 0-100 scale across multiple dimensions.
"""

from __future__ import annotations

from typing import Any

from analysis.config import get_score_label
from analysis.engine.comparator import FirmEconomyComparator


class CompositeScorer:
    """Produce a multi-dimensional scorecard from comparator results."""

    # Dimension weights (sum to 1.0)
    DIMENSION_WEIGHTS = {
        "growth_alignment":       0.25,
        "inflation_resilience":   0.15,
        "rate_exposure":          0.10,
        "labor_context":          0.10,
        "valuation_attractiveness": 0.15,
        "industry_positioning":   0.25,
    }

    def __init__(self, comparator: FirmEconomyComparator):
        self.comparator = comparator
        self._comparison = comparator.full_comparison()

    # ------------------------------------------------------------------
    # Individual dimension scores (each returns 0-100)
    # ------------------------------------------------------------------
    def _score_growth(self) -> float | None:
        ga = self._comparison["comparisons"]["growth_alignment"]
        delta = ga.get("vs_us_gdp_delta")
        if delta is None:
            return None
        # Map: -10 pp → 0, +10 pp → 100
        return min(100, max(0, ((delta + 10) / 20) * 100))

    def _score_inflation(self) -> float | None:
        inf = self._comparison["comparisons"]["inflation_sensitivity"]
        ratio = inf.get("margin_to_cpi_ratio")
        if ratio is None:
            return None
        # ratio 0 → 0, ratio ≥ 5 → 100
        return min(100, max(0, (ratio / 5) * 100))

    def _score_rate_exposure(self) -> float | None:
        ire = self._comparison["comparisons"]["interest_rate_exposure"]
        product = ire.get("rate_sensitivity_product")
        if product is None:
            return None
        # Lower is better: product 0 → 100, product ≥ 10 → 0
        return min(100, max(0, ((10 - product) / 10) * 100))

    def _score_labor(self) -> float | None:
        lmc = self._comparison["comparisons"]["labor_market_context"]
        state = lmc.get("labor_market_state")
        margin = lmc.get("firm_operating_margin")
        if state is None or margin is None:
            return None
        # Balanced market + good margins is best
        state_bonus = {"tight": -10, "balanced": 10, "slack": 0}.get(state, 0)
        base = min(100, max(0, (margin / 25) * 100))
        return min(100, max(0, base + state_bonus))

    def _score_valuation(self) -> float | None:
        vm = self._comparison["comparisons"]["valuation_vs_market"]
        erp = vm.get("equity_risk_premium")
        if erp is None:
            return None
        # ERP: -2 → 0, +6 → 100
        return min(100, max(0, ((erp + 2) / 8) * 100))

    def _score_industry(self) -> float | None:
        ip = self._comparison.get("industry_position", {})
        composite = ip.get("composite", {})
        return composite.get("score")

    # ------------------------------------------------------------------
    # Composite scorecard
    # ------------------------------------------------------------------
    def scorecard(self) -> dict[str, Any]:
        """
        Return the full scorecard: per-dimension scores, weighted
        composite, and qualitative label.
        """
        scorers = {
            "growth_alignment": self._score_growth,
            "inflation_resilience": self._score_inflation,
            "rate_exposure": self._score_rate_exposure,
            "labor_context": self._score_labor,
            "valuation_attractiveness": self._score_valuation,
            "industry_positioning": self._score_industry,
        }

        dimensions: dict[str, dict] = {}
        weighted_sum = 0.0
        weight_sum = 0.0

        for dim, scorer in scorers.items():
            score = scorer()
            w = self.DIMENSION_WEIGHTS[dim]
            dimensions[dim] = {
                "score": round(score, 1) if score is not None else None,
                "label": get_score_label(score) if score is not None else "No Data",
                "weight": w,
            }
            if score is not None:
                weighted_sum += score * w
                weight_sum += w

        composite = round(weighted_sum / weight_sum, 1) if weight_sum > 0 else None

        return {
            "firm": self._comparison["firm"],
            "ticker": self._comparison["ticker"],
            "industry": self._comparison["industry"],
            "fiscal_year": self._comparison["fiscal_year"],
            "dimensions": dimensions,
            "composite_score": composite,
            "composite_label": (
                get_score_label(composite) if composite is not None else "Unrated"
            ),
            "dimensions_with_data": sum(
                1 for d in dimensions.values() if d["score"] is not None
            ),
            "total_dimensions": len(dimensions),
        }

    # ------------------------------------------------------------------
    # Key findings extraction
    # ------------------------------------------------------------------
    def key_findings(self) -> list[str]:
        """
        Generate a list of plain-English key findings based on the
        scorecard and underlying comparisons.
        """
        card = self.scorecard()
        findings: list[str] = []

        # Overall
        if card["composite_score"] is not None:
            findings.append(
                f"{card['firm']} ({card['ticker']}) receives an overall "
                f"economic-position score of {card['composite_score']}/100 "
                f"({card['composite_label']})."
            )

        # Growth
        ga = self._comparison["comparisons"]["growth_alignment"]
        if "vs_us_assessment" in ga:
            findings.append(
                f"Growth alignment: The firm is "
                f"{ga['vs_us_assessment'].replace('_', ' ')} "
                f"(revenue growth {ga.get('firm_revenue_growth')}% vs "
                f"US GDP growth {ga.get('us_gdp_growth')}%)."
            )

        # Inflation
        inf = self._comparison["comparisons"]["inflation_sensitivity"]
        if "pricing_power" in inf:
            findings.append(
                f"Pricing power assessment: {inf['pricing_power']} "
                f"(operating margin / CPI ratio = "
                f"{inf.get('margin_to_cpi_ratio')})."
            )

        # Rate exposure
        ire = self._comparison["comparisons"]["interest_rate_exposure"]
        if "exposure_assessment" in ire:
            findings.append(
                f"Interest rate exposure: {ire['exposure_assessment']} "
                f"(D/E = {ire.get('firm_debt_to_equity')}, "
                f"policy rate = {ire.get('us_policy_rate')}%)."
            )

        # Valuation
        vm = self._comparison["comparisons"]["valuation_vs_market"]
        if "erp_assessment" in vm:
            findings.append(
                f"Valuation vs bonds: {vm['erp_assessment'].replace('_', ' ')} "
                f"(earnings yield {vm.get('firm_earnings_yield')}% vs "
                f"10Y yield {vm.get('us_10y_yield')}%)."
            )

        # Industry position
        ip = self._comparison.get("industry_position", {})
        pos = ip.get("position", "unclassified")
        findings.append(
            f"Industry position: classified as '{pos}' within "
            f"{card['industry']}."
        )

        # Strongest / weakest dimensions
        dims = card["dimensions"]
        rated = {k: v for k, v in dims.items() if v["score"] is not None}
        if rated:
            best = max(rated, key=lambda k: rated[k]["score"])
            worst = min(rated, key=lambda k: rated[k]["score"])
            findings.append(
                f"Strongest dimension: {best.replace('_', ' ')} "
                f"({rated[best]['score']}/100)."
            )
            findings.append(
                f"Weakest dimension: {worst.replace('_', ' ')} "
                f"({rated[worst]['score']}/100)."
            )

        return findings

    # ------------------------------------------------------------------
    # Risk factors
    # ------------------------------------------------------------------
    def risk_factors(self) -> list[str]:
        """Identify key risk factors based on the analysis."""
        risks: list[str] = []

        ire = self._comparison["comparisons"]["interest_rate_exposure"]
        if ire.get("exposure_assessment") == "high":
            risks.append(
                "HIGH: Elevated interest-rate exposure due to high leverage "
                "in a rising-rate environment."
            )

        inf = self._comparison["comparisons"]["inflation_sensitivity"]
        if inf.get("pricing_power") == "weak":
            risks.append(
                "HIGH: Weak pricing power — margins may compress further "
                "if inflation persists."
            )

        ga = self._comparison["comparisons"]["growth_alignment"]
        if ga.get("vs_us_assessment") == "trailing_us_economy":
            risks.append(
                "MEDIUM: Firm growth trails the broader US economy, "
                "suggesting loss of competitive momentum."
            )

        ip = self._comparison.get("industry_position", {})
        structure = ip.get("industry_structure", {})
        if structure.get("regulatory_risk") is not None:
            if structure["regulatory_risk"] >= 7:
                risks.append(
                    "MEDIUM: Industry faces elevated regulatory risk "
                    f"(score {structure['regulatory_risk']}/10)."
                )

        if not risks:
            risks.append(
                "No major risk flags identified within the current dataset."
            )

        return risks

    def __repr__(self) -> str:
        card = self.scorecard()
        return (f"<CompositeScorer {card['ticker']} "
                f"composite={card['composite_score']}>")
