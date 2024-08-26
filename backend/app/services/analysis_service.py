# backend/app/services/analysis_service.py

import logging
from .llm_service import extract_concepts, combine_concepts
import json

logger = logging.getLogger(__name__)

async def generate_analysis(processed_text: dict) -> dict:
    logger.info("Generating analysis for single essay")
    
    try:
        # Extract concepts using the LLM
        concepts_result = await extract_concepts(processed_text['processed_text'])
        
        logger.info("Analysis generated successfully for single essay")
        
        return {
            "concepts": concepts_result['insights']['key_themes'],
            "readability_score": processed_text['readability_score'],
            "sentiment": processed_text['sentiment'],
            "insights": concepts_result['insights']['summary']
        }
    except Exception as e:
        logger.error(f"Error in generate_analysis: {str(e)}", exc_info=True)
        return {
            "concepts": ["Error generating concepts"],
            "readability_score": 0,
            "sentiment": "Unknown"
        }



async def analyze_multiple_essays(processed_essays: list) -> dict:
    logger.info(f"Analyzing {len(processed_essays)} essays")
    
    all_concepts = []
    total_readability = 0
    sentiments = []
    all_insights = []

    for essay in processed_essays:
        analysis = await generate_analysis(essay)
        all_concepts.append(analysis['concepts'])
        total_readability += analysis['readability_score']
        sentiments.append(analysis['sentiment'])
        all_insights.append(analysis['insights'])

    # Combine concepts from all essays
    combined_concepts = await combine_concepts(all_concepts)

    # Calculate average readability
    avg_readability = total_readability / len(processed_essays) if processed_essays else 0

    # Determine overall sentiment
    overall_sentiment = max(set(sentiments), key=sentiments.count) if sentiments else "Unknown"

    logger.info("Combined analysis generated successfully")

    return {
        "combined_concepts": combined_concepts['key_themes'],
        "conclusion": combined_concepts['conclusion'],
        "avg_readability_score": avg_readability,
        "overall_sentiment": overall_sentiment,
        "essays_analyzed": len(processed_essays),
        "insights": all_insights
    }

async def generate_full_analysis(processed_essays: list) -> dict:
    logger.info("Generating full analysis")

    try:
        combined_analysis = await analyze_multiple_essays(processed_essays)
        
        result = {
            "overall_analysis": {
                "writing_style": combined_analysis['conclusion'],
                "key_themes": combined_analysis['combined_concepts'],
                "readability_score": combined_analysis['avg_readability_score'],
                "sentiment": combined_analysis['overall_sentiment'],
                "post_count": combined_analysis['essays_analyzed'],
            },
            "essay_insights": combined_analysis['insights']  # This is now a list of insights per essay
        }
        
        logger.info(f"Full analysis result: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        logger.error(f"Error in generate_full_analysis: {str(e)}", exc_info=True)
        return {
            "overall_analysis": {
                "writing_style": "Not available",
                "key_themes": [],
                "readability_score": 0,
                "sentiment": "Unknown",
                "post_count": 0,
            },
            "essay_insights": []
        }