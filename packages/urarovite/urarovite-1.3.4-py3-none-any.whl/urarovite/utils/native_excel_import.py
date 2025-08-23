"""
Native Excel to Google Sheets Import Utility

This module provides utilities for directly importing Excel files to Google Sheets
using the Google Drive API's native conversion capabilities, without downloading
or copying content manually.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def import_excel_to_google_sheets_native(
    excel_file_id: str,
    target_folder_id: str,
    auth_secret: str,
    custom_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Import Excel file to Google Sheets using native Google Drive API conversion.

    This method uses the Drive API's copy() method with mimetype conversion to
    directly convert Excel files to Google Sheets format without downloading
    or manually copying content.

    Args:
        excel_file_id: Google Drive file ID of the Excel file
        target_folder_id: Google Drive folder ID where Google Sheets should be created
        auth_secret: Base64 encoded service account credentials
        custom_name: Optional custom name for the Google Sheets (defaults to Excel filename)

    Returns:
        Dict with keys: success, file_id, web_link, name, error
    """
    try:
        from urarovite.auth.google_drive import create_drive_service_from_encoded_creds

        # Create Drive service
        drive_service = create_drive_service_from_encoded_creds(auth_secret)

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
            return {
                "success": False,
                "error": "not_excel",
                "error_msg": f"Source file is not an Excel file. MimeType: {file_info['mimeType']}",
            }

        # Determine the name for the Google Sheets
        if custom_name:
            sheets_name = custom_name
        else:
            # Use original name but remove Excel extensions
            sheets_name = file_info["name"].replace(".xlsx", "").replace(".xls", "")

        # Create Google Sheets file with native conversion
        sheets_metadata = {
            "name": sheets_name,
            "parents": [target_folder_id],
            "mimeType": "application/vnd.google-apps.spreadsheet",  # This triggers the conversion
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
            f"✅ Successfully imported Excel to Google Sheets using native conversion: {converted_file['name']}"
        )

        return {
            "success": True,
            "file_id": converted_file["id"],
            "web_link": converted_file["webViewLink"],
            "name": converted_file["name"],
            "conversion_method": "google_drive_api_native",
        }

    except Exception as e:
        logger.error(f"Failed to import Excel file using native conversion: {str(e)}")
        return {
            "success": False,
            "error": "conversion_failed",
            "error_msg": str(e),
        }


def import_excel_to_google_sheets_from_url(
    excel_url: str,
    target_folder_id: str,
    auth_secret: str,
    custom_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Import Excel file to Google Sheets from URL using native Drive API conversion.

    Args:
        excel_url: Google Drive URL of the Excel file
        target_folder_id: Google Drive folder ID where Google Sheets should be created
        auth_secret: Base64 encoded service account credentials
        custom_name: Optional custom name for the Google Sheets

    Returns:
        Dict with keys: success, file_id, web_link, name, error
    """
    try:
        from urarovite.utils.drive import extract_google_file_id

        # Extract file ID from URL
        file_id = extract_google_file_id(excel_url)
        if not file_id:
            return {
                "success": False,
                "error": "invalid_url",
                "error_msg": "Could not extract file ID from URL",
            }

        # Use the file ID method
        return import_excel_to_google_sheets_native(
            excel_file_id=file_id,
            target_folder_id=target_folder_id,
            auth_secret=auth_secret,
            custom_name=custom_name,
        )

    except Exception as e:
        return {
            "success": False,
            "error": "url_processing_failed",
            "error_msg": str(e),
        }


def batch_import_excel_files_native(
    excel_file_ids: list[str],
    target_folder_id: str,
    auth_secret: str,
    custom_names: Optional[list[str]] = None,
) -> Dict[str, Any]:
    """
    Batch import multiple Excel files to Google Sheets using native conversion.

    Args:
        excel_file_ids: List of Google Drive file IDs for Excel files
        target_folder_id: Google Drive folder ID where Google Sheets should be created
        auth_secret: Base64 encoded service account credentials
        custom_names: Optional list of custom names (must match length of excel_file_ids)

    Returns:
        Dict with keys: success, results (list of conversion results), summary
    """
    if custom_names and len(custom_names) != len(excel_file_ids):
        return {
            "success": False,
            "error": "length_mismatch",
            "error_msg": "custom_names length must match excel_file_ids length",
        }

    results = []
    successful = 0
    failed = 0

    for i, file_id in enumerate(excel_file_ids):
        custom_name = custom_names[i] if custom_names else None

        result = import_excel_to_google_sheets_native(
            excel_file_id=file_id,
            target_folder_id=target_folder_id,
            auth_secret=auth_secret,
            custom_name=custom_name,
        )

        results.append(
            {
                "file_id": file_id,
                "result": result,
            }
        )

        if result["success"]:
            successful += 1
        else:
            failed += 1

    return {
        "success": successful > 0,
        "results": results,
        "summary": {
            "total": len(excel_file_ids),
            "successful": successful,
            "failed": failed,
        },
    }
