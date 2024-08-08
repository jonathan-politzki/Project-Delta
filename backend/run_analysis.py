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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def analyze_file(file_path: str):
    logger.info(f"Analyzing file: {file_path}")
    df = pd.read_csv(file_path)
    
    results = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing posts"):
        processed_text = process_text(row['content'])
        insights = await generate_insights(processed_text)
        embedding = generate_embedding(processed_text)
        analysis = await generate_analysis(processed_text, embedding)
        results.append(analysis)
    
    combined_analysis = {
        "insights": "\n".join([r['insights'] for r in results]),
        "writing_style": pd.Series([r['writing_style'] for r in results]).mode().iloc[0],
        "key_themes": list(set([theme for r in results for theme in r['key_themes']])),
        "readability_score": sum([r['readability_score'] for r in results]) / len(results),
        "sentiment": pd.Series([r['sentiment'] for r in results]).mode().iloc[0],
        "post_count": len(results)
    }
    
    return AnalysisResponse(**combined_analysis)

async def main():
    output_dir = "output"  # Directory where your scraped CSV files are stored
    file_paths = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith('.csv')]
    
    for file_path in file_paths:
        try:
            analysis_result = await analyze_file(file_path)
            logger.info(f"Analysis result for {file_path}:")
            logger.info(analysis_result.json(indent=2))
            
            # Save the result to a file
            result_file = f"{os.path.splitext(file_path)[0]}_analysis_result.json"
            with open(result_file, "w") as f:
                f.write(analysis_result.json(indent=2))
            logger.info(f"Analysis result saved to {result_file}")
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())