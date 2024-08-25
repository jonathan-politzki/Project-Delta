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
        logger.info(f"Starting background analysis for task {task_id}, URL: {url}")
        scraped_data = await scrape_url(url)
        df = scraper_output_to_df(scraped_data)
        
        total_posts = len(df)
        analysis_results[task_id]["total_essays"] = total_posts
        logger.info(f"Scraped {total_posts} posts")
        
        if df.empty:
            raise ValueError(f"No posts were scraped from the URL: {url}. Please check if the URL is correct and accessible.")

        # Process each article/post
        all_insights = []
        for index, row in df.iterrows():
            try:
                processed_text = process_text(row['content'])
                insights = await extract_concepts(processed_text['processed_text'])
                all_insights.append(insights)
                
                # Update progress
                progress = int((index + 1) / total_posts * 100)
                analysis_results[task_id]["progress"] = progress
                analysis_results[task_id]["essays_analyzed"] = index + 1
                logger.info(f"Task {task_id}: Processed {index + 1}/{total_posts} posts")
            except Exception as e:
                logger.error(f"Error processing post: {str(e)}")
                # Continue with the next post instead of breaking the loop

        if not all_insights:
            raise ValueError("No posts were successfully analyzed. Please try again later or contact support if the issue persists.")

        # Combine results
        combined_insights = {
            "writing_style": [],
            "key_themes": [],
            "conclusion": ""
        }
        
        for insight in all_insights:
            combined_insights["writing_style"].extend(insight["writing_style"])
            combined_insights["key_themes"].extend(insight["key_themes"])
        
        # Deduplicate and limit the number of points
        combined_insights["writing_style"] = list(set(combined_insights["writing_style"]))[:5]
        combined_insights["key_themes"] = list(set(combined_insights["key_themes"]))[:5]
        
        # Generate an overall conclusion
        combined_insights["conclusion"] = f"Analysis based on {len(all_insights)} essays. " + all_insights[-1]["conclusion"]
        
        logger.info(f"Analysis completed for task {task_id}")
        analysis_results[task_id] = {
            "status": "completed",
            "result": {
                "insights": combined_insights
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