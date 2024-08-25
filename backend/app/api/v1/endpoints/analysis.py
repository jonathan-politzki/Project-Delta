# backend/app/api/v1/endpoints/analysis.py

import uuid
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
    analysis_results[task_id] = {"status": "processing", "progress": 0, "total_essays": 0}  # Initialize the task
    
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
        scraped_data = await scrape_url(url)
        df = scraper_output_to_df(scraped_data)
        
        all_concepts = []
        
        for _, row in df.iterrows():
            processed_text = process_text(row['content'])
            analysis = await generate_analysis(processed_text)
            all_concepts.append(analysis['concepts'])
        
        aggregated_concepts = aggregate_concepts(all_concepts)
        
        analysis_results[task_id] = {
            "status": "completed",
            "result": {
                "individual_concepts": all_concepts,
                "aggregated_concepts": aggregated_concepts
            },
            "progress": 100
        }
    except Exception as e:
        logger.error(f"Error in analyze_url_background for task {task_id}: {str(e)}")
        analysis_results[task_id] = {"status": "error", "message": str(e)}
        logger.info(f"Final analysis result for task {task_id}: {json.dumps(analysis_results[task_id])}")



@router.get("/status/{task_id}")
async def get_analysis_status(task_id: str):
    logger.info(f"Checking status for task: {task_id}")
    if task_id not in analysis_results:
        logger.warning(f"Task not found: {task_id}")
        return {"status": "not_found"}
    status = analysis_results[task_id]
    logger.info(f"Returning status for task {task_id}: {status}")
    return status