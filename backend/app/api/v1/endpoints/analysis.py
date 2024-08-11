import uuid
from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.schemas.analysis_schemas import AnalysisRequest, AnalysisResponse
from app.services.text_processor import process_text
from app.services.llm_service import generate_insights
from app.services.embedding_service import generate_embedding
from app.services.analysis_service import generate_analysis
from app.utils.scraper import scrape_url, scraper_output_to_df
import pandas as pd
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory storage for analysis results (replace with a database in production)
analysis_results = {}

@router.post("/", response_model=dict)
async def analyze_url(request: AnalysisRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    background_tasks.add_task(analyze_url_background, request.url, task_id)
    return {"task_id": task_id, "status": "processing"}

async def analyze_url_background(url: str, task_id: str):
    try:
        logger.info(f"Analyzing URL: {url}")
        scraped_data = await scrape_url(url)
        df = scraper_output_to_df(scraped_data)
        
        logger.info(f"Scraped {len(df)} posts")
        
        if df.empty:
            raise ValueError(f"No posts were scraped from the URL: {url}. Please check if the URL is correct and accessible.")

        # Process each article/post
        results = []
        for _, row in df.iterrows():
            try:
                processed_text = process_text(row['content'])
                insights = await generate_insights(processed_text)
                embedding = await generate_embedding(processed_text)
                analysis = await generate_analysis(processed_text, embedding)
                results.append(analysis)
            except Exception as e:
                logger.error(f"Error processing post: {str(e)}")
                # Continue with the next post instead of breaking the loop

        if not results:
            raise ValueError("No posts were successfully analyzed. Please try again later or contact support if the issue persists.")

        # Combine results
        combined_analysis = {
            "insights": "\n".join([r['insights'] for r in results if 'insights' in r]),
            "writing_style": pd.Series([r['writing_style'] for r in results if 'writing_style' in r]).mode().iloc[0] if results else "Unknown",
            "key_themes": list(set([theme for r in results if 'key_themes' in r for theme in r['key_themes']])),
            "readability_score": sum([r['readability_score'] for r in results if 'readability_score' in r]) / len(results) if results else 0,
            "sentiment": pd.Series([r['sentiment'] for r in results if 'sentiment' in r]).mode().iloc[0] if results else "Unknown",
            "post_count": len(results)
        }
        
        logger.info("Analysis completed successfully")
        analysis_results[task_id] = {"status": "completed", "result": combined_analysis}
    except Exception as e:
        logger.error(f"Error in analyze_url_background: {str(e)}")
        analysis_results[task_id] = {"status": "error", "message": str(e)}

@router.get("/status/{task_id}")
async def get_analysis_status(task_id: str):
    if task_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Task not found")
    return analysis_results[task_id]