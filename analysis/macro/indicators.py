"""
Macroeconomic Indicators Module
================================
Loads, validates, and structures macroeconomic data for both the
United States and a configurable set of global/regional benchmarks.

The class exposes helper methods that the comparison engine uses
to score the macro environment surrounding a firm.
"""

from __future__ import annotations

from typing import Any

from analysis.config import MACRO_VARIABLES


class MacroIndicators:
    """Container and accessor for macroeconomic indicator data."""

    def __init__(self, us_data: dict[str, Any], global_data: dict[str, Any]):
        """
        Parameters
        ----------
        us_data : dict
            Key-value pairs whose keys match MACRO_VARIABLES keys,
            representing current US economic readings.
        global_data : dict
            Same structure but for the global (or weighted-average
            world) economy.
        """
        self.us = self._validate(us_data, "US")
        self.globe = self._validate(global_data, "Global")

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    @staticmethod
    def _validate(data: dict[str, Any], label: str) -> dict[str, Any]:
        validated: dict[str, Any] = {}
        for key in MACRO_VARIABLES:
            if key in data:
                validated[key] = data[key]
            else:
                validated[key] = None  # missing data recorded explicitly
        unknown = set(data) - set(MACRO_VARIABLES)
        if unknown:
            print(f"[MacroIndicators] Warning – {label} data contains "
                  f"unknown keys that will be ignored: {unknown}")
        return validated

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------
    def get_us(self, variable: str) -> Any:
        """Return the US reading for *variable*, or None if missing."""
        return self.us.get(variable)

    def get_global(self, variable: str) -> Any:
        """Return the global reading for *variable*, or None if missing."""
        return self.globe.get(variable)

    def get_spread(self, variable: str) -> float | None:
        """Return US value minus global value (US relative position)."""
        us_val = self.get_us(variable)
        gl_val = self.get_global(variable)
        if us_val is not None and gl_val is not None:
            return float(us_val) - float(gl_val)
        return None

    def available_variables(self, scope: str = "us") -> list[str]:
        """Return variable keys that have non-None data."""
        source = self.us if scope == "us" else self.globe
        return [k for k, v in source.items() if v is not None]

    # ------------------------------------------------------------------
    # Summaries
    # ------------------------------------------------------------------
    def category_summary(self, scope: str = "us") -> dict[str, dict]:
        """Group readings by their config category, with metadata."""
        source = self.us if scope == "us" else self.globe
        summary: dict[str, dict] = {}
        for key, meta in MACRO_VARIABLES.items():
            cat = meta["category"]
            if cat not in summary:
                summary[cat] = {"variables": {}}
            summary[cat]["variables"][key] = {
                "label": meta["label"],
                "value": source.get(key),
                "unit": meta["unit"],
                "direction": meta["direction"],
            }
        return summary

    def us_vs_global_table(self) -> list[dict]:
        """
        Return a list of dicts suitable for tabular display, showing
        US value, global value, and the spread for every variable.
        """
        rows = []
        for key, meta in MACRO_VARIABLES.items():
            rows.append({
                "variable": meta["label"],
                "us_value": self.us.get(key),
                "global_value": self.globe.get(key),
                "spread": self.get_spread(key),
                "unit": meta["unit"],
                "direction": meta["direction"],
            })
        return rows

    def __repr__(self) -> str:
        us_count = len(self.available_variables("us"))
        gl_count = len(self.available_variables("global"))
        total = len(MACRO_VARIABLES)
        return (f"<MacroIndicators US={us_count}/{total} "
                f"Global={gl_count}/{total}>")
