"""
Configuration and variable definitions for the economic research framework.

This module defines the full taxonomy of micro and macro variables used
throughout the analysis, along with their metadata (units, direction,
category, and weight in composite scoring).
"""

# ---------------------------------------------------------------------------
# Macro-economic variable definitions
# ---------------------------------------------------------------------------
# Each variable carries:
#   label       – human-readable name
#   unit        – measurement unit
#   direction   – "higher_better" or "lower_better" for scoring purposes
#   category    – grouping for report sections
#   weight      – default weight in composite macro score (sums to 1.0)

MACRO_VARIABLES = {
    # --- Output & Growth ---
    "gdp_growth_rate": {
        "label": "Real GDP Growth Rate",
        "unit": "%",
        "direction": "higher_better",
        "category": "output_growth",
        "weight": 0.15,
    },
    "gdp_per_capita": {
        "label": "GDP Per Capita (PPP)",
        "unit": "USD",
        "direction": "higher_better",
        "category": "output_growth",
        "weight": 0.05,
    },
    "industrial_production_index": {
        "label": "Industrial Production Index (YoY %)",
        "unit": "%",
        "direction": "higher_better",
        "category": "output_growth",
        "weight": 0.05,
    },
    # --- Price Stability ---
    "cpi_inflation_rate": {
        "label": "CPI Inflation Rate",
        "unit": "%",
        "direction": "lower_better",
        "category": "price_stability",
        "weight": 0.10,
    },
    "ppi_inflation_rate": {
        "label": "PPI Inflation Rate",
        "unit": "%",
        "direction": "lower_better",
        "category": "price_stability",
        "weight": 0.05,
    },
    # --- Labor Market ---
    "unemployment_rate": {
        "label": "Unemployment Rate",
        "unit": "%",
        "direction": "lower_better",
        "category": "labor_market",
        "weight": 0.10,
    },
    "labor_force_participation": {
        "label": "Labor Force Participation Rate",
        "unit": "%",
        "direction": "higher_better",
        "category": "labor_market",
        "weight": 0.05,
    },
    # --- Monetary Policy ---
    "policy_interest_rate": {
        "label": "Central Bank Policy Rate",
        "unit": "%",
        "direction": "neutral",
        "category": "monetary_policy",
        "weight": 0.05,
    },
    "money_supply_m2_growth": {
        "label": "M2 Money Supply Growth (YoY %)",
        "unit": "%",
        "direction": "neutral",
        "category": "monetary_policy",
        "weight": 0.03,
    },
    # --- Fiscal Position ---
    "govt_debt_to_gdp": {
        "label": "Government Debt-to-GDP Ratio",
        "unit": "%",
        "direction": "lower_better",
        "category": "fiscal_position",
        "weight": 0.07,
    },
    "fiscal_deficit_to_gdp": {
        "label": "Fiscal Deficit as % of GDP",
        "unit": "%",
        "direction": "lower_better",
        "category": "fiscal_position",
        "weight": 0.05,
    },
    # --- Trade & External ---
    "current_account_to_gdp": {
        "label": "Current Account Balance (% of GDP)",
        "unit": "%",
        "direction": "higher_better",
        "category": "trade_external",
        "weight": 0.05,
    },
    "trade_balance": {
        "label": "Trade Balance",
        "unit": "USD (billions)",
        "direction": "higher_better",
        "category": "trade_external",
        "weight": 0.05,
    },
    # --- Financial Markets ---
    "equity_market_return_ytd": {
        "label": "Equity Market Return (YTD)",
        "unit": "%",
        "direction": "higher_better",
        "category": "financial_markets",
        "weight": 0.05,
    },
    "sovereign_10y_yield": {
        "label": "10-Year Sovereign Bond Yield",
        "unit": "%",
        "direction": "neutral",
        "category": "financial_markets",
        "weight": 0.05,
    },
}

# ---------------------------------------------------------------------------
# Micro-economic (firm-level) variable definitions
# ---------------------------------------------------------------------------

MICRO_VARIABLES = {
    # --- Profitability ---
    "revenue": {
        "label": "Total Revenue",
        "unit": "USD (millions)",
        "direction": "higher_better",
        "category": "profitability",
        "weight": 0.10,
    },
    "revenue_growth_yoy": {
        "label": "Revenue Growth (YoY %)",
        "unit": "%",
        "direction": "higher_better",
        "category": "profitability",
        "weight": 0.10,
    },
    "gross_margin": {
        "label": "Gross Profit Margin",
        "unit": "%",
        "direction": "higher_better",
        "category": "profitability",
        "weight": 0.08,
    },
    "operating_margin": {
        "label": "Operating Margin",
        "unit": "%",
        "direction": "higher_better",
        "category": "profitability",
        "weight": 0.08,
    },
    "net_margin": {
        "label": "Net Profit Margin",
        "unit": "%",
        "direction": "higher_better",
        "category": "profitability",
        "weight": 0.08,
    },
    "roe": {
        "label": "Return on Equity",
        "unit": "%",
        "direction": "higher_better",
        "category": "profitability",
        "weight": 0.06,
    },
    "roa": {
        "label": "Return on Assets",
        "unit": "%",
        "direction": "higher_better",
        "category": "profitability",
        "weight": 0.05,
    },
    # --- Valuation ---
    "market_cap": {
        "label": "Market Capitalization",
        "unit": "USD (millions)",
        "direction": "higher_better",
        "category": "valuation",
        "weight": 0.05,
    },
    "pe_ratio": {
        "label": "Price-to-Earnings Ratio",
        "unit": "x",
        "direction": "neutral",
        "category": "valuation",
        "weight": 0.05,
    },
    "ev_to_ebitda": {
        "label": "EV/EBITDA",
        "unit": "x",
        "direction": "neutral",
        "category": "valuation",
        "weight": 0.04,
    },
    "price_to_book": {
        "label": "Price-to-Book Ratio",
        "unit": "x",
        "direction": "neutral",
        "category": "valuation",
        "weight": 0.03,
    },
    # --- Market Position ---
    "market_share": {
        "label": "Estimated Market Share",
        "unit": "%",
        "direction": "higher_better",
        "category": "market_position",
        "weight": 0.08,
    },
    "market_share_delta_yoy": {
        "label": "Market Share Change (YoY pp)",
        "unit": "pp",
        "direction": "higher_better",
        "category": "market_position",
        "weight": 0.05,
    },
    # --- Efficiency & Leverage ---
    "debt_to_equity": {
        "label": "Debt-to-Equity Ratio",
        "unit": "x",
        "direction": "lower_better",
        "category": "efficiency_leverage",
        "weight": 0.05,
    },
    "current_ratio": {
        "label": "Current Ratio",
        "unit": "x",
        "direction": "higher_better",
        "category": "efficiency_leverage",
        "weight": 0.03,
    },
    "asset_turnover": {
        "label": "Asset Turnover Ratio",
        "unit": "x",
        "direction": "higher_better",
        "category": "efficiency_leverage",
        "weight": 0.04,
    },
    # --- Innovation & Investment ---
    "rd_to_revenue": {
        "label": "R&D Spending as % of Revenue",
        "unit": "%",
        "direction": "higher_better",
        "category": "innovation",
        "weight": 0.03,
    },
}

# ---------------------------------------------------------------------------
# Industry variable definitions (for benchmarking the firm)
# ---------------------------------------------------------------------------

INDUSTRY_VARIABLES = {
    "industry_revenue_growth": {
        "label": "Industry Revenue Growth (YoY %)",
        "unit": "%",
        "direction": "higher_better",
        "category": "industry_health",
        "weight": 0.20,
    },
    "industry_avg_operating_margin": {
        "label": "Industry Avg Operating Margin",
        "unit": "%",
        "direction": "higher_better",
        "category": "industry_health",
        "weight": 0.15,
    },
    "industry_avg_pe": {
        "label": "Industry Avg P/E Ratio",
        "unit": "x",
        "direction": "neutral",
        "category": "industry_health",
        "weight": 0.10,
    },
    "industry_total_market_size": {
        "label": "Total Addressable Market Size",
        "unit": "USD (billions)",
        "direction": "higher_better",
        "category": "industry_health",
        "weight": 0.15,
    },
    "industry_hhi": {
        "label": "Herfindahl-Hirschman Index (HHI)",
        "unit": "index (0-10000)",
        "direction": "neutral",
        "category": "industry_structure",
        "weight": 0.10,
    },
    "industry_num_major_competitors": {
        "label": "Number of Major Competitors",
        "unit": "count",
        "direction": "neutral",
        "category": "industry_structure",
        "weight": 0.05,
    },
    "industry_entry_barrier_score": {
        "label": "Barrier to Entry Score (1-10)",
        "unit": "score",
        "direction": "neutral",
        "category": "industry_structure",
        "weight": 0.10,
    },
    "industry_regulatory_risk_score": {
        "label": "Regulatory Risk Score (1-10)",
        "unit": "score",
        "direction": "lower_better",
        "category": "industry_risk",
        "weight": 0.10,
    },
    "industry_tech_disruption_score": {
        "label": "Technology Disruption Risk (1-10)",
        "unit": "score",
        "direction": "neutral",
        "category": "industry_risk",
        "weight": 0.05,
    },
}

# ---------------------------------------------------------------------------
# Scoring configuration
# ---------------------------------------------------------------------------

SCORE_SCALE = {"min": 0, "max": 100}

# Thresholds for qualitative labels
SCORE_LABELS = {
    (90, 100): "Exceptional",
    (75, 89):  "Strong",
    (60, 74):  "Above Average",
    (40, 59):  "Average",
    (25, 39):  "Below Average",
    (10, 24):  "Weak",
    (0, 9):    "Critical",
}


def get_score_label(score: float) -> str:
    """Return a qualitative label for a numeric score."""
    for (lo, hi), label in SCORE_LABELS.items():
        if lo <= score <= hi:
            return label
    return "Unrated"


# ---------------------------------------------------------------------------
# Report sections (ordered)
# ---------------------------------------------------------------------------

REPORT_SECTIONS = [
    "executive_summary",
    "macro_us",
    "macro_global",
    "macro_comparison",
    "industry_overview",
    "firm_micro_analysis",
    "firm_vs_industry",
    "firm_vs_economy",
    "composite_scorecard",
    "key_findings",
    "risk_factors",
    "methodology_notes",
]
