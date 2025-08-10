"""
Google Sheets logger: append DataFrame sections to tabs.
Uses gspread with ServiceAccountCredentials.
"""

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

from config import settings
from utils.logger import logger

SCOPE = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]


def _get_client(creds_file: str):
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, SCOPE)
    return gspread.authorize(creds)


def append_to_single_sheet(df: pd.DataFrame, sheet_tab: str,
                           creds_file: str = settings.GS_CREDS_FILE):
    """
    Appends df to a tab in the configured Google Sheet.
    Expects df to include a 'Type' column indicating section type.
    """
    try:
        client = _get_client(creds_file)
        sheet = client.open(settings.SHEET_NAME)
        try:
            worksheet = sheet.worksheet(sheet_tab)
        except gspread.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title=sheet_tab, rows="1000",
                                            cols="20")

        existing = worksheet.get_all_values()
        next_row = len(existing) + 2
        section = df['Type'].iloc[0] if 'Type' in df.columns else "Unknown"
        worksheet.update(f"A{next_row}", [[f"Section: {section}"]])
        rows = [df.columns.tolist()] + df.values.tolist()
        worksheet.update(f"A{next_row + 1}", rows)
        logger.info("Appended %s to Google Sheet tab %s", section, sheet_tab)
    except Exception:
        logger.exception("Failed to append to Google Sheet %s tab %s",
                         settings.SHEET_NAME, sheet_tab)
        raise
