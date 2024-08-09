# backend/app/api/v1/endpoints/analysis.py

from fastapi import APIRouter, HTTPException
from app.schemas.analysis_schemas import AnalysisResponse, AnalysisRequest
from app.services.text_processor import process_text
from app.services.llm_service import generate_insights
from app.services.embedding_service import generate_embedding
from app.services.analysis_service import generate_analysis
from app.utils.scraper import scrape_url, scraper_output_to_df, scrape_medium, scrape_substack
import pandas as pd
import logging
from openai import OpenAIError

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=AnalysisResponse)
async def analyze_url(request: AnalysisRequest):
    try:
        logger.info(f"Analyzing URL: {request.url}")
        url = request.url
        
        if 'medium.com' in url:
            scraped_data = await scrape_medium(url)
        elif 'substack.com' in url:
            scraped_data = await scrape_substack(url)
        else:
            raise ValueError(f"Unsupported URL: {url}")
        
        df = scraper_output_to_df(scraped_data)
        
        logger.info(f"Scraped {len(df)} posts")
        
        if df.empty:
            raise ValueError(f"No posts were scraped from the URL: {url}")

        # Process each article/post
        results = []
        for _, row in df.iterrows():
            processed_text = process_text(row['content'])
            insights = await generate_insights(processed_text)
            embedding = await generate_embedding(processed_text)  # Now awaiting the async function
            analysis = await generate_analysis(processed_text, embedding)
            results.append(analysis)
        
        logger.info(f"Analyzed {len(results)} posts")
        
        if not results:
            raise ValueError("No posts were successfully analyzed")

        # Combine results
        combined_analysis = {
            "insights": "\n".join([r['insights'] for r in results]),
            "writing_style": pd.Series([r['writing_style'] for r in results]).mode().iloc[0] if results else "Unknown",
            "key_themes": list(set([theme for r in results for theme in r['key_themes']])),
            "readability_score": sum([r['readability_score'] for r in results]) / len(results) if results else 0,
            "sentiment": pd.Series([r['sentiment'] for r in results]).mode().iloc[0] if results else "Unknown",
            "post_count": len(results)
        }
        
        logger.info("Analysis completed successfully")
        return AnalysisResponse(**combined_analysis)

    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")