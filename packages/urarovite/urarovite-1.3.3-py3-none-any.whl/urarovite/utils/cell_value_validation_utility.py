#!/usr/bin/env python3
"""
Cell Value Validation CLI Utility.

This utility validates cell values against expected values from metadata sheets.
"""

from __future__ import annotations
import argparse
import pandas as pd
from typing import Any, Dict

from urarovite.cli_base import SingleBatchUtility, UtilityResult
from urarovite.utils.sheets import extract_sheet_id
from urarovite.auth.google_sheets import get_gspread_client


class CellValueValidationUtility(SingleBatchUtility):
    """Utility for validating cell values against expected values from metadata sheets."""
    
    def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "metadata_file",
            help="Google Sheets URL or CSV file containing validation metadata"
        )
        
        # Option 1: Separate columns for cells and values
        parser.add_argument(
            "--cells-column",
            help="Column name containing cell references (e.g., 'answer cells')"
        )
        parser.add_argument(
            "--values-column", 
            help="Column name containing expected values (e.g., 'answer values')"
        )
        
        # Option 2: Combined column for cell-value pairs
        parser.add_argument(
            "--cell-value-pairs-column",
            help="Column name containing cell-value pairs (e.g., 'answer cell-value pairs')"
        )
        
        # Required: linked sheet column
        parser.add_argument(
            "--linked-sheet-column",
            required=True,
            help="Column name containing URLs of sheets to validate (e.g., 'input_sheet_url')"
        )
        
        # Optional parameters
        parser.add_argument(
            "--validation-mode",
            choices=["flag", "fix"],
            default="flag",
            help="Validation mode: 'flag' to report issues, 'fix' to auto-correct (default: flag)"
        )
        parser.add_argument(
            "--tolerance",
            type=float,
            default=0.001,
            help="Numeric tolerance for floating point comparisons (default: 0.001)"
        )
        parser.add_argument(
            "--separator",
            default=":",
            help="Separator used between cell and value in cell-value pairs (default: ':')"
        )
        parser.add_argument(
            "--pair-separator",
            default=",",
            help="Separator used between multiple cell-value pairs in same cell (default: ',')"
        )
        parser.add_argument(
            "--output-format",
            choices=["table", "json", "csv"],
            default="table",
            help="Output format (default: table)"
        )
    
    def _extract_utility_args(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Extract utility-specific arguments from parsed args."""
        return {
            "metadata_file": args.metadata_file,
            "cells_column": args.cells_column,
            "values_column": args.values_column,
            "cell_value_pairs_column": args.cell_value_pairs_column,
            "linked_sheet_column": args.linked_sheet_column,
            "validation_mode": args.validation_mode,
            "tolerance": args.tolerance,
            "separator": args.separator,
            "pair_separator": args.pair_separator,
            "output_format": args.output_format,
        }
    
    def execute_single(self, **kwargs) -> UtilityResult:
        """Execute single cell value validation - delegates to batch."""
        return self.execute_batch(**kwargs)
    
    def execute_batch(self, **kwargs) -> UtilityResult:
        """Execute batch cell value validation."""
        try:
            from urarovite import execute_validation
            
            # Read metadata file
            metadata_file = kwargs["metadata_file"]
            if metadata_file.startswith("http"):
                # Google Sheets URL - use authenticated API
                try:
                    sheet_id = extract_sheet_id(metadata_file)
                    client = get_gspread_client(kwargs.get("auth_credentials", {}).get("auth_secret"))
                    spreadsheet = client.open_by_key(sheet_id)
                    worksheet = spreadsheet.get_worksheet(0)
                    data = worksheet.get_all_values()
                    
                    # Convert to DataFrame
                    if data:
                        df = pd.DataFrame(data[1:], columns=data[0])
                    else:
                        df = pd.DataFrame()
                        
                    print(f"✅ Successfully read metadata from Google Sheets: {spreadsheet.title}")
                    
                except Exception as e:
                    return UtilityResult(
                        success=False,
                        message="Failed to read metadata from Google Sheets",
                        error=f"Error reading sheet: {str(e)}"
                    )
            else:
                # Local CSV file
                df = pd.read_csv(metadata_file)
            
            # Validate arguments
            cells_column = kwargs.get("cells_column")
            values_column = kwargs.get("values_column")
            cell_value_pairs_column = kwargs.get("cell_value_pairs_column")
            linked_sheet_column = kwargs["linked_sheet_column"]
            
            # Check that we have either separate columns OR combined column
            if not ((cells_column and values_column) or cell_value_pairs_column):
                return UtilityResult(
                    success=False,
                    message="Invalid arguments",
                    error="Must provide either (--cells-column AND --values-column) OR --cell-value-pairs-column"
                )
            
            # Validate required columns exist
            missing_columns = []
            if linked_sheet_column not in df.columns:
                missing_columns.append(linked_sheet_column)
            
            if cells_column and cells_column not in df.columns:
                missing_columns.append(cells_column)
            if values_column and values_column not in df.columns:
                missing_columns.append(values_column)
            if cell_value_pairs_column and cell_value_pairs_column not in df.columns:
                missing_columns.append(cell_value_pairs_column)
            
            if missing_columns:
                return UtilityResult(
                    success=False,
                    message="Missing required columns",
                    error=f"Columns not found in metadata: {missing_columns}. Available columns: {list(df.columns)}"
                )
            
            # Process each row
            results = []
            successful = 0
            failed = 0
            total_flags = 0
            total_fixes = 0
            
            for index, row in df.iterrows():
                try:
                    # Get the linked sheet URL
                    sheet_url = row[linked_sheet_column]
                    if pd.isna(sheet_url) or not sheet_url.strip():
                        results.append({
                            "row": index + 1,
                            "sheet_url": sheet_url,
                            "status": "skipped",
                            "message": "Empty sheet URL"
                        })
                        continue
                    
                    # Parse cell-value pairs
                    expected_values = {}
                    
                    if cell_value_pairs_column:
                        # Parse combined format like "Mar 2025'!A2: U-672345" or multiple pairs like "'Sheet1'!A1@42, 'Sheet1'!A2@abc"
                        pairs_text = row[cell_value_pairs_column]
                        if pd.isna(pairs_text) or not pairs_text.strip():
                            results.append({
                                "row": index + 1,
                                "sheet_url": sheet_url,
                                "status": "skipped",
                                "message": "Empty cell-value pairs"
                            })
                            continue
                        
                        separator = kwargs.get("separator", ":")
                        pair_separator = kwargs.get("pair_separator", ",")
                        
                        # Split multiple pairs first
                        individual_pairs = [pair.strip() for pair in pairs_text.split(pair_separator)]
                        
                        parsing_errors = []
                        separator_corrections = []
                        
                        # If we only got one pair but it looks like it contains multiple pairs, try to detect pair separator
                        if len(individual_pairs) == 1 and kwargs.get("validation_mode") == "fix":
                            detected_pair_sep = self._detect_pair_separator(pairs_text, separator)
                            if detected_pair_sep and detected_pair_sep != pair_separator:
                                individual_pairs = [pair.strip() for pair in pairs_text.split(detected_pair_sep)]
                                separator_corrections.append(f"Auto-corrected pair separator (detected '{detected_pair_sep}' instead of '{pair_separator}')")
                        for pair in individual_pairs:
                            if not pair:  # Skip empty pairs
                                continue
                                
                            if separator in pair:
                                cell_ref, expected_value = pair.split(separator, 1)
                                expected_values[cell_ref.strip()] = expected_value.strip()
                            else:
                                # Try to detect correct separator if in fix mode
                                if kwargs.get("validation_mode") == "fix":
                                    detected_separator, suggestion = self._detect_separator(pair)
                                    if detected_separator:
                                        cell_ref, expected_value = pair.split(detected_separator, 1)
                                        expected_values[cell_ref.strip()] = expected_value.strip()
                                        separator_corrections.append(f"Auto-corrected separator in '{pair}' (detected '{detected_separator}' instead of '{separator}')")
                                    else:
                                        parsing_errors.append(f"Invalid pair format: '{pair}'. {suggestion}")
                                else:
                                    # In flag mode, just suggest possible separators
                                    _, suggestion = self._detect_separator(pair)
                                    parsing_errors.append(f"Invalid pair format: '{pair}'. {suggestion}")
                        
                        # Handle parsing errors (only fail if there are actual errors, not corrections)
                        if parsing_errors:
                            results.append({
                                "row": index + 1,
                                "sheet_url": sheet_url,
                                "status": "failed",
                                "error": f"Parsing errors: {'; '.join(parsing_errors)}"
                            })
                            failed += 1
                            continue
                        
                        if not expected_values:
                            results.append({
                                "row": index + 1,
                                "sheet_url": sheet_url,
                                "status": "skipped",
                                "message": "No valid cell-value pairs found"
                            })
                            continue
                    else:
                        # Parse separate columns
                        cells_text = row[cells_column]
                        values_text = row[values_column]
                        
                        if pd.isna(cells_text) or pd.isna(values_text) or not cells_text.strip() or not values_text.strip():
                            results.append({
                                "row": index + 1,
                                "sheet_url": sheet_url,
                                "status": "skipped",
                                "message": "Empty cells or values"
                            })
                            continue
                        
                        expected_values[cells_text.strip()] = values_text.strip()
                    
                    # Run validation using the existing cell_value_validation validator
                    # IMPORTANT: Always use "flag" mode for cell value validation - we only fix separators, not cell values
                    check = {
                        "id": "cell_value_validation",
                        "mode": "flag",  # Always flag, never fix cell values in target sheets
                        "expected_values": expected_values,
                        "tolerance": kwargs.get("tolerance", 0.001)
                    }
                    
                    result = execute_validation(
                        check=check,
                        sheet_url=sheet_url,
                        auth_secret=kwargs.get("auth_credentials", {}).get("auth_secret"),
                        subject=kwargs.get("auth_credentials", {}).get("subject")
                    )
                    
                    # Extract results
                    flags_found = result.get("flags_found", 0)
                    fixes_applied = 0  # We don't apply fixes to cell values, only to separators
                    errors = result.get("errors", [])
                    
                    # Count separator corrections as fixes if in fix mode
                    separator_fixes = len(separator_corrections) if kwargs.get("validation_mode") == "fix" else 0
                    
                    total_flags += flags_found
                    total_fixes += separator_fixes
                    
                    if errors:
                        error_msg = "; ".join(errors)
                        results.append({
                            "row": index + 1,
                            "sheet_url": sheet_url,
                            "status": "failed",
                            "error": error_msg,
                            "expected_values": expected_values
                        })
                        failed += 1
                    else:
                        mode = kwargs.get("validation_mode", "flag")
                        if mode == "fix":
                            if separator_fixes > 0:
                                message = f"Applied {separator_fixes} separator fixes, found {flags_found} cell value discrepancies"
                            else:
                                message = f"Found {flags_found} cell value discrepancies (no separator fixes needed)"
                        else:
                            message = f"Found {flags_found} cell value discrepancies"
                        
                        # Include separator corrections in the result
                        result_data = {
                            "row": index + 1,
                            "sheet_url": sheet_url,
                            "status": "success",
                            "message": message,
                            "flags_found": flags_found,
                            "fixes_applied": separator_fixes,  # Only separator fixes
                            "expected_values": expected_values,
                            "validation_result": result
                        }
                        
                        # Add separator corrections if any
                        if separator_corrections:
                            result_data["separator_corrections"] = separator_corrections
                            
                        results.append(result_data)
                        successful += 1
                        
                except Exception as e:
                    error_msg = str(e)
                    results.append({
                        "row": index + 1,
                        "sheet_url": sheet_url if 'sheet_url' in locals() else "unknown",
                        "status": "failed",
                        "error": error_msg
                    })
                    failed += 1
            
            # Generate output based on format
            output_format = kwargs.get("output_format", "table")
            
            if output_format == "csv":
                # Create CSV output
                csv_data = []
                for result in results:
                    csv_data.append({
                        "Row": result["row"],
                        "Sheet_URL": result["sheet_url"],
                        "Status": result["status"],
                        "Message": result.get("message", ""),
                        "Flags_Found": result.get("flags_found", 0),
                        "Fixes_Applied": result.get("fixes_applied", 0),
                        "Error": result.get("error", ""),
                        "Expected_Values": str(result.get("expected_values", {}))
                    })
                
                csv_df = pd.DataFrame(csv_data)
                csv_output = csv_df.to_csv(index=False)
                
                return UtilityResult(
                    success=successful > 0,
                    message=f"Cell value validation completed: {successful} successful, {failed} failed, {total_flags} total flags, {total_fixes} total fixes",
                    data={"results": results, "csv_output": csv_output},
                    metadata={
                        "total_processed": len(results),
                        "successful": successful,
                        "failed": failed,
                        "total_flags": total_flags,
                        "total_fixes": total_fixes,
                        "validation_mode": kwargs.get("validation_mode", "flag"),
                        "output_format": output_format
                    }
                )
            else:
                # Default table output
                return UtilityResult(
                    success=successful > 0,
                    message=f"Cell value validation completed: {successful} successful, {failed} failed, {total_flags} total flags, {total_fixes} total fixes",
                    data={"results": results},
                    metadata={
                        "total_processed": len(results),
                        "successful": successful,
                        "failed": failed,
                        "total_flags": total_flags,
                        "total_fixes": total_fixes,
                        "validation_mode": kwargs.get("validation_mode", "flag"),
                        "output_format": output_format
                    }
                )
            
        except Exception as e:
            return UtilityResult(
                success=False,
                message="Cell value validation failed",
                error=str(e)
            )
    
    def _detect_separator(self, pair_text: str) -> tuple[str | None, str]:
        """Detect the most likely separator in a malformed cell-value pair.
        
        Args:
            pair_text: The malformed pair text to analyze
            
        Returns:
            Tuple of (detected_separator, suggestion_message)
        """
        # Common separators to try, in order of preference
        common_separators = [":", "@", "=", "->", " → ", "|", ";", "~"]
        
        # Look for cell reference patterns (A1, Sheet1!A1, 'Sheet Name'!A1)
        cell_patterns = [
            r"^[A-Z]+\d+",  # Simple A1 notation
            r"^[^'!]+![A-Z]+\d+",  # Sheet!A1 notation
            r"^'[^']+'\![A-Z]+\d+",  # 'Sheet Name'!A1 notation
        ]
        
        detected_separators = []
        
        for sep in common_separators:
            if sep in pair_text:
                parts = pair_text.split(sep, 1)
                if len(parts) == 2:
                    left_part = parts[0].strip()
                    right_part = parts[1].strip()
                    
                    # Check if left part looks like a cell reference
                    import re
                    for pattern in cell_patterns:
                        if re.match(pattern, left_part, re.IGNORECASE):
                            detected_separators.append(sep)
                            break
        
        if detected_separators:
            # Return the first (most preferred) detected separator
            best_separator = detected_separators[0]
            suggestion = f"Try using separator '{best_separator}' instead"
            return best_separator, suggestion
        else:
            # No valid separator detected
            available_seps = ", ".join([f"'{s}'" for s in common_separators[:5]])
            suggestion = f"Expected format: 'CellRef{common_separators[0]}Value'. Try separators: {available_seps}"
            return None, suggestion
    
    def _detect_pair_separator(self, pairs_text: str, cell_value_separator: str) -> str | None:
        """Detect the most likely pair separator in text that should contain multiple pairs.
        
        Args:
            pairs_text: The text that should contain multiple cell-value pairs
            cell_value_separator: The separator used between cell and value
            
        Returns:
            The detected pair separator, or None if no valid separator found
        """
        # Common pair separators to try
        common_pair_separators = [",", "|", ";", "&", "~", "^"]
        
        # Look for cell reference patterns to count potential pairs
        import re
        cell_pattern = r"[A-Z]+\d+|[^'!]+![A-Z]+\d+|'[^']+'\![A-Z]+\d+"
        
        best_separator = None
        max_valid_pairs = 0
        
        for pair_sep in common_pair_separators:
            if pair_sep in pairs_text:
                potential_pairs = [p.strip() for p in pairs_text.split(pair_sep)]
                valid_pairs = 0
                
                for pair in potential_pairs:
                    if cell_value_separator in pair:
                        parts = pair.split(cell_value_separator, 1)
                        if len(parts) == 2:
                            cell_part = parts[0].strip()
                            if re.search(cell_pattern, cell_part, re.IGNORECASE):
                                valid_pairs += 1
                
                # We need at least 2 valid pairs to consider this a good pair separator
                if valid_pairs >= 2 and valid_pairs > max_valid_pairs:
                    max_valid_pairs = valid_pairs
                    best_separator = pair_sep
        
        return best_separator
