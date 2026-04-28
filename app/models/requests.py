from pydantic import BaseModel, Field
from typing import List, Optional

class ExplainRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=2000, example="What is photosynthesis?")
    student_level: str = Field("intermediate", pattern="^(beginner|intermediate|advanced)$", example="intermediate")
    teaching_style: Optional[str] = Field(None, example="supportive")

class SyllabusRequest(BaseModel):
    syllabus_text: str = Field(..., min_length=10, max_length=10000)
    course_title: str = Field(..., min_length=3, max_length=200)

class LectureRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=200)
    level: str = Field(..., example="beginner")

class SlidesRequest(BaseModel):
    lecture_id: str = Field(...)
    format: Optional[str] = Field(None, example="pdf")
