# backend/app/services/analysis_service.py

import logging
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
            "concepts": concepts_result['insights']['key_themes'],
            "readability_score": processed_text['readability_score'],
            "sentiment": processed_text['sentiment'],
            "insights": concepts_result['insights']['summary']
        }
        
        logger.info("Analysis generated successfully for single essay")
        return analysis
    
    except Exception as e:
        logger.error(f"Error in generate_analysis: {str(e)}", exc_info=True)
        return {
            "concepts": ["Error generating concepts"],
            "readability_score": 0,
            "sentiment": "Unknown",
            "insights": "Error occurred during analysis"
        }

async def analyze_multiple_essays(processed_essays: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze multiple essays and combine their results.
    """
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

    try:
        combined_concepts = await combine_concepts(all_concepts)
        avg_readability = total_readability / len(processed_essays) if processed_essays else 0
        overall_sentiment = max(set(sentiments), key=sentiments.count) if sentiments else "Unknown"

        combined_analysis = {
            "combined_concepts": combined_concepts['key_themes'],
            "conclusion": combined_concepts['conclusion'],
            "avg_readability_score": avg_readability,
            "overall_sentiment": overall_sentiment,
            "essays_analyzed": len(processed_essays),
            "insights": all_insights
        }

        logger.info("Combined analysis generated successfully")
        return combined_analysis

    except Exception as e:
        logger.error(f"Error in analyze_multiple_essays: {str(e)}", exc_info=True)
        return {
            "combined_concepts": [],
            "conclusion": "Error occurred during analysis",
            "avg_readability_score": 0,
            "overall_sentiment": "Unknown",
            "essays_analyzed": len(processed_essays),
            "insights": []
        }

async def generate_full_analysis(processed_essays: list) -> dict:
    try:
        combined_analysis = await analyze_multiple_essays(processed_essays)
        
        result = {
            "overall_analysis": {
                "key_themes": combined_analysis['insights']['key_themes'],  # Changed from 'combined_concepts'
                "writing_style": "Analytical and informative",  # You might want to generate this dynamically
                "readability_score": combined_analysis.get('avg_readability_score', 0),
                "sentiment": combined_analysis.get('overall_sentiment', "Unknown"),
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