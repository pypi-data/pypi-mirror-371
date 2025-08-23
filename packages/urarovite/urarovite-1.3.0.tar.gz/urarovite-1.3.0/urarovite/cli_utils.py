#!/usr/bin/env python3
"""
CLI utilities for Urarovite using the base CLI infrastructure.

This module provides the `run_util` command pattern with various utility operations.
"""

from __future__ import annotations
import argparse
import os
import sys
import re
from typing import Any, Dict, List, Optional

from urarovite.cli_base import (
    SingleBatchUtility, 
    UtilityResult, 
    run_utility_cli,
    create_utility_command
)
from urarovite.utils.generic_spreadsheet import (
    convert_google_sheets_to_excel,
    check_spreadsheet_access
)
from urarovite.utils.simple_converter import (
    convert_single_file,
    convert_batch_from_metadata,
    convert_folder_batch
)
from urarovite.utils.sheets import extract_sheet_id
from urarovite.auth.google_sheets import get_gspread_client


class ConversionUtility(SingleBatchUtility):
    """Utility for converting between Google Sheets and Excel formats."""
    
    def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
        # Single mode arguments
        parser.add_argument(
            "input_file",
            help="Google Sheets URL or local Excel file path to convert"
        )
        parser.add_argument(
            "output_path",
            nargs="?",
            help="Path where converted file should be saved"
        )
        parser.add_argument(
            "--output-folder",
            help="Output folder path (overrides output_path, generates automatic filename)"
        )
        parser.add_argument(
            "--sheets",
            help="Comma-separated list of sheet names to convert (optional, converts all if not specified)"
        )
        parser.add_argument(
            "--drive-folder-id",
            help="Google Drive folder ID for creating new Google Sheets (optional)"
        )
        parser.add_argument(
            "--output-filename",
            help="Custom filename for output (without extension)"
        )
        parser.add_argument(
            "--output-format",
            choices=["excel", "sheets"],
            default="excel",
            help="Output format for batch mode (default: excel)"
        )
        
        # Batch mode arguments
        parser.add_argument(
            "--link-columns",
            help="Comma-separated list of column names containing links to convert (batch mode)"
        )
        parser.add_argument(
            "--input-column-name",
            default="input_url",
            help="Column name containing input URLs (folder batch mode)"
        )
        parser.add_argument(
            "--output-column-name",
            default="output_url",
            help="Column name for output URLs (folder batch mode)"
        )
        parser.add_argument(
            "--metadata-sheet-name",
            default="conversion_metadata",
            help="Sheet name containing metadata (folder batch mode)"
        )
    
    def _extract_utility_args(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Extract utility-specific arguments from parsed args."""
        base_args = {
            "input_file": args.input_file,
            "output_path": args.output_path,
            "output_folder": args.output_folder,
            "sheets": args.sheets,
            "drive_folder_id": args.drive_folder_id,
            "output_filename": args.output_filename,
        }
        
        if args.mode == "batch":
            base_args.update({
                "link_columns": args.link_columns,
                "output_format": args.output_format,
            })
        elif args.mode == "single":
            # Single mode specific args
            pass
        
        return base_args
    
    def execute_single(self, **kwargs) -> UtilityResult:
        """Execute single file conversion."""
        try:
            # Parse sheets if provided
            sheets = None
            if kwargs.get("sheets"):
                sheets = [s.strip() for s in kwargs["sheets"].split(",") if s.strip()]
            
            result = convert_single_file(
                input_file=kwargs["input_file"],
                output_path=kwargs.get("output_path"),
                auth_credentials=kwargs.get("auth_credentials", {}),
                sheet_names=sheets,
                output_folder=kwargs.get("output_folder"),
                drive_folder_id=kwargs.get("drive_folder_id"),
                output_filename=kwargs.get("output_filename"),
            )
            
            if result["success"]:
                # Determine output location for metadata
                output_location = "Unknown"
                if "output_path" in result and result["output_path"]:
                    output_location = result["output_path"]
                elif "output_url" in result and result["output_url"]:
                    output_location = result["output_url"]
                
                # Check if any sheet names were truncated
                original_names = result.get("original_sheet_names", [])
                excel_names = result.get("excel_sheet_names", [])
                truncated_info = []
                
                if original_names and excel_names:
                    for orig, excel in zip(original_names, excel_names):
                        if orig != excel:
                            truncated_info.append(f"'{orig}' → '{excel}'")
                
                metadata_dict = {
                    "input_file": kwargs["input_file"],
                    "output_location": output_location,
                    "sheets_converted": len(sheets) if sheets else "All sheets",
                    "converted_sheets": result.get("converted_sheets", [])
                }
                
                if truncated_info:
                    metadata_dict["sheet_name_truncations"] = truncated_info
                
                return UtilityResult(
                    success=True,
                    message="File conversion completed successfully",
                    data=result,
                    metadata=metadata_dict
                )
            else:
                return UtilityResult(
                    success=False,
                    message="File conversion failed",
                    error=result.get("error", "Unknown error")
                )
                
        except Exception as e:
            return UtilityResult(
                success=False,
                message="File conversion failed",
                error=str(e)
            )
    
    def execute_batch(self, **kwargs) -> UtilityResult:
        """Execute batch conversion."""
        try:
            # Parse link columns
            link_columns = kwargs.get("link_columns", "")
            if not link_columns:
                return UtilityResult(
                    success=False,
                    message="Batch conversion requires --link-columns parameter",
                    error="No link columns specified"
                )
            
            link_columns_list = [col.strip() for col in link_columns.split(",") if col.strip()]
            
            result = convert_batch_from_metadata(
                metadata_file=kwargs["input_file"],
                output_location=kwargs.get("output_path", ""),
                auth_credentials=kwargs.get("auth_credentials", {}),
                link_columns=link_columns_list,
                output_format=kwargs.get("output_format", "excel"),
            )
            
            if result["success"]:
                return UtilityResult(
                    success=True,
                    message="Batch conversion completed successfully",
                    data=result,
                    metadata={
                        "successful_conversions": result.get("success_count", 0),
                        "failed_conversions": result.get("failure_count", 0),
                        "output_location": result.get("output_location", "Unknown"),
                        "failed_conversions_details": result.get("failed_conversions", [])
                    }
                )
            else:
                return UtilityResult(
                    success=False,
                    message="Batch conversion failed",
                    error=result.get("error", "Unknown error")
                )
                
        except Exception as e:
            return UtilityResult(
                success=False,
                message="Batch conversion failed",
                error=str(e)
            )


class FolderBatchConversionUtility(SingleBatchUtility):
    """Utility for converting all Excel files in a folder to Google Sheets."""
    
    def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "input_folder",
            help="Local folder containing Excel files to convert"
        )
        parser.add_argument(
            "drive_folder_id",
            help="Google Drive folder ID where converted sheets will be created"
        )
        parser.add_argument(
            "--input-column-name",
            default="input_url",
            help="Name for the input file column in metadata sheet"
        )
        parser.add_argument(
            "--output-column-name",
            default="output_url",
            help="Name for the output URL column in metadata sheet"
        )
        parser.add_argument(
            "--metadata-sheet-name",
            default="conversion_metadata",
            help="Name for the metadata sheet to create"
        )
    
    def _extract_utility_args(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Extract utility-specific arguments from parsed args."""
        return {
            "input_folder": args.input_folder,
            "drive_folder_id": args.drive_folder_id,
            "input_column_name": args.input_column_name,
            "output_column_name": args.output_column_name,
            "metadata_sheet_name": args.metadata_sheet_name,
        }
    
    def execute_single(self, **kwargs) -> UtilityResult:
        """Execute folder batch conversion (single mode same as batch for this utility)."""
        return self.execute_batch(**kwargs)
    
    def execute_batch(self, **kwargs) -> UtilityResult:
        """Execute folder batch conversion."""
        try:
            result = convert_folder_batch(
                input_folder=kwargs["input_folder"],
                drive_folder_id=kwargs["drive_folder_id"],
                auth_credentials=kwargs.get("auth_credentials", {}),
                input_column_name=kwargs["input_column_name"],
                output_column_name=kwargs["output_column_name"],
                metadata_sheet_name=kwargs["metadata_sheet_name"],
            )
            
            if result["success"]:
                # Create batch results structure for each file processed
                results = []
                successful_conversions = result.get("successful_conversions", 0)
                total_files = result.get("total_files", 0)
                failed_conversions = result.get("failed_conversions", 0)
                
                # Add successful conversions
                for i in range(successful_conversions):
                    results.append({
                        "row": i + 1,
                        "status": "success",
                        "message": "File converted successfully",
                        "file_index": i + 1,
                        "total_files": total_files
                    })
                
                # Add failed conversions
                for i in range(failed_conversions):
                    results.append({
                        "row": successful_conversions + i + 1,
                        "status": "failed",
                        "error": "Conversion failed",
                        "file_index": successful_conversions + i + 1,
                        "total_files": total_files
                    })
                
                return UtilityResult(
                    success=True,
                    message="Folder batch conversion completed successfully",
                    data={"results": results},
                    metadata={
                        "successful_conversions": successful_conversions,
                        "total_files": total_files,
                        "failed_conversions": failed_conversions,
                        "metadata_sheet_url": result.get("metadata_sheet_url", "Unknown")
                    }
                )
            else:
                # Create failed result structure
                results = [{
                    "row": 1,
                    "status": "failed",
                    "error": result.get("error", "Unknown error"),
                    "input_folder": kwargs.get("input_folder", "Unknown")
                }]
                
                return UtilityResult(
                    success=False,
                    message="Folder batch conversion failed",
                    data={"results": results},
                    error=result.get("error", "Unknown error")
                )
                
        except Exception as e:
            return UtilityResult(
                success=False,
                message="Folder batch conversion failed",
                error=str(e)
            )


class ValidationUtility(SingleBatchUtility):
    """Utility for running validations on spreadsheets."""
    
    def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "spreadsheet_source",
            help="Google Sheets URL or local Excel file path to validate"
        )
        parser.add_argument(
            "--validator",
            help="Specific validator ID to run (use 'list' command to see options)"
        )
        parser.add_argument(
            "--validation-mode",
            choices=["flag", "fix"],
            default="flag",
            help="Validation mode: 'flag' to report flags, 'fix' to automatically fix them (default: flag)"
        )
        parser.add_argument(
            "--params",
            help="JSON string with additional validator parameters"
        )
    
    def _extract_utility_args(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Extract utility-specific arguments from parsed args."""
        return {
            "spreadsheet_source": args.spreadsheet_source,
            "validator": args.validator,
            "mode": args.validation_mode,
            "params": args.params,
        }
    
    def execute_single(self, **kwargs) -> UtilityResult:
        """Execute single validation."""
        try:
            from urarovite import execute_validation
            
            # Parse params if provided
            extra_params = {}
            if kwargs.get("params"):
                import json
                try:
                    extra_params = json.loads(kwargs["params"])
                except json.JSONDecodeError:
                    return UtilityResult(
                        success=False,
                        message="Invalid JSON in --params",
                        error="Could not parse JSON parameters"
                    )
            
            # Build validation check
            check = {
                "id": kwargs.get("validator", "all"),
                "mode": kwargs["mode"]
            }
            check.update(extra_params)
            
            result = execute_validation(
                check=check,
                sheet_url=kwargs["spreadsheet_source"],
                auth_secret=kwargs.get("auth_credentials", {}).get("auth_secret"),
                subject=kwargs.get("auth_credentials", {}).get("subject"),
            )
            
            return UtilityResult(
                success=True,
                message="Validation completed successfully",
                data=result,
                metadata={
                    "validator": kwargs.get("validator", "all"),
                    "mode": kwargs["mode"],
                    "flags_found": result.get("flags_found", 0),
                    "fixes_applied": result.get("fixes_applied", 0),
                    "errors": result.get("errors", [])
                }
            )
                
        except Exception as e:
            return UtilityResult(
                success=False,
                message="Validation failed",
                error=str(e)
            )
    
    def execute_batch(self, **kwargs) -> UtilityResult:
        """Execute batch validation."""
        # For now, batch validation just runs the same validation on multiple sheets
        # This could be enhanced to support metadata-based batch validation
        
        # Create a single result structure for now
        single_result = self.execute_single(**kwargs)
        
        if single_result.success:
            # Create batch results structure
            results = [{
                "row": 1,  # Single file processed
                "status": "success",
                "message": single_result.message,
                "spreadsheet_source": kwargs.get("spreadsheet_source", "Unknown"),
                "validator": kwargs.get("validator", "all"),
                "mode": kwargs.get("mode", "flag"),
                "flags_found": single_result.metadata.get("flags_found", 0),
                "fixes_applied": single_result.metadata.get("fixes_applied", 0)
            }]
            
            return UtilityResult(
                success=True,
                message=single_result.message,
                data={"results": results},
                metadata=single_result.metadata
            )
        else:
            # Create failed result structure
            results = [{
                "row": 1,
                "status": "failed",
                "error": single_result.error,
                "spreadsheet_source": kwargs.get("spreadsheet_source", "Unknown")
            }]
            
            return UtilityResult(
                success=False,
                message=single_result.message,
                data={"results": results},
                error=single_result.error
            )


class ForteProcessingUtility(SingleBatchUtility):
    """Utility for processing Forte CSV files."""
    
    def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "csv_file",
            help="Path to the Forte CSV export file"
        )
        parser.add_argument(
            "--output-file",
            help="Output CSV file path (default: ./output/{input_name}_processed.csv)"
        )
        parser.add_argument(
            "--target",
            default="1S2V36WyAkNCSByYK4H-uJazfWN56SXCD",
            help="Google Drive folder ID where files will be copied"
        )
        parser.add_argument(
            "--validation-mode",
            choices=["flag", "fix"],
            default="fix",
            help="Validation mode: 'flag' to report flags, 'fix' to automatically fix them (default: fix)"
        )
        parser.add_argument(
            "--local",
            action="store_true",
            help="Download files locally as Excel instead of uploading to Google Sheets"
        )
    
    def _extract_utility_args(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Extract utility-specific arguments from parsed args."""
        return {
            "csv_file": args.csv_file,
            "output": args.output_file,
            "target": args.target,
            "mode": args.validation_mode,
            "local": args.local,
        }
    
    def execute_single(self, **kwargs) -> UtilityResult:
        """Execute Forte CSV processing."""
        try:
            # Import the processing function
            from urarovite.core.api import process_forte_csv_batch
            from urarovite.utils.forte_processing import generate_summary_report
            
            # Determine target format based on --local flag
            target_format = "excel" if kwargs.get("local") else "sheets"
            target_folder = None if kwargs.get("local") else kwargs.get("target")
            
            # Set default output file with timestamp
            output_csv = kwargs.get("output")
            if not output_csv:
                from datetime import datetime
                base_name = os.path.splitext(os.path.basename(kwargs["csv_file"]))[0]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_csv = f"./output/{base_name}_processed_{timestamp}.csv"
            
            # Ensure output directory exists
            output_dir = os.path.dirname(output_csv)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Get auth credentials
            auth_credentials = kwargs.get("auth_credentials", {})
            auth_secret = auth_credentials.get("auth_secret")
            if not auth_secret:
                return UtilityResult(
                    success=False,
                    message="No authentication credentials provided",
                    error="Set URAROVITE_AUTH_SECRET env var or use --auth-secret"
                )
            
            # Process the CSV
            result = process_forte_csv_batch(
                csv_file_path=kwargs["csv_file"],
                auth_secret=auth_secret,
                target_folder_id=target_folder,
                subject=auth_credentials.get("subject"),
                validation_mode=kwargs["mode"],
                preserve_visual_formatting=True,
                output_file_path=output_csv,
            )
            
            if result["success"]:
                # Generate summary report
                summary_report = generate_summary_report(result)
                
                return UtilityResult(
                    success=True,
                    message="Forte CSV processing completed successfully",
                    data=result,
                    metadata={
                        "input_file": kwargs["csv_file"],
                        "output_file": output_csv,
                        "target_folder": target_folder,
                        "mode": kwargs["mode"],
                        "target_format": target_format,
                        "summary_report": summary_report
                    }
                )
            else:
                return UtilityResult(
                    success=False,
                    message="Forte CSV processing failed",
                    error=result.get("error", "Unknown error")
                )
                
        except Exception as e:
            return UtilityResult(
                success=False,
                message="Forte CSV processing failed",
                error=str(e)
            )
    
    def execute_batch(self, **kwargs) -> UtilityResult:
        """Execute batch Forte processing (same as single for this utility)."""
        # For batch processing, we need to create a results array structure
        single_result = self.execute_single(**kwargs)
        
        if single_result.success:
            # Create batch results structure
            results = [{
                "row": 1,  # Single file processed
                "status": "success",
                "message": single_result.message,
                "input_file": kwargs.get("csv_file", "Unknown"),
                "output_file": single_result.metadata.get("output_file", "Unknown"),
                "target_folder": single_result.metadata.get("target_folder", "Unknown"),
                "mode": single_result.metadata.get("mode", "Unknown")
            }]
            
            return UtilityResult(
                success=True,
                message=single_result.message,
                data={"results": results},
                metadata=single_result.metadata
            )
        else:
            # Create failed result structure
            results = [{
                "row": 1,
                "status": "failed",
                "error": single_result.error,
                "input_file": kwargs.get("csv_file", "Unknown")
            }]
            
            return UtilityResult(
                success=False,
                message=single_result.message,
                data={"results": results},
                error=single_result.error
            )


class SheetsToExcelDriveUtility(SingleBatchUtility):
    """Utility for converting Google Sheets to Excel and uploading to Google Drive."""
    
    def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "google_sheets_url",
            help="Google Sheets URL to convert to Excel"
        )
        parser.add_argument(
            "drive_folder_id",
            help="Google Drive folder ID where Excel file will be uploaded"
        )
        parser.add_argument(
            "--filename",
            help="Custom filename for the Excel file (without extension)"
        )
        parser.add_argument(
            "--sheets",
            help="Comma-separated list of sheet names to convert (optional, converts all if not specified)"
        )
    
    def _extract_utility_args(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Extract utility-specific arguments from parsed args."""
        return {
            "google_sheets_url": args.google_sheets_url,
            "drive_folder_id": args.drive_folder_id,
            "filename": args.filename,
            "sheets": args.sheets,
        }
    
    def execute_single(self, **kwargs) -> UtilityResult:
        """Execute Google Sheets to Excel + Drive upload."""
        try:
            from urarovite.utils.generic_spreadsheet import convert_google_sheets_to_excel
            from urarovite.utils.drive import upload_file_to_drive_folder
            from urarovite.utils.sheets import extract_sheet_id
            import tempfile
            import os
            
            # Parse sheet names if provided
            sheets = None
            if kwargs.get("sheets"):
                sheets = [s.strip() for s in kwargs["sheets"].split(",") if s.strip()]
            
            # Create temporary Excel file with proper extension
            import tempfile
            temp_dir = tempfile.mkdtemp()
            temp_excel_path = os.path.join(temp_dir, "temp_conversion.xlsx")
            
            try:
                # Convert Google Sheets to temporary Excel
                conversion_result = convert_google_sheets_to_excel(
                    google_sheets_url=kwargs["google_sheets_url"],
                    excel_file_path=temp_excel_path,
                    auth_credentials=kwargs.get("auth_credentials", {}),
                    sheet_names=sheets,
                )
                
                if not conversion_result["success"]:
                    return UtilityResult(
                        success=False,
                        message="Google Sheets to Excel conversion failed",
                        error=conversion_result.get("error", "Unknown error")
                    )
                
                # Determine filename
                if kwargs.get("filename"):
                    excel_filename = f"{kwargs['filename']}.xlsx"
                else:
                    # Extract from source Google Sheets title (not metadata sheet)
                    source_sheet_id = extract_sheet_id(kwargs["google_sheets_url"])
                    client = get_gspread_client(kwargs.get("auth_credentials", {}).get("auth_secret"))
                    source_spreadsheet = client.open_by_key(source_sheet_id)
                    excel_filename = f"{source_spreadsheet.title}.xlsx"
                
                # Upload to Drive
                upload_result = upload_file_to_drive_folder(
                    file_path=temp_excel_path,
                    filename=excel_filename,
                    folder_id=kwargs["drive_folder_id"],
                    auth_credentials=kwargs.get("auth_credentials", {}),
                )
                
                if upload_result["success"]:
                    return UtilityResult(
                        success=True,
                        message="Google Sheets successfully converted to Excel and uploaded to Drive",
                        data={
                            "conversion": conversion_result,
                            "upload": upload_result,
                            "drive_file_id": upload_result.get("file_id"),
                            "drive_file_url": upload_result.get("file_url"),
                        },
                        metadata={
                            "input_url": kwargs["google_sheets_url"],
                            "drive_folder_id": kwargs["drive_folder_id"],
                            "excel_filename": excel_filename,
                            "sheets_converted": len(conversion_result.get("converted_sheets", [])),
                            "drive_file_id": upload_result.get("file_id"),
                            "drive_file_url": upload_result.get("file_url"),
                        }
                    )
                else:
                    return UtilityResult(
                        success=False,
                        message="Excel file created but Drive upload failed",
                        error=upload_result.get("error", "Unknown upload error"),
                        data={"conversion": conversion_result}
                    )
                    
            finally:
                # Clean up temporary directory and file
                import shutil
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    
        except Exception as e:
            return UtilityResult(
                success=False,
                message="Google Sheets to Excel + Drive conversion failed",
                error=str(e)
            )
    
    def execute_batch(self, **kwargs) -> UtilityResult:
        """Execute batch conversion (same as single for this utility)."""
        return self.execute_single(**kwargs)


class ExcelToSheetsDriveUtility(SingleBatchUtility):
    """Utility for converting Excel files to Google Sheets and uploading to Google Drive."""
    
    def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "excel_source",
            help="Excel file path or Google Drive file ID/URL to convert to Google Sheets"
        )
        parser.add_argument(
            "drive_folder_id",
            help="Google Drive folder ID where Google Sheets will be created"
        )
        parser.add_argument(
            "--filename",
            help="Custom filename for the Google Sheets (without extension)"
        )
        parser.add_argument(
            "--sheets",
            help="Comma-separated list of sheet names to convert (optional, converts all if not specified)"
        )
    
    def _extract_utility_args(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Extract utility-specific arguments from parsed args."""
        return {
            "excel_source": args.excel_source,
            "drive_folder_id": args.drive_folder_id,
            "filename": args.filename,
            "sheets": args.sheets,
        }
    
    def execute_single(self, **kwargs) -> UtilityResult:
        """Execute Excel to Google Sheets + Drive upload."""
        try:
            from urarovite.utils.generic_spreadsheet import convert_excel_to_google_sheets
            from urarovite.utils.sheets import create_new_spreadsheet_in_folder
            import tempfile
            import os
            
            # Parse sheet names if provided
            sheets = None
            if kwargs.get("sheets"):
                sheets = [s.strip() for s in kwargs["sheets"].split(",") if s.strip()]
            
            excel_source = kwargs["excel_source"]
            drive_folder_id = kwargs["drive_folder_id"]
            
            # Handle different input types
            if excel_source.startswith("http"):
                # Google Drive URL - download first
                from urarovite.utils.drive import download_file_from_drive
                
                # Extract file ID from URL
                from urarovite.utils.drive import extract_google_file_id
                file_id = extract_google_file_id(excel_source)
                if not file_id:
                    return UtilityResult(
                        success=False,
                        message="Invalid Google Drive URL",
                        error="Could not extract file ID from URL"
                    )
                
                # Check if this is actually a Google Sheets URL (which we can't convert back to Sheets)
                if "spreadsheets/d/" in excel_source:
                    # Special case: Some Excel files are served through Sheets interface
                    # Let's try to download it anyway and see what we get
                    print("⚠️  Warning: URL appears to be Google Sheets format, but attempting download...")
                    # Don't return error, continue with download attempt
                
                # Download to temporary file
                with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp_file:
                    temp_excel_path = temp_file.name
                
                try:
                    download_result = download_file_from_drive(
                        file_url=excel_source,
                        local_path=temp_excel_path,
                        auth_credentials=kwargs.get("auth_credentials", {})
                    )
                    
                    if not download_result["success"]:
                        return UtilityResult(
                            success=False,
                            message="Failed to download Excel file from Drive",
                            error=download_result.get("error", "Unknown error")
                        )
                    
                    excel_file_path = temp_excel_path
                    
                    # Download completed successfully
                    excel_file_path = temp_excel_path
                    
                    # Store downloaded file path for filename extraction
                    downloaded_excel_path = temp_excel_path
                    
                except Exception as e:
                    return UtilityResult(
                        success=False,
                        message="Failed to download Excel file from Drive",
                        error=str(e)
                    )
            else:
                # Local file path
                excel_file_path = excel_source
                temp_excel_path = None
            
            try:
                # Create new Google Sheets document in the specified folder
                gspread_client = get_gspread_client(
                    kwargs.get("auth_credentials", {}).get("auth_secret")
                )
                
                # Determine filename using consolidated utility from drive.py
                if kwargs.get("filename"):
                    # Custom filename takes highest priority
                    sheets_name = kwargs["filename"]
                    print(f"✅ Using custom filename: {sheets_name}")
                else:
                    # Use consolidated filename extraction utility
                    from urarovite.utils.drive import extract_original_filename_from_source
                    
                    # Get downloaded file path if available
                    downloaded_path = locals().get('downloaded_excel_path')
                    
                    filename_result = extract_original_filename_from_source(
                        source_url_or_path=excel_source,
                        auth_credentials=kwargs.get("auth_credentials", {}),
                        downloaded_file_path=downloaded_path
                    )
                    
                    base_filename = filename_result["filename"]
                    source_method = filename_result["source"]
                    
                    # Use base filename without column suffix
                    sheets_name = base_filename
                    
                    if filename_result["success"]:
                        print(f"✅ Using filename from {source_method}: {sheets_name}")
                    else:
                        print(f"⚠️  Using fallback filename: {sheets_name}")
                        if filename_result["error"]:
                            print(f"   Error: {filename_result['error']}")
                
                # Create new Google Sheets in Drive folder
                new_spreadsheet = create_new_spreadsheet_in_folder(
                    gspread_client=gspread_client,
                    folder_id=drive_folder_id,
                    spreadsheet_name=sheets_name,
                )
                
                if not new_spreadsheet:
                    return UtilityResult(
                        success=False,
                        message="Failed to create new Google Sheets document in Drive folder",
                        error="Could not create spreadsheet"
                    )
                
                # Convert Excel data to the new Google Sheets
                new_sheets_url = f"https://docs.google.com/spreadsheets/d/{new_spreadsheet.id}/edit"
                
                conversion_result = convert_excel_to_google_sheets(
                    excel_file_path=excel_file_path,
                    google_sheets_url=new_sheets_url,
                    auth_credentials=kwargs.get("auth_credentials", {}),
                    create_new_sheets=True,
                    sheet_names=sheets,
                )
                
                if conversion_result["success"]:
                    return UtilityResult(
                        success=True,
                        message="Excel file successfully converted to Google Sheets and uploaded to Drive",
                        data={
                            "conversion": conversion_result,
                            "spreadsheet_id": new_spreadsheet.id,
                            "spreadsheet_url": new_sheets_url,
                        },
                        metadata={
                            "input_source": excel_source,
                            "drive_folder_id": drive_folder_id,
                            "sheets_name": sheets_name,
                            "spreadsheet_id": new_spreadsheet.id,
                            "spreadsheet_url": new_sheets_url,
                            "sheets_converted": len(conversion_result.get("converted_sheets", [])),
                        }
                    )
                else:
                    return UtilityResult(
                        success=False,
                        message="Excel to Google Sheets conversion failed",
                        error=conversion_result.get("error", "Unknown error")
                    )
                    
            finally:
                # Clean up temporary file if we created one
                if temp_excel_path and os.path.exists(temp_excel_path):
                    os.unlink(temp_excel_path)
                    
        except Exception as e:
            return UtilityResult(
                success=False,
                message="Excel to Google Sheets + Drive conversion failed",
                error=str(e)
            )
    
    def execute_batch(self, **kwargs) -> UtilityResult:
        """Execute batch conversion (same as single for this utility)."""
        return self.execute_single(**kwargs)


class BatchSheetsToExcelDriveUtility(SingleBatchUtility):
    """Utility for batch converting multiple Google Sheets to Excel and uploading to Google Drive."""
    
    def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "metadata_file",
            help="CSV file or Google Sheets URL containing list of sheets to convert"
        )
        parser.add_argument(
            "drive_folder_id",
            nargs="?",
            help="Google Drive folder ID where Excel files will be uploaded (optional, defaults to original folder)"
        )
        parser.add_argument(
            "--url-columns",
            default="sheet_url",
            help="Comma-separated column names containing Google Sheets URLs (default: sheet_url)"
        )
        parser.add_argument(
            "--filename-column",
            help="Column name containing custom filenames (optional)"
        )
        parser.add_argument(
            "--sheets-column",
            help="Column name containing sheet names to convert (optional)"
        )
        parser.add_argument(
            "--excel-url-column",
            default="excel_url",
            help="Column name for storing converted Excel file URLs (default: excel_url)"
        )

    
    def _extract_utility_args(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Extract utility-specific arguments from parsed args."""
        return {
            "metadata_file": args.metadata_file,
            "drive_folder_id": getattr(args, 'drive_folder_id', None),
            "url_columns": args.url_columns,
            "filename_column": args.filename_column,
            "sheets_column": args.sheets_column,
            "excel_url_column": args.excel_url_column,
        }
    
    def execute_single(self, **kwargs) -> UtilityResult:
        """Execute batch conversion (same as batch for this utility)."""
        return self.execute_batch(**kwargs)
    
    def execute_batch(self, **kwargs) -> UtilityResult:
        """Execute batch Google Sheets to Excel + Drive conversion."""
        try:
            import pandas as pd
            

            
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
            
            # Parse URL columns
            url_columns = [col.strip() for col in kwargs["url_columns"].split(",")]
            
            # Validate all URL columns exist
            missing_columns = [col for col in url_columns if col not in df.columns]
            if missing_columns:
                return UtilityResult(
                    success=False,
                    message=f"URL columns not found in metadata file",
                    error=f"Missing columns: {missing_columns}. Available columns: {list(df.columns)}"
                )
            
            # Process each row
            results = []
            successful = 0
            failed = 0
            
            for index, row in df.iterrows():
                # Process each URL column for this row
                for url_col in url_columns:
                    sheet_url = row[url_col]
                    if pd.isna(sheet_url) or not str(sheet_url).strip():
                        continue
                    
                    # Get custom filename if specified
                    custom_filename = None
                    if kwargs.get("filename_column") and kwargs["filename_column"] in df.columns:
                        custom_filename = row[kwargs["filename_column"]]
                        if pd.isna(custom_filename):
                            custom_filename = None
                    
                    # Get sheets to convert if specified
                    sheets_to_convert = None
                    if kwargs.get("sheets_column") and kwargs["sheets_column"] in df.columns:
                        sheets_spec = row[kwargs["sheets_column"]]
                        if not pd.isna(sheets_spec):
                            sheets_to_convert = [s.strip() for s in str(sheets_spec).split(",")]
                    
                    # Convert this sheet
                    try:

                        import tempfile
                        import os
                        
                        # Create temporary Excel file
                        temp_dir = tempfile.mkdtemp()
                        temp_excel_path = os.path.join(temp_dir, "temp_conversion.xlsx")
                        
                        try:
                            # Import the upload function
                            from urarovite.utils.drive import upload_file_to_drive_folder
                            
                            # Convert to Excel
                            conversion_result = convert_google_sheets_to_excel(
                                google_sheets_url=sheet_url,
                                excel_file_path=temp_excel_path,
                                auth_credentials=kwargs.get("auth_credentials", {}),
                                sheet_names=sheets_to_convert,
                            )
                            
                            if conversion_result["success"]:
                                # Determine filename
                                if custom_filename:
                                    excel_filename = f"{custom_filename}.xlsx"
                                else:
                                    # Extract from source Google Sheets title (not metadata sheet)
                                    source_sheet_id = extract_sheet_id(sheet_url)
                                    client = get_gspread_client(kwargs.get("auth_credentials", {}).get("auth_secret"))
                                    source_spreadsheet = client.open_by_key(source_sheet_id)
                                    excel_filename = f"{source_spreadsheet.title}.xlsx"
                                
                                # Determine target folder ID - fallback to original folder if none specified
                                target_folder_id = kwargs["drive_folder_id"]
                                if not target_folder_id:
                                    # Try to get original folder ID
                                    from urarovite.utils.drive import get_original_folder_id
                                    original_folder = get_original_folder_id(sheet_url, kwargs.get("auth_credentials", {}))
                                    if original_folder:
                                        target_folder_id = original_folder
                                        print(f"📁 Using original folder for {sheet_url}")
                                    else:
                                        print(f"⚠️ Warning: No folder specified and couldn't determine original folder for {sheet_url}")
                                        # Skip upload but mark as successful conversion
                                        results.append({
                                            "row": index + 1,
                                            "url_column": url_col,
                                            "sheet_url": sheet_url,
                                            "filename": excel_filename,
                                            "status": "converted_no_upload",
                                            "message": "Excel converted but not uploaded (no folder specified)",
                                        })
                                        successful += 1
                                        continue
                                
                                # Upload to Drive
                                upload_result = upload_file_to_drive_folder(
                                    file_path=temp_excel_path,
                                    filename=excel_filename,
                                    folder_id=target_folder_id,
                                    auth_credentials=kwargs.get("auth_credentials", {}),
                                )
                                
                                if upload_result["success"]:
                                    results.append({
                                        "row": index + 1,
                                        "url_column": url_col,
                                        "sheet_url": sheet_url,
                                        "filename": excel_filename,
                                        "drive_file_id": upload_result["file_id"],
                                        "drive_file_url": upload_result["file_url"],
                                        "excel_url": upload_result["file_url"],  # Store Excel URL for metadata update
                                        "status": "success",
                                    })
                                    successful += 1
                                else:
                                    results.append({
                                        "row": index + 1,
                                        "url_column": url_col,
                                        "sheet_url": sheet_url,
                                        "status": "failed",
                                        "error": f"Upload failed: {upload_result.get('error', 'Unknown error')}"
                                    })
                                    failed += 1
                            else:
                                results.append({
                                    "row": index + 1,
                                    "url_column": url_col,
                                    "sheet_url": sheet_url,
                                    "status": "failed",
                                    "error": f"Conversion failed: {conversion_result.get('error', 'Unknown error')}"
                                })
                                failed += 1
                                
                        finally:
                            # Clean up temporary directory
                            import shutil
                            if os.path.exists(temp_dir):
                                shutil.rmtree(temp_dir)
                                
                    except Exception as e:
                        results.append({
                            "row": index + 1,
                            "url_column": url_col,
                            "sheet_url": sheet_url,
                            "status": "failed",
                            "error": str(e)
                        })
                        failed += 1
            
            # Create metadata for result columns
            metadata = {
                "total_processed": len(results),
                "successful": successful,
                "failed": failed,
                "drive_folder_id": kwargs["drive_folder_id"],
                "url_columns": url_columns,
            }
            
            # Add the Excel URL column to metadata so it gets written back to the spreadsheet
            # Prepend the source column name to make the output column more descriptive
            for url_col in url_columns:
                output_column_name = f"{url_col}_{kwargs.get('excel_url_column', 'excel_url')}"
                self._add_column_to_metadata(metadata, output_column_name, "excel_url")
            
            return UtilityResult(
                success=successful > 0,
                message=f"Batch conversion completed: {successful} successful, {failed} failed",
                data={"results": results},
                metadata=metadata
            )
            
        except Exception as e:
            return UtilityResult(
                success=False,
                message="Batch conversion failed",
                error=str(e)
            )


class BatchExcelToSheetsDriveUtility(SingleBatchUtility):
    """Utility for batch converting multiple Excel files to Google Sheets and uploading to Google Drive."""
    
    def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "metadata_file",
            help="CSV file or Google Sheets URL containing list of Excel files to convert"
        )
        parser.add_argument(
            "drive_folder_id",
            nargs="?",
            help="Google Drive folder ID where Google Sheets will be created (optional, defaults to original folder)"
        )
        parser.add_argument(
            "--url-columns",
            default="excel_url",
            help="Comma-separated column names containing Excel file URLs or paths (default: excel_url)"
        )
        parser.add_argument(
            "--filename-column",
            help="Column name containing custom filenames (optional)"
        )
        parser.add_argument(
            "--sheets-column",
            help="Column name containing sheet names to convert (optional)"
        )
        parser.add_argument(
            "--sheets-url-column",
            default="sheets_url",
            help="Column name for storing converted Google Sheets URLs (default: sheets_url)"
        )
    
    def _extract_utility_args(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Extract utility-specific arguments from parsed args."""
        return {
            "metadata_file": args.metadata_file,
            "drive_folder_id": getattr(args, 'drive_folder_id', None),
            "url_columns": args.url_columns,
            "filename_column": args.filename_column,
            "sheets_column": args.sheets_column,
            "sheets_url_column": args.sheets_url_column,
        }
    
    def execute_single(self, **kwargs) -> UtilityResult:
        """Execute batch conversion (same as batch for this utility)."""
        return self.execute_batch(**kwargs)
    
    def execute_batch(self, **kwargs) -> UtilityResult:
        """Execute batch Excel to Google Sheets + Drive conversion."""
        try:
            import pandas as pd
            
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
            
            # Parse URL columns
            url_columns = [col.strip() for col in kwargs["url_columns"].split(",")]
            
            # Validate all URL columns exist
            missing_columns = [col for col in url_columns if col not in df.columns]
            if missing_columns:
                return UtilityResult(
                    success=False,
                    message=f"URL columns not found in metadata file",
                    error=f"Missing columns: {missing_columns}. Available columns: {list(df.columns)}"
                )
            
            # Process each row
            results = []
            successful = 0
            failed = 0
            
            for index, row in df.iterrows():
                # Process each URL column for this row
                for url_col in url_columns:
                    excel_source = row[url_col]
                    if pd.isna(excel_source) or not str(excel_source).strip():
                        continue
                    
                    # Get custom filename if specified
                    custom_filename = None
                    if kwargs.get("filename_column") and kwargs["filename_column"] in df.columns:
                        custom_filename = row[kwargs["filename_column"]]
                        if pd.isna(custom_filename):
                            custom_filename = None
                    
                    # Get sheets to convert if specified
                    sheets_to_convert = None
                    if kwargs.get("sheets_column") and kwargs["sheets_column"] in df.columns:
                        sheets_spec = row[kwargs["sheets_column"]]
                        if not pd.isna(sheets_spec):
                            sheets_to_convert = [s.strip() for s in str(sheets_spec).split(",")]
                    
                    # Convert this Excel file using our existing utility
                    try:
                        excel_utility = ExcelToSheetsDriveUtility("temp", "temp")
                        
                        # Determine target folder ID - fallback to original folder if none specified
                        target_folder_id = kwargs["drive_folder_id"]
                        if not target_folder_id:
                            # Try to get original folder ID
                            from urarovite.utils.drive import get_original_folder_id
                            original_folder = get_original_folder_id(excel_source, kwargs.get("auth_credentials", {}))
                            if original_folder:
                                target_folder_id = original_folder
                                print(f"📁 Using original folder for {excel_source}")
                            else:
                                print(f"⚠️ Warning: No folder specified and couldn't determine original folder for {excel_source}")
                                # Skip conversion but mark as failed
                                results.append({
                                    "row": index + 1,
                                    "url_column": url_col,
                                    "excel_source": excel_source,
                                    "status": "failed",
                                    "error": "No folder specified and couldn't determine original folder"
                                })
                                failed += 1
                                continue
                        
                        # Prepare arguments
                        conversion_kwargs = {
                            "excel_source": excel_source,
                            "drive_folder_id": target_folder_id,
                            "filename": custom_filename,
                            "sheets": ",".join(sheets_to_convert) if sheets_to_convert else None,
                            "auth_credentials": kwargs.get("auth_credentials", {}),
                            "url_column": url_col  # Pass the column name to distinguish files
                        }
                        
                        result = excel_utility.execute_single(**conversion_kwargs)
                        
                        if result.success:
                            results.append({
                                "row": index + 1,
                                "url_column": url_col,
                                "excel_source": excel_source,
                                "sheets_name": result.metadata.get("sheets_name"),
                                "spreadsheet_id": result.metadata.get("spreadsheet_id"),
                                "spreadsheet_url": result.metadata.get("spreadsheet_url"),
                                "sheets_url": result.metadata.get("spreadsheet_url"),  # Store Sheets URL for metadata update
                                "status": "success"
                            })
                            successful += 1
                        else:
                            results.append({
                                "row": index + 1,
                                "url_column": url_col,
                                "excel_source": excel_source,
                                "status": "failed",
                                "error": result.error
                            })
                            failed += 1
                            
                    except Exception as e:
                        results.append({
                            "row": index + 1,
                            "url_column": url_col,
                            "excel_source": excel_source,
                            "status": "failed",
                            "error": str(e)
                        })
                        failed += 1
            
            # Create metadata for result columns
            metadata = {
                "total_processed": len(results),
                "successful": successful,
                "failed": failed,
                "drive_folder_id": kwargs["drive_folder_id"],
                "url_columns": url_columns,
            }
            
            # Add the Sheets URL column to metadata so it gets written back to the spreadsheet
            # Prepend the source column name to make the output column more descriptive
            for url_col in url_columns:
                output_column_name = f"{url_col}_{kwargs.get('sheets_url_column', 'sheets_url')}"
                self._add_column_to_metadata(metadata, output_column_name, "sheets_url")
            
            return UtilityResult(
                success=successful > 0,
                message=f"Batch conversion completed: {successful} successful, {failed} failed",
                data={"results": results},
                metadata=metadata
            )
            
        except Exception as e:
            return UtilityResult(
                success=False,
                message="Batch conversion failed",
                error=str(e)
            )


class SanitizeTabNamesUtility(SingleBatchUtility):
    """Utility for sanitizing tab names to be alphanumeric with spaces only."""
    
    def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "spreadsheet_source",
            help="Google Sheets URL or local Excel file path to sanitize tab names"
        )
        parser.add_argument(
            "--flag-only",
            action="store_true",
            help="Analyze only, don't make changes (analysis mode)"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Analyze only, don't make changes (deprecated, use --flag-only)"
        )
        parser.add_argument(
            "--apply-changes",
            action="store_true",
            help="Actually apply the tab name changes (deprecated, changes are applied by default)"
        )
    
    def _extract_utility_args(self, args: argparse.ArgumentParser) -> Dict[str, Any]:
        """Extract utility-specific arguments from parsed args."""
        return {
            "spreadsheet_source": args.spreadsheet_source,
            "dry_run": args.flag_only,  # Default to applying changes, use --flag-only for analysis only
        }
    
    def execute_single(self, **kwargs) -> UtilityResult:
        """Execute tab name sanitization on a single spreadsheet."""
        try:
            from urarovite.utils.tab_name_sanitizer import sanitize_spreadsheet_tab_names
            
            spreadsheet_source = kwargs["spreadsheet_source"]
            dry_run = kwargs.get("dry_run", True)
            
            # Sanitize tab names
            result = sanitize_spreadsheet_tab_names(
                spreadsheet_source=spreadsheet_source,
                auth_credentials=kwargs.get("auth_credentials", {}),
                dry_run=dry_run
            )
            
            if result["success"]:
                if result["changes_made"]:
                    return UtilityResult(
                        success=True,
                        message=f"Successfully sanitized tab names: {result['message']}",
                        data=result,
                        metadata={
                            "spreadsheet_source": spreadsheet_source,
                            "changes_made": True,
                            "tabs_affected": result.get("analysis", {}).get("tabs_affected", 0),
                            "dry_run": dry_run
                        }
                    )
                else:
                    return UtilityResult(
                        success=True,
                        message=result["message"],
                        data=result,
                        metadata={
                            "spreadsheet_source": spreadsheet_source,
                            "changes_made": False,
                            "tabs_affected": result.get("analysis", {}).get("tabs_affected", 0),
                            "dry_run": dry_run
                        }
                    )
            else:
                return UtilityResult(
                    success=False,
                    message="Tab name sanitization failed",
                    error=result.get("error", "Unknown error"),
                    data=result
                )
                
        except Exception as e:
            return UtilityResult(
                success=False,
                message="Tab name sanitization failed",
                error=str(e)
            )
    
    def execute_batch(self, **kwargs) -> UtilityResult:
        """Execute batch sanitization (same as single for this utility)."""
        return self.execute_single(**kwargs)


class BatchSanitizeTabNamesUtility(SingleBatchUtility):
    """Utility for batch sanitizing tab names in multiple spreadsheets."""
    
    def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "metadata_file",
            help="CSV file or Google Sheets URL containing list of spreadsheets to process"
        )
        parser.add_argument(
            "--url-columns",
            default="spreadsheet_url",
            help="Comma-separated column names containing spreadsheet URLs (default: spreadsheet_url)"
        )
        parser.add_argument(
            "--flag-only",
            action="store_true",
            help="Analyze only, don't make changes (analysis mode)"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Analyze only, don't make changes (deprecated, use --flag-only)"
        )
        parser.add_argument(
            "--apply-changes",
            action="store_true",
            help="Actually apply the tab name changes (deprecated, changes are applied by default)"
        )
    
    def _extract_utility_args(self, args: argparse.ArgumentParser) -> Dict[str, Any]:
        """Extract utility-specific arguments from parsed args."""
        return {
            "metadata_file": args.metadata_file,
            "url_columns": args.url_columns,
            "dry_run": args.flag_only,  # Default to applying changes, use --flag-only for analysis only
        }
    
    def execute_single(self, **kwargs) -> UtilityResult:
        """Execute batch sanitization (same as batch for this utility)."""
        return self.execute_batch(**kwargs)
    
    def execute_batch(self, **kwargs) -> UtilityResult:
        """Execute batch tab name sanitization."""
        try:
            import pandas as pd
            
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
            
            # Parse URL columns
            url_columns = [col.strip() for col in kwargs["url_columns"].split(",")]
            
            # Validate all URL columns exist
            missing_columns = [col for col in url_columns if col not in df.columns]
            if missing_columns:
                return UtilityResult(
                    success=False,
                    message=f"URL columns not found in metadata file",
                    error=f"Missing columns: {missing_columns}. Available columns: {list(df.columns)}"
                )
            
            # Process each row
            results = []
            successful = 0
            failed = 0
            
            for index, row in df.iterrows():
                # Process each URL column for this row
                for url_col in url_columns:
                    spreadsheet_url = row[url_col]
                    if pd.isna(spreadsheet_url) or not str(spreadsheet_url).strip():
                        continue
                    
                    # Sanitize tab names in this spreadsheet
                    try:
                        from urarovite.utils.tab_name_sanitizer import sanitize_spreadsheet_tab_names
                        
                        result = sanitize_spreadsheet_tab_names(
                            spreadsheet_source=spreadsheet_url,
                            auth_credentials=kwargs.get("auth_credentials", {}),
                            dry_run=kwargs.get("dry_run", True)
                        )
                        
                        if result["success"]:
                            results.append({
                                "row": index + 1,
                                "url_column": url_col,
                                "spreadsheet_url": spreadsheet_url,
                                "tabs_affected": result.get("analysis", {}).get("tabs_affected", 0),
                                "changes_made": result.get("changes_made", False),
                                "status": "success",
                                "message": result.get("message", "Analysis completed")
                            })
                            successful += 1
                        else:
                            results.append({
                                "row": index + 1,
                                "url_column": url_col,
                                "spreadsheet_url": spreadsheet_url,
                                "status": "failed",
                                "error": result.get("error", "Unknown error")
                            })
                            failed += 1
                            
                    except Exception as e:
                        results.append({
                            "row": index + 1,
                            "url_column": url_col,
                            "spreadsheet_url": spreadsheet_url,
                            "status": "failed",
                            "error": str(e)
                        })
                        failed += 1
            
            return UtilityResult(
                success=successful > 0,
                message=f"Batch tab name sanitization completed: {successful} successful, {failed} failed",
                data={"results": results},
                metadata={
                    "total_processed": len(results),
                    "successful": successful,
                    "failed": failed,
                    "dry_run": kwargs.get("dry_run", True)
                }
            )
            
        except Exception as e:
            return UtilityResult(
                success=False,
                message="Batch tab name sanitization failed",
                error=str(e)
            )


class RenameTabUtility(SingleBatchUtility):
    """Utility for renaming a single tab in a spreadsheet with a custom name."""
    
    def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "spreadsheet_source",
            help="Google Sheets URL or local Excel file path"
        )
        parser.add_argument(
            "tab_name",
            help="Current name of the tab to rename"
        )
        parser.add_argument(
            "new_tab_name",
            help="New name for the tab"
        )
        parser.add_argument(
            "--a1-reference-columns",
            nargs="+",
            help="Column names that contain A1 references to the tab being renamed (e.g., 'formula_column', 'reference_column')"
        )
        parser.add_argument(
            "--analyze-only",
            action="store_true",
            help="Analyze only, don't make changes"
        )
    
    def _extract_utility_args(self, args: argparse.ArgumentParser) -> Dict[str, Any]:
        """Extract utility-specific arguments from parsed args."""
        return {
            "spreadsheet_source": args.spreadsheet_source,
            "tab_name": args.tab_name,
            "new_tab_name": args.new_tab_name,
            "a1_reference_columns": args.a1_reference_columns or [],
            "analyze_only": args.analyze_only,
        }
    
    def execute_single(self, **kwargs) -> UtilityResult:
        """Execute single tab rename."""
        try:
            from urarovite.utils.tab_renamer import rename_single_tab, analyze_tab_rename_requirements
            
            spreadsheet_source = kwargs["spreadsheet_source"]
            tab_name = kwargs["tab_name"]
            new_tab_name = kwargs["new_tab_name"]
            analyze_only = kwargs.get("analyze_only", False)
            
            if analyze_only:
                # Analyze only
                analysis_result = analyze_tab_rename_requirements(
                    spreadsheet_source=spreadsheet_source,
                    rename_mapping={tab_name: new_tab_name},
                    auth_credentials=kwargs.get("auth_credentials", {})
                )
                
                if analysis_result["success"]:
                    return UtilityResult(
                        success=True,
                        message=f"Analysis completed: {analysis_result['message']}",
                        data=analysis_result,
                        metadata={
                            "spreadsheet_source": spreadsheet_source,
                            "tab_name": tab_name,
                            "new_tab_name": new_tab_name,
                            "analyze_only": True,
                            "can_rename": analysis_result.get("can_rename", False)
                        }
                    )
                else:
                    return UtilityResult(
                        success=False,
                        message="Analysis failed",
                        error=analysis_result.get("error", "Unknown error"),
                        data=analysis_result
                    )
            else:
                # Perform the rename
                result = rename_single_tab(
                    spreadsheet_source=spreadsheet_source,
                    tab_name=tab_name,
                    new_tab_name=new_tab_name,
                    auth_credentials=kwargs.get("auth_credentials", {})
                )
                
                if result["success"]:
                    # Update A1 references if specified
                    a1_reference_columns = kwargs.get("a1_reference_columns", [])
                    a1_result = None
                    
                    if a1_reference_columns:
                        # Use the shared A1 reference update logic
                        from urarovite.utils.a1_range_validator import update_a1_references_in_spreadsheet_cells
                        from urarovite.core.spreadsheet import SpreadsheetFactory
                        
                        # Create spreadsheet interface for A1 reference updates
                        with SpreadsheetFactory.create_spreadsheet(
                            spreadsheet_source, 
                            kwargs.get("auth_credentials", {})
                        ) as spreadsheet:
                            a1_results = []
                            total_references_updated = 0
                            
                            # Update A1 references in each specified column
                            for col_name in a1_reference_columns:
                                try:
                                    col_result = update_a1_references_in_spreadsheet_cells(
                                        spreadsheet=spreadsheet,
                                        sheet_name=None,  # Will process all sheets
                                        column_name=col_name,
                                        old_tab_name=tab_name,
                                        new_tab_name=new_tab_name
                                    )
                                    
                                    if col_result["success"]:
                                        a1_results.append(col_result)
                                        total_references_updated += col_result.get("references_updated", 0)
                                    else:
                                        print(f"Warning: Failed to update A1 references in column '{col_name}': {col_result.get('error', 'Unknown error')}")
                                        
                                except Exception as e:
                                    print(f"Warning: Error updating A1 references in column '{col_name}': {e}")
                            
                            # Create combined A1 result
                            a1_result = {
                                "success": len(a1_results) > 0,
                                "changes_made": total_references_updated > 0,
                                "message": f"Updated {total_references_updated} A1 references in {len(a1_reference_columns)} columns",
                                "references_updated": total_references_updated,
                                "column_results": a1_results
                            }
                    
                    # Combine results
                    combined_message = result["message"]
                    if a1_result and a1_result.get("changes_made"):
                        combined_message += f" + {a1_result['message']}"
                    
                    return UtilityResult(
                        success=True,
                        message=combined_message,
                        data={
                            "tab_rename": result,
                            "a1_references": a1_result
                        },
                        metadata={
                            "spreadsheet_source": spreadsheet_source,
                            "tab_name": tab_name,
                            "new_tab_name": new_tab_name,
                            "changes_made": result.get("changes_made", False) or (a1_result and a1_result.get("changes_made", False)),
                            "analyze_only": False,
                            "a1_references_updated": a1_result.get("references_updated", 0) if a1_result else 0
                        }
                    )
                else:
                    return UtilityResult(
                        success=False,
                        message="Tab rename failed",
                        error=result.get("error", "Unknown error"),
                        data=result
                    )
                
        except Exception as e:
            return UtilityResult(
                success=False,
                message="Tab rename operation failed",
                error=str(e)
            )
    
    def execute_batch(self, **kwargs) -> UtilityResult:
        """Execute batch rename (same as single for this utility)."""
        return self.execute_single(**kwargs)


class BatchRenameTabsFromSheetUtility(SingleBatchUtility):
    """Utility for batch renaming multiple tabs using metadata from a sheet."""
    
    def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "metadata_file",
            help="CSV file or Google Sheets URL containing tab rename instructions"
        )
        parser.add_argument(
            "--url-column",
            default="spreadsheet_url",
            help="Column name containing spreadsheet URLs (default: spreadsheet_url)"
        )
        parser.add_argument(
            "--old-name-column",
            default="old_tab_name",
            help="Column name containing current tab names (default: old_tab_name)"
        )
        parser.add_argument(
            "--new-name-column",
            default="new_tab_name",
            help="Column name containing new tab names (default: new_tab_name)"
        )
        parser.add_argument(
            "--combined-column",
            help="Column containing both old and new names (e.g., 'old_name → new_name' or 'old_name|new_name')"
        )
        parser.add_argument(
            "--separator",
            default="→",
            help="Separator for combined column (default: →)"
        )
        parser.add_argument(
            "--a1-reference-columns",
            nargs="+",
            help="Column names that contain A1 references to tabs being renamed (e.g., 'formula_column', 'reference_column')"
        )
        parser.add_argument(
            "--analyze-only",
            action="store_true",
            help="Analyze only, don't make changes"
        )
    
    def _extract_utility_args(self, args: argparse.ArgumentParser) -> Dict[str, Any]:
        """Extract utility-specific arguments from parsed args."""
        return {
            "metadata_file": args.metadata_file,
            "url_column": args.url_column,
            "old_name_column": args.old_name_column,
            "new_name_column": args.new_name_column,
            "combined_column": args.combined_column,
            "separator": args.separator,
            "a1_reference_columns": args.a1_reference_columns or [],
            "analyze_only": args.analyze_only,
        }
    
    def execute_single(self, **kwargs) -> UtilityResult:
        """Execute batch rename (same as batch for this utility)."""
        return self.execute_batch(**kwargs)
    
    def execute_batch(self, **kwargs) -> UtilityResult:
        """Execute batch tab renaming."""
        try:
            import pandas as pd
            
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
            
            # Parse column names
            url_column = kwargs["url_column"]
            combined_column = kwargs.get("combined_column")
            separator = kwargs.get("separator", "→")
            
            if combined_column:
                # Using combined column approach
                if combined_column not in df.columns:
                    return UtilityResult(
                        success=False,
                        message=f"Combined column '{combined_column}' not found in metadata file",
                        error=f"Available columns: {list(df.columns)}"
                    )
                
                # Validate URL column exists
                if url_column not in df.columns:
                    return UtilityResult(
                        success=False,
                        message=f"URL column '{url_column}' not found in metadata file",
                        error=f"Available columns: {list(df.columns)}"
                    )
            else:
                # Using separate columns approach
                old_name_column = kwargs["old_name_column"]
                new_name_column = kwargs["new_name_column"]
                
                # Validate all required columns exist
                required_columns = [url_column, old_name_column, new_name_column]
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    return UtilityResult(
                        success=False,
                        message=f"Required columns not found in metadata file",
                        error=f"Missing columns: {missing_columns}. Available columns: {list(df.columns)}"
                    )
            
            # Process each row
            results = []
            successful = 0
            failed = 0
            
            for index, row in df.iterrows():
                spreadsheet_url = row[url_column]
                
                if pd.isna(spreadsheet_url) or not str(spreadsheet_url).strip():
                    continue
                
                if combined_column:
                    # Parse combined column
                    combined_value = row[combined_column]
                    if pd.isna(combined_value) or not str(combined_value).strip():
                        continue
                    
                    # Split by separator
                    parts = str(combined_value).split(separator)
                    if len(parts) != 2:
                        continue
                    
                    old_tab_name = parts[0].strip()
                    new_tab_name = parts[1].strip()
                    
                    if not old_tab_name or not new_tab_name:
                        continue
                else:
                    # Use separate columns
                    old_tab_name = row[old_name_column]
                    new_tab_name = row[new_name_column]
                    
                    if pd.isna(old_tab_name) or pd.isna(new_tab_name):
                        continue
                    
                    if not str(old_tab_name).strip() or not str(new_tab_name).strip():
                        continue
                
                # Process this tab rename
                try:
                    from urarovite.utils.tab_renamer import rename_single_tab, analyze_tab_rename_requirements
                    
                    if kwargs.get("analyze_only", False):
                        # Analyze only
                        result = analyze_tab_rename_requirements(
                            spreadsheet_source=spreadsheet_url,
                            rename_mapping={str(old_tab_name): str(new_tab_name)},
                            auth_credentials=kwargs.get("auth_credentials", {})
                        )
                        
                        if result["success"]:
                            results.append({
                                "row": index + 1,
                                "spreadsheet_url": spreadsheet_url,
                                "old_tab_name": old_tab_name,
                                "new_tab_name": new_tab_name,
                                "status": "analyzed",
                                "can_rename": result.get("can_rename", False),
                                "message": result.get("message", "Analysis completed")
                            })
                            successful += 1
                        else:
                            results.append({
                                "row": index + 1,
                                "spreadsheet_url": spreadsheet_url,
                                "old_tab_name": old_tab_name,
                                "new_tab_name": new_tab_name,
                                "status": "analysis_failed",
                                "error": result.get("error", "Unknown error")
                            })
                            failed += 1
                    else:
                        # Perform the rename
                        result = rename_single_tab(
                            spreadsheet_source=spreadsheet_url,
                            tab_name=str(old_tab_name),
                            new_tab_name=str(new_tab_name),
                            auth_credentials=kwargs.get("auth_credentials", {})
                        )
                        
                        if result["success"]:
                            # Update A1 references if specified
                            a1_reference_columns = kwargs.get("a1_reference_columns", [])
                            a1_result = None
                            
                            if a1_reference_columns:
                                # Use the shared A1 reference update logic
                                from urarovite.utils.a1_range_validator import update_a1_references_in_spreadsheet_cells
                                from urarovite.core.spreadsheet import SpreadsheetFactory
                                
                                # Create spreadsheet interface for A1 reference updates
                                with SpreadsheetFactory.create_spreadsheet(
                                    spreadsheet_url, 
                                    kwargs.get("auth_credentials", {})
                                ) as spreadsheet:
                                    a1_results = []
                                    total_references_updated = 0
                                    
                                    # Update A1 references in each specified column
                                    for col_name in a1_reference_columns:
                                        try:
                                            col_result = update_a1_references_in_spreadsheet_cells(
                                                spreadsheet=spreadsheet,
                                                sheet_name=None,  # Will process all sheets
                                                column_name=col_name,
                                                old_tab_name=str(old_tab_name),
                                                new_tab_name=str(new_tab_name)
                                            )
                                            
                                            if col_result["success"]:
                                                a1_results.append(col_result)
                                                total_references_updated += col_result.get("references_updated", 0)
                                            else:
                                                print(f"Warning: Failed to update A1 references in column '{col_name}': {col_result.get('error', 'Unknown error')}")
                                                
                                        except Exception as e:
                                            print(f"Warning: Error updating A1 references in column '{col_name}': {e}")
                                    
                                    # Create combined A1 result
                                    a1_result = {
                                        "success": len(a1_results) > 0,
                                        "changes_made": total_references_updated > 0,
                                        "message": f"Updated {total_references_updated} A1 references in {len(a1_reference_columns)} columns",
                                        "references_updated": total_references_updated,
                                        "column_results": a1_results
                                    }
                            
                            # Combine results
                            combined_message = result.get("message", "Rename completed")
                            if a1_result and a1_result.get("changes_made"):
                                combined_message += f" + {a1_result['message']}"
                            
                            results.append({
                                "row": index + 1,
                                "spreadsheet_url": spreadsheet_url,
                                "old_tab_name": old_tab_name,
                                "new_tab_name": new_tab_name,
                                "status": "success",
                                "changes_made": result.get("changes_made", False) or (a1_result and a1_result.get("changes_made", False)),
                                "message": combined_message,
                                "a1_references_updated": a1_result.get("references_updated", 0) if a1_result else 0
                            })
                            successful += 1
                        else:
                            results.append({
                                "row": index + 1,
                                "spreadsheet_url": spreadsheet_url,
                                "old_tab_name": old_tab_name,
                                "new_tab_name": new_tab_name,
                                "status": "failed",
                                "error": result.get("error", "Unknown error")
                            })
                            failed += 1
                            
                except Exception as e:
                    results.append({
                        "row": index + 1,
                        "spreadsheet_url": spreadsheet_url,
                        "old_tab_name": old_tab_name,
                        "new_tab_name": new_tab_name,
                        "status": "failed",
                        "error": str(e)
                    })
                    failed += 1
            
            mode = "analysis" if kwargs.get("analyze_only", False) else "rename"
            return UtilityResult(
                success=successful > 0,
                message=f"Batch tab {mode} completed: {successful} successful, {failed} failed",
                data={"results": results},
                metadata={
                    "total_processed": len(results),
                    "successful": successful,
                    "failed": failed,
                    "mode": mode
                }
            )
            
        except Exception as e:
            return UtilityResult(
                success=False,
                message="Batch tab rename operation failed",
                error=str(e)
            )


class BatchRenameTabsUtility(SingleBatchUtility):
    """Utility for batch renaming tabs with direct URL and tab name arguments (flat approach)."""
    
    def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "spreadsheet_urls",
            nargs="+",
            help="One or more Google Sheets URLs to process"
        )
        parser.add_argument(
            "--old-names",
            nargs="+",
            required=True,
            help="Current tab names to rename (must match number of URLs)"
        )
        parser.add_argument(
            "--new-names",
            nargs="+",
            required=True,
            help="New tab names (must match number of URLs)"
        )
        parser.add_argument(
            "--a1-reference-columns",
            nargs="+",
            help="Column names that contain A1 references to tabs being renamed (e.g., 'formula_column', 'reference_column')"
        )
        parser.add_argument(
            "--analyze-only",
            action="store_true",
            help="Analyze only, don't make changes"
        )
    
    def _extract_utility_args(self, args: argparse.ArgumentParser) -> Dict[str, Any]:
        """Extract utility-specific arguments from parsed args."""
        return {
            "spreadsheet_urls": args.spreadsheet_urls,
            "old_names": args.old_names,
            "new_names": args.new_names,
            "a1_reference_columns": args.a1_reference_columns or [],
            "analyze_only": args.analyze_only,
        }
    
    def execute_single(self, **kwargs) -> UtilityResult:
        """Execute batch rename (same as batch for this utility)."""
        return self.execute_batch(**kwargs)
    
    def execute_batch(self, **kwargs) -> UtilityResult:
        """Execute flat batch tab renaming."""
        try:
            spreadsheet_urls = kwargs["spreadsheet_urls"]
            old_names = kwargs["old_names"]
            new_names = kwargs["new_names"]
            analyze_only = kwargs.get("analyze_only", False)
            
            # Validate argument counts match
            if len(spreadsheet_urls) != len(old_names) or len(spreadsheet_urls) != len(new_names):
                return UtilityResult(
                    success=False,
                    message="Argument count mismatch",
                    error=f"Must provide same number of URLs ({len(spreadsheet_urls)}), old names ({len(old_names)}), and new names ({len(new_names)})"
                )
            
            # Process each rename operation
            results = []
            successful = 0
            failed = 0
            
            for i, (spreadsheet_url, old_name, new_name) in enumerate(zip(spreadsheet_urls, old_names, new_names)):
                try:
                    from urarovite.utils.tab_renamer import rename_single_tab, analyze_tab_rename_requirements
                    
                    if analyze_only:
                        # Analyze only
                        result = analyze_tab_rename_requirements(
                            spreadsheet_source=spreadsheet_url,
                            rename_mapping={old_name: new_name},
                            auth_credentials=kwargs.get("auth_credentials", {})
                        )
                        
                        if result["success"]:
                            results.append({
                                "index": i + 1,
                                "spreadsheet_url": spreadsheet_url,
                                "old_name": old_name,
                                "new_name": new_name,
                                "status": "analyzed",
                                "can_rename": result.get("can_rename", False),
                                "message": result.get("message", "Analysis completed")
                            })
                            successful += 1
                        else:
                            results.append({
                                "index": i + 1,
                                "spreadsheet_url": spreadsheet_url,
                                "old_name": old_name,
                                "new_name": new_name,
                                "status": "analysis_failed",
                                "error": result.get("error", "Unknown error")
                            })
                            failed += 1
                    else:
                        # Perform the rename
                        result = rename_single_tab(
                            spreadsheet_source=spreadsheet_url,
                            tab_name=old_name,
                            new_tab_name=new_name,
                            auth_credentials=kwargs.get("auth_credentials", {})
                        )
                        
                        if result["success"]:
                            # Update A1 references if specified
                            a1_reference_columns = kwargs.get("a1_reference_columns", [])
                            a1_result = None
                            
                            if a1_reference_columns:
                                # Use the shared A1 reference update logic
                                from urarovite.utils.a1_range_validator import update_a1_references_in_spreadsheet_cells
                                from urarovite.core.spreadsheet import SpreadsheetFactory
                                
                                # Create spreadsheet interface for A1 reference updates
                                with SpreadsheetFactory.create_spreadsheet(
                                    spreadsheet_url, 
                                    kwargs.get("auth_credentials", {})
                                ) as spreadsheet:
                                    a1_results = []
                                    total_references_updated = 0
                                    
                                    # Update A1 references in each specified column
                                    for col_name in a1_reference_columns:
                                        try:
                                            col_result = update_a1_references_in_spreadsheet_cells(
                                                spreadsheet=spreadsheet,
                                                sheet_name=None,  # Will process all sheets
                                                column_name=col_name,
                                                old_tab_name=old_name,
                                                new_tab_name=new_name
                                            )
                                            
                                            if col_result["success"]:
                                                a1_results.append(col_result)
                                                total_references_updated += col_result.get("references_updated", 0)
                                            else:
                                                print(f"Warning: Failed to update A1 references in column '{col_name}': {col_result.get('error', 'Unknown error')}")
                                                
                                        except Exception as e:
                                            print(f"Warning: Error updating A1 references in column '{col_name}': {e}")
                                    
                                    # Create combined A1 result
                                    a1_result = {
                                        "success": len(a1_results) > 0,
                                        "changes_made": total_references_updated > 0,
                                        "message": f"Updated {total_references_updated} A1 references in {len(a1_reference_columns)} columns",
                                        "references_updated": total_references_updated,
                                        "column_results": a1_results
                                    }
                            
                            # Combine results
                            combined_message = result.get("message", "Rename completed")
                            if a1_result and a1_result.get("changes_made"):
                                combined_message += f" + {a1_result['message']}"
                            
                            results.append({
                                "index": i + 1,
                                "spreadsheet_url": spreadsheet_url,
                                "old_name": old_name,
                                "new_name": new_name,
                                "status": "success",
                                "changes_made": result.get("changes_made", False) or (a1_result and a1_result.get("changes_made", False)),
                                "message": combined_message,
                                "a1_references_updated": a1_result.get("references_updated", 0) if a1_result else 0
                            })
                            successful += 1
                        else:
                            results.append({
                                "index": i + 1,
                                "spreadsheet_url": spreadsheet_url,
                                "old_name": old_name,
                                "new_name": new_name,
                                "status": "failed",
                                "error": result.get("error", "Unknown error")
                            })
                            failed += 1
                            
                except Exception as e:
                    results.append({
                        "index": i + 1,
                        "spreadsheet_url": spreadsheet_url,
                        "old_name": old_name,
                        "new_name": new_name,
                        "status": "failed",
                        "error": str(e)
                    })
                    failed += 1
            
            mode = "analysis" if analyze_only else "rename"
            return UtilityResult(
                success=successful > 0,
                message=f"Flat batch tab {mode} completed: {successful} successful, {failed} failed",
                data={"results": results},
                metadata={
                    "total_processed": len(results),
                    "successful": successful,
                    "failed": failed,
                    "mode": mode
                }
            )
            
        except Exception as e:
            return UtilityResult(
                success=False,
                message="Flat batch tab rename operation failed",
                error=str(e)
            )


class ValidateA1RangesUtility(SingleBatchUtility):
    """Utility for validating A1 notation ranges for proper tab name formatting."""
    
    def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "spreadsheet_source",
            help="Google Sheets URL or local Excel file path"
        )
        parser.add_argument(
            "--column",
            required=True,
            help="Column name containing A1 ranges to validate/fix"
        )
        parser.add_argument(
            "--url-columns",
            default="spreadsheet_url",
            help="Column names containing spreadsheet URLs for batch processing (default: spreadsheet_url)"
        )
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Use strict validation mode (default: True)"
        )
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Attempt to fix common issues in the range text (default behavior)"
        )
        parser.add_argument(
            "--validate-only",
            action="store_true",
            help="Only validate ranges, don't fix them"
        )
        parser.add_argument(
            "--default-tab-name",
            help="Default tab name to use when fixing ranges that lack tab names"
        )
        parser.add_argument(
            "--examples",
            action="store_true",
            help="Show examples of correct and incorrect formats"
        )
        parser.add_argument(
            "--input-url-column",
            help="Column name containing input sheet URLs (for truncated tab name matching)"
        )
        parser.add_argument(
            "--output-url-column",
            help="Column name containing output sheet URLs (for truncated tab name matching)"
        )
    
    def _extract_utility_args(self, args: argparse.ArgumentParser) -> Dict[str, Any]:
        """Extract utility-specific arguments from parsed args."""
        return {
            "spreadsheet_source": args.spreadsheet_source,
            "column": args.column,
            "url_columns": args.url_columns,
            "strict": not args.strict,  # Default to True, --strict flips it
            "fix": not args.validate_only,  # Default to True (fix mode), --validate-only flips it
            "default_tab_name": args.default_tab_name,
            "examples": args.examples,
            "input_url_column": args.input_url_column,
            "output_url_column": args.output_url_column,
        }
    
    def execute_single(self, **kwargs) -> UtilityResult:
        """Execute A1 range validation from spreadsheet column."""
        try:
            from urarovite.utils.a1_range_validator import (
                validate_a1_ranges,
                fix_a1_ranges,
                get_a1_validation_examples
            )
            from urarovite.utils.generic_spreadsheet import get_spreadsheet_data
            from urarovite.core.spreadsheet import SpreadsheetFactory
            
            spreadsheet_source = kwargs["spreadsheet_source"]
            column_name = kwargs["column"]
            strict_mode = kwargs.get("strict", True)
            fix_mode = kwargs.get("fix", True)  # Default to fix mode
            default_tab_name = kwargs.get("default_tab_name")
            show_examples = kwargs.get("examples", False)
            input_url_column = kwargs.get("input_url_column")
            output_url_column = kwargs.get("output_url_column")
            
            if show_examples:
                examples = get_a1_validation_examples()
                return UtilityResult(
                    success=True,
                    message="A1 range format examples",
                    data=examples,
                    metadata={
                        "operation": "examples",
                        "spreadsheet_source": spreadsheet_source,
                        "column": column_name
                    }
                )
            
            # Get spreadsheet tabs first
            from urarovite.utils.generic_spreadsheet import get_spreadsheet_tabs
            
            tabs_result = get_spreadsheet_tabs(spreadsheet_source, auth_credentials=kwargs.get("auth_credentials", {}))
            if not tabs_result["accessible"]:
                return UtilityResult(
                    success=False,
                    message="Failed to access spreadsheet",
                    error=tabs_result["error"],
                    data=tabs_result
                )
            
            # Find the specified column across all sheets
            column_data = []
            column_found = False
            available_columns = []
            
            # Check if we need to extract URLs (use hyperlink extraction if URL columns are specified)
            need_urls = input_url_column or output_url_column
            
            for sheet_name in tabs_result["tabs"]:
                try:
                    if need_urls:
                        # Use hyperlink extraction to get actual URLs from smart chips
                        from urarovite.utils.sheets import get_sheet_data_with_hyperlinks
                        from urarovite.auth.google_sheets import create_sheets_service_from_encoded_creds
                        from urarovite.utils.drive import _extract_auth_secret
                        
                        auth_secret = _extract_auth_secret(kwargs.get("auth_credentials", {}))
                        sheets_service = create_sheets_service_from_encoded_creds(auth_secret)
                        
                        # Extract spreadsheet ID and sheet GID
                        import re
                        spreadsheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', spreadsheet_source)
                        sheet_gid_match = re.search(r'gid=([0-9]+)', spreadsheet_source)
                        
                        if spreadsheet_id_match:
                            spreadsheet_id = spreadsheet_id_match.group(1)
                            sheet_gid = int(sheet_gid_match.group(1)) if sheet_gid_match else 0
                            
                            # Get data with hyperlinks
                            values = get_sheet_data_with_hyperlinks(sheets_service, spreadsheet_id, sheet_name, sheet_gid)
                        else:
                            # Fallback to regular data extraction
                            sheet_data_result = get_spreadsheet_data(
                                spreadsheet_source, 
                                f"'{sheet_name}'!A1:ZZ1000",
                                auth_credentials=kwargs.get("auth_credentials", {})
                            )
                            values = sheet_data_result["values"] if sheet_data_result["success"] else []
                    else:
                        # Regular data extraction when URLs are not needed
                        sheet_data_result = get_spreadsheet_data(
                            spreadsheet_source, 
                            f"'{sheet_name}'!A1:ZZ1000",  # Large range to get all data
                            auth_credentials=kwargs.get("auth_credentials", {})
                        )
                        values = sheet_data_result["values"] if sheet_data_result["success"] else []
                    
                    if values:
                        # First row contains headers
                        headers = values[0] if values else []
                        available_columns.extend(headers)
                        
                        if column_name in headers:
                            col_idx = headers.index(column_name)
                            column_found = True
                            
                            # Find URL column indices if specified
                            input_url_idx = headers.index(input_url_column) if input_url_column and input_url_column in headers else None
                            output_url_idx = headers.index(output_url_column) if output_url_column and output_url_column in headers else None
                            
                            # Extract all non-empty values from this column
                            for row_idx, row in enumerate(values[1:], start=1):  # Skip header row
                                if col_idx < len(row) and row[col_idx]:
                                    cell_value = str(row[col_idx]).strip()
                                    if cell_value:  # Skip empty cells
                                        # Extract URLs from the same row if URL columns are specified
                                        input_url = None
                                        output_url = None
                                        if input_url_idx is not None and input_url_idx < len(row):
                                            input_url = str(row[input_url_idx]).strip() if row[input_url_idx] else None
                                        if output_url_idx is not None and output_url_idx < len(row):
                                            output_url = str(row[output_url_idx]).strip() if row[output_url_idx] else None
                                        
                                        column_data.append({
                                            "sheet": sheet_name,
                                            "row": row_idx + 1,
                                            "value": cell_value,
                                            "input_url": input_url,
                                            "output_url": output_url
                                        })
                except Exception as e:
                    print(f"Warning: Failed to process sheet {sheet_name}: {e}")
                    continue
            
            if not column_found:
                return UtilityResult(
                    success=False,
                    message=f"Column '{column_name}' not found in any sheet",
                    error="column_not_found",
                    data={"available_columns": list(set(available_columns))}
                )
            
            if not column_data:
                return UtilityResult(
                    success=False,
                    message=f"Column '{column_name}' is empty or contains no data",
                    error="no_data",
                    data={"column": column_name}
                )
            
            # Helper function to extract tab names from URLs
            def get_tabs_from_url(url: str) -> List[str]:
                """Extract tab names from a spreadsheet URL."""
                if not url or not isinstance(url, str) or not url.startswith('http'):
                    return []
                try:
                    from urarovite.utils.generic_spreadsheet import get_spreadsheet_tabs
                    result = get_spreadsheet_tabs(url, auth_credentials=kwargs.get("auth_credentials", {}))
                    return result.get("tabs", []) if result.get("accessible", False) else []
                except Exception as e:
                    print(f"Warning: Failed to get tabs from {url}: {e}")
                    return []
            
            # Process each range value
            total_ranges = len(column_data)
            validation_results = []
            fix_results = []
            changes_applied = False
            
            # Get all available tab names from the metadata spreadsheet for comparison
            metadata_tabs = tabs_result.get("tabs", [])
            
            for item in column_data:
                range_text = item["value"]
                
                # Get tab names from input/output URLs if available
                input_tabs = get_tabs_from_url(item.get("input_url")) if item.get("input_url") else []
                output_tabs = get_tabs_from_url(item.get("output_url")) if item.get("output_url") else []
                
                # Combine all available tab names: metadata tabs + input/output tabs
                all_available_tabs = list(set(metadata_tabs + input_tabs + output_tabs))
                
                # Always validate the range with tab name matching
                validation_result = validate_a1_ranges(
                    range_text=range_text,
                    strict_mode=strict_mode,
                    input_sheet_tabs=all_available_tabs,  # Use all available tabs
                    output_sheet_tabs=[]  # We already included these above
                )
                
                # If in fix mode, also show what the fixed version would be
                if fix_mode:
                    fix_result = fix_a1_ranges(
                        range_text=range_text,
                        default_tab_name=default_tab_name,
                        input_sheet_tabs=all_available_tabs,  # Use all available tabs
                        output_sheet_tabs=[]  # We already included these above
                    )
                    
                    if fix_result["success"] and fix_result.get("changes_made"):
                        fix_results.append({
                            "sheet": item["sheet"],
                            "row": item["row"],
                            "original": range_text,
                            "fixed": fix_result["fixed_text"],
                            "changes": fix_result.get("changes_made", [])
                        })
                        
                        # Actually apply the fix to the spreadsheet
                        try:
                            # Use the spreadsheet object directly to update the cell
                            with SpreadsheetFactory.create_spreadsheet(
                                spreadsheet_source, 
                                kwargs.get("auth_credentials", {})
                            ) as spreadsheet:
                                # Get the current sheet data to find the column index
                                sheet_data = spreadsheet.get_sheet_data(item['sheet'])
                                if sheet_data and sheet_data.values:
                                    headers = sheet_data.values[0] if sheet_data.values else []
                                    if column_name in headers:
                                        col_idx = headers.index(column_name)
                                        # Create a 2D list with just the single cell value
                                        cell_value = [[fix_result["fixed_text"]]]
                                        # Update the specific cell using update_sheet_data
                                        spreadsheet.update_sheet_data(
                                            item['sheet'],
                                            cell_value,
                                            start_row=item['row'],
                                            start_col=col_idx + 1  # Convert to 1-based
                                        )
                                        spreadsheet.save()
                                        changes_applied = True
                                        print(f"✅ Fixed row {item['row']}: '{range_text}' → '{fix_result['fixed_text']}'")
                                    else:
                                        print(f"❌ Column '{column_name}' not found in sheet '{item['sheet']}'")
                                else:
                                    print(f"❌ Failed to get sheet data for '{item['sheet']}'")
                        except Exception as e:
                            print(f"❌ Error applying fix to row {item['row']}: {e}")
                
                validation_results.append({
                    "sheet": item["sheet"],
                    "row": item["row"],
                    "original": range_text,
                    "validation": validation_result
                })
            
            # Compile results
            valid_count = sum(1 for r in validation_results if r["validation"]["is_valid"])
            invalid_count = total_ranges - valid_count
            fixed_count = len(fix_results)
            
            if fix_mode:
                message = f"Processed {total_ranges} ranges: {valid_count} valid, {invalid_count} invalid, {fixed_count} fixed"
            else:
                message = f"Validated {total_ranges} ranges: {valid_count} valid, {invalid_count} invalid"
            
            return UtilityResult(
                success=True,
                message=message,
                data={
                    "validation_results": validation_results,
                    "fix_results": fix_results if fix_mode else [],
                    "summary": {
                        "total_ranges": total_ranges,
                        "valid_ranges": valid_count,
                        "invalid_ranges": invalid_count,
                        "ranges_fixed": fixed_count
                    }
                },
                metadata={
                    "operation": "spreadsheet_validation" if not fix_mode else "spreadsheet_fix",
                    "spreadsheet_source": spreadsheet_source,
                    "column": column_name,
                    "strict_mode": strict_mode,
                    "fix_mode": fix_mode,
                    "changes_made": changes_applied
                }
            )
                    
        except Exception as e:
            return UtilityResult(
                success=False,
                message="A1 range validation from spreadsheet failed",
                error=str(e)
            )
    
    def execute_batch(self, **kwargs) -> UtilityResult:
        """Execute batch validation across multiple spreadsheets using metadata sheet."""
        try:
            from urarovite.utils.a1_range_validator import (
                validate_a1_ranges,
                fix_a1_ranges,
                get_a1_validation_examples
            )
            from urarovite.utils.generic_spreadsheet import get_spreadsheet_data, get_spreadsheet_tabs
            from urarovite.core.spreadsheet import SpreadsheetFactory
            
            metadata_file = kwargs["spreadsheet_source"]
            column_name = kwargs["column"]
            url_columns = kwargs.get("url_columns", "spreadsheet_url")
            strict_mode = kwargs.get("strict", True)
            fix_mode = kwargs.get("fix", True)
            default_tab_name = kwargs.get("default_tab_name")
            show_examples = kwargs.get("examples", False)
            
            if show_examples:
                examples = get_a1_validation_examples()
                return UtilityResult(
                    success=True,
                    message="A1 range format examples",
                    data=examples,
                    metadata={
                        "operation": "examples",
                        "metadata_file": metadata_file,
                        "column": column_name
                    }
                )
            
            # Parse URL columns
            if isinstance(url_columns, str):
                url_columns = [col.strip() for col in url_columns.split(',')]
            
            # Get metadata spreadsheet data
            metadata_result = get_spreadsheet_data(metadata_file, "A1:ZZ1000", auth_credentials=kwargs.get("auth_credentials", {}))
            if not metadata_result["success"]:
                return UtilityResult(
                    success=False,
                    message="Failed to access metadata spreadsheet",
                    error=metadata_result.get("error", "unknown_error"),
                    data=metadata_result
                )
            
            metadata_values = metadata_result["values"]
            if not metadata_values or len(metadata_values) < 2:
                return UtilityResult(
                    success=False,
                    message="Metadata spreadsheet is empty or has no data rows",
                    error="no_data",
                    data={"metadata_file": metadata_file}
                )
            
            # Find required columns
            headers = metadata_values[0]
            column_idx = None
            url_column_indices = []
            
            # Find A1 column
            if column_name in headers:
                column_idx = headers.index(column_name)
            else:
                return UtilityResult(
                    success=False,
                    message=f"Column '{column_name}' not found in metadata spreadsheet",
                    error="column_not_found",
                    data={"available_columns": headers}
                )
            
            # Find URL columns
            for url_col in url_columns:
                if url_col in headers:
                    url_column_indices.append(headers.index(url_col))
                else:
                    print(f"Warning: URL column '{url_col}' not found in metadata")
            
            if not url_column_indices:
                return UtilityResult(
                    success=False,
                    message="No valid URL columns found for batch processing",
                    error="no_url_columns",
                    data={"url_columns": url_columns, "available_columns": headers}
                )
            
            # Find the first valid URL from the tabs_to_fix column to use for all rows
            base_url = None
            for row_idx, row in enumerate(metadata_values[1:], start=2):
                for url_idx in url_column_indices:
                    if url_idx < len(row) and row[url_idx]:
                        url = str(row[url_idx]).strip()
                        if url and url.startswith('http'):
                            base_url = url
                            break
                if base_url:
                    break
            
            if not base_url:
                return UtilityResult(
                    success=False,
                    message="No valid URLs found in the specified URL columns",
                    error="no_valid_urls",
                    data={"url_columns": url_columns}
                )
            
            # Get tabs from the base URL once
            tabs_result = get_spreadsheet_tabs(base_url, auth_credentials=kwargs.get("auth_credentials", {}))
            if not tabs_result.get("accessible", False):
                return UtilityResult(
                    success=False,
                    message=f"Cannot access spreadsheet at {base_url[:50]}...",
                    error="spreadsheet_not_accessible",
                    data={"url": base_url}
                )
            
            available_tabs = tabs_result.get("tabs", [])
            
            # Process each row in the metadata spreadsheet
            total_spreadsheets = len(metadata_values) - 1  # Skip header
            processed_count = 0
            validation_results = []
            fix_results = []
            changes_applied = False
            
            for row_idx, row in enumerate(metadata_values[1:], start=2):
                if column_idx >= len(row) or not row[column_idx]:
                    continue  # Skip rows without A1 ranges
                
                a1_ranges = str(row[column_idx]).strip()
                if not a1_ranges:
                    continue
                
                # Split by commas to handle multiple A1 ranges in one cell
                individual_ranges = [r.strip() for r in a1_ranges.split(',') if r.strip()]
                
                # Process each individual A1 range using the base URL and available tabs
                for range_idx, single_range in enumerate(individual_ranges):
                    
                    # Validate this individual A1 range
                    validation_result = validate_a1_ranges(
                        range_text=single_range,
                        strict_mode=strict_mode,
                        input_sheet_tabs=available_tabs,
                        output_sheet_tabs=[]
                    )
                    
                    # If in fix mode, also get fix suggestions
                    if fix_mode:
                        fix_result = fix_a1_ranges(
                            range_text=single_range,
                            default_tab_name=default_tab_name,
                            input_sheet_tabs=available_tabs,
                            output_sheet_tabs=[]
                        )
                        
                        if fix_result["success"] and fix_result.get("changes_made"):
                            fix_results.append({
                                "metadata_row": row_idx,
                                "spreadsheet_url": base_url,
                                "range_index": range_idx + 1,
                                "original": single_range,
                                "fixed": fix_result["fixed_text"],
                                "changes": fix_result.get("changes_made", [])
                            })
                            
                            # Actually apply the fix to the metadata spreadsheet
                            try:
                                from urarovite.utils.a1_range_validator import update_a1_references_in_spreadsheet_cells
                                
                                # Extract the old and new tab names from the fix
                                old_tab_match = re.match(r"^'([^']+)'!", single_range)
                                new_tab_match = re.match(r"^'([^']+)'!", fix_result["fixed_text"])
                                
                                if old_tab_match and new_tab_match:
                                    old_tab_name = old_tab_match.group(1)
                                    new_tab_name = new_tab_match.group(1)
                                    
                                    if old_tab_name != new_tab_name:
                                        # Use the centralized utility to update the spreadsheet
                                        with SpreadsheetFactory.create_spreadsheet(
                                            metadata_file, 
                                            kwargs.get("auth_credentials", {})
                                        ) as spreadsheet:
                                            update_result = update_a1_references_in_spreadsheet_cells(
                                                spreadsheet=spreadsheet,
                                                sheet_name=None,  # Process all sheets
                                                column_name=column_name,
                                                old_tab_name=old_tab_name,
                                                new_tab_name=new_tab_name
                                            )
                                            
                                            if update_result["success"] and update_result["references_updated"] > 0:
                                                changes_applied = True
                                            else:
                                                # Log error but continue processing
                                                pass
                                        
                            except Exception as e:
                                # Log error but continue processing
                                pass
                    
                    validation_results.append({
                        "metadata_row": row_idx,
                        "spreadsheet_url": base_url,
                        "range_index": range_idx + 1,
                        "a1_range": single_range,
                        "available_tabs": available_tabs,
                        "validation": validation_result
                    })
                
                processed_count += 1
            
            if processed_count == 0:
                return UtilityResult(
                    success=False,
                    message="No spreadsheets were successfully processed",
                    error="no_spreadsheets_processed",
                    data={"metadata_file": metadata_file, "url_columns": url_columns}
                )
            
            # Compile results
            valid_count = sum(1 for r in validation_results if r["validation"]["is_valid"])
            invalid_count = processed_count - valid_count
            fixed_count = len(fix_results)
            
            if fix_mode:
                message = f"Batch processed {processed_count} spreadsheets: {valid_count} valid, {invalid_count} invalid, {fixed_count} with fixes available"
            else:
                message = f"Batch validated {processed_count} spreadsheets: {valid_count} valid, {invalid_count} invalid"
            
            return UtilityResult(
                success=True,
                message=message,
                data={
                    "validation_results": validation_results,
                    "fix_results": fix_results if fix_mode else [],
                    "summary": {
                        "total_spreadsheets": total_spreadsheets,
                        "processed_spreadsheets": processed_count,
                        "valid_ranges": valid_count,
                        "invalid_ranges": invalid_count,
                        "ranges_with_fixes": fixed_count
                    }
                },
                metadata={
                    "operation": "batch_validation" if not fix_mode else "batch_validation_with_fixes",
                    "metadata_file": metadata_file,
                    "column": column_name,
                    "url_columns": url_columns,
                    "strict_mode": strict_mode,
                    "fix_mode": fix_mode,
                    "changes_made": changes_applied
                }
            )
                    
        except Exception as e:
            return UtilityResult(
                success=False,
                message="Batch A1 range validation failed",
                error=str(e)
            )


class BatchValidateA1RangesUtility(SingleBatchUtility):
    """Utility for batch validating and fixing A1 notation ranges across multiple spreadsheets."""
    
    def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "metadata_file",
            help="CSV file or Google Sheets URL containing list of spreadsheets to process"
        )
        parser.add_argument(
            "--url-columns",
            default="spreadsheet_url",
            help="Comma-separated column names containing spreadsheet URLs (default: spreadsheet_url)"
        )
        parser.add_argument(
            "--column",
            required=True,
            help="Column name containing A1 ranges to validate/fix in each spreadsheet"
        )
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Use strict validation mode (default: True)"
        )
        parser.add_argument(
            "--validate-only",
            action="store_true",
            help="Only validate ranges, don't fix them"
        )
        parser.add_argument(
            "--default-tab-name",
            help="Default tab name to use when fixing ranges that lack tab names"
        )
        parser.add_argument(
            "--output-format",
            choices=["table", "json", "csv"],
            default="table",
            help="Output format for results (default: table)"
        )
    
    def _extract_utility_args(self, args: argparse.ArgumentParser) -> Dict[str, Any]:
        """Extract utility-specific arguments from parsed args."""
        return {
            "metadata_file": args.metadata_file,
            "url_columns": args.url_columns,
            "column": args.column,
            "strict": not args.strict,  # Default to True, --strict flips it
            "fix": not args.validate_only,  # Default to True (fix mode), --validate-only flips it
            "default_tab_name": args.default_tab_name,
            "output_format": args.output_format,
        }
    
    def execute_single(self, **kwargs) -> UtilityResult:
        """Execute batch A1 range validation (same as batch for this utility)."""
        return self.execute_batch(**kwargs)
    
    def execute_batch(self, **kwargs) -> UtilityResult:
        """Execute batch A1 range validation and fixing."""
        try:
            import pandas as pd
            
            # Read metadata file
            metadata_file = kwargs["metadata_file"]
            if metadata_file.startswith("http"):
                # Google Sheets URL - use authenticated API
                try:
                    from urarovite.utils.sheets import extract_sheet_id
                    from urarovite.auth.google_sheets import get_gspread_client
                    
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
            
            # Parse URL columns
            url_columns = [col.strip() for col in kwargs["url_columns"].split(",")]
            
            # Validate all URL columns exist
            missing_columns = [col for col in url_columns if col not in df.columns]
            if missing_columns:
                return UtilityResult(
                    success=False,
                    message=f"URL columns not found in metadata file",
                    error=f"Missing columns: {missing_columns}. Available columns: {list(df.columns)}"
                )
            
            # Process each row
            results = []
            successful = 0
            failed = 0
            total_ranges_processed = 0
            total_ranges_valid = 0
            total_ranges_invalid = 0
            total_ranges_fixed = 0
            
            for index, row in df.iterrows():
                # Process each URL column for this row
                for url_col in url_columns:
                    spreadsheet_url = row[url_col]
                    if pd.isna(spreadsheet_url) or not str(spreadsheet_url).strip():
                        continue
                    
                    # Process A1 ranges in this spreadsheet
                    try:
                        from urarovite.utils.a1_range_validator import (
                            validate_a1_ranges,
                            fix_a1_ranges,
                            get_a1_validation_examples
                        )
                        from urarovite.utils.generic_spreadsheet import get_spreadsheet_tabs, get_spreadsheet_data
                        
                        # Get spreadsheet tabs first
                        tabs_result = get_spreadsheet_tabs(
                            spreadsheet_url, 
                            auth_credentials=kwargs.get("auth_credentials", {})
                        )
                        
                        if not tabs_result["accessible"]:
                            results.append({
                                "row": index + 1,
                                "url_column": url_col,
                                "spreadsheet_url": spreadsheet_url,
                                "status": "failed",
                                "error": f"Failed to access spreadsheet: {tabs_result['error']}"
                            })
                            failed += 1
                            continue
                        
                        # Find the specified column across all sheets
                        column_name = kwargs["column"]
                        column_data = []
                        column_found = False
                        
                        for sheet_name in tabs_result["tabs"]:
                            try:
                                # Get data from this sheet
                                sheet_data_result = get_spreadsheet_data(
                                    spreadsheet_url, 
                                    f"'{sheet_name}'!A1:ZZ1000",  # Large range to get all data
                                    auth_credentials=kwargs.get("auth_credentials", {})
                                )
                                
                                if sheet_data_result["success"] and sheet_data_result["values"]:
                                    values = sheet_data_result["values"]
                                    if values:
                                        # First row contains headers
                                        headers = values[0] if values else []
                                        
                                        if column_name in headers:
                                            col_idx = headers.index(column_name)
                                            column_found = True
                                            
                                            # Extract all non-empty values from this column
                                            for row_idx, row_data in enumerate(values[1:], start=1):
                                                if col_idx < len(row_data) and row_data[col_idx]:
                                                    cell_value = str(row_data[col_idx]).strip()
                                                    if cell_value:  # Skip empty cells
                                                        column_data.append({
                                                            "sheet": sheet_name,
                                                            "row": row_idx + 1,
                                                            "value": cell_value
                                                        })
                            except Exception as e:
                                print(f"Warning: Failed to process sheet {sheet_name} in {spreadsheet_url}: {e}")
                                continue
                        
                        if not column_found:
                            results.append({
                                "row": index + 1,
                                "url_column": url_col,
                                "spreadsheet_url": spreadsheet_url,
                                "status": "failed",
                                "error": f"Column '{column_name}' not found in any sheet"
                            })
                            failed += 1
                            continue
                        
                        if not column_data:
                            results.append({
                                "row": index + 1,
                                "url_column": url_col,
                                "spreadsheet_url": spreadsheet_url,
                                "status": "success",
                                "message": f"Column '{column_name}' is empty or contains no data",
                                "ranges_processed": 0,
                                "ranges_valid": 0,
                                "ranges_invalid": 0,
                                "ranges_fixed": 0
                            })
                            successful += 1
                            continue
                        
                        # Process each range value
                        ranges_processed = len(column_data)
                        ranges_valid = 0
                        ranges_invalid = 0
                        ranges_fixed = 0
                        validation_results = []
                        fix_results = []
                        
                        strict_mode = kwargs.get("strict", True)
                        fix_mode = kwargs.get("fix", True)
                        default_tab_name = kwargs.get("default_tab_name")
                        
                        for item in column_data:
                            range_text = item["value"]
                            
                            # Always validate the range
                            validation_result = validate_a1_ranges(
                                range_text=range_text,
                                strict_mode=strict_mode
                            )
                            
                            if validation_result["is_valid"]:
                                ranges_valid += 1
                            else:
                                ranges_invalid += 1
                            
                            validation_results.append({
                                "sheet": item["sheet"],
                                "row": item["row"],
                                "original": range_text,
                                "validation": validation_result
                            })
                            
                            # If in fix mode, also show what the fixed version would be
                            if fix_mode:
                                fix_result = fix_a1_ranges(
                                    range_text=range_text,
                                    default_tab_name=default_tab_name
                                )
                                
                                if fix_result["success"] and fix_result.get("changes_made"):
                                    ranges_fixed += 1
                                    fix_results.append({
                                        "sheet": item["sheet"],
                                        "row": item["row"],
                                        "original": range_text,
                                        "fixed": fix_result["fixed_text"],
                                        "changes": fix_result.get("changes_made", [])
                                    })
                        
                        # Compile results for this spreadsheet
                        total_ranges_processed += ranges_processed
                        total_ranges_valid += ranges_valid
                        total_ranges_invalid += ranges_invalid
                        total_ranges_fixed += ranges_fixed
                        
                        if fix_mode:
                            message = f"Processed {ranges_processed} ranges: {ranges_valid} valid, {ranges_invalid} invalid, {ranges_fixed} fixed"
                        else:
                            message = f"Validated {ranges_processed} ranges: {ranges_valid} valid, {ranges_invalid} invalid"
                        
                        results.append({
                            "row": index + 1,
                            "url_column": url_col,
                            "spreadsheet_url": spreadsheet_url,
                            "status": "success",
                            "message": message,
                            "ranges_processed": ranges_processed,
                            "ranges_valid": ranges_valid,
                            "ranges_invalid": ranges_invalid,
                            "ranges_fixed": ranges_fixed,
                            "validation_results": validation_results,
                            "fix_results": fix_results
                        })
                        successful += 1
                        
                    except Exception as e:
                        results.append({
                            "row": index + 1,
                            "url_column": url_col,
                            "spreadsheet_url": spreadsheet_url,
                            "status": "failed",
                            "error": str(e)
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
                        "URL_Column": result["url_column"],
                        "Spreadsheet_URL": result["spreadsheet_url"],
                        "Status": result["status"],
                        "Message": result.get("message", ""),
                        "Ranges_Processed": result.get("ranges_processed", 0),
                        "Ranges_Valid": result.get("ranges_valid", 0),
                        "Ranges_Invalid": result.get("ranges_invalid", 0),
                        "Ranges_Fixed": result.get("ranges_fixed", 0),
                        "Error": result.get("error", "")
                    })
                
                csv_df = pd.DataFrame(csv_data)
                csv_output = csv_df.to_csv(index=False)
                
                return UtilityResult(
                    success=successful > 0,
                    message=f"Batch A1 range validation completed: {successful} successful, {failed} failed",
                    data={"results": results, "csv_output": csv_output},
                    metadata={
                        "total_processed": len(results),
                        "successful": successful,
                        "failed": failed,
                        "total_ranges_processed": total_ranges_processed,
                        "total_ranges_valid": total_ranges_valid,
                        "total_ranges_invalid": total_ranges_invalid,
                        "total_ranges_fixed": total_ranges_fixed,
                        "fix_mode": kwargs.get("fix", True),
                        "output_format": output_format
                    }
                )
            else:
                # Default table output
                return UtilityResult(
                    success=successful > 0,
                    message=f"Batch A1 range validation completed: {successful} successful, {failed} failed",
                    data={"results": results},
                    metadata={
                        "total_processed": len(results),
                        "successful": successful,
                        "failed": failed,
                        "total_ranges_processed": total_ranges_processed,
                        "total_ranges_valid": total_ranges_valid,
                        "total_ranges_invalid": total_ranges_invalid,
                        "total_ranges_fixed": total_ranges_fixed,
                        "fix_mode": kwargs.get("fix", True),
                        "output_format": output_format
                    }
                )
            
        except Exception as e:
            return UtilityResult(
                success=False,
                message="Batch A1 range validation failed",
                error=str(e)
            )


class SpreadsheetAccessUtility(SingleBatchUtility):
    """Utility for checking spreadsheet access and metadata."""
    
    def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "spreadsheet_source",
            help="Google Sheets URL or Excel file path to check"
        )
        parser.add_argument(
            "--output-format",
            choices=["table", "json", "quiet"],
            default="table",
            help="Output format (default: table)"
        )
        parser.add_argument(
            "--detailed",
            action="store_true",
            help="Show detailed information including file metadata"
        )
        
        # Batch mode arguments
        parser.add_argument(
            "--url-columns",
            help="Comma-separated list of column names containing URLs to check (batch mode)"
        )
        parser.add_argument(
            "--metadata-sheet-name",
            default="access_check_metadata",
            help="Sheet name containing metadata (batch mode)"
        )
    
    def _extract_utility_args(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Extract utility-specific arguments from parsed args."""
        return {
            "spreadsheet_source": args.spreadsheet_source,
            "output_format": args.output_format,
            "detailed": args.detailed,
            "url_columns": args.url_columns,
            "metadata_sheet_name": args.metadata_sheet_name,
        }
    
    def execute_single(self, **kwargs) -> UtilityResult:
        """Execute single spreadsheet access check."""
        spreadsheet_source = kwargs["spreadsheet_source"]
        output_format = kwargs.get("output_format", "table")
        detailed = kwargs.get("detailed", False)
        auth_credentials = kwargs.get("auth_credentials", {})
        
        try:
            # Check spreadsheet access
            access_result = check_spreadsheet_access(
                spreadsheet_source, auth_credentials
            )
            
            if access_result["accessible"]:
                message = (
                    f"✅ Spreadsheet is accessible\n"
                    f"Type: {access_result['file_type']}\n"
                    f"Tabs: {len(access_result['tabs'])}"
                )
                
                if detailed and access_result.get("details"):
                    details = access_result["details"]
                    message += (
                        f"\nFile ID: {details.get('file_id', 'N/A')}\n"
                        f"File Name: {details.get('file_name', 'N/A')}\n"
                        f"MIME Type: {details.get('mime_type', 'N/A')}\n"
                        f"Size: {details.get('size_bytes', 'N/A')} bytes"
                    )
            else:
                error_type = access_result.get("error_type", "unknown")
                message = (
                    f"❌ Spreadsheet is not accessible\n"
                    f"Error Type: {error_type}\n"
                    f"Error: {access_result['error']}"
                )
            
            return UtilityResult(
                success=access_result["accessible"],
                message=message,
                data=access_result,
                metadata={
                    "spreadsheet_source": spreadsheet_source,
                    "accessible": access_result["accessible"],
                    "file_type": access_result.get("file_type"),
                    "error_type": access_result.get("error_type"),
                    "output_format": output_format,
                    "detailed": detailed
                }
            )
            
        except Exception as e:
            return UtilityResult(
                success=False,
                message=f"Failed to check spreadsheet access: {str(e)}",
                error=str(e)
            )
    
    def execute_batch(self, **kwargs) -> UtilityResult:
        """Execute batch spreadsheet access check."""
        metadata_sheet_url = kwargs["spreadsheet_source"]
        url_columns = kwargs.get("url_columns", "url")
        output_format = kwargs.get("output_format", "table")
        detailed = kwargs.get("detailed", False)
        metadata_sheet_name = kwargs.get("metadata_sheet_name", "access_check_metadata")
        auth_credentials = kwargs.get("auth_credentials", {})
        
        try:
            # Parse URL columns
            if isinstance(url_columns, str):
                url_columns = [col.strip() for col in url_columns.split(",")]
            
            # Get metadata sheet data
            metadata_result = check_spreadsheet_access(
                metadata_sheet_url, auth_credentials
            )
            
            if not metadata_result["accessible"]:
                return UtilityResult(
                    success=False,
                    message=f"Metadata sheet is not accessible: {metadata_result['error']}",
                    error=metadata_result["error"]
                )
            
            # Extract URLs from metadata sheet by reading actual data
            urls_to_check = []
            
            for col in url_columns:
                try:
                    # Read data from the metadata sheet to get URLs
                    from urarovite.utils.generic_spreadsheet import get_spreadsheet_data
                    
                    # Get all data from the sheet to find the column
                    sheet_data = get_spreadsheet_data(
                        metadata_sheet_url, 
                        "A1:Z1000",  # Large range to capture all data
                        auth_credentials
                    )
                    
                    if not sheet_data["success"]:
                        print(f"⚠️ Warning: Failed to read data from column {col}: {sheet_data.get('error', 'Unknown error')}")
                        continue
                    
                    values = sheet_data["values"]
                    if not values or len(values) < 2:
                        print(f"⚠️ Warning: No data found in sheet for column {col}")
                        continue
                    
                    # Find the column index
                    headers = values[0]
                    col_index = None
                    for i, header in enumerate(headers):
                        if header and str(header).strip().lower() == col.strip().lower():
                            col_index = i
                            break
                    
                    if col_index is None:
                        print(f"⚠️ Warning: Column '{col}' not found in headers: {headers}")
                        continue
                    
                    # Extract URLs from the column (skip header row)
                    for row_idx, row in enumerate(values[1:], 1):
                        if col_index < len(row) and row[col_index]:
                            url = str(row[col_index]).strip()
                            if url and url != "":
                                urls_to_check.append({
                                    "url": url,
                                    "row": row_idx,
                                    "column": col
                                })
                    
                    print(f"📊 Found {len([u for u in urls_to_check if u['column'] == col])} URLs in column '{col}'")
                    
                except Exception as e:
                    print(f"⚠️ Warning: Error reading column {col}: {str(e)}")
                    continue
            
            if not urls_to_check:
                return UtilityResult(
                    success=False,
                    message="No URLs found in specified columns",
                    error="No URLs found"
                )
            
            # Check access for each URL
            results = []
            successful = 0
            failed = 0
            
            print(f"🔍 Checking access to {len(urls_to_check)} URLs...")
            
            for url_info in urls_to_check:
                try:
                    url = url_info["url"]
                    row = url_info["row"]
                    column = url_info["column"]
                    
                    print(f"  📋 Row {row}: Checking {url[:50]}{'...' if len(url) > 50 else ''}")
                    
                    access_result = check_spreadsheet_access(
                        url, auth_credentials
                    )
                    
                    results.append({
                        "url": url,
                        "row": row,
                        "column": column,
                        "accessible": access_result["accessible"],
                        "file_type": access_result.get("file_type"),
                        "error_type": access_result.get("error_type"),
                        "error": access_result.get("error"),
                        "tabs_count": len(access_result.get("tabs", []))
                    })
                    
                    if access_result["accessible"]:
                        successful += 1
                        print(f"    ✅ Accessible - {len(access_result.get('tabs', []))} tabs")
                    else:
                        failed += 1
                        print(f"    ❌ Not accessible - {access_result.get('error_type', 'unknown')}")
                        
                except Exception as e:
                    results.append({
                        "url": url_info.get("url", "unknown"),
                        "row": url_info.get("row", 0),
                        "column": url_info.get("column", "unknown"),
                        "accessible": False,
                        "file_type": "unknown",
                        "error_type": "check_failed",
                        "error": str(e),
                        "tabs_count": 0
                    })
                    failed += 1
                    print(f"    💥 Error checking access: {str(e)}")
            
            message = f"Batch access check completed: {successful} accessible, {failed} failed"
            
            return UtilityResult(
                success=successful > 0,
                message=message,
                data={"results": results},
                metadata={
                    "total_processed": len(results),
                    "successful": successful,
                    "failed": failed,
                    "output_format": output_format,
                    "detailed": detailed
                }
            )
            
        except Exception as e:
            return UtilityResult(
                success=False,
                message="Batch access check failed",
                error=str(e)
            )
    



class UtilityRegistry:
    """Registry for all available utilities."""
    
    def __init__(self):
        self.utilities = {}
        
        # Register all utilities
        self.register("convert", ConversionUtility(
            "convert",
            "Convert between Google Sheets and Excel formats"
        ))
        
        self.register("sheets-to-excel-drive", SheetsToExcelDriveUtility(
            "sheets-to-excel-drive",
            "Convert Google Sheets to Excel and upload to Google Drive"
        ))
        
        self.register("excel-to-sheets-drive", ExcelToSheetsDriveUtility(
            "excel-to-sheets-drive",
            "Convert Excel to Google Sheets and upload to Google Drive"
        ))
        
        self.register("batch-sheets-to-excel-drive", BatchSheetsToExcelDriveUtility(
            "batch-sheets-to-excel-drive",
            "Batch convert multiple Google Sheets to Excel and upload to Google Drive"
        ))
        
        self.register("batch-excel-to-sheets-drive", BatchExcelToSheetsDriveUtility(
            "batch-excel-to-sheets-drive",
            "Batch convert multiple Excel files to Google Sheets and upload to Google Drive"
        ))
        
        self.register("folder-batch", FolderBatchConversionUtility(
            "folder-batch",
            "Convert all Excel files in a folder to Google Sheets"
        ))
        
        self.register("process-forte", ForteProcessingUtility(
            "process-forte",
            "Process Forte CSV files"
        ))
        
        self.register("sanitize-tab-names", SanitizeTabNamesUtility(
            "sanitize-tab-names",
            "Sanitize tab names to be alphanumeric with spaces only"
        ))
        
        self.register("batch-sanitize-tab-names", BatchSanitizeTabNamesUtility(
            "batch-sanitize-tab-names",
            "Batch sanitize tab names in multiple spreadsheets"
        ))
        
        self.register("validate-a1-ranges", ValidateA1RangesUtility(
            "validate-a1-ranges",
            "Validate and fix A1 notation ranges with proper tab name formatting"
        ))
        
        self.register("rename-tab", RenameTabUtility(
            "rename-tab",
            "Rename a tab and update all associated A1 references"
        ))
        
        self.register("batch-rename-tabs-from-sheet", BatchRenameTabsFromSheetUtility(
            "batch-rename-tabs-from-sheet",
            "Batch rename tabs based on a metadata sheet"
        ))
        
        self.register("batch-rename-tabs", BatchRenameTabsUtility(
            "batch-rename-tabs",
            "Batch rename tabs in multiple spreadsheets"
        ))
        
        self.register("batch-validate-a1-ranges", BatchValidateA1RangesUtility(
            "batch-validate-a1-ranges",
            "Batch validate and fix A1 notation ranges across multiple spreadsheets"
        ))
        
        self.register("validate", ValidationUtility(
            "validate",
            "Run validations on spreadsheets"
        ))
        
        self.register("check-access", SpreadsheetAccessUtility(
            "check-access",
            "Check if spreadsheets are accessible and get metadata"
        ))
    
    def register(self, name: str, utility: SingleBatchUtility):
        """Register a new utility."""
        self.utilities[name] = utility
    
    def get_utility(self, name: str) -> Optional[SingleBatchUtility]:
        """Get a utility by name."""
        return self.utilities.get(name)
    
    def list_utilities(self) -> List[str]:
        """List all available utility names."""
        return list(self.utilities.keys())
    
    def get_utility_help(self, name: str) -> Optional[str]:
        """Get help text for a specific utility."""
        utility = self.get_utility(name)
        if utility:
            parser = utility.get_argument_parser()
            return parser.format_help()
        return None


def main():
    """Main entry point for the run_util command."""
    if len(sys.argv) < 2:
        print("Usage: urarovite run_util <utility> [utility_args...]")
        print("\nAvailable utilities:")
        registry = UtilityRegistry()
        for util_name in registry.list_utilities():
            util = registry.get_utility(util_name)
            print(f"  {util_name}: {util.description}")
        sys.exit(1)
    
    utility_name = sys.argv[1]
    utility_args = sys.argv[2:]
    
    registry = UtilityRegistry()
    utility = registry.get_utility(utility_name)
    
    if not utility:
        print(f"Unknown utility: {utility_name}")
        print("\nAvailable utilities:")
        for util_name in registry.list_utilities():
            util = registry.get_utility(util_name)
            print(f"  {util_name}: {util.description}")
        sys.exit(1)
    
    # Run the utility with the provided arguments
    run_utility_cli(utility, utility_args)


if __name__ == "__main__":
    main()
