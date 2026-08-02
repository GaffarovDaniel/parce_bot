import logging
import os

import gspread
from google.auth import default

logger = logging.getLogger(__name__)

SPREADSHEET_ID = "1xWqzhmDh3694QgQj50OU1e9MXTO0fdw1"
SHEET_NAME = "Поставщики"


def get_google_sheet():
    credentials, _ = default()
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    return spreadsheet.worksheet(SHEET_NAME)


def append_unique_suppliers(rows: list[list[str]]) -> int:
    if not rows:
        logger.info("No rows to append to Google Sheet")
        return 0

    try:
        worksheet = get_google_sheet()
    except Exception as exc:
        logger.exception("Failed to authorize Google Sheets: %s", exc)
        return 0

    existing_links = set()
    try:
        values = worksheet.col_values(4)
        existing_links = {value.strip() for value in values[1:] if value.strip()}
        logger.info("Loaded %d existing contacts from Google Sheet", len(existing_links))
    except Exception as exc:
        logger.warning("Could not fetch existing sheet links: %s", exc)

    unique_rows = []
    for row in rows:
        contact_link = row[3]
        if contact_link in existing_links:
            continue
        unique_rows.append(row)

    if not unique_rows:
        logger.info("No unique rows to append after de-duplication")
        return 0

    try:
        worksheet.append_rows(unique_rows, value_input_option="USER_ENTERED")
        logger.info("Appended %d rows to Google Sheet", len(unique_rows))
    except Exception as exc:
        logger.exception("Failed to append rows to Google Sheet: %s", exc)
        return 0

    return len(unique_rows)
