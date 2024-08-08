# backend/app/schemas/analysis_schemas.py

from pydantic import BaseModel, HttpUrl, Field

class AnalysisRequest(BaseModel):
    url: HttpUrl = Field(..., description="URL of the article to analyze")

class AnalysisResponse(BaseModel):
    insights: str
    writing_style: str
    key_themes: list[str]
    readability_score: float
    sentiment: str
    post_count: int

