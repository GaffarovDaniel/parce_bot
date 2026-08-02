import logging
import os

import requests

logger = logging.getLogger(__name__)


def send_telegram_report(keyword: str, new_count: int, duplicates_count: int, max_score: int) -> None:
    bot_token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        logger.warning("Telegram credentials are not configured")
        return

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
