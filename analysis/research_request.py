"""
Research Request Model
=======================
The packaged entry point that ties together:
  1. Input validation (MarketResearchValidator)
  2. Product configuration (research type, tier, timeframe)
  3. Data loading
  4. Analysis execution
  5. Report generation

This is the "product" interface that external consumers would use.

Usage
-----
    from analysis.research_request import ResearchRequest

    request = ResearchRequest(
        industry="Technology",
        market="Cloud computing SaaS platforms for enterprise...",
        research_type="economic",
        timeframe="current",
        focus="economic_perspective",
        tier="premium",
    )

    # Validate inputs
    if not request.is_valid():
        print(request.validation_errors)

    # Load data and run analysis
    request.load_data(firm_data, industry_data, macro_us, macro_global)
    result = request.execute()

    # Get outputs
    print(result.report_text)
    print(result.report_json)
    print(result.scorecard)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from analysis.validation.market_validator import MarketResearchValidator
from analysis.product_config import (
    PRODUCT_TIERS,
    RESEARCH_TYPE_VARIABLES,
    TIMEFRAME_CONFIG,
    PRICING_MODEL,
    get_variables_for_request,
    get_analyses_for_request,
)
from analysis.macro.indicators import MacroIndicators
from analysis.micro.firm_metrics import FirmMetrics
from analysis.micro.industry_position import IndustryPosition
from analysis.engine.comparator import FirmEconomyComparator
from analysis.engine.scorer import CompositeScorer
from analysis.report.generator import ReportGenerator


@dataclass
class ResearchResult:
    """Container for analysis results."""

    request_id: str
    timestamp: str
    research_type: str
    tier: str
    firm_name: str
    ticker: str
    industry: str

    # Outputs
    scorecard: dict = field(default_factory=dict)
    key_findings: list = field(default_factory=list)
    risk_factors: list = field(default_factory=list)
    full_comparison: dict = field(default_factory=dict)
    report_text: str = ""
    report_json: str = ""

    # Metadata
    variables_analyzed: dict = field(default_factory=dict)
    analyses_run: list = field(default_factory=list)
    execution_time_ms: float = 0.0

    def to_dict(self) -> dict:
        """Return all results as a dictionary."""
        return {
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "research_type": self.research_type,
            "tier": self.tier,
            "firm": {
                "name": self.firm_name,
                "ticker": self.ticker,
                "industry": self.industry,
            },
            "scorecard": self.scorecard,
            "key_findings": self.key_findings,
            "risk_factors": self.risk_factors,
            "full_comparison": self.full_comparison,
            "variables_analyzed": self.variables_analyzed,
            "analyses_run": self.analyses_run,
            "execution_time_ms": self.execution_time_ms,
        }


class ResearchRequest:
    """
    Packaged research request that validates inputs, configures the
    analysis pipeline, and produces deliverable outputs.
    """

    def __init__(
        self,
        industry: str,
        market: str,
        research_type: str,
        timeframe: str = "current",
        focus: str = "comprehensive",
        tier: str = "premium",
        firm_name: Optional[str] = None,
        ticker: Optional[str] = None,
    ):
        # Request inputs
        self.industry = MarketResearchValidator.sanitize_input(industry)
        self.market = MarketResearchValidator.sanitize_input(market)
        self.research_type = research_type
        self.timeframe = timeframe
        self.focus = focus
        self.tier = tier
        self.firm_name = firm_name
        self.ticker = ticker

        # Validation state
        self._validated = False
        self._validation_errors: list[str] = []

        # Data containers
        self._firm: Optional[FirmMetrics] = None
        self._macro: Optional[MacroIndicators] = None
        self._industry_position: Optional[IndustryPosition] = None
        self._data_loaded = False

        # Request ID
        self._request_id = self._generate_request_id()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def validate(self) -> bool:
        """Run all input validations. Returns True if valid."""
        is_valid, errors = MarketResearchValidator.validate_all(
            industry=self.industry,
            market=self.market,
            research_type=self.research_type,
            timeframe=self.timeframe,
            focus=self.focus,
        )

        # Additional validation: tier
        if self.tier not in PRODUCT_TIERS:
            is_valid = False
            errors.append(
                f"Tier must be one of: {', '.join(PRODUCT_TIERS.keys())}"
            )

        self._validated = True
        self._validation_errors = errors
        return is_valid

    def is_valid(self) -> bool:
        """Check if request is valid. Runs validation if not yet done."""
        if not self._validated:
            return self.validate()
        return len(self._validation_errors) == 0

    @property
    def validation_errors(self) -> list[str]:
        """Return list of validation errors (empty if valid)."""
        if not self._validated:
            self.validate()
        return self._validation_errors

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------
    def load_data(
        self,
        firm_data: dict[str, Any],
        industry_data: dict[str, Any],
        macro_us: dict[str, Any],
        macro_global: dict[str, Any],
    ) -> None:
        """
        Load all required data for the analysis.

        Parameters
        ----------
        firm_data : dict
            Firm metrics (keys matching MICRO_VARIABLES).
            Must include 'firm_name', 'ticker', 'industry', 'fiscal_year'.
        industry_data : dict
            Industry benchmarks (keys matching INDUSTRY_VARIABLES).
        macro_us : dict
            US macro indicators (keys matching MACRO_VARIABLES).
        macro_global : dict
            Global macro indicators (keys matching MACRO_VARIABLES).
        """
        # Build macro
        self._macro = MacroIndicators(
            us_data=macro_us,
            global_data=macro_global,
        )

        # Build firm
        self._firm = FirmMetrics(
            firm_name=firm_data.get("firm_name", self.firm_name or "Unknown"),
            ticker=firm_data.get("ticker", self.ticker or "N/A"),
            industry=firm_data.get("industry", self.industry),
            data=firm_data.get("data", firm_data),
            fiscal_year=firm_data.get("fiscal_year"),
        )

        # Update request-level firm info
        self.firm_name = self._firm.firm_name
        self.ticker = self._firm.ticker

        # Build industry position
        self._industry_position = IndustryPosition(
            firm=self._firm,
            industry_data=industry_data,
        )

        self._data_loaded = True

    def load_from_json(self, json_path: str) -> None:
        """Load data from a JSON file (same format as sample_data.json)."""
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.load_data(
            firm_data=data["firm"],
            industry_data=data["industry"],
            macro_us=data["macro_us"],
            macro_global=data["macro_global"],
        )

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------
    def execute(self) -> ResearchResult:
        """
        Execute the research analysis and return packaged results.

        Raises
        ------
        ValueError
            If request is not valid or data is not loaded.
        """
        if not self.is_valid():
            raise ValueError(
                f"Request is not valid: {self._validation_errors}"
            )
        if not self._data_loaded:
            raise ValueError("Data not loaded. Call load_data() first.")

        import time
        start = time.perf_counter()

        # Build comparator
        comparator = FirmEconomyComparator(
            firm=self._firm,
            macro=self._macro,
            industry_position=self._industry_position,
        )

        # Build scorer
        scorer = CompositeScorer(comparator)

        # Build report generator
        report_gen = ReportGenerator(scorer)

        # Determine what to include based on tier
        tier_config = PRODUCT_TIERS[self.tier]

        # Generate outputs
        scorecard = scorer.scorecard()
        key_findings = scorer.key_findings()
        risk_factors = scorer.risk_factors() if tier_config["includes"]["risk_factors"] else []
        full_comparison = comparator.full_comparison()

        report_text = report_gen.generate()
        report_json = report_gen.to_json()

        elapsed_ms = (time.perf_counter() - start) * 1000

        # Build result
        result = ResearchResult(
            request_id=self._request_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            research_type=self.research_type,
            tier=self.tier,
            firm_name=self._firm.firm_name,
            ticker=self._firm.ticker,
            industry=self._firm.industry,
            scorecard=scorecard,
            key_findings=key_findings,
            risk_factors=risk_factors,
            full_comparison=full_comparison,
            report_text=report_text,
            report_json=report_json,
            variables_analyzed=get_variables_for_request(
                self.research_type, self.tier
            ),
            analyses_run=get_analyses_for_request(self.research_type),
            execution_time_ms=round(elapsed_ms, 2),
        )

        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _generate_request_id(self) -> str:
        """Generate a unique request ID."""
        import hashlib
        ts = datetime.now(timezone.utc).isoformat()
        payload = f"{ts}-{self.industry}-{self.research_type}-{self.tier}"
        return hashlib.sha256(payload.encode()).hexdigest()[:12]

    def get_pricing(self) -> dict:
        """Return pricing info for this request's tier."""
        return PRICING_MODEL.get(self.tier, PRICING_MODEL["premium"])

    def get_required_variables(self) -> dict:
        """Return the variables needed for this research type + tier."""
        return get_variables_for_request(self.research_type, self.tier)

    def summary(self) -> dict:
        """Return a summary of the request configuration."""
        return {
            "request_id": self._request_id,
            "industry": self.industry,
            "market_preview": self.market[:100] + "..." if len(self.market) > 100 else self.market,
            "research_type": self.research_type,
            "timeframe": self.timeframe,
            "focus": self.focus,
            "tier": self.tier,
            "tier_name": PRODUCT_TIERS[self.tier]["name"],
            "pricing": self.get_pricing(),
            "is_valid": self.is_valid(),
            "validation_errors": self.validation_errors,
            "data_loaded": self._data_loaded,
        }

    def __repr__(self) -> str:
        status = "valid" if self.is_valid() else "invalid"
        loaded = "loaded" if self._data_loaded else "no data"
        return (
            f"<ResearchRequest {self._request_id} "
            f"type={self.research_type} tier={self.tier} "
            f"[{status}, {loaded}]>"
        )
