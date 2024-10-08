# backend/app/api/v1/endpoints/analysis.py

import uuid
import json
from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.schemas.analysis_schemas import AnalysisRequest, AnalysisResponse
from app.services.text_processor import process_text
from app.services.llm_service import extract_concepts, combine_concepts
from app.services.embedding_service import generate_embedding
from app.services.analysis_service import generate_full_analysis
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
    analysis_results[task_id] = {"status": "processing", "progress": 0, "total_essays": 0}
    
    try:
        normalized_url = normalize_url(request.url)
        background_tasks.add_task(analyze_url_background, normalized_url, task_id)
        return {"task_id": task_id, "status": "processing"}
    except ValueError as e:
        logger.error(f"Error processing URL for task {task_id}: {str(e)}")
        return {"task_id": task_id, "status": "error", "message": str(e)}

def normalize_url(url: str) -> str:
    parsed_url = urlparse(str(url))
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError("Invalid URL provided")
    normalized_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    if parsed_url.query:
        normalized_url += f"?{parsed_url.query}"
    return normalized_url

async def analyze_url_background(url: str, task_id: str):
    try:
        logger.info(f"Starting background analysis for task {task_id}, URL: {url}")
        scraped_data = await scrape_url(url)
        logger.info(f"Scraped data: {json.dumps(scraped_data, indent=2)}")
        df = scraper_output_to_df(scraped_data)
        
        if df.empty:
            logger.warning(f"No posts were scraped from the URL: {url}")
            raise ValueError(f"No posts were scraped from the URL: {url}. Please check if the URL is correct and accessible.")

        logger.info(f"Number of posts scraped: {len(df)}")
        all_insights = await process_posts(df, task_id)
        logger.info(f"All insights: {json.dumps(all_insights, indent=2)}")
        combined_insights = await generate_full_analysis(all_insights)
        logger.info(f"Combined insights: {json.dumps(combined_insights, indent=2)}")
        
        analysis_results[task_id] = {
            "status": "completed",
            "result": combined_insights,
            "progress": 100
        }
        logger.info(f"Analysis completed for task {task_id}. Result: {json.dumps(analysis_results[task_id], indent=2)}")
    except Exception as e:
        logger.error(f"Error in analyze_url_background for task {task_id}: {str(e)}")
        logger.exception("Full traceback:")
        analysis_results[task_id] = {"status": "error", "message": str(e)}
    
    logger.info(f"Final analysis result for task {task_id}: {json.dumps(analysis_results[task_id], indent=2)}")
    
async def process_posts(df: pd.DataFrame, task_id: str) -> list:
    all_insights = []
    total_posts = len(df)
    analysis_results[task_id]["total_essays"] = total_posts

    for index, row in df.iterrows():
        try:
            processed_text = process_text(row['content'])
            insights = await extract_concepts(processed_text['processed_text'])
            all_insights.append(insights)
            
            progress = int((index + 1) / total_posts * 100)
            update_progress(task_id, progress, index + 1)
        except Exception as e:
            logger.error(f"Error processing post {index + 1}: {str(e)}")
    
    if not all_insights:
        raise ValueError("No posts were successfully analyzed. Please try again later or contact support if the issue persists.")
    
    return all_insights

def update_progress(task_id: str, progress: int, essays_analyzed: int):
    analysis_results[task_id]["progress"] = progress
    analysis_results[task_id]["essays_analyzed"] = essays_analyzed
    logger.info(f"Task {task_id}: Processed {essays_analyzed}/{analysis_results[task_id]['total_essays']} posts")

async def analyze_multiple_essays(processed_essays: list) -> dict:
    logger.info(f"Analyzing {len(processed_essays)} essays")
    
    all_concepts = [essay['insights']['key_themes'] for essay in processed_essays]
    combined_concepts = await combine_concepts(all_concepts)
    
    return {
        "insights": combined_concepts,
        "avg_readability_score": 0,  # You might want to calculate this
        "overall_sentiment": "Neutral",  # You might want to calculate this
        "essays_analyzed": len(processed_essays),
    }


async def generate_full_analysis(processed_essays: list) -> dict:
    try:
        combined_analysis = await analyze_multiple_essays(processed_essays)
        
        result = {
            "overall_analysis": {
                "key_themes": combined_analysis['insights']['key_themes'],
                "writing_style": "Analytical and informative",  # You might want to generate this dynamically
                "readability_score": combined_analysis.get('avg_readability_score', 0),
                "sentiment": combined_analysis.get('overall_sentiment', "Neutral"),
                "post_count": len(processed_essays),
            },
            "essays": [
                {"insights": {"key_themes": essay['insights']['key_themes']}} 
                for essay in processed_essays
            ]
        }
        
        logger.info(f"Full analysis result: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        logger.error(f"Error in generate_full_analysis: {str(e)}", exc_info=True)
        return {
            "overall_analysis": {
                "key_themes": [],
                "writing_style": "Not available",
                "readability_score": 0,
                "sentiment": "Unknown",
                "post_count": len(processed_essays),
            },
            "essays": []
        }
    

@router.get("/status/{task_id}")
async def get_analysis_status(task_id: str):
    logger.info(f"Checking status for task: {task_id}")
    if task_id not in analysis_results:
        logger.warning(f"Task not found: {task_id}")
        raise HTTPException(status_code=404, detail="Task not found")
    
    status = analysis_results[task_id]
    if status["status"] == "processing":
        return {
            "status": "processing",
            "progress": status["progress"],
            "essays_analyzed": status.get("essays_analyzed", 0),
            "total_essays": status.get("total_essays", 0)
        }
    return status