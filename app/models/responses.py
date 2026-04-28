from pydantic import BaseModel, Field
from typing import List, Optional

class ExplainResponse(BaseModel):
    answer: str
    cached: bool
    latency_ms: int
    sources: Optional[List[str]] = None

class SyllabusResponse(BaseModel):
    job_id: str
    status: str
    detail: Optional[str] = None

class LectureResponse(BaseModel):
    lecture_id: str
    content: str
    sources: Optional[List[str]] = None

class SlidesResponse(BaseModel):
    slides_url: str
    format: str
    generated_at: str
