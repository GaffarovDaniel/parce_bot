import logging

from services.ai_helper import categorize_products_with_gemini
from services.scraper import scrape_made_in_china
from services.scoring import calculate_supplier_score
from services.sheets_helper import append_unique_suppliers
from services.db_clickhouse import insert_suppliers
from services.status_tracker import tracker
from services.telegram_helper import send_telegram_report

logger = logging.getLogger(__name__)


def run_scrape_pipeline(job_id: str, keyword: str, pages: int) -> None:
    logger.info("Starting pipeline for job_id=%s keyword=%s pages=%s", job_id, keyword, pages)
    tracker.update_job(job_id, status="running", last_message="Scraping started")
    try:
        suppliers = scrape_made_in_china(keyword, pages)
        logger.info("Scraped %d supplier cards for keyword=%s", len(suppliers), keyword)
        tracker.update_job(job_id, last_message=f"Scraped {len(suppliers)} supplier cards")

        rows_to_append = []
        scores = []

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

        # Primary storage: ClickHouse
        try:
            db_new = insert_suppliers(rows_to_append)
            logger.info("Inserted %d rows into ClickHouse", db_new)
        except Exception as exc:
            logger.exception("ClickHouse insert failed for job_id=%s: %s", job_id, exc)
            tracker.fail_job(job_id, f"ClickHouse error: {exc}")
            send_telegram_report(keyword, 0, 0, 0, error=str(exc))
            return

        # Secondary / optional: Google Sheets sync (best-effort)
        try:
            new_count = append_unique_suppliers(rows_to_append)
        except Exception as exc:
            logger.exception("Google Sheets append failed for job_id=%s: %s", job_id, exc)
            # do not fail the job, data is persisted in ClickHouse
            tracker.update_job(job_id, last_message=f"Google Sheets error: {exc}")
            send_telegram_report(keyword, 0, 0, 0, error=str(exc))
            # continue — we already have data in ClickHouse
            new_count = 0

        duplicates_count = len(rows_to_append) - new_count
        max_score = max(scores) if scores else 0

        if rows_to_append and new_count == 0:
            if duplicates_count == len(rows_to_append):
                tracker.update_job(job_id, last_message="No new rows appended: all scraped suppliers already exist")
            else:
                tracker.update_job(
                    job_id,
                    last_message="No rows appended to Google Sheets; verify sheet name, service account access, and sheet tab name",
                )

        logger.info(
            "Append results: new_count=%d duplicates=%d max_score=%d",
            new_count,
            duplicates_count,
            max_score,
        )
        tracker.update_job(
            job_id,
            last_message="Sheet append completed",
            new_count=new_count,
            duplicates_count=duplicates_count,
            max_score=max_score,
        )

        send_telegram_report(keyword, new_count, duplicates_count, max_score)
        tracker.complete_job(job_id, new_count, duplicates_count, max_score)
        logger.info("Pipeline completed for job_id=%s keyword=%s", job_id, keyword)
    except Exception as exc:
        logger.exception("Pipeline failed for job_id=%s keyword=%s: %s", job_id, keyword, exc)
        tracker.fail_job(job_id, str(exc))
