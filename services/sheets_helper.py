import logging
import os
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials as ServiceAccountCredentials

logger = logging.getLogger(__name__)


def get_spreadsheet_id() -> str:
    return os.getenv("SPREADSHEET_ID", "1Bn_hEvkF4I0jhBsVEKIwBiI8E8bEK5OO")


def get_sheet_name() -> str:
    return os.getenv("SHEET_NAME", "Поставщики")


def ensure_google_credentials() -> None:
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        return

    credentials_path = Path(__file__).resolve().parents[1] / "credentials.json"
    if credentials_path.exists():
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path)
        logger.info("Using local Google credentials file %s", credentials_path)


def get_google_sheet():
    ensure_google_credentials()
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        raise RuntimeError("Google credentials not configured. Set GOOGLE_APPLICATION_CREDENTIALS to service account JSON path.")

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = ServiceAccountCredentials.from_service_account_file(creds_path, scopes=scopes)
    client = gspread.authorize(creds)

    spreadsheet_id = get_spreadsheet_id()
    sheet_name = get_sheet_name()

    spreadsheet = client.open_by_key(spreadsheet_id)
    return spreadsheet.worksheet(sheet_name)


def append_unique_suppliers(rows: list[list[str]]) -> int:
    if not rows:
        logger.info("No rows to append to Google Sheet")
        return 0

    worksheet = get_google_sheet()

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
        raise RuntimeError("Failed to append rows to Google Sheets") from exc

    return len(unique_rows)
