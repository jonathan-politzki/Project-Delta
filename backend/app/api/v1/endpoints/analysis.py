# backend/app/api/v1/endpoints/analysis.py

import uuid
import json
from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.schemas.analysis_schemas import AnalysisRequest, AnalysisResponse
from app.services.text_processor import process_text
from app.services.llm_service import extract_concepts
from app.services.embedding_service import generate_embedding
from app.services.analysis_service import generate_analysis, aggregate_concepts
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
        df = scraper_output_to_df(scraped_data)
        
        if df.empty:
            raise ValueError(f"No posts were scraped from the URL: {url}. Please check if the URL is correct and accessible.")

        all_insights = await process_posts(df, task_id)
        combined_insights = combine_insights(all_insights)
        
        analysis_results[task_id] = {
            "status": "completed",
            "result": {"insights": combined_insights},
            "progress": 100
        }
        logger.info(f"Analysis completed for task {task_id}")
    except Exception as e:
        logger.error(f"Error in analyze_url_background for task {task_id}: {str(e)}")
        analysis_results[task_id] = {"status": "error", "message": str(e)}
    
    logger.info(f"Final analysis result for task {task_id}: {json.dumps(analysis_results[task_id])}")

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

def combine_insights(all_insights: list) -> dict:
    combined_insights = {
        "writing_style": [],
        "key_themes": [],
        "conclusion": ""
    }
    
    for insight in all_insights:
        combined_insights["writing_style"].extend(insight["writing_style"])
        combined_insights["key_themes"].extend(insight["key_themes"])
    
    combined_insights["writing_style"] = list(set(combined_insights["writing_style"]))[:5]
    combined_insights["key_themes"] = list(set(combined_insights["key_themes"]))[:5]
    combined_insights["conclusion"] = f"Analysis based on {len(all_insights)} essays. " + all_insights[-1]["conclusion"]
    
    return combined_insights

@router.get("/status/{task_id}")
async def get_analysis_status(task_id: str):
    logger.info(f"Checking status for task: {task_id}")
    if task_id not in analysis_results:
        logger.warning(f"Task not found: {task_id}")
        raise HTTPException(status_code=404, detail="Task not found")
    
    status = analysis_results[task_id]
    logger.info(f"Returning status for task {task_id}: {status}")
    return status