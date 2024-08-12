# backend/app/api/v1/endpoints/analysis.py

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
from urllib.parse import urlparse

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory storage for analysis results (replace with a database in production)
analysis_results = {}

@router.post("/", response_model=dict)
async def analyze_url(request: AnalysisRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    analysis_results[task_id] = {"status": "processing"}  # Initialize the task
    
    try:
        # Validate and normalize the URL
        parsed_url = urlparse(str(request.url))
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL")
        normalized_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        if parsed_url.query:
            normalized_url += f"?{parsed_url.query}"
        
        background_tasks.add_task(analyze_url_background, normalized_url, task_id)
        return {"task_id": task_id, "status": "processing"}
    except Exception as e:
        logger.error(f"Error processing URL for task {task_id}: {str(e)}")
        analysis_results[task_id] = {"status": "error", "message": str(e)}
        return {"task_id": task_id, "status": "error", "message": "Invalid URL provided"}

async def analyze_url_background(url: str, task_id: str):
    try:
        logger.info(f"Starting background analysis for task {task_id}, URL: {url}")
        analysis_results[task_id] = {"status": "processing"}
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
        
        logger.info(f"Analysis completed for task {task_id}")
        analysis_results[task_id] = {"status": "completed", "result": combined_analysis}
    except Exception as e:
        logger.error(f"Error in analyze_url_background for task {task_id}: {str(e)}")
        analysis_results[task_id] = {"status": "error", "message": str(e)}

    logger.info(f"Final status for task {task_id}: {analysis_results[task_id]['status']}")

@router.post("/", response_model=dict)
async def analyze_url(request: AnalysisRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    analysis_results[task_id] = {"status": "processing"}  # Initialize the task
    background_tasks.add_task(analyze_url_background, request.url, task_id)
    return {"task_id": task_id, "status": "processing"}

@router.get("/status/{task_id}")
async def get_analysis_status(task_id: str):
    logger.info(f"Checking status for task: {task_id}")
    logger.info(f"Current analysis_results: {analysis_results}")
    if task_id not in analysis_results:
        logger.warning(f"Task not found: {task_id}")
        return {"status": "not_found"}  # Return a status instead of raising an exception
    logger.info(f"Returning status for task {task_id}: {analysis_results[task_id]}")
    return analysis_results[task_id]