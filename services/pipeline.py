import logging

from services.ai_helper import categorize_products_with_gemini
from services.scraper import scrape_made_in_china
from services.scoring import calculate_supplier_score
from services.sheets_helper import append_unique_suppliers
from services.telegram_helper import send_telegram_report

logger = logging.getLogger(__name__)


def run_scrape_pipeline(keyword: str, pages: int) -> None:
    logger.info("Starting pipeline for keyword=%s pages=%s", keyword, pages)
    suppliers = scrape_made_in_china(keyword, pages)

    rows_to_append = []
    scores = []
    duplicates_count = 0

    for supplier in suppliers:
        company_name = supplier.get("company_name", "")
        products_text = supplier.get("products_text", "")
        profile_link = supplier.get("profile_link", "")

        score = calculate_supplier_score(company_name, products_text, keyword)
        scores.append(score)

        category = categorize_products_with_gemini(products_text)
        row = [
            category,
            keyword,
            company_name,
            profile_link,
            "Уточняется",
            "",
            "",
            "Требует проверки",
            "Новый лид",
            f"[Score: {score}/100] Авто-парсинг. Продукты: {products_text}",
        ]
        rows_to_append.append(row)

    new_count = append_unique_suppliers(rows_to_append)
    duplicates_count = len(rows_to_append) - new_count
    max_score = max(scores) if scores else 0

    send_telegram_report(keyword, new_count, duplicates_count, max_score)
    logger.info("Pipeline completed for keyword=%s", keyword)
