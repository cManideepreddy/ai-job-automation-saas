from pydantic import BaseModel
from typing import List, Optional


class ATSRequest(BaseModel):
    resume_text: str
    job_description: str


class ATSResponse(BaseModel):
    ats_score: int
    matched_keywords: List[str]
    missing_keywords: List[str]
    suggestions: List[str]
    summary: str