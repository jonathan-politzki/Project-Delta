# backend/app/services/analysis_service.py

import logging
import json
from typing import List, Dict, Any
from .llm_service import extract_concepts, combine_concepts

logger = logging.getLogger(__name__)

async def generate_analysis(processed_text: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate analysis for a single essay.
    """
    logger.info("Generating analysis for single essay")
    
    try:
        concepts_result = await extract_concepts(processed_text['processed_text'])
        
        analysis = {
            "insights": {
                "key_themes": concepts_result['insights']['key_themes']
            },
            "readability_score": processed_text['readability_score'],
            "sentiment": processed_text['sentiment']
        }
        
        logger.info("Analysis generated successfully for single essay")
        return analysis
    
    except Exception as e:
        logger.error(f"Error in generate_analysis: {str(e)}", exc_info=True)
        return {
            "insights": {
                "key_themes": ["Error generating concepts"]
            },
            "readability_score": 0,
            "sentiment": "Unknown"
        }

async def analyze_multiple_essays(processed_essays: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze multiple essays and combine their results.
    """
    logger.info(f"Analyzing {len(processed_essays)} essays")
    
    all_concepts = []
    total_readability = 0
    sentiments = []
    individual_essay_insights = []

    for essay in processed_essays:
        analysis = await generate_analysis(essay)
        all_concepts.append(analysis['insights']['key_themes'])
        total_readability += analysis['readability_score']
        sentiments.append(analysis['sentiment'])
        individual_essay_insights.append(analysis['insights'])

    try:
        combined_concepts = await combine_concepts(all_concepts)
        avg_readability = total_readability / len(processed_essays) if processed_essays else 0
        overall_sentiment = max(set(sentiments), key=sentiments.count) if sentiments else "Unknown"

        combined_analysis = {
            "insights": combined_concepts,
            "avg_readability_score": avg_readability,
            "overall_sentiment": overall_sentiment,
            "essays_analyzed": len(processed_essays),
            "individual_essay_insights": individual_essay_insights
        }

        logger.info("Combined analysis generated successfully")
        return combined_analysis

    except Exception as e:
        logger.error(f"Error in analyze_multiple_essays: {str(e)}", exc_info=True)
        return {
            "insights": {"key_themes": []},
            "avg_readability_score": 0,
            "overall_sentiment": "Unknown",
            "essays_analyzed": len(processed_essays),
            "individual_essay_insights": []
        }

async def generate_full_analysis(processed_essays: List[Dict[str, Any]]) -> Dict[str, Any]:
    logger.info("Generating full analysis")

    try:
        combined_analysis = await analyze_multiple_essays(processed_essays)
        
        result = {
            "overall_analysis": {
                "key_themes": combined_analysis['insights']['key_themes'],
                "writing_style": "Analytical and informative",
                "readability_score": combined_analysis['avg_readability_score'],
                "sentiment": combined_analysis['overall_sentiment'],
                "post_count": combined_analysis['essays_analyzed'],
            },
            "essays": combined_analysis['individual_essay_insights']
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