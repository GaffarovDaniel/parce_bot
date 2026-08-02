import logging
import os

import requests
from services.db_clickhouse import fetch_suppliers_csv

logger = logging.getLogger(__name__)


def send_telegram_report(keyword: str, new_count: int, duplicates_count: int, max_score: int, error: str | None = None) -> None:
    bot_token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        logger.warning("Telegram credentials are not configured")
        return

    if error:
        message = (
            "⚠️ *Парсинг завершился с ошибкой!*\n"
            f"Ключевое слово: `{keyword}`\n"
            f"Ошибка: `{error}`\n"
        )
    else:
        message = (
            "✅ *Парсинг завершен!*\n"
            f"Ключевое слово: `{keyword}`\n"
            f"Найдено новых поставщиков: `{new_count}`\n"
            f"Дубликатов: `{duplicates_count}`\n"
            f"Лучший Score: `{max_score}`"
        )

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
            timeout=20,
        )
        response.raise_for_status()
        logger.info("Telegram notification sent, response=%s", response.text)
    except requests.RequestException as exc:
        if hasattr(exc, 'response') and exc.response is not None:
            logger.error(
                "Telegram response code=%s text=%s",
                exc.response.status_code,
                exc.response.text,
            )
        logger.exception("Telegram notification failed: %s", exc)


def send_suppliers_csv_via_telegram(chat_id: str | None = None, limit: int | None = None) -> bool:
    """
    Fetch suppliers CSV from ClickHouse and send it to Telegram chat as a file.
    Returns True if sent successfully.
    """
    bot_token = os.getenv("BOT_TOKEN")
    chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        logger.warning("Telegram credentials are not configured for CSV export")
        return False

    try:
        csv_bytes = fetch_suppliers_csv(limit=limit)
    except Exception as exc:
        logger.exception("Failed to fetch CSV from ClickHouse: %s", exc)
        return False

    files = {"document": ("suppliers.csv", csv_bytes, "text/csv")}
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendDocument",
            data={"chat_id": chat_id},
            files=files,
            timeout=60,
        )
        response.raise_for_status()
        logger.info("Telegram CSV sent, response=%s", response.text)
        return True
    except requests.RequestException as exc:
        if hasattr(exc, 'response') and exc.response is not None:
            logger.error(
                "Telegram sendDocument response code=%s text=%s",
                exc.response.status_code,
                exc.response.text,
            )
        logger.exception("Telegram sendDocument failed: %s", exc)
        return False
