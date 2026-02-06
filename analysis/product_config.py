"""
Research Product Configuration
===============================
Defines the packaged research products: what variables, analyses, and
outputs are included for each research type and product tier.

Research Types
--------------
- competitive: Firm vs industry positioning, market share, competitive landscape
- pricing: Valuation, pricing power, margin analysis, inflation sensitivity
- economic: Macro alignment, GDP correlation, rate exposure, labor/trade context
- report: Comprehensive (all of the above combined)

Product Tiers
-------------
- basic: Single-firm snapshot with key metrics
- standard: Firm + industry comparison
- premium: Full micro + macro + US vs global + all research dimensions

Timeframes
----------
- current: Latest available data (point-in-time)
- quarterly: Quarter-over-quarter trends
- yearly: Year-over-year analysis
- historical: Multi-year trend analysis (3-5 years)
"""

from typing import Any

# ---------------------------------------------------------------------------
# Research type → variable sets
# ---------------------------------------------------------------------------
# Each research type focuses on a subset of variables for targeted analysis

RESEARCH_TYPE_VARIABLES = {
    "competitive": {
        "micro": [
            "revenue",
            "revenue_growth_yoy",
            "market_share",
            "market_share_delta_yoy",
            "operating_margin",
            "roe",
        ],
        "industry": [
            "industry_revenue_growth",
            "industry_total_market_size",
            "industry_hhi",
            "industry_num_major_competitors",
            "industry_entry_barrier_score",
        ],
        "macro": [],  # Competitive analysis is micro-focused
        "analyses": [
            "industry_position",
            "growth_comparison",
            "margin_comparison",
            "market_structure",
        ],
    },
    "pricing": {
        "micro": [
            "revenue",
            "gross_margin",
            "operating_margin",
            "net_margin",
            "pe_ratio",
            "ev_to_ebitda",
            "price_to_book",
        ],
        "industry": [
            "industry_avg_operating_margin",
            "industry_avg_pe",
        ],
        "macro": [
            "cpi_inflation_rate",
            "ppi_inflation_rate",
            "policy_interest_rate",
        ],
        "analyses": [
            "valuation_comparison",
            "margin_analysis",
            "inflation_sensitivity",
            "pricing_power",
        ],
    },
    "economic": {
        "micro": [
            "revenue_growth_yoy",
            "operating_margin",
            "debt_to_equity",
            "pe_ratio",
        ],
        "industry": [],  # Economic analysis is macro-focused
        "macro": [
            "gdp_growth_rate",
            "cpi_inflation_rate",
            "unemployment_rate",
            "policy_interest_rate",
            "sovereign_10y_yield",
            "equity_market_return_ytd",
            "trade_balance",
            "current_account_to_gdp",
        ],
        "analyses": [
            "growth_alignment",
            "inflation_sensitivity",
            "interest_rate_exposure",
            "labor_market_context",
            "valuation_vs_market",
            "trade_exposure",
            "us_vs_global",
        ],
    },
    "report": {
        # Comprehensive: includes everything
        "micro": "all",
        "industry": "all",
        "macro": "all",
        "analyses": "all",
    },
}

# ---------------------------------------------------------------------------
# Product tiers → scope and features
# ---------------------------------------------------------------------------

PRODUCT_TIERS = {
    "basic": {
        "name": "Basic Snapshot",
        "description": "Quick firm overview with key metrics",
        "includes": {
            "firm_metrics": True,
            "industry_comparison": False,
            "macro_analysis": False,
            "us_vs_global": False,
            "composite_scorecard": False,
            "risk_factors": False,
        },
        "output_sections": [
            "executive_summary",
            "firm_micro_analysis",
        ],
        "max_variables": 10,
    },
    "standard": {
        "name": "Standard Analysis",
        "description": "Firm + industry benchmarking",
        "includes": {
            "firm_metrics": True,
            "industry_comparison": True,
            "macro_analysis": False,
            "us_vs_global": False,
            "composite_scorecard": True,
            "risk_factors": True,
        },
        "output_sections": [
            "executive_summary",
            "industry_overview",
            "firm_micro_analysis",
            "firm_vs_industry",
            "composite_scorecard",
            "key_findings",
            "risk_factors",
        ],
        "max_variables": 25,
    },
    "premium": {
        "name": "Premium Research Report",
        "description": "Full micro + macro + global comparative analysis",
        "includes": {
            "firm_metrics": True,
            "industry_comparison": True,
            "macro_analysis": True,
            "us_vs_global": True,
            "composite_scorecard": True,
            "risk_factors": True,
        },
        "output_sections": "all",  # All sections from config.REPORT_SECTIONS
        "max_variables": None,  # Unlimited
    },
}

# ---------------------------------------------------------------------------
# Timeframe → data requirements
# ---------------------------------------------------------------------------

TIMEFRAME_CONFIG = {
    "current": {
        "periods_required": 1,
        "trend_analysis": False,
        "comparison_type": "point_in_time",
    },
    "quarterly": {
        "periods_required": 4,
        "trend_analysis": True,
        "comparison_type": "quarter_over_quarter",
    },
    "yearly": {
        "periods_required": 2,
        "trend_analysis": True,
        "comparison_type": "year_over_year",
    },
    "historical": {
        "periods_required": 5,
        "trend_analysis": True,
        "comparison_type": "multi_year_trend",
    },
}

# ---------------------------------------------------------------------------
# Additional variables by research type (beyond core framework)
# ---------------------------------------------------------------------------
# These are variables that SHOULD be added to enhance each research type

RECOMMENDED_ADDITIONS = {
    "competitive": {
        "variables": {
            "customer_concentration": {
                "label": "Customer Concentration (Top 10 %)",
                "unit": "%",
                "direction": "lower_better",
                "rationale": "Diversification reduces competitive risk",
            },
            "brand_value_score": {
                "label": "Brand Value Score (1-100)",
                "unit": "score",
                "direction": "higher_better",
                "rationale": "Brand strength drives pricing power and loyalty",
            },
            "patent_portfolio_count": {
                "label": "Active Patents",
                "unit": "count",
                "direction": "higher_better",
                "rationale": "IP moat indicates defensibility",
            },
            "switching_cost_score": {
                "label": "Customer Switching Cost (1-10)",
                "unit": "score",
                "direction": "higher_better",
                "rationale": "High switching costs protect market share",
            },
        },
    },
    "pricing": {
        "variables": {
            "price_elasticity_estimate": {
                "label": "Estimated Price Elasticity",
                "unit": "coefficient",
                "direction": "lower_better",
                "rationale": "Inelastic demand enables pricing power",
            },
            "asp_trend_yoy": {
                "label": "Average Selling Price Change (YoY %)",
                "unit": "%",
                "direction": "higher_better",
                "rationale": "Rising ASPs indicate pricing strength",
            },
            "cost_pass_through_rate": {
                "label": "Cost Pass-Through Rate (%)",
                "unit": "%",
                "direction": "higher_better",
                "rationale": "Ability to pass costs to customers",
            },
        },
    },
    "economic": {
        "variables": {
            "gdp_beta": {
                "label": "Revenue-to-GDP Beta",
                "unit": "coefficient",
                "direction": "neutral",
                "rationale": "Cyclicality exposure to economic growth",
            },
            "interest_coverage_ratio": {
                "label": "Interest Coverage Ratio",
                "unit": "x",
                "direction": "higher_better",
                "rationale": "Resilience to rate increases",
            },
            "forex_revenue_exposure": {
                "label": "Foreign Revenue Exposure (%)",
                "unit": "%",
                "direction": "neutral",
                "rationale": "Currency and global trade sensitivity",
            },
            "labor_cost_pct_revenue": {
                "label": "Labor Cost as % of Revenue",
                "unit": "%",
                "direction": "lower_better",
                "rationale": "Wage inflation sensitivity",
            },
        },
    },
}

# ---------------------------------------------------------------------------
# Packaging / Pricing structure (example tiers)
# ---------------------------------------------------------------------------

PRICING_MODEL = {
    "basic": {
        "price_usd": 49,
        "credits_required": 1,
        "turnaround": "instant",
    },
    "standard": {
        "price_usd": 199,
        "credits_required": 3,
        "turnaround": "instant",
    },
    "premium": {
        "price_usd": 499,
        "credits_required": 10,
        "turnaround": "instant",
    },
    "enterprise": {
        "price_usd": "custom",
        "credits_required": "unlimited",
        "turnaround": "scheduled",
        "features": [
            "API access",
            "Custom variables",
            "White-label reports",
            "Dedicated support",
        ],
    },
}


def get_variables_for_request(
    research_type: str,
    tier: str = "premium"
) -> dict[str, list[str]]:
    """
    Return the variable sets to use for a given research type and tier.
    """
    type_config = RESEARCH_TYPE_VARIABLES.get(research_type, {})
    tier_config = PRODUCT_TIERS.get(tier, PRODUCT_TIERS["premium"])

    result = {"micro": [], "industry": [], "macro": []}

    for scope in result:
        vars_list = type_config.get(scope, [])
        if vars_list == "all":
            result[scope] = "all"
        else:
            max_vars = tier_config.get("max_variables")
            if max_vars and len(vars_list) > max_vars:
                result[scope] = vars_list[:max_vars]
            else:
                result[scope] = vars_list

    return result


def get_analyses_for_request(research_type: str) -> list[str]:
    """Return the analysis types to run for a given research type."""
    type_config = RESEARCH_TYPE_VARIABLES.get(research_type, {})
    analyses = type_config.get("analyses", [])
    return analyses if analyses != "all" else ["all"]
