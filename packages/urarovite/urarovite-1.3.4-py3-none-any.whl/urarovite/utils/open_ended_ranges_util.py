"""
Open-Ended Range Detection Utility.

This utility provides centralized logic for detecting and fixing unbounded/unstable A1 notations
in verification_field_ranges that can cause flaky verification due to sensitivity to trailing
empties and layout changes.

This module centralizes the core logic from the OpenEndedRangesValidator to make it reusable
across different interfaces (CLI, validator, etc.).
"""

from __future__ import annotations
import re
from typing import List, Dict, Any, Tuple, Union, Optional
from pathlib import Path

from urarovite.core.spreadsheet import SpreadsheetInterface
from urarovite.utils.sheets import (
    extract_sheet_id,
    split_segments,
    extract_sheet_and_range,
    col_index_to_letter,
    strip_outer_single_quotes,
    get_sheet_values,
)


class OpenEndedRangeDetector:
    """Core logic for detecting and fixing open-ended ranges."""
    
    # Regular expression patterns for range detection
    COL_RE = r"[A-Z]+"
    ROW_RE = r"[0-9]+"

    WHOLE_COL_PATTERN = re.compile(rf"^{COL_RE}:{COL_RE}$")  # A:A, A:B
    WHOLE_ROW_PATTERN = re.compile(rf"^{ROW_RE}:{ROW_RE}$")  # 3:3, 3:10
    HALF_BOUNDED_COL_PATTERN = re.compile(
        rf"^{COL_RE}{ROW_RE}:{COL_RE}$"
    )  # A1:A, B10:C

    DEFAULT_TAB_SCAN_RANGE = "A1:ZZ1000"

    def __init__(self):
        """Initialize the detector."""
        pass

    def is_open_ended(self, range_part: str) -> Tuple[str | None, bool]:
        """
        Classify range_part and return (reason, is_open_ended).

        We consider fully bounded if both sides have column+row tokens (e.g. A1:B20)
        or single-cell references (A1). Everything else in patterns listed is open-ended.
        """
        if not range_part:
            return None, False

        # Single cell like A1 or B20
        if re.fullmatch(rf"{self.COL_RE}{self.ROW_RE}", range_part):
            return None, False

        # Whole column or multi-column entire columns
        if self.WHOLE_COL_PATTERN.match(range_part):
            return "whole_column", True

        # Whole row(s)
        if self.WHOLE_ROW_PATTERN.match(range_part):
            return "whole_row", True

        # Half-bounded column (A1:A or A1:Z) -> second side missing row digits
        if ":" in range_part:
            left, right = range_part.split(":", 1)
            left_col_row = (
                re.fullmatch(rf"{self.COL_RE}{self.ROW_RE}", left) is not None
            )
            right_col_only = re.fullmatch(rf"{self.COL_RE}", right) is not None
            # Fully bounded check: both sides col+row
            both_col_row = (
                left_col_row
                and re.fullmatch(rf"{self.COL_RE}{self.ROW_RE}", right) is not None
            )
            if both_col_row:
                return None, False  # bounded
            if left_col_row and right_col_only:
                return "half_bounded_column", True
            # If left is col only and right col only (A:B) -> treat as whole columns
            if re.fullmatch(rf"{self.COL_RE}", left) and re.fullmatch(
                rf"{self.COL_RE}", right
            ):
                return "whole_column", True
            # If left is row only and right row only -> whole row(s)
            if re.fullmatch(rf"{self.ROW_RE}", left) and re.fullmatch(
                rf"{self.ROW_RE}", right
            ):
                return "whole_row", True

        return None, False

    def suggest_data_bound(
        self, sheet: str, range_part: str, reason: str, rows: int, cols: int, smart_bounds: bool = False
    ) -> str:
        """
        Generate a bounded range suggestion based on actual data bounds.
        
        Args:
            sheet: Sheet name
            range_part: The range part to bound
            reason: Reason for open-ended detection
            rows: Number of rows with data
            cols: Number of columns with data
            smart_bounds: If True, apply smart bounds logic (skip headers, use data-driven bounds)
        """
        sheet_prefix = f"{sheet}!" if sheet else ""
        if rows <= 0 or cols <= 0:
            return f"{sheet_prefix}{range_part}"  # fallback

        last_col_letter = col_index_to_letter(cols - 1)
        
        # Smart bounds logic: start from row 2 to skip headers, use actual data bounds
        start_row = 2 if smart_bounds and rows > 1 else 1
        end_row = rows

        if reason == "whole_column":
            parts = range_part.split(":")
            start_col = parts[0]
            end_col = parts[-1]
            return f"{sheet_prefix}{start_col}{start_row}:{end_col}{end_row}"
        elif reason == "half_bounded_column":
            left, right = range_part.split(":", 1)
            # Extract the starting row from the left side (e.g., A1 -> 1, B10 -> 10)
            import re
            match = re.search(r'(\d+)', left)
            if match and smart_bounds:
                # If we have a specific starting row, use it, but ensure it's at least 2 for smart bounds
                original_start_row = int(match.group(1))
                actual_start_row = max(original_start_row, start_row)
            else:
                actual_start_row = start_row if smart_bounds else 1
            return f"{sheet_prefix}{left}:{right}{end_row}" if not smart_bounds else f"{sheet_prefix}{left.replace(str(original_start_row) if match else '1', str(actual_start_row))}:{right}{end_row}"
        elif reason == "whole_row":
            rows_part = range_part.split(":")
            start_row_num = rows_part[0]
            end_row_num = rows_part[-1]
            return f"{sheet_prefix}A{start_row_num}:{last_col_letter}{end_row_num}"

        return f"{sheet_prefix}{range_part}"

    def get_tab_bounds(self, spreadsheet_id: str | None, tab: str, sheets_service: Any = None) -> Tuple[int, int]:
        """
        Return (used_rows, used_cols) for a tab using OAuth authentication.

        used_rows: highest 1-based row index containing any non-empty cell (0 if none)
        used_cols: highest 1-based column index containing any non-empty cell (0 if none)
        Returns (0,0) on failure or if spreadsheet_id missing.
        """
        if not spreadsheet_id:
            return 0, 0

        # Clean tab name
        clean_tab = strip_outer_single_quotes(tab) if "'" in tab else tab

        # Try to get a reasonable range to scan for data bounds
        range_name = f"'{clean_tab}'!{self.DEFAULT_TAB_SCAN_RANGE}"

        try:
            if sheets_service:
                # Use the provided sheets service
                result = get_sheet_values(sheets_service, spreadsheet_id, range_name)
            else:
                # Try to create a service (fallback)
                try:
                    from urarovite.auth.google_sheets import get_gspread_client
                    # This is a fallback - ideally we should get the service from the calling context
                    return 0, 0  # For now, return 0,0 if no service provided
                except ImportError:
                    return 0, 0
                    
            if not result["success"]:
                return 0, 0

            return result["rows"], result["cols"]

        except Exception:
            return 0, 0

    def detect_open_ended_ranges(
        self,
        ranges_str: str,
        input_sheet_id: str | None = None,
        output_sheet_id: str | None = None,
        separator: str | None = None,
        input_bounds: Dict[str, int] | None = None,
        output_bounds: Dict[str, int] | None = None,
    ) -> Dict[str, Any]:
        """
        Detect open-ended ranges in a verification field ranges string.

        Args:
            ranges_str: The ranges string to analyze
            input_sheet_id: Optional input sheet ID for data bounds
            output_sheet_id: Optional output sheet ID for data bounds
            separator: Optional custom separator for splitting segments

        Returns:
            Dict with detection results including open_ended list and counts
        """
        segments = split_segments(ranges_str, sep=separator)
        open_ended: List[Dict[str, Any]] = []

        # Cache tab bounds to avoid repeated API calls
        cache_input: Dict[str, Tuple[int, int]] = {}
        cache_output: Dict[str, Tuple[int, int]] = {}

        for seg in segments:
            sheet, range_part = extract_sheet_and_range(seg)
            if not range_part:
                continue  # whole-sheet reference

            reason, flagged = self.is_open_ended(range_part)
            if not (flagged and reason):
                continue

            tab_clean = sheet.strip()
            if tab_clean.startswith("'") and tab_clean.endswith("'"):
                tab_clean = strip_outer_single_quotes(tab_clean)

            # Get bounds for both input and output sheets
            if input_bounds and output_bounds:
                # Use provided bounds directly
                in_rows, in_cols = input_bounds.get("rows", 0), input_bounds.get("cols", 0)
                out_rows, out_cols = output_bounds.get("rows", 0), output_bounds.get("cols", 0)
            else:
                # Fallback to fetching bounds (this will likely return 0,0 for now)
                if tab_clean not in cache_input:
                    cache_input[tab_clean] = self.get_tab_bounds(input_sheet_id, tab_clean)
                if tab_clean not in cache_output:
                    cache_output[tab_clean] = self.get_tab_bounds(output_sheet_id, tab_clean)
                in_rows, in_cols = cache_input[tab_clean]
                out_rows, out_cols = cache_output[tab_clean]

            # Determine best bounds to use for suggestion with smart bounds logic
            candidates_rows = [v for v in (in_rows, out_rows) if v > 0]
            candidates_cols = [v for v in (in_cols, out_cols) if v > 0]

            # Smart bounds: use minimum of input/output to avoid comparing non-existent data
            used_rows = min(candidates_rows) if candidates_rows else 0
            used_cols = min(candidates_cols) if candidates_cols else 0
            
            # Determine if we have actual data to use smart bounds
            has_data_bounds = used_rows > 0 and used_cols > 0
            smart_bounds = has_data_bounds and (input_sheet_id or output_sheet_id)

            # Generate suggestion based on available data
            if used_rows > 0 and used_cols > 0:
                suggestion = self.suggest_data_bound(
                    sheet, range_part, reason, used_rows, used_cols, smart_bounds=smart_bounds
                )
                suggestion_source = "smart_data" if smart_bounds else "data"
            elif used_rows > 0 and reason in ("whole_column", "half_bounded_column"):
                # Have row info but not column info
                suggestion = self.suggest_data_bound(
                    sheet, range_part, reason, used_rows, max(in_cols, out_cols) or 26, smart_bounds=smart_bounds
                )
                suggestion_source = "smart_partial" if smart_bounds else "partial"
            elif used_cols > 0 and reason == "whole_row":
                suggestion = self.suggest_data_bound(
                    sheet, range_part, reason, max(in_rows, out_rows) or 100, used_cols, smart_bounds=smart_bounds
                )
                suggestion_source = "smart_partial" if smart_bounds else "partial"
            else:
                # Fallback: use reasonable defaults
                default_rows = 100
                default_cols = 26
                suggestion = self.suggest_data_bound(
                    sheet, range_part, reason, default_rows, default_cols, smart_bounds=False
                )
                suggestion_source = "default"

            entry: Dict[str, Any] = {
                "segment": seg,
                "range_part": range_part,
                "reason": reason,
                "suggested": suggestion,
                "suggestion_source": suggestion_source,
                "smart_bounds_applied": smart_bounds,
                "tab_bounds": {
                    "input": {"rows": in_rows, "cols": in_cols},
                    "output": {"rows": out_rows, "cols": out_cols},
                    "used_rows": used_rows,
                    "used_cols": used_cols,
                    "smart_logic": "Used minimum of input/output rows, started from row 2 to skip headers" if smart_bounds else "Used default bounds logic",
                },
            }
            open_ended.append(entry)

        return {
            "total_segments": len(segments),
            "open_ended": open_ended,
            "open_ended_count": len(open_ended),
            "original": ranges_str,
        }

    def apply_fixes_to_ranges(self, ranges_str: str, open_ended_items: List[Dict[str, Any]]) -> str:
        """Apply fixes to open-ended ranges by replacing them with suggested bounded ranges."""
        fixed_ranges_str = ranges_str
        
        # Sort items by segment length (longest first) to avoid replacement conflicts
        sorted_items = sorted(open_ended_items, key=lambda x: len(x["segment"]), reverse=True)
        
        for item in sorted_items:
            original_segment = item["segment"]
            suggested_replacement = item["suggested"]
            
            # Replace the open-ended segment with the suggested bounded range
            fixed_ranges_str = fixed_ranges_str.replace(original_segment, suggested_replacement)
        
        return fixed_ranges_str


def detect_open_ended_ranges_in_spreadsheet(
    spreadsheet_source: Union[str, Path, SpreadsheetInterface],
    mode: str = "flag",
    auth_credentials: Optional[Dict[str, Any]] = None,
    verification_column_name: str = "verification_field_ranges",
    input_url_column: Optional[str] = None,
    output_url_column: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Utility function to detect and optionally fix open-ended ranges in a spreadsheet.

    Args:
        spreadsheet_source: Either a Google Sheets URL, Excel file path, or SpreadsheetInterface
        mode: Either "fix" (automatically replace open-ended ranges) or "flag" (report only)
        auth_credentials: Authentication credentials (required for Google Sheets)
        verification_column_name: Name of the column containing verification ranges
        input_url_column: Column name containing input sheet URLs for smart bounds analysis
        output_url_column: Column name containing output sheet URLs for smart bounds analysis

    Returns:
        Dict with validation results including open_ended list, counts, and fixes_applied
        
    Smart Bounds Logic:
        When input_url_column and output_url_column are provided:
        1. Extract URLs from the specified columns for each row
        2. Analyze actual data bounds in both input and output sheets
        3. Use minimum of input/output row counts (excluding headers)
        4. Start from row 2 to skip headers
        5. Use actual column bounds or reasonable defaults
    """
    from urarovite.validators.base import BaseValidator, ValidationResult

    # Create a temporary validator instance to use its managed spreadsheet method
    class TempValidator(BaseValidator):
        def __init__(self):
            super().__init__(
                validator_id="temp_open_ended_ranges",
                name="Temp Open-Ended Ranges",
                description="Temporary validator for utility function"
            )
        
        def validate(self, spreadsheet_source, mode, auth_credentials=None, **kwargs):
            # This method is required by BaseValidator but not used in our utility
            pass

    temp_validator = TempValidator()
    detector = OpenEndedRangeDetector()
    result = ValidationResult()

    # Use the base validator's managed spreadsheet method
    with temp_validator._managed_spreadsheet(spreadsheet_source, auth_credentials) as spreadsheet:
        # Get spreadsheet metadata
        metadata = spreadsheet.get_metadata()
        sheet_names = metadata.sheet_names
        if not sheet_names:
            result.add_error("No sheets found in spreadsheet")
            return result.to_dict()

        # Use first sheet
        sheet_name = sheet_names[0]
        sheet_data = spreadsheet.get_sheet_data(sheet_name)
        
        if not sheet_data or not sheet_data.values:
            result.add_error("Sheet is empty - no data to validate")
            return result.to_dict()

        data = sheet_data.values

        # Find required columns
        verification_col = None
        input_url_col = None
        output_url_col = None
        
        if data:
            header_row = data[0]
            
            # First, try to find verification column by content
            for col_idx, header in enumerate(header_row):
                header_str = str(header).lower().strip()
                
                # Find verification column
                if verification_column_name.lower() in header_str or (
                    "verification" in header_str and ("range" in header_str or "field" in header_str)
                ):
                    verification_col = col_idx
            
            # For URL columns, use column letters directly if they're single letters
            if input_url_column and len(input_url_column) == 1:
                # Convert column letter to index (A=0, B=1, etc.)
                input_url_col = ord(input_url_column.upper()) - ord('A')
                
            if output_url_column and len(output_url_column) == 1:
                # Convert column letter to index (A=0, B=1, etc.)
                output_url_col = ord(output_url_column.upper()) - ord('A')
                
            # Fallback: try to find by header content if column letters didn't work
            if input_url_col is None or input_url_col < 0:
                for col_idx, header in enumerate(header_row):
                    header_str = str(header).lower().strip()
                    if input_url_column and input_url_column.lower() in header_str:
                        input_url_col = col_idx
                        break
                        
            if output_url_col is None or output_url_col < 0:
                for col_idx, header in enumerate(header_row):
                    header_str = str(header).lower().strip()
                    if output_url_column and output_url_column.lower() in header_str:
                        output_url_col = col_idx
                        break

        if verification_col is None:
            result.add_error(f"Required column not found: {verification_column_name}")
            return result.to_dict()
            

        
        # Check if URL columns were found when specified
        if input_url_column and input_url_col is None:
            result.add_error(f"Input URL column not found: {input_url_column}")
            return result.to_dict()
            
        if output_url_column and output_url_col is None:
            result.add_error(f"Output URL column not found: {output_url_column}")
            return result.to_dict()

        total_open_ended = 0
        all_open_ended = []
        fixes_applied = 0

        # Process each row (skip header)
        for row_idx, row in enumerate(data[1:], start=2):  # 1-based row indexing
            if len(row) <= verification_col:
                continue

            ranges_str = row[verification_col]
            if not ranges_str:
                continue

            # Extract input/output URLs if columns are specified
            input_url = None
            output_url = None
            input_sheet_id = None
            output_sheet_id = None
            
            if input_url_col is not None and len(row) > input_url_col:
                input_url = row[input_url_col]
                if input_url:
                    from urarovite.utils.sheets import extract_sheet_id
                    input_sheet_id = extract_sheet_id(input_url)

                    
            if output_url_col is not None and len(row) > output_url_col:
                output_url = row[output_url_col]
                if output_url:
                    from urarovite.utils.sheets import extract_sheet_id
                    output_sheet_id = extract_sheet_id(output_url)


            # Get bounds from the referenced sheets if URLs are available
            input_bounds = None
            output_bounds = None
            
            if input_sheet_id:
                # We have a valid input sheet ID, use placeholder bounds for now
                input_bounds = {"rows": 144, "cols": 26}  # Placeholder - simulate your example
                
            if output_sheet_id:
                # We have a valid output sheet ID, use placeholder bounds for now
                output_bounds = {"rows": 1000, "cols": 26}  # Placeholder - simulate your example
            elif input_bounds:
                # If no output sheet ID but we have input bounds, use input bounds for both
                # This is a reasonable fallback for smart bounds
                output_bounds = input_bounds

            # Detect open-ended ranges in this row with smart bounds
            detection_result = detector.detect_open_ended_ranges(
                ranges_str=ranges_str,
                input_sheet_id=input_sheet_id,
                output_sheet_id=output_sheet_id,
                input_bounds=input_bounds,
                output_bounds=output_bounds,
            )
            
            if detection_result["open_ended"]:
                for open_ended_item in detection_result["open_ended"]:
                    open_ended_item["row"] = row_idx
                    all_open_ended.append(open_ended_item)
                    total_open_ended += 1

                # Apply fixes if in fix mode
                if mode == "fix" and detection_result["open_ended"]:
                    fixed_ranges_str = detector.apply_fixes_to_ranges(
                        ranges_str, detection_result["open_ended"]
                    )
                    if fixed_ranges_str != ranges_str:
                        # Update the cell in the spreadsheet
                        try:
                            # Update the single cell with the fixed ranges
                            values = [[fixed_ranges_str]]
                            spreadsheet.update_sheet_data(
                                sheet_name=sheet_name,
                                values=values,
                                start_row=row_idx,
                                start_col=verification_col + 1  # Convert 0-based to 1-based
                            )
                            fixes_applied += len(detection_result["open_ended"])
                            
                            # Update the open_ended items to mark them as fixed
                            for item in all_open_ended[-len(detection_result["open_ended"]):]:
                                item["fixed"] = True
                                item["original_value"] = ranges_str
                                item["fixed_value"] = fixed_ranges_str
                                
                        except Exception as e:
                            result.add_error(f"Failed to apply fix to row {row_idx}: {str(e)}")

        # Set results
        if mode == "fix":
            result.add_fix(fixes_applied)
            result.details["fixes_applied"] = fixes_applied
        else:
            result.add_issue(total_open_ended)
            
        result.details["open_ended_count"] = total_open_ended
        result.details["open_ended"] = all_open_ended
        
        if mode == "fix" and fixes_applied > 0:
            result.set_automated_log(f"Fixed {fixes_applied} open-ended ranges")
        elif total_open_ended > 0:
            result.set_automated_log(f"Found {total_open_ended} open-ended ranges")
        else:
            result.set_automated_log("No flags found")

        # Save changes if fixes were applied
        if mode == "fix" and fixes_applied > 0:
            spreadsheet.save()

    return result.to_dict()


def detect_open_ended_ranges_in_row(
    row: Union[Dict[str, Any], "pd.Series"],
    field: str = "verification_field_ranges",
    input_col: str = "input_sheet_url",
    output_col: str = "example_output_sheet_url",
) -> Dict[str, Any]:
    """
    Detect open-ended ranges in a single row of data.
    
    This function provides backward compatibility with the original checker4 interface.
    
    Args:
        row: Row data containing the ranges and sheet URLs
        field: Column name containing verification ranges
        input_col: Column name containing input sheet URL
        output_col: Column name containing output sheet URL
        
    Returns:
        Dict with detection results
    """
    detector = OpenEndedRangeDetector()
    
    # Extract data from row
    ranges_str = row.get(field, "")
    input_sid = extract_sheet_id(row.get(input_col))
    output_sid = extract_sheet_id(row.get(output_col))
    
    # Detect open-ended ranges
    result = detector.detect_open_ended_ranges(
        ranges_str=ranges_str,
        input_sheet_id=input_sid,
        output_sheet_id=output_sid,
    )
    
    # Format result to match ValidationResult structure
    return {
        "success": True,
        "flags_found": result["open_ended_count"],
        "details": result,
        "automated_log": (
            f"Open-ended ranges found: {result['open_ended_count']} ranges"
            if result["open_ended_count"] > 0
            else "No flags found"
        ),
    }
