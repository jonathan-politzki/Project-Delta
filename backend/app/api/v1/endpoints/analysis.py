# backend/app/api/v1/endpoints/analysis.py

from fastapi import APIRouter, HTTPException
from app.schemas.analysis_schemas import AnalysisResponse, AnalysisRequest
from app.services.text_processor import process_text
from app.services.llm_service import generate_insights
from app.services.embedding_service import generate_embedding
from app.services.analysis_service import generate_analysis
from app.utils.scraper import scrape_url, scraper_output_to_df
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
        platform = 'medium' if 'medium.com' in url else 'substack'
        username = url.split('@')[-1] if platform == 'medium' else url.split('//')[1].split('.')[0]
        scraped_data = await scrape_url(username, platform)
        df = scraper_output_to_df(scraped_data)
        
        logger.info(f"Scraped {len(df)} posts")
        
        # Process each article/post
        results = []
        for _, row in df.iterrows():
            processed_text = process_text(row['content'])
            insights = await generate_insights(processed_text)
            embedding = generate_embedding(processed_text)
            analysis = await generate_analysis(processed_text, embedding)
            results.append(analysis)
        
        logger.info(f"Analyzed {len(results)} posts")
        
        # Combine results
        combined_analysis = {
            "insights": "\n".join([r['insights'] for r in results]),
            "writing_style": pd.Series([r['writing_style'] for r in results]).mode().iloc[0],
            "key_themes": list(set([theme for r in results for theme in r['key_themes']])),
            "readability_score": sum([r['readability_score'] for r in results]) / len(results),
            "sentiment": pd.Series([r['sentiment'] for r in results]).mode().iloc[0],
            "post_count": len(results)
        }
        
        logger.info("Analysis completed successfully")
        return AnalysisResponse(**combined_analysis)

    except OpenAIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable due to API limitations")
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")