"""
Spreadsheet Differences Validator - Fixed Column C Writing.

This validator compares spreadsheets referenced in columns A and B,
then generates a detailed JSON report of all differences found.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

from urarovite.core.spreadsheet import SpreadsheetFactory, SpreadsheetInterface
from urarovite.utils.sheets import extract_sheet_id, fetch_workbook_with_formulas, get_sheet_data_with_hyperlinks
from urarovite.validators.base import BaseValidator, ValidationResult


class SpreadsheetDifferencesValidator(BaseValidator):
    """Validator that compares two spreadsheets and reports differences."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="spreadsheet_differences",
            name="Spreadsheet Differences",
            description=(
                "Compares spreadsheets in columns A and B and reports all differences. "
                "Supports verification ranges for targeted comparison."
            ),
        )
        
        # Pattern for A1 range notation
        self._A1_RANGE_PATTERN = re.compile(
            r"^(?:'?(?P<sheet>[^'!]+)'?!)?(?P<start>[A-Z]+\d+)(?::(?P<end>[A-Z]+\d+))?$"
        )

    def _get_sheet_data_with_hyperlinks(
        self, spreadsheet: SpreadsheetInterface, sheet_name: str
    ) -> list[list[Any]]:
        """
        Fetches sheet data, resolving hyperlinks to their URLs.
        Uses the existing utility function that handles smart chips properly.
        """
        # Check if it's a Google Sheet with sheets_service
        if not hasattr(spreadsheet, "sheets_service"):
            sheet_data_obj = spreadsheet.get_sheet_data(sheet_name)
            return sheet_data_obj.values if sheet_data_obj else []

        try:
            g_spreadsheet: Any = spreadsheet  # To satisfy type checkers
            
            # Get spreadsheet ID and sheet GID
            spreadsheet_id = None
            sheet_gid = None
            
            if hasattr(g_spreadsheet, "spreadsheet") and g_spreadsheet.spreadsheet:
                # Using gspread wrapper
                worksheet = g_spreadsheet.spreadsheet.worksheet(sheet_name)
                sheet_gid = worksheet.id
                spreadsheet_id = g_spreadsheet.spreadsheet.id
            elif hasattr(g_spreadsheet, "spreadsheet_id"):
                # Direct API access
                spreadsheet_id = g_spreadsheet.spreadsheet_id
                # Get sheet info to find the GID
                sheet_metadata = (
                    g_spreadsheet.sheets_service.spreadsheets()
                    .get(spreadsheetId=spreadsheet_id, fields="sheets(properties)")
                    .execute()
                )
                for sheet in sheet_metadata.get("sheets", []):
                    if sheet.get("properties", {}).get("title") == sheet_name:
                        sheet_gid = sheet.get("properties", {}).get("sheetId")
                        break
            
            if not spreadsheet_id or sheet_gid is None:
                # Fallback to standard method
                sheet_data_obj = spreadsheet.get_sheet_data(sheet_name)
                return sheet_data_obj.values if sheet_data_obj else []

            # Use the existing utility function that handles smart chips
            return get_sheet_data_with_hyperlinks(
                g_spreadsheet.sheets_service, spreadsheet_id, sheet_name, sheet_gid
            )

        except Exception:
            # Fallback to the standard method on any error
            sheet_data_obj = spreadsheet.get_sheet_data(sheet_name)
            return sheet_data_obj.values if sheet_data_obj else []

    def _compare_workbooks(
        self, input_wb: Dict[str, Any], output_wb: Dict[str, Any], verification_ranges: List[Dict[str, Any]] = None, compare_whole_sheet: bool = True
    ) -> Dict[str, Any]:
        """Compare two workbooks and return detailed differences."""
        differences = {
            "equal": True,
            "differences": [],
            "summary": {"total_differences": 0},
        }

        # Get the first sheet from each workbook
        input_sheets = input_wb.get("sheets", []) if isinstance(input_wb, dict) else []
        output_sheets = (
            output_wb.get("sheets", []) if isinstance(output_wb, dict) else []
        )

        if not input_sheets or not output_sheets:
            return differences

        # Compare the first sheet of each workbook
        self._compare_sheets(input_sheets[0], output_sheets[0], differences, verification_ranges, compare_whole_sheet)

        return differences

    def _compare_sheets(
        self,
        input_sheet: Dict[str, Any],
        output_sheet: Dict[str, Any],
        differences: Dict[str, Any],
        verification_ranges: List[Dict[str, Any]] = None,
        compare_whole_sheet: bool = True,
    ) -> None:
        """Compare two sheets and append differences."""
        sheet_name = (
            input_sheet.get("properties", {}).get("title", "Sheet1")
            if isinstance(input_sheet, dict)
            else "Sheet1"
        )

        # Extract row data
        input_data = []
        output_data = []

        if isinstance(input_sheet, dict):
            data = input_sheet.get("data", {})
            if isinstance(data, dict):
                input_data = data.get("rowData", [])
            elif isinstance(data, list) and len(data) > 0:
                first_data = data[0]
                if isinstance(first_data, dict):
                    input_data = first_data.get("rowData", [])

        if isinstance(output_sheet, dict):
            data = output_sheet.get("data", {})
            if isinstance(data, dict):
                output_data = data.get("rowData", [])
            elif isinstance(data, list) and len(data) > 0:
                first_data = data[0]
                if isinstance(first_data, dict):
                    output_data = first_data.get("rowData", [])

        # Compare cell contents
        max_rows = max(len(input_data), len(output_data))
        for row_idx in range(max_rows):
            input_row = (
                input_data[row_idx] if row_idx < len(input_data) else {"values": []}
            )
            output_row = (
                output_data[row_idx] if row_idx < len(output_data) else {"values": []}
            )

            input_values = (
                input_row.get("values", []) if isinstance(input_row, dict) else []
            )
            output_values = (
                output_row.get("values", []) if isinstance(output_row, dict) else []
            )

            max_cols = max(len(input_values), len(output_values))
            for col_idx in range(max_cols):
                input_cell = (
                    input_values[col_idx] if col_idx < len(input_values) else {}
                )
                output_cell = (
                    output_values[col_idx] if col_idx < len(output_values) else {}
                )

                input_formatted = (
                    input_cell.get("formattedValue", "")
                    if isinstance(input_cell, dict)
                    else str(input_cell)
                )
                output_formatted = (
                    output_cell.get("formattedValue", "")
                    if isinstance(output_cell, dict)
                    else str(output_cell)
                )

                if input_formatted != output_formatted:
                    # If verification ranges are specified and compare_whole_sheet is False,
                    # only compare cells within those ranges
                    if verification_ranges and not compare_whole_sheet:
                        if not self._is_cell_in_ranges(row_idx, col_idx, sheet_name, verification_ranges):
                            continue  # Skip cells outside verification ranges
                    col_letter = self._get_column_letter(col_idx + 1)
                    cell_location = f"{col_letter}{row_idx + 1}"

                    differences["differences"].append(
                        {
                            "sheet": sheet_name,
                            "location": cell_location,
                            "input_value": input_formatted,
                            "output_value": output_formatted,
                        }
                    )
                    differences["equal"] = False
                    differences["summary"]["total_differences"] += 1

    def _get_column_letter(self, col_num: int) -> str:
        """Convert column number to Excel column letter."""
        result = ""
        while col_num > 0:
            col_num -= 1
            result = chr(65 + (col_num % 26)) + result
            col_num //= 26
        return result
    
    def _get_column_index(self, col_letter: str) -> int:
        """Convert Excel column letter to zero-based index."""
        col_letter = col_letter.upper()
        result = 0
        for char in col_letter:
            result = result * 26 + (ord(char) - ord('A') + 1)
        return result - 1
    
    def _parse_verification_ranges(self, ranges_str: str) -> List[Dict[str, Any]]:
        """Parse verification ranges string into structured format.
        
        Args:
            ranges_str: String containing verification ranges (e.g., "Sheet1!A1:B2@@Sheet2!C1:D3")
            
        Returns:
            List of dictionaries with sheet_name, start_row, start_col, end_row, end_col
        """
        ranges = []
        if not ranges_str:
            return ranges
            
        # Split by @@ separator (common in verification field ranges)
        range_segments = ranges_str.split("@@")
        
        for segment in range_segments:
            segment = segment.strip()
            if not segment:
                continue
                
            range_info = self._parse_single_range(segment)
            if range_info:
                ranges.append(range_info)
        
        return ranges
    
    def _parse_single_range(self, range_str: str) -> Dict[str, Any] | None:
        """Parse a single A1 range string.
        
        Args:
            range_str: Single range like "Sheet1!A1:B2" or "A1:B2"
            
        Returns:
            Dictionary with range information or None if invalid
        """
        if not range_str or not isinstance(range_str, str):
            return None
            
        range_str = range_str.strip()
        
        # Match the A1 range pattern
        match = self._A1_RANGE_PATTERN.match(range_str)
        if not match:
            return None
            
        sheet_name = match.group("sheet") or ""
        start_cell = match.group("start")
        end_cell = match.group("end") or start_cell
        
        # Parse start and end coordinates
        start_coords = self._parse_cell_coordinates(start_cell)
        end_coords = self._parse_cell_coordinates(end_cell)
        
        if not start_coords or not end_coords:
            return None
            
        return {
            "sheet_name": sheet_name.strip("'"),
            "start_cell": start_cell,
            "end_cell": end_cell,
            "start_row": start_coords[0],
            "start_col": start_coords[1],
            "end_row": end_coords[0],
            "end_col": end_coords[1],
            "range_string": range_str,
        }
    
    def _parse_cell_coordinates(self, cell: str) -> Tuple[int, int] | None:
        """Parse A1 cell notation to (row, col) coordinates.
        
        Args:
            cell: Cell reference like "A1" or "BC123"
            
        Returns:
            Tuple of (row, col) as 0-based indices, or None if invalid
        """
        if not cell:
            return None
            
        # Extract column letters and row number
        match = re.match(r"^([A-Z]+)(\d+)$", cell.upper())
        if not match:
            return None
            
        col_letters, row_str = match.groups()
        
        try:
            row = int(row_str) - 1  # Convert to 0-based
            col = self._get_column_index(col_letters)
            return (row, col)
        except ValueError:
            return None
    
    def _is_cell_in_ranges(self, row: int, col: int, sheet_name: str, ranges: List[Dict[str, Any]]) -> bool:
        """Check if a cell is within any of the specified ranges.
        
        Args:
            row: 0-based row index
            col: 0-based column index
            sheet_name: Name of the sheet
            ranges: List of range dictionaries
            
        Returns:
            True if cell is in any range, False otherwise
        """
        for range_info in ranges:
            # Check sheet name match (empty sheet name means any sheet)
            if range_info["sheet_name"]:
                if not self._sheet_names_match(range_info["sheet_name"], sheet_name):
                    continue
                
            # Check if cell is within range bounds
            if (range_info["start_row"] <= row <= range_info["end_row"] and
                range_info["start_col"] <= col <= range_info["end_col"]):
                return True
                
        return False
    
    def _sheet_names_match(self, range_sheet: str, actual_sheet: str) -> bool:
        """Check if two sheet names match, with flexible matching for common abbreviations.
        
        Args:
            range_sheet: Sheet name from the verification range
            actual_sheet: Actual sheet name from the spreadsheet
            
        Returns:
            True if the names should be considered a match
        """
        # Exact match
        if range_sheet == actual_sheet:
            return True
            
        # Case-insensitive match
        if range_sheet.lower() == actual_sheet.lower():
            return True
            
        # Flexible matching for common patterns
        range_lower = range_sheet.lower().strip()
        actual_lower = actual_sheet.lower().strip()
        
        # Handle month abbreviations and common patterns
        # Split by spaces and compare each part
        range_parts = range_lower.split()
        actual_parts = actual_lower.split()
        
        if len(range_parts) == len(actual_parts):
            # Check if each part matches (allowing abbreviations)
            for range_part, actual_part in zip(range_parts, actual_parts):
                if not self._parts_match(range_part, actual_part):
                    return False
            return True
            
        return False
    
    def _parts_match(self, range_part: str, actual_part: str) -> bool:
        """Check if two parts of a sheet name match (allowing abbreviations).
        
        Args:
            range_part: Part from range sheet name
            actual_part: Part from actual sheet name
            
        Returns:
            True if parts match
        """
        # Exact match
        if range_part == actual_part:
            return True
            
        # Check if one is an abbreviation of the other
        # Allow 3+ character abbreviations
        if len(range_part) >= 3 and len(actual_part) >= 3:
            if range_part.startswith(actual_part) or actual_part.startswith(range_part):
                return True
                
        return False

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        input_url_column: str = "A",
        output_url_column: str = "B",
        verification_range_column: str | None = None,
        compare_whole_sheet: bool = True,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Compare spreadsheets listed in specified columns.

        This validator:
        1. Reads the provided spreadsheet
        2. Gets URLs from specified input and output columns
        3. Optionally reads verification ranges from specified column
        4. Compares each pair (whole sheet or verification ranges only)
        5. Writes results to column C if in fix mode
        
        Args:
            spreadsheet_source: Task sheet containing URLs to compare
            mode: "flag" or "fix" mode
            auth_credentials: Authentication credentials
            input_url_column: Column letter for input URLs (default: "A")
            output_url_column: Column letter for output URLs (default: "B")
            verification_range_column: Column letter for verification ranges (optional)
            compare_whole_sheet: If True, compare entire sheets when no ranges specified
        """

        def validation_logic(
            spreadsheet: SpreadsheetInterface, result: ValidationResult, **kwargs
        ) -> None:
            # Read the main sheet data
            try:
                sheet_info = spreadsheet.get_sheet_data()
                if not sheet_info:
                    result.set_automated_log("No data found in spreadsheet")
                    return

                sheet_name = sheet_info.sheet_name
                sheet_values = self._get_sheet_data_with_hyperlinks(
                    spreadsheet, sheet_name
                )

                if not sheet_values:
                    result.set_automated_log("No data found in spreadsheet")
                    return

            except Exception as e:
                result.add_error(f"Failed to read spreadsheet data: {str(e)}")
                return

            # Check if there are any Google Sheet URLs to process in the specified columns
            input_col_idx = self._get_column_index(input_url_column)
            output_col_idx = self._get_column_index(output_url_column)
            
            has_google_sheets_urls = False
            for row in sheet_values:
                # Check input column
                if (
                    row
                    and len(row) > input_col_idx
                    and isinstance(row[input_col_idx], str)
                    and "docs.google.com" in row[input_col_idx]
                ):
                    has_google_sheets_urls = True
                    break
                # Check output column
                if (
                    row
                    and len(row) > output_col_idx
                    and isinstance(row[output_col_idx], str)
                    and "docs.google.com" in row[output_col_idx]
                ):
                    has_google_sheets_urls = True
                    break

            if not has_google_sheets_urls:
                result.set_automated_log("No Google Sheet URLs found to compare.")
                return

            # Get credentials now that we know we need them
            auth_creds = os.environ.get("SPREADSHEET_SERVICE_ACCOUNT_CRED")
            if not auth_creds:
                auth_creds = (
                    auth_credentials.get("encoded_credentials")
                    if auth_credentials
                    else None
                )
                if not auth_creds:
                    auth_creds = (
                        auth_credentials.get("auth_secret")
                        if auth_credentials
                        else None
                    )

            if not auth_creds:
                result.add_error(
                    "Authentication credentials not found for Google Sheets comparison"
                )
                return

            total_rows_processed = 0
            total_differences_found = 0
            all_comparisons = []

            # Build complete column C data (including existing rows)
            column_c_data = []

            # Process each row
            for row_idx, row in enumerate(sheet_values):
                # Check if first row is a header
                if row_idx == 0:
                    if row and len(row) >= 2:
                        # Check if this looks like a header
                        if isinstance(row[0], str) and isinstance(row[1], str):
                            if (
                                "url" in row[0].lower()
                                or "url" in row[1].lower()
                                or "input" in row[0].lower()
                                or "output" in row[1].lower()
                            ):
                                column_c_data.append(
                                    ["Comparison Results"]
                                )  # Add header for column C
                                continue

                # Get URLs from specified columns and verification ranges if provided
                # Column indices already calculated above
                if not row or len(row) <= max(input_col_idx, output_col_idx):
                    column_c_data.append([""])  # Empty result for empty row
                    continue

                input_url = row[input_col_idx] if len(row) > input_col_idx and row[input_col_idx] else ""
                output_url = row[output_col_idx] if len(row) > output_col_idx and row[output_col_idx] else ""
                
                # Get verification ranges if column is specified
                verification_ranges = []
                if verification_range_column:
                    range_col_idx = self._get_column_index(verification_range_column)
                    if len(row) > range_col_idx and row[range_col_idx]:
                        verification_ranges = self._parse_verification_ranges(str(row[range_col_idx]))
                
                # If verification ranges are provided, default to range-only comparison
                # The user must explicitly set --compare-whole-sheet true to override this
                if verification_ranges:
                    # When ranges are provided, default to range-only comparison
                    # This is the expected behavior when someone specifies verification ranges
                    effective_compare_whole_sheet = False
                else:
                    # No ranges provided, use user's compare_whole_sheet setting
                    effective_compare_whole_sheet = compare_whole_sheet
                # Validate URLs
                if not input_url or not output_url:
                    column_c_data.append(["No URLs provided"])
                    continue

                if not isinstance(input_url, str) or not isinstance(output_url, str):
                    column_c_data.append(["Invalid URL format"])
                    continue

                if "docs.google.com" not in input_url and "sheets" not in input_url:
                    column_c_data.append(["Invalid input URL"])
                    continue

                if "docs.google.com" not in output_url and "sheets" not in output_url:
                    column_c_data.append(["Invalid output URL"])
                    continue

                try:
                    # Extract sheet IDs
                    input_id = extract_sheet_id(input_url)
                    output_id = extract_sheet_id(output_url)

                    if not input_id or not output_id:
                        column_c_data.append(["Failed to extract sheet IDs"])
                        continue

                    # Create interfaces for each sheet
                    input_spreadsheet = SpreadsheetFactory.create_spreadsheet(
                        input_url, {"encoded_credentials": auth_creds}
                    )
                    output_spreadsheet = SpreadsheetFactory.create_spreadsheet(
                        output_url, {"encoded_credentials": auth_creds}
                    )

                    # Fetch workbooks with formulas
                    input_workbook = fetch_workbook_with_formulas(
                        input_spreadsheet.sheets_service, input_id
                    )
                    output_workbook = fetch_workbook_with_formulas(
                        output_spreadsheet.sheets_service, output_id
                    )

                    # Compare workbooks
                    comparison = self._compare_workbooks(
                        input_workbook, output_workbook, verification_ranges, effective_compare_whole_sheet
                    )

                    # Log detailed flags for each difference
                    for diff in comparison.get("differences", []):
                        result.add_detailed_issue(
                            sheet_name=diff["sheet"],
                            cell=diff["location"],
                            message="Cell content differs between spreadsheets",
                            value=(
                                f"Input: '{diff['input_value']}', "
                                f"Output: '{diff['output_value']}'"
                            ),
                        )

                    # Add metadata
                    comparison["row_number"] = row_idx + 1
                    comparison["input_url"] = input_url
                    comparison["output_url"] = output_url

                    all_comparisons.append(comparison)

                    # Prepare result for column C
                    if comparison["equal"]:
                        column_c_data.append(["✅ MATCH"])
                    else:
                        # Create a compact summary
                        diff_count = comparison["summary"]["total_differences"]

                        # Show first 3 differences in a compact format
                        diff_details = []
                        for diff in comparison["differences"][:3]:
                            diff_details.append(
                                f"{diff['location']}: '{diff['input_value']}' "
                                f"→ '{diff['output_value']}'"
                            )

                        summary_text = f"❌ {diff_count} differences found\n"
                        summary_text += "\n".join(diff_details)

                        if len(comparison["differences"]) > 3:
                            summary_text += (
                                f"\n... and {len(comparison['differences']) - 3} more"
                            )

                        column_c_data.append([summary_text])

                    if not comparison["equal"]:
                        total_differences_found += comparison["summary"][
                            "total_differences"
                        ]

                    total_rows_processed += 1

                except Exception as e:
                    # Add error result for this row
                    column_c_data.append([f"❌ ERROR: {str(e)[:100]}"])
                    result.add_error(f"Error processing row {row_idx + 1}: {str(e)}")
                    continue

            # Write results to column C if in fix mode
            if mode == "fix" and column_c_data:
                try:
                    # First, get the current sheet to check if we need to clear column C
                    current_data = spreadsheet.get_sheet_data(sheet_name)

                    # Clear any existing data in column C if needed
                    # This is important to avoid leftover data from previous runs
                    if current_data and current_data.values:
                        max_rows = len(current_data.values)
                        # Prepare a clear range for column C
                        clear_range = (
                            f"C1:C{max_rows + 10}"  # Add extra rows to be safe
                        )

                        try:
                            # Clear column C first
                            spreadsheet.clear_sheet_range(
                                sheet_name=sheet_name,
                                range_name=clear_range,
                            )
                        except Exception:
                            # If clear doesn't work, we'll overwrite anyway
                            pass

                    # Now write the new data to column C
                    # Using a specific range to ensure it writes
                    end_row = len(column_c_data)
                    update_range = f"C1:C{end_row}"

                    # Update column C with all results
                    spreadsheet.update_sheet_data(
                        sheet_name=sheet_name,
                        values=column_c_data,
                        range_name=update_range,
                    )

                    try:
                        spreadsheet.save()
                    except Exception:
                        # If save fails, we can ignore it as we already updated
                        pass

                except Exception as e:
                    result.add_error(f"Failed to write results to column C: {str(e)}")
                    # Try alternative approach - write one by one
                    try:
                        for idx, cell_value in enumerate(column_c_data):
                            if cell_value and cell_value[0]:
                                cell_range = f"C{idx + 1}"
                                spreadsheet.update_sheet_data(
                                    sheet_name=sheet_name,
                                    values=[cell_value],
                                    range_name=cell_range,
                                )
                    except Exception as e2:
                        result.add_error(f"Alternative write also failed: {str(e2)}")

            # Set result details
            result.details["total_rows_processed"] = total_rows_processed
            result.details["total_differences_found"] = total_differences_found
            result.details["comparisons"] = all_comparisons

            # Set log message
            if mode == "fix":
                log_msg = f"Processed {total_rows_processed} spreadsheet pairs"
                if total_differences_found > 0:
                    log_msg += f", found {total_differences_found} total differences."
                else:
                    log_msg += ", all spreadsheets match."
                result.set_automated_log(log_msg)
            else:
                log_msg = f"Checked {total_rows_processed} spreadsheet pairs"
                if total_differences_found > 0:
                    log_msg += f", found {total_differences_found} total differences"
                else:
                    log_msg += ", all spreadsheets match"
                result.set_automated_log(log_msg)

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, **kwargs
        )


def run(
    sheets_service: Any,
    input_sheet_url: str,
    output_sheet_url: str,
) -> Dict[str, Any]:
    """Legacy run function for backward compatibility."""
    v = SpreadsheetDifferencesValidator()
    return v.validate(
        spreadsheet_source=input_sheet_url,
        mode="flag",
        auth_credentials={"sheets_service": sheets_service},
    )
