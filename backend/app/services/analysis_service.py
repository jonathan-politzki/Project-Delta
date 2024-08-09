from collections import Counter
from nltk import pos_tag, word_tokenize
import nltk
from .llm_service import generate_insights
from ..core.vector_db import insert_data, search_vectors
import logging

nltk.download('averaged_perceptron_tagger')
logger = logging.getLogger(__name__)

async def generate_analysis(processed_text: dict, embedding: list[float]) -> dict:
    logger.info("Generating analysis")
    
    try:
        # Extract key themes (most common nouns)
        words = word_tokenize(processed_text['processed_text'])
        tagged_words = pos_tag(words)
        nouns = [word.lower() for word, pos in tagged_words if pos.startswith('NN')]
        key_themes = [theme for theme, _ in Counter(nouns).most_common(5)]
        
        # Determine writing style based on sentence length and word choice
        avg_sentence_length = processed_text['word_count'] / processed_text['sentence_count']
        if avg_sentence_length > 20:
            writing_style = "Complex and detailed"
        elif avg_sentence_length < 10:
            writing_style = "Concise and to-the-point"
        else:
            writing_style = "Balanced and clear"
        
        # Generate insights using the LLM
        insights = await generate_insights(processed_text['processed_text'])
        
        # Store in vector database
        insert_data("demo_collection", [{
            "id": processed_text.get('id', 0),  # You might want to generate a unique ID
            "vector": embedding,
            "text": processed_text['processed_text'],
            "subject": "analysis"  # You can adjust this as needed
        }])
        
        # Perform a similarity search
        similar_texts = search_vectors("demo_collection", [embedding], limit=3, output_fields=["text"])
        
        logger.info("Analysis generated successfully")
        
        return {
            "insights": insights,
            "writing_style": writing_style,
            "key_themes": key_themes,
            "readability_score": processed_text['readability_score'],
            "sentiment": processed_text['sentiment'],
            "similar_texts": [result['entity']['text'] for result in similar_texts[0] if 'entity' in result and 'text' in result['entity']]
        }
    except Exception as e:
        logger.error(f"Error in generate_analysis: {str(e)}", exc_info=True)
        return {
            "insights": "Error generating insights",
            "writing_style": "Unknown",
            "key_themes": [],
            "readability_score": 0,
            "sentiment": "Unknown",
            "similar_texts": []
        }