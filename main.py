import logging
import uuid

from dotenv import load_dotenv
load_dotenv()

from fastapi import BackgroundTasks, FastAPI, HTTPException

from models import JobStatusResponse, ScrapeRequest, ScrapeResponse
from services.pipeline import run_scrape_pipeline
from services.status_tracker import tracker

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
    job_id = str(uuid.uuid4())
    logger.info("Received scrape request for keyword=%s pages=%s job_id=%s", payload.keyword, payload.pages, job_id)
    tracker.create_job(job_id=job_id, keyword=payload.keyword)
    background_tasks.add_task(run_scrape_pipeline, job_id, payload.keyword, payload.pages)
    return {"status": "processing started", "keyword": payload.keyword, "job_id": job_id}


@app.get("/api/v1/status/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str) -> JobStatusResponse:
    job = tracker.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse.from_job(job)


@app.get("/api/v1/status", response_model=list[JobStatusResponse])
def list_job_statuses() -> list[JobStatusResponse]:
    return [JobStatusResponse.from_job(job) for job in tracker.list_jobs()]
