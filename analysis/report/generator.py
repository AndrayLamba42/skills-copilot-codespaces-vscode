"""
Report Generator
=================
Transforms the structured output of CompositeScorer (and its underlying
modules) into a readable, plain-text research report.

The report follows the section ordering defined in config.REPORT_SECTIONS.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from analysis.config import MACRO_VARIABLES, MICRO_VARIABLES, REPORT_SECTIONS
from analysis.engine.comparator import FirmEconomyComparator
from analysis.engine.scorer import CompositeScorer
from analysis.macro.global_comparison import GlobalComparison


class ReportGenerator:
    """Generate a full-text research report from analysis results."""

    SEPARATOR = "=" * 72
    SUB_SEP = "-" * 72

    def __init__(self, scorer: CompositeScorer):
        self.scorer = scorer
        self.comparator = scorer.comparator
        self.card = scorer.scorecard()
        self.comp = scorer.comparator.full_comparison()

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------
    def generate(self) -> str:
        """Return the complete report as a string."""
        sections = {
            "executive_summary":   self._executive_summary,
            "macro_us":            self._macro_us,
            "macro_global":        self._macro_global,
            "macro_comparison":    self._macro_comparison,
            "industry_overview":   self._industry_overview,
            "firm_micro_analysis": self._firm_micro,
            "firm_vs_industry":    self._firm_vs_industry,
            "firm_vs_economy":     self._firm_vs_economy,
            "composite_scorecard": self._scorecard,
            "key_findings":        self._key_findings,
            "risk_factors":        self._risk_factors,
            "methodology_notes":   self._methodology,
        }

        parts: list[str] = [self._header()]
        for section_key in REPORT_SECTIONS:
            builder = sections.get(section_key)
            if builder:
                parts.append(builder())
        parts.append(self._footer())
        return "\n\n".join(parts)

    # ------------------------------------------------------------------
    # Header / Footer
    # ------------------------------------------------------------------
    def _header(self) -> str:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        return (
            f"{self.SEPARATOR}\n"
            f"  FIRM PERFORMANCE vs ECONOMY — RESEARCH REPORT\n"
            f"{self.SEPARATOR}\n"
            f"  Company : {self.card['firm']} ({self.card['ticker']})\n"
            f"  Industry: {self.card['industry']}\n"
            f"  Period  : {self.card['fiscal_year'] or 'N/A'}\n"
            f"  Generated: {now}\n"
            f"{self.SEPARATOR}"
        )

    def _footer(self) -> str:
        return (
            f"{self.SEPARATOR}\n"
            f"  END OF REPORT\n"
            f"  Disclaimer: This report is generated for research purposes\n"
            f"  only and does not constitute investment advice.\n"
            f"{self.SEPARATOR}"
        )

    # ------------------------------------------------------------------
    # Section builders
    # ------------------------------------------------------------------
    def _executive_summary(self) -> str:
        findings = self.scorer.key_findings()
        lines = [f"EXECUTIVE SUMMARY\n{self.SUB_SEP}"]
        for i, f in enumerate(findings, 1):
            lines.append(f"  {i}. {f}")
        return "\n".join(lines)

    def _macro_us(self) -> str:
        lines = [f"US MACROECONOMIC ENVIRONMENT\n{self.SUB_SEP}"]
        table = self.comparator.macro.us_vs_global_table()
        for row in table:
            us = row["us_value"]
            if us is not None:
                lines.append(
                    f"  {row['variable']:<45} {us:>10} {row['unit']}"
                )
        return "\n".join(lines)

    def _macro_global(self) -> str:
        lines = [f"GLOBAL MACROECONOMIC ENVIRONMENT\n{self.SUB_SEP}"]
        table = self.comparator.macro.us_vs_global_table()
        for row in table:
            gl = row["global_value"]
            if gl is not None:
                lines.append(
                    f"  {row['variable']:<45} {gl:>10} {row['unit']}"
                )
        return "\n".join(lines)

    def _macro_comparison(self) -> str:
        gc = GlobalComparison(self.comparator.macro)
        sw = gc.strengths_and_weaknesses()
        comp = gc.composite_score()
        lines = [f"US vs GLOBAL MACRO COMPARISON\n{self.SUB_SEP}"]
        lines.append(
            f"  Composite US-vs-Global Score: {comp['score']}/100 "
            f"({comp['label']})"
        )
        lines.append("")
        lines.append("  US Relative Strengths:")
        for s in sw["us_strengths"]:
            lines.append(f"    + {s}")
        lines.append("  US Relative Weaknesses:")
        for w in sw["us_weaknesses"]:
            lines.append(f"    - {w}")
        return "\n".join(lines)

    def _industry_overview(self) -> str:
        ip = self.comp.get("industry_position", {})
        structure = ip.get("industry_structure", {})
        lines = [f"INDUSTRY OVERVIEW: {self.card['industry'].upper()}\n{self.SUB_SEP}"]
        for key, val in structure.items():
            lines.append(f"  {key.replace('_', ' ').title():<40} {val}")
        return "\n".join(lines)

    def _firm_micro(self) -> str:
        lines = [f"FIRM MICRO ANALYSIS: {self.card['firm'].upper()}\n{self.SUB_SEP}"]
        cats = self.comparator.firm.by_category()
        for cat, data in cats.items():
            lines.append(f"\n  [{cat.replace('_', ' ').upper()}]")
            for key, info in data["variables"].items():
                val = info["value"]
                if val is not None:
                    lines.append(
                        f"    {info['label']:<40} {val:>10} {info['unit']}"
                    )
        return "\n".join(lines)

    def _firm_vs_industry(self) -> str:
        ip = self.comp.get("industry_position", {})
        lines = [f"FIRM vs INDUSTRY COMPARISON\n{self.SUB_SEP}"]
        lines.append(f"  Competitive Position : {ip.get('position', 'N/A')}")

        growth = ip.get("growth", {})
        if growth.get("assessment") != "no_data":
            lines.append(
                f"  Growth vs Industry   : {growth.get('assessment', 'N/A')} "
                f"(firm {growth.get('firm_growth')}% vs "
                f"industry {growth.get('industry_growth')}%)"
            )

        margins = ip.get("margins", {})
        if margins.get("assessment") != "no_data":
            lines.append(
                f"  Margin vs Industry   : {margins.get('assessment', 'N/A')} "
                f"(firm {margins.get('firm_margin')}% vs "
                f"industry {margins.get('industry_avg_margin')}%)"
            )

        val = ip.get("valuation", {})
        if val.get("assessment") != "no_data":
            lines.append(
                f"  Valuation vs Industry: {val.get('assessment', 'N/A')} "
                f"(firm P/E {val.get('firm_pe')}x vs "
                f"industry {val.get('industry_avg_pe')}x)"
            )

        composite = ip.get("composite", {})
        lines.append(
            f"  Industry Position Score: "
            f"{composite.get('score', 'N/A')}/100 "
            f"({composite.get('label', 'N/A')})"
        )
        return "\n".join(lines)

    def _firm_vs_economy(self) -> str:
        comps = self.comp["comparisons"]
        lines = [f"FIRM vs ECONOMY COMPARISON\n{self.SUB_SEP}"]

        # Growth
        ga = comps["growth_alignment"]
        lines.append(f"\n  [GROWTH ALIGNMENT]")
        if "vs_us_assessment" in ga:
            lines.append(
                f"    vs US GDP    : {ga['vs_us_assessment']} "
                f"(delta {ga['vs_us_gdp_delta']:+.1f} pp)"
            )
        if "vs_global_assessment" in ga:
            lines.append(
                f"    vs Global GDP: {ga['vs_global_assessment']} "
                f"(delta {ga['vs_global_gdp_delta']:+.1f} pp)"
            )

        # Inflation
        inf = comps["inflation_sensitivity"]
        lines.append(f"\n  [INFLATION SENSITIVITY]")
        if "pricing_power" in inf:
            lines.append(
                f"    Pricing Power: {inf['pricing_power']} "
                f"(margin/CPI = {inf['margin_to_cpi_ratio']})"
            )

        # Rate exposure
        ire = comps["interest_rate_exposure"]
        lines.append(f"\n  [INTEREST RATE EXPOSURE]")
        if "exposure_assessment" in ire:
            lines.append(
                f"    Exposure: {ire['exposure_assessment']} "
                f"(D/E × rate = {ire['rate_sensitivity_product']})"
            )

        # Valuation
        vm = comps["valuation_vs_market"]
        lines.append(f"\n  [VALUATION vs BONDS]")
        if "erp_assessment" in vm:
            lines.append(
                f"    Assessment: {vm['erp_assessment']} "
                f"(ERP = {vm['equity_risk_premium']}%)"
            )

        return "\n".join(lines)

    def _scorecard(self) -> str:
        lines = [f"COMPOSITE SCORECARD\n{self.SUB_SEP}"]
        for dim, info in self.card["dimensions"].items():
            score_str = (
                f"{info['score']:5.1f}" if info["score"] is not None
                else "  N/A"
            )
            lines.append(
                f"  {dim.replace('_', ' ').title():<35} "
                f"{score_str}/100  ({info['label']})  "
                f"[weight {info['weight']:.0%}]"
            )
        lines.append(f"\n  {'COMPOSITE':.<35} "
                      f"{self.card['composite_score']}/100  "
                      f"({self.card['composite_label']})")
        lines.append(
            f"  Data coverage: {self.card['dimensions_with_data']}"
            f"/{self.card['total_dimensions']} dimensions scored"
        )
        return "\n".join(lines)

    def _key_findings(self) -> str:
        lines = [f"KEY FINDINGS\n{self.SUB_SEP}"]
        for i, f in enumerate(self.scorer.key_findings(), 1):
            lines.append(f"  {i}. {f}")
        return "\n".join(lines)

    def _risk_factors(self) -> str:
        lines = [f"RISK FACTORS\n{self.SUB_SEP}"]
        for r in self.scorer.risk_factors():
            lines.append(f"  * {r}")
        return "\n".join(lines)

    def _methodology(self) -> str:
        return (
            f"METHODOLOGY NOTES\n{self.SUB_SEP}\n"
            f"  - Macro variables tracked : {len(MACRO_VARIABLES)}\n"
            f"  - Micro variables tracked : {len(MICRO_VARIABLES)}\n"
            f"  - Scoring scale           : 0-100 (weighted composite)\n"
            f"  - Direction conventions   : 'higher_better', 'lower_better',\n"
            f"                              'neutral' per variable\n"
            f"  - Industry position model : market-share thresholds +\n"
            f"                              growth/margin/valuation deltas\n"
            f"  - Firm-vs-economy model   : growth alignment, inflation\n"
            f"                              sensitivity, rate exposure,\n"
            f"                              labor context, valuation vs bonds\n"
            f"  - Data source expectation : User-supplied JSON; plug in\n"
            f"                              live API feeds as needed"
        )

    # ------------------------------------------------------------------
    # JSON export
    # ------------------------------------------------------------------
    def to_json(self) -> str:
        """Export the full comparison data and scorecard as JSON."""
        payload = {
            "scorecard": self.card,
            "full_comparison": self.comp,
            "key_findings": self.scorer.key_findings(),
            "risk_factors": self.scorer.risk_factors(),
        }
        return json.dumps(payload, indent=2, default=str)
