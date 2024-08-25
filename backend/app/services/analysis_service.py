# backend/app/services/analysis_service.py

from collections import Counter
import logging
from .llm_service import extract_concepts

logger = logging.getLogger(__name__)

def aggregate_concepts(all_concepts):
    flat_concepts = [concept for essay_concepts in all_concepts for concept in essay_concepts]
    concept_counts = Counter(flat_concepts)
    top_5_concepts = concept_counts.most_common(5)
    
    return [{"concept": concept, "count": count} for concept, count in top_5_concepts]

async def generate_analysis(processed_text: dict) -> dict:
    logger.info("Generating analysis")
    
    try:
        # Extract concepts using the LLM
        concepts = await extract_concepts(processed_text['processed_text'])
        
        logger.info("Analysis generated successfully")
        
        return {
            "concepts": concepts,
            "readability_score": processed_text['readability_score'],
            "sentiment": processed_text['sentiment']
        }
    except Exception as e:
        logger.error(f"Error in generate_analysis: {str(e)}", exc_info=True)
        return {
            "concepts": ["Error generating concepts"],
            "readability_score": 0,
            "sentiment": "Unknown"
        }