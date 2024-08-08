# backend/app/schemas/analysis.py

from pydantic import BaseModel, HttpUrl, Field

class AnalysisRequest(BaseModel):
    url: HttpUrl = Field(..., description="URL of the article to analyze")

class AnalysisResponse(BaseModel):
    insights: str = Field(..., description="General insights about the writing")
    writing_style: str = Field(..., description="Analysis of the writing style")
    key_themes: list[str] = Field(..., description="List of key themes in the writing")
    readability_score: float = Field(..., description="Readability score of the text")
    sentiment: str = Field(..., description="Overall sentiment of the text")
