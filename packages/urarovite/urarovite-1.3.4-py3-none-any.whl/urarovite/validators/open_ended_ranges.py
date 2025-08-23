"""
Open-Ended Range Validator.

This validator detects unbounded/unstable A1 notations in verification_field_ranges
that can cause flaky verification due to sensitivity to trailing empties and layout changes.

Goal:
Identify open-ended range patterns that should be bounded for stable verification:
- Whole columns: A:A, A:B, C:Z
- Whole rows: 3:3, 10:12
- Half-bounded columns: A1:A, A1:Z (missing terminating row number)

Why:
Open ranges are sensitive to trailing empties; layout changes create spurious diffs,
making verification unstable. This validator helps identify and suggest fixes.
"""

from __future__ import annotations
from typing import List, Dict, Any, Union
from pathlib import Path
import pandas as pd

from urarovite.validators.base import BaseValidator
from urarovite.core.spreadsheet import SpreadsheetInterface
from urarovite.utils.open_ended_ranges_util import (
    detect_open_ended_ranges_in_spreadsheet,
    detect_open_ended_ranges_in_row,
)


class OpenEndedRangesValidator(BaseValidator):
    """Validator that detects open-ended ranges in verification field ranges."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="open_ended_ranges",
            name="Open-Ended Ranges Detection",
            description=(
                "Detects unbounded A1 notations in verification ranges that "
                "can cause flaky verification (whole columns, rows, half-bounded ranges)"
            ),
        )

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Execute open-ended range detection using centralized utility function.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (automatically replace open-ended ranges) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)

        Returns:
            Dict with validation results
        """


        # Use the centralized utility function
        return detect_open_ended_ranges_in_spreadsheet(
            spreadsheet_source=spreadsheet_source,
            mode=mode,
            auth_credentials=auth_credentials,
            verification_column_name=kwargs.get("verification_column_name", "verification_field_ranges"),

        )


# Convenience function for backward compatibility
def run(
    row: Union[Dict[str, Any], "pd.Series"],
    field: str = "verification_field_ranges",
    input_col: str = "input_sheet_url",
    output_col: str = "example_output_sheet_url",
) -> Dict[str, Any]:
    """
    Execute open-ended range detection.
    This function provides backward compatibility with the original checker4 interface.
    """

    # Use the centralized utility function for row-based detection
    return detect_open_ended_ranges_in_row(
        row=row,
        field=field,
        input_col=input_col,
        output_col=output_col,
    )


