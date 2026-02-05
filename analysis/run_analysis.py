#!/usr/bin/env python3
"""
Firm Performance vs Economy — Research Analysis Runner
=======================================================
Entry point that wires together every module in the framework:

    1. Loads economic data (firm, industry, US macro, global macro)
    2. Builds the Macro, Micro, and Industry objects
    3. Runs the FirmEconomyComparator
    4. Scores via CompositeScorer
    5. Generates the full research report (text + JSON)

Usage
-----
    python -m analysis.run_analysis                       # uses default sample data
    python -m analysis.run_analysis path/to/custom.json   # uses your own dataset

Data Format
-----------
See analysis/data/sample_data.json for the expected JSON schema.
"""

from __future__ import annotations

import json
import os
import sys

from analysis.macro.indicators import MacroIndicators
from analysis.micro.firm_metrics import FirmMetrics
from analysis.micro.industry_position import IndustryPosition
from analysis.engine.comparator import FirmEconomyComparator
from analysis.engine.scorer import CompositeScorer
from analysis.report.generator import ReportGenerator


DEFAULT_DATA = os.path.join(os.path.dirname(__file__), "data", "sample_data.json")


def load_data(path: str) -> dict:
    """Load and return the JSON dataset."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_analysis(data: dict) -> tuple[CompositeScorer, ReportGenerator]:
    """
    Construct the full analysis pipeline from a data dict and return
    the scorer and report generator.
    """
    # --- Macro ---
    macro = MacroIndicators(
        us_data=data["macro_us"],
        global_data=data["macro_global"],
    )
    print(f"  Macro indicators loaded: {macro}")

    # --- Firm ---
    firm_cfg = data["firm"]
    firm = FirmMetrics(
        firm_name=firm_cfg["firm_name"],
        ticker=firm_cfg["ticker"],
        industry=firm_cfg["industry"],
        data=firm_cfg["data"],
        fiscal_year=firm_cfg.get("fiscal_year"),
    )
    print(f"  Firm metrics loaded: {firm}")

    # --- Industry position ---
    industry_pos = IndustryPosition(
        firm=firm,
        industry_data=data["industry"],
    )
    print(f"  Industry position: {industry_pos}")

    # --- Comparator ---
    comparator = FirmEconomyComparator(
        firm=firm,
        macro=macro,
        industry_position=industry_pos,
    )
    print(f"  Comparator ready: {comparator}")

    # --- Scorer ---
    scorer = CompositeScorer(comparator)

    # --- Report ---
    report = ReportGenerator(scorer)

    return scorer, report


def main(data_path: str | None = None) -> None:
    """Run the full analysis and print the report."""
    path = data_path or DEFAULT_DATA
    print(f"\n{'=' * 72}")
    print(f"  Loading data from: {path}")
    print(f"{'=' * 72}\n")

    data = load_data(path)
    scorer, report = build_analysis(data)

    # Print full text report
    print("\n")
    print(report.generate())

    # Also write JSON output alongside
    json_path = path.rsplit(".", 1)[0] + "_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(report.to_json())
    print(f"\n  JSON results written to: {json_path}")


if __name__ == "__main__":
    custom_path = sys.argv[1] if len(sys.argv) > 1 else None
    main(custom_path)
