import logging

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI

from models import ScrapeRequest, ScrapeResponse
from services.pipeline import run_scrape_pipeline

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Made-in-China Supplier Scraper",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/scrape", status_code=202, response_model=ScrapeResponse)
def start_scrape(payload: ScrapeRequest, background_tasks: BackgroundTasks) -> ScrapeResponse:
    logger.info("Received scrape request for keyword=%s pages=%s", payload.keyword, payload.pages)
    background_tasks.add_task(run_scrape_pipeline, payload.keyword, payload.pages)
    return {"status": "processing started", "keyword": payload.keyword}
