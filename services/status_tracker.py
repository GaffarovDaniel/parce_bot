import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class JobStatus:
    job_id: str
    keyword: str
    status: str
    started_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: datetime | None = None
    last_message: str = ""
    new_count: int | None = None
    duplicates_count: int | None = None
    max_score: int | None = None
    error: str | None = None
    events: list[str] = field(default_factory=list)


class StatusTracker:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._jobs: dict[str, JobStatus] = {}

    def create_job(self, job_id: str, keyword: str) -> JobStatus:
        job = JobStatus(job_id=job_id, keyword=keyword, status="pending")
        job.events.append("Job created")
        with self._lock:
            self._jobs[job_id] = job
        return job

    def update_job(self, job_id: str, **kwargs: Any) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            for key, value in kwargs.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            if "last_message" in kwargs:
                job.events.append(kwargs["last_message"] or "")

    def complete_job(self, job_id: str, new_count: int, duplicates_count: int, max_score: int) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job.status = "completed"
            job.finished_at = datetime.utcnow()
            job.new_count = new_count
            job.duplicates_count = duplicates_count
            job.max_score = max_score
            job.last_message = "Pipeline completed"
            job.events.append(job.last_message)

    def fail_job(self, job_id: str, error: str) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job.status = "failed"
            job.finished_at = datetime.utcnow()
            job.error = error
            job.last_message = error
            job.events.append(error)

    def get_job(self, job_id: str) -> JobStatus | None:
        with self._lock:
            return self._jobs.get(job_id)

    def list_jobs(self) -> list[JobStatus]:
        with self._lock:
            return list(self._jobs.values())


tracker = StatusTracker()
