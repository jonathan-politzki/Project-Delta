from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from app.services.scraper import scrape_url
from app.services.text_processor import process_text
from app.services.llm_service import generate_insights
from app.services.embedding_service import generate_embedding
from app.services.analysis_service import generate_analysis
from app.core.vector_db import store_embedding

router = APIRouter()

class AnalysisRequest(BaseModel):
    url: HttpUrl

class AnalysisResponse(BaseModel):
    insights: str
    writing_style: str
    key_themes: list[str]

@router.post("/", response_model=AnalysisResponse)
async def analyze_url(request: AnalysisRequest):
    try:
        # Scrape content
        content = await scrape_url(request.url)
        
        # Process text
        processed_text = process_text(content)
        
        # Generate insights using LLM
        insights = await generate_insights(processed_text)
        
        # Generate and store embedding
        embedding = generate_embedding(processed_text)
        await store_embedding(str(request.url), embedding)
        
        # Generate final analysis
        analysis = generate_analysis(insights, processed_text)
        
        return AnalysisResponse(
            insights=analysis['insights'],
            writing_style=analysis['writing_style'],
            key_themes=analysis['key_themes']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))