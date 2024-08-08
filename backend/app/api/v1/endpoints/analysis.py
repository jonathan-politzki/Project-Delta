# backend/app/api/v1/endpoints/analysis.py

from fastapi import APIRouter, HTTPException
from app.schemas.analysis_schemas import AnalysisResponse, AnalysisRequest
from app.services.text_processor import process_text
from app.services.llm_service import generate_insights
from app.services.embedding_service import generate_embedding
from app.services.analysis_service import generate_analysis
from app.core.error_handlers import handle_analysis_error
import pandas as pd
from app.utils.scraper import scrape_url, scraper_output_to_df
import logging
from app.schemas.analysis_schemas import AnalysisResponse, AnalysisRequest
from app.utils.scraper import scrape_url, scraper_output_to_df


router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=AnalysisResponse)
async def analyze_url(request: AnalysisRequest):
    try:
        logger.info(f"Analyzing URL: {request.url}")
        scraped_data = await scrape_url(request.url)
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
            "post_count": len(results),
            "similar_texts": [text for r in results for text in r.get('similar_texts', [])]
        }
        
        logger.info("Analysis completed successfully")
        return AnalysisResponse(**combined_analysis)
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        return handle_analysis_error(e)