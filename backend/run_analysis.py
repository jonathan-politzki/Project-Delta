# run_analysis.py

import asyncio
import pandas as pd
from app.services.text_processor import process_text
from app.services.llm_service import generate_insights
from app.services.embedding_service import generate_embedding
from app.services.analysis_service import generate_analysis
from app.schemas.analysis_schemas import AnalysisResponse
import logging
import os
from tqdm import tqdm
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple cache implementation
cache = {}

async def cached_generate_insights(text: str) -> str:
    if text in cache:
        return cache[text]
    insights = await generate_insights(text)
    cache[text] = insights
    return insights

def cached_generate_embedding(text: str) -> list[float]:
    if text in cache:
        return cache[text]
    embedding = generate_embedding(text)
    cache[text] = embedding
    return embedding

async def process_post(content: str):
    try:
        processed_text = process_text(content)
        logger.info(f"Processed text: {processed_text['processed_text'][:100]}...")

        insights = await generate_insights(processed_text['processed_text'])
        logger.info(f"Generated insights: {insights[:100]}...")

        embedding = await generate_embedding(processed_text['processed_text'])
        logger.info(f"Generated embedding (first 5 values): {embedding[:5]}")

        analysis = await generate_analysis(processed_text, embedding)
        logger.info(f"Generated analysis: {json.dumps(analysis, indent=2)}")

        return analysis
    except Exception as e:
        logger.error(f"Error in process_post: {str(e)}", exc_info=True)
        return {
            "insights": f"Error processing post: {str(e)}",
            "writing_style": "Unknown",
            "key_themes": [],
            "readability_score": 0,
            "sentiment": "Unknown",
        }
    
async def analyze_file(file_path: str):
    logger.info(f"Analyzing file: {file_path}")
    df = pd.read_csv(file_path)
    
    results = []
    for _, post in tqdm(df.iterrows(), total=len(df), desc="Processing posts"):
        result = await process_post(post['content'])
        results.append(result)

    if not results:
        raise ValueError("No results were processed successfully")

    combined_analysis = {
        "insights": "\n".join([r['insights'] for r in results]),
        "writing_style": pd.Series([r['writing_style'] for r in results]).mode().iloc[0],
        "key_themes": list(set([theme for r in results for theme in r.get('key_themes', [])])),
        "readability_score": sum([r['readability_score'] for r in results]) / len(results),
        "sentiment": pd.Series([r['sentiment'] for r in results]).mode().iloc[0],
        "post_count": len(results)
    }
    
    return AnalysisResponse(**combined_analysis)

async def main():
    output_dir = "output"
    file_paths = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith('.csv')]
    
    for file_path in file_paths:
        try:
            analysis_result = await analyze_file(file_path)
            logger.info(f"Analysis result for {file_path}:")
            logger.info(analysis_result.json(indent=2))
            
            result_file = f"{os.path.splitext(file_path)[0]}_analysis_result.json"
            with open(result_file, "w") as f:
                f.write(analysis_result.json(indent=2))
            logger.info(f"Analysis result saved to {result_file}")
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())