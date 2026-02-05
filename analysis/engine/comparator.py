"""
Firm-vs-Economy Comparator
===========================
The central comparison engine.  It ties together macro indicators, firm
micro metrics, and industry positioning to answer the core research
question: *How does this firm's market position compare to the broader
US and global economy?*

Key outputs
-----------
- Firm growth vs GDP growth (is the firm growing faster than the economy?)
- Firm profitability vs economy-wide trends
- Firm valuation relative to macro financial-market conditions
- Firm leverage vs sovereign fiscal health
- Composite "economic alignment" scorecard
"""

from __future__ import annotations

from typing import Any

from analysis.config import get_score_label
from analysis.macro.indicators import MacroIndicators
from analysis.macro.global_comparison import GlobalComparison
from analysis.micro.firm_metrics import FirmMetrics
from analysis.micro.industry_position import IndustryPosition


class FirmEconomyComparator:
    """Compare a firm's micro performance against macro economic backdrop."""

    def __init__(
        self,
        firm: FirmMetrics,
        macro: MacroIndicators,
        industry_position: IndustryPosition,
    ):
        self.firm = firm
        self.macro = macro
        self.industry_position = industry_position
        self.global_comp = GlobalComparison(macro)

    # ------------------------------------------------------------------
    # 1. Growth alignment  (firm revenue growth vs GDP growth)
    # ------------------------------------------------------------------
    def growth_alignment(self) -> dict[str, Any]:
        """
        Compare firm revenue growth against US and global real GDP growth.
        A firm growing faster than the economy is *outperforming* the
        macro cycle.
        """
        firm_growth = self.firm.get("revenue_growth_yoy")
        us_gdp = self.macro.get_us("gdp_growth_rate")
        gl_gdp = self.macro.get_global("gdp_growth_rate")

        result: dict[str, Any] = {
            "firm_revenue_growth": firm_growth,
            "us_gdp_growth": us_gdp,
            "global_gdp_growth": gl_gdp,
        }

        if firm_growth is not None and us_gdp is not None:
            delta_us = firm_growth - us_gdp
            result["vs_us_gdp_delta"] = round(delta_us, 2)
            result["vs_us_assessment"] = (
                "outpacing_us_economy" if delta_us > 2
                else "trailing_us_economy" if delta_us < -2
                else "tracking_us_economy"
            )
        if firm_growth is not None and gl_gdp is not None:
            delta_gl = firm_growth - gl_gdp
            result["vs_global_gdp_delta"] = round(delta_gl, 2)
            result["vs_global_assessment"] = (
                "outpacing_global_economy" if delta_gl > 2
                else "trailing_global_economy" if delta_gl < -2
                else "tracking_global_economy"
            )
        return result

    # ------------------------------------------------------------------
    # 2. Inflation sensitivity
    # ------------------------------------------------------------------
    def inflation_sensitivity(self) -> dict[str, Any]:
        """
        Evaluate whether the firm's margins can withstand inflationary
        pressure by comparing margin trends against CPI and PPI.
        """
        gross_m = self.firm.get("gross_margin")
        op_m = self.firm.get("operating_margin")
        cpi = self.macro.get_us("cpi_inflation_rate")
        ppi = self.macro.get_us("ppi_inflation_rate")

        result: dict[str, Any] = {
            "firm_gross_margin": gross_m,
            "firm_operating_margin": op_m,
            "us_cpi": cpi,
            "us_ppi": ppi,
        }

        if op_m is not None and cpi is not None:
            # Simple heuristic: if operating margin > 3x CPI, firm has
            # strong pricing power / cost control.
            ratio = op_m / cpi if cpi != 0 else None
            result["margin_to_cpi_ratio"] = (
                round(ratio, 2) if ratio is not None else None
            )
            if ratio is not None:
                if ratio >= 3:
                    result["pricing_power"] = "strong"
                elif ratio >= 1.5:
                    result["pricing_power"] = "moderate"
                else:
                    result["pricing_power"] = "weak"
        return result

    # ------------------------------------------------------------------
    # 3. Interest-rate exposure
    # ------------------------------------------------------------------
    def interest_rate_exposure(self) -> dict[str, Any]:
        """
        Cross-reference firm leverage (debt/equity) against the
        prevailing policy rate and 10-year yield to gauge financing
        risk.
        """
        d_e = self.firm.get("debt_to_equity")
        policy_rate = self.macro.get_us("policy_interest_rate")
        ten_y = self.macro.get_us("sovereign_10y_yield")

        result: dict[str, Any] = {
            "firm_debt_to_equity": d_e,
            "us_policy_rate": policy_rate,
            "us_10y_yield": ten_y,
        }

        if d_e is not None and policy_rate is not None:
            # High leverage + high rates = elevated risk
            risk_product = d_e * policy_rate
            if risk_product > 5:
                exposure = "high"
            elif risk_product > 2:
                exposure = "moderate"
            else:
                exposure = "low"
            result["rate_sensitivity_product"] = round(risk_product, 2)
            result["exposure_assessment"] = exposure
        return result

    # ------------------------------------------------------------------
    # 4. Labor-market alignment
    # ------------------------------------------------------------------
    def labor_market_context(self) -> dict[str, Any]:
        """
        Contextualise firm performance within the labor market.
        Tight labor markets (low unemployment) can pressure wages,
        impacting margins, but also indicate strong demand.
        """
        unemp = self.macro.get_us("unemployment_rate")
        lfpr = self.macro.get_us("labor_force_participation")
        op_m = self.firm.get("operating_margin")

        result: dict[str, Any] = {
            "us_unemployment": unemp,
            "us_lfpr": lfpr,
            "firm_operating_margin": op_m,
        }

        if unemp is not None:
            if unemp < 4.0:
                result["labor_market_state"] = "tight"
                result["wage_pressure_risk"] = "elevated"
            elif unemp < 6.0:
                result["labor_market_state"] = "balanced"
                result["wage_pressure_risk"] = "moderate"
            else:
                result["labor_market_state"] = "slack"
                result["wage_pressure_risk"] = "low"
        return result

    # ------------------------------------------------------------------
    # 5. Market-valuation context
    # ------------------------------------------------------------------
    def valuation_vs_market(self) -> dict[str, Any]:
        """
        Compare firm P/E against equity-market YTD return and
        sovereign yields to judge if the firm trades at a premium
        or discount relative to the broader market environment.
        """
        pe = self.firm.get("pe_ratio")
        mkt_ret = self.macro.get_us("equity_market_return_ytd")
        ten_y = self.macro.get_us("sovereign_10y_yield")

        result: dict[str, Any] = {
            "firm_pe": pe,
            "us_equity_market_ytd": mkt_ret,
            "us_10y_yield": ten_y,
        }

        if pe is not None and ten_y is not None and ten_y > 0:
            # Earnings yield vs bond yield (crude equity risk premium)
            earnings_yield = (1 / pe) * 100 if pe > 0 else 0
            erp = earnings_yield - ten_y
            result["firm_earnings_yield"] = round(earnings_yield, 2)
            result["equity_risk_premium"] = round(erp, 2)
            if erp > 3:
                result["erp_assessment"] = "attractive_vs_bonds"
            elif erp > 0:
                result["erp_assessment"] = "moderate_vs_bonds"
            else:
                result["erp_assessment"] = "unattractive_vs_bonds"
        return result

    # ------------------------------------------------------------------
    # 6. Trade / external exposure
    # ------------------------------------------------------------------
    def trade_exposure_context(self) -> dict[str, Any]:
        """
        Summarise the macro trade environment as context for firms
        with international revenue exposure.
        """
        ca = self.macro.get_us("current_account_to_gdp")
        tb = self.macro.get_us("trade_balance")
        gl_ca = self.macro.get_global("current_account_to_gdp")

        return {
            "us_current_account_pct_gdp": ca,
            "us_trade_balance_bn": tb,
            "global_current_account_pct_gdp": gl_ca,
            "macro_trade_environment": (
                "deficit" if (tb is not None and tb < 0) else
                "surplus" if (tb is not None and tb > 0) else
                "balanced"
            ),
        }

    # ------------------------------------------------------------------
    # Full comparison bundle
    # ------------------------------------------------------------------
    def full_comparison(self) -> dict[str, Any]:
        """Run every comparison and return as a structured dict."""
        return {
            "firm": self.firm.firm_name,
            "ticker": self.firm.ticker,
            "industry": self.firm.industry,
            "fiscal_year": self.firm.fiscal_year,
            "comparisons": {
                "growth_alignment": self.growth_alignment(),
                "inflation_sensitivity": self.inflation_sensitivity(),
                "interest_rate_exposure": self.interest_rate_exposure(),
                "labor_market_context": self.labor_market_context(),
                "valuation_vs_market": self.valuation_vs_market(),
                "trade_exposure_context": self.trade_exposure_context(),
            },
            "industry_position": self.industry_position.full_comparison(),
            "us_vs_global_macro": self.global_comp.composite_score(),
        }

    def __repr__(self) -> str:
        return (f"<FirmEconomyComparator firm={self.firm.ticker} "
                f"macro_vars={len(self.macro.available_variables('us'))}>")
