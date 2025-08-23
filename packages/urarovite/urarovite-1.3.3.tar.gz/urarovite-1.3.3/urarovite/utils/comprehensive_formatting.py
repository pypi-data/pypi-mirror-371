"""Comprehensive formatting preservation and enhancement utilities.

This module provides advanced formatting preservation by leveraging all existing
formatting utilities and adding new capabilities for maximum quality conversions.
"""

import logging
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
# dataclasses import removed - was unused

logger = logging.getLogger(__name__)

# Import existing formatting utilities
try:
    from urarovite.utils.format_preservation import (
        FormatExtractor,
        FormatApplier,
    )
    from urarovite.utils.enhanced_conversion import convert_with_full_formatting
    from urarovite.utils.formula_aware_conversion import convert_with_formulas
    from urarovite.utils.generic_spreadsheet import convert_excel_to_google_sheets

    FORMATTING_UTILITIES_AVAILABLE = True
except ImportError:
    FORMATTING_UTILITIES_AVAILABLE = False


# Class removed - was unused


class ComprehensiveFormatPreserver:
    """Comprehensive formatting preservation with fallback strategies."""

    def __init__(self, config: Optional[Any] = None):
        """Initialize the comprehensive format preserver.

        Args:
            config: Configuration for formatting preservation behavior (unused)
        """
        self.config = config or None
        self.format_extractor = (
            FormatExtractor() if FORMATTING_UTILITIES_AVAILABLE else None
        )
        self.format_applier = (
            FormatApplier() if FORMATTING_UTILITIES_AVAILABLE else None
        )

        # Track formatting preservation statistics
        self.stats = {
            "total_cells": 0,
            "cells_with_formatting": 0,
            "formats_preserved": 0,
            "formats_translated": 0,
            "formats_failed": 0,
            "formulas_preserved": 0,
            "formulas_failed": 0,
            "enhancements_applied": 0,
            "fallbacks_used": 0,
        }

    def convert_with_native_drive_api(
        self, source: str, target_folder_id: str, auth_credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert Excel to Google Sheets using Google Drive API's native conversion.

        This method uses Google Drive API's built-in conversion which provides
        better formatting preservation than manual conversion.

        Args:
            source: Excel file URL or Google Drive file ID
            target_folder_id: Google Drive folder ID to upload converted file to
            auth_credentials: Authentication credentials

        Returns:
            Conversion result dictionary
        """
        try:
            from urarovite.auth.google_drive import (
                create_drive_service_from_encoded_creds,
            )
            from urarovite.utils.drive import extract_google_file_id

            # Get auth secret
            auth_secret = auth_credentials.get("auth_secret")
            if not auth_secret:
                return self._create_response(
                    False, error="no_auth", error_msg="No authentication provided"
                )

            # Create drive service
            drive_service = create_drive_service_from_encoded_creds(auth_secret)

            # Extract file ID from URL if it's a URL
            if source.startswith("http"):
                file_id = extract_google_file_id(source)
                if not file_id:
                    return self._create_response(
                        False,
                        error="invalid_url",
                        error_msg="Could not extract file ID from URL",
                    )
            else:
                file_id = source

            # Convert the Drive file to Google Sheets
            return self._convert_drive_excel_to_sheets(
                drive_service, file_id, target_folder_id
            )

        except Exception as e:
            return self._create_response(
                False, error="drive_api_error", error_msg=str(e)
            )

    def _convert_drive_excel_to_sheets(
        self, drive_service: Any, excel_file_id: str, target_folder_id: str
    ) -> Dict[str, Any]:
        """Convert Excel file from Drive to Google Sheets using native conversion."""
        try:
            # Get file info first
            file_info = (
                drive_service.files()
                .get(
                    fileId=excel_file_id,
                    fields="name, mimeType",
                    supportsAllDrives=True,
                )
                .execute()
            )

            # Verify it's an Excel file
            if not file_info["mimeType"].endswith("spreadsheetml.sheet"):
                return self._create_response(
                    False,
                    error="not_excel",
                    error_msg="Source file is not an Excel file",
                )

            base_name = file_info["name"].replace(".xlsx", "").replace(".xls", "")

            # Create Google Sheets file with conversion
            sheets_metadata = {
                "name": base_name,
                "parents": [target_folder_id],
                "mimeType": "application/vnd.google-apps.spreadsheet",
            }

            # Use the copy method which automatically converts Excel to Sheets
            converted_file = (
                drive_service.files()
                .copy(
                    fileId=excel_file_id,
                    body=sheets_metadata,
                    fields="id, name, webViewLink",
                    supportsAllDrives=True,
                )
                .execute()
            )

            logger.info(
                f"✅ Successfully converted Excel to Google Sheets: {converted_file['name']}"
            )

            return self._create_response(
                True,
                result={
                    "file_id": converted_file["id"],
                    "file_name": converted_file["name"],
                    "web_link": converted_file["webViewLink"],
                    "conversion_method": "google_drive_api_native",
                    "formatting_preservation": "maximum",
                    "formula_preservation": "high",
                    "message": "Native Google Drive API conversion successful - maximum quality achieved!",
                },
            )

        except Exception as e:
            return self._create_response(
                False, error="conversion_error", error_msg=str(e)
            )

    def _extract_folder_id_from_target(
        self, target: Union[str, Path], auth_credentials: Dict[str, Any]
    ) -> Optional[str]:
        """Extract folder ID from target Google Sheets URL or create a default folder."""
        try:
            if isinstance(target, str) and "docs.google.com/spreadsheets" in target:
                # Extract sheet ID and get its parent folder
                from urarovite.utils.sheets import extract_sheet_id

                sheet_id = extract_sheet_id(target)
                if sheet_id:
                    # Get the sheet's parent folder
                    from urarovite.auth.google_drive import (
                        create_drive_service_from_encoded_creds,
                    )

                    drive_service = create_drive_service_from_encoded_creds(
                        auth_credentials["auth_secret"]
                    )

                    file_info = (
                        drive_service.files()
                        .get(fileId=sheet_id, fields="parents", supportsAllDrives=True)
                        .execute()
                    )

                    if "parents" in file_info and file_info["parents"]:
                        return file_info["parents"][0]

            # If no folder found, create a default "Converted Files" folder
            if "auth_secret" in auth_credentials:
                from urarovite.auth.google_drive import (
                    create_drive_service_from_encoded_creds,
                )

                drive_service = create_drive_service_from_encoded_creds(
                    auth_credentials["auth_secret"]
                )

                # Check if default folder exists
                query = "name='Converted Files' and mimeType='application/vnd.google-apps.folder' and trashed=false"
                results = (
                    drive_service.files()
                    .list(q=query, fields="files(id, name)", supportsAllDrives=True)
                    .execute()
                )

                if results["files"]:
                    return results["files"][0]["id"]
                else:
                    # Create default folder
                    folder_metadata = {
                        "name": "Converted Files",
                        "mimeType": "application/vnd.google-apps.folder",
                    }

                    folder = (
                        drive_service.files()
                        .create(
                            body=folder_metadata, fields="id", supportsAllDrives=True
                        )
                        .execute()
                    )

                    return folder["id"]

            return None

        except Exception as e:
            logger.warning(f"⚠️ Could not determine target folder: {e}")
            return None

    def _create_response(self, success: bool, **kwargs) -> Dict[str, Any]:
        """Create a standardized response dictionary."""
        response = {"success": success}
        response.update(kwargs)
        return response

    def convert_with_maximum_quality(
        self,
        source: Union[str, Path],
        target: Union[str, Path],
        auth_credentials: Optional[Dict[str, Any]] = None,
        sheet_names: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Convert with maximum quality formatting preservation.

        This method tries multiple conversion strategies in order of preference:
        1. Enhanced conversion with full formatting
        2. Formula-aware conversion with formatting
        3. Standard conversion with formatting
        4. Basic conversion as fallback

        Args:
            source: Source spreadsheet path or URL
            target: Target spreadsheet path or URL
            auth_credentials: Authentication credentials
            sheet_names: Specific sheets to convert
            **kwargs: Additional conversion options

        Returns:
            Conversion result with detailed formatting statistics
        """
        if not FORMATTING_UTILITIES_AVAILABLE:
            logger.warning(
                "Formatting utilities not available - using basic conversion"
            )
            return self._basic_conversion_fallback(
                source, target, auth_credentials, sheet_names
            )

        # Strategy 1: Try native Google Drive API conversion first (best quality)
        if auth_credentials and "auth_secret" in auth_credentials:
            logger.info("🚀 Attempting native Google Drive API conversion...")
            try:
                # Use explicit folder ID if provided, otherwise extract from target URL
                target_folder_id = kwargs.get("target_folder_id")
                if not target_folder_id:
                    target_folder_id = self._extract_folder_id_from_target(
                        target, auth_credentials
                    )

                if target_folder_id:
                    # Use original source URL if available (for Drive API conversion)
                    # This is crucial for batch operations where source is a local temp file
                    original_source = kwargs.get("original_source_url", source)

                    result = self.convert_with_native_drive_api(
                        source=original_source,  # Use original URL for Drive API
                        target_folder_id=target_folder_id,
                        auth_credentials=auth_credentials,
                    )

                    if result["success"]:
                        logger.info("✅ Native Drive API conversion successful!")
                        self._update_stats_from_result(result)
                        return result  # Return the native conversion result directly
                    else:
                        logger.warning(
                            f"⚠️ Native Drive API conversion failed: {result.get('error_msg', 'Unknown error')}"
                        )
                else:
                    logger.info(
                        "ℹ️ No target folder ID available, skipping native conversion"
                    )

            except Exception as e:
                logger.warning(f"⚠️ Native Drive API conversion failed: {e}")

        # Strategy 2: Try enhanced conversion with full formatting
        try:
            logger.info("🎨 Attempting enhanced conversion with full formatting...")
            result = convert_with_full_formatting(
                source=source,
                target=target,
                auth_credentials=auth_credentials,
                sheet_names=sheet_names,
                preserve_formulas=self.config.preserve_formulas,
                preserve_visual_formatting=self.config.preserve_visual_formatting,
                source_file_type=kwargs.get("source_file_type"),
                target_file_type=kwargs.get("target_file_type"),
            )

            if result["success"]:
                self._update_stats_from_result(result)
                logger.info("✅ Enhanced conversion successful with full formatting")
                return result

        except Exception as e:
            logger.warning(f"Enhanced conversion failed: {e}")

        # Strategy 2: Try formula-aware conversion with formatting
        try:
            logger.info("📝 Attempting formula-aware conversion with formatting...")
            result = convert_with_formulas(
                source=source,
                target=target,
                auth_credentials=auth_credentials,
                sheet_names=sheet_names,
                translate_references=True,
                preserve_formatting=self.config.preserve_visual_formatting,
                source_file_type=kwargs.get("source_file_type"),
                target_file_type=kwargs.get("target_file_type"),
            )

            if result.get("success"):
                self._update_stats_from_result(result)
                logger.info("✅ Formula-aware conversion successful")
                return result

        except Exception as e:
            logger.warning(f"Formula-aware conversion failed: {e}")

        # Strategy 3: Try standard conversion with formatting
        try:
            logger.info("🔄 Attempting standard conversion with formatting...")
            if "excel" in str(source).lower() and "sheets" in str(target).lower():
                result = convert_excel_to_google_sheets(
                    excel_file_path=source,
                    google_sheets_url=target,
                    auth_credentials=auth_credentials,
                    sheet_names=sheet_names,
                    create_new_sheets=True,
                )

                if result.get("success"):
                    self._update_stats_from_result(result)
                    logger.info("✅ Standard conversion successful")
                    return result

        except Exception as e:
            logger.warning(f"Standard conversion failed: {e}")

        # Strategy 4: Basic fallback conversion
        logger.warning("⚠️ All enhanced conversion methods failed, using basic fallback")
        return self._basic_conversion_fallback(
            source, target, auth_credentials, sheet_names
        )

    def _basic_conversion_fallback(
        self,
        source: Union[str, Path],
        target: Union[str, Path],
        auth_credentials: Optional[Dict[str, Any]] = None,
        sheet_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Basic conversion fallback when all enhanced methods fail."""
        try:
            # Use the most basic conversion available
            from urarovite.utils.generic_spreadsheet import convert_spreadsheet_format

            result = convert_spreadsheet_format(
                source=source,
                target=target,
                auth_credentials=auth_credentials,
                sheet_names=sheet_names,
                preserve_formulas=False,
                preserve_visual_formatting=False,
            )

            self.stats["fallbacks_used"] += 1
            return result

        except Exception as e:
            logger.error(f"Basic conversion fallback also failed: {e}")
            return {
                "success": False,
                "error": f"All conversion methods failed: {str(e)}",
                "fallback_used": True,
            }

    def _update_stats_from_result(self, result: Dict[str, Any]) -> None:
        """Update internal statistics from conversion result."""
        if "formatting_stats" in result:
            stats = result["formatting_stats"]
            self.stats["cells_with_formatting"] += stats.get("cells_with_formatting", 0)
            self.stats["formats_preserved"] += stats.get("formats_preserved", 0)
            self.stats["formats_translated"] += stats.get("formats_translated", 0)
            self.stats["formats_failed"] += stats.get("formats_failed", 0)

        if "formula_stats" in result:
            stats = result["formula_stats"]
            self.stats["formulas_preserved"] += stats.get("preserved_formulas", 0)
            self.stats["formulas_failed"] += stats.get("failed_formulas", 0)

    def get_formatting_summary(self) -> Dict[str, Any]:
        """Get a summary of formatting preservation statistics."""
        total_formats = (
            self.stats["formats_preserved"]
            + self.stats["formats_translated"]
            + self.stats["formats_failed"]
        )
        format_success_rate = (
            (self.stats["formats_preserved"] + self.stats["formats_translated"])
            / total_formats
            if total_formats > 0
            else 0
        )

        total_formulas = (
            self.stats["formulas_preserved"] + self.stats["formulas_failed"]
        )
        formula_success_rate = (
            self.stats["formulas_preserved"] / total_formulas
            if total_formulas > 0
            else 0
        )

        return {
            "formatting_preservation": {
                "total_cells_with_formatting": self.stats["cells_with_formatting"],
                "formats_preserved": self.stats["formats_preserved"],
                "formats_translated": self.stats["formats_translated"],
                "formats_failed": self.stats["formats_failed"],
                "success_rate": format_success_rate,
            },
            "formula_preservation": {
                "total_formulas": total_formulas,
                "formulas_preserved": self.stats["formulas_preserved"],
                "formulas_failed": self.stats["formulas_failed"],
                "success_rate": formula_success_rate,
            },
            "conversion_quality": {
                "enhancements_applied": self.stats["enhancements_applied"],
                "fallbacks_used": self.stats["fallbacks_used"],
                "overall_quality": "high"
                if format_success_rate > 0.8
                else "medium"
                if format_success_rate > 0.5
                else "low",
            },
        }


# Functions removed - were unused or only used internally
