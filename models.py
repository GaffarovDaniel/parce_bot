from pydantic import BaseModel, Field


class ScrapeRequest(BaseModel):
    keyword: str = Field(..., min_length=1)
    pages: int = Field(default=1, ge=1, le=10)


class ScrapeResponse(BaseModel):
    status: str
    keyword: str
