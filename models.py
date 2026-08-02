from datetime import datetime

from pydantic import BaseModel, Field


class ScrapeRequest(BaseModel):
    keyword: str = Field(..., min_length=1)
    pages: int = Field(default=1, ge=1, le=10)


class ScrapeResponse(BaseModel):
    status: str
    keyword: str
    job_id: str


class JobStatusResponse(BaseModel):
    job_id: str
    keyword: str
    status: str
    started_at: datetime
    finished_at: datetime | None = None
    last_message: str = ""
    new_count: int | None = None
    duplicates_count: int | None = None
    max_score: int | None = None
    error: str | None = None
    events: list[str] = []

    @classmethod
    def from_job(cls, job: "JobStatus") -> "JobStatusResponse":
        return cls(
            job_id=job.job_id,
            keyword=job.keyword,
            status=job.status,
            started_at=job.started_at,
            finished_at=job.finished_at,
            last_message=job.last_message,
            new_count=job.new_count,
            duplicates_count=job.duplicates_count,
            max_score=job.max_score,
            error=job.error,
            events=job.events,
        )
