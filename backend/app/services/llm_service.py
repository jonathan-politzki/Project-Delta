# llm_service.py

from openai import AsyncOpenAI
from app.core.config import LLM_PROVIDER, OPENAI_API_KEY
import logging

client = AsyncOpenAI(api_key=OPENAI_API_KEY)
logger = logging.getLogger(__name__)

async def extract_concepts(text: str) -> dict:
    if LLM_PROVIDER != "openai":
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")

    try:
        if not isinstance(text, str):
            text = str(text)
        
        logger.info(f"Extracting concepts for text: {text[:100]}...")  # Log first 100 chars

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an experienced writing analyst. Analyze the given text and extract the 3 main concepts that make up the author's personality fingerprint. Each concept should be a combination of beliefs, values, and experiences."},
                {"role": "user", "content": text}
            ],
            temperature=0.1
        )

        logger.info(f"Raw OpenAI API response: {response}")

        if response and response.choices and len(response.choices) > 0:
            result = response.choices[0].message.content
            logger.info(f"Raw LLM result: {result}")
            structured_insights = parse_insights(result)
            logger.info(f"Extracted insights: {structured_insights}")
            return structured_insights
        else:
            logger.error("No choices returned in response.")
            return {"key_themes": [], "conclusion": "Error: No insights extracted."}

    except Exception as e:
        logger.error(f"Error in extract_concepts: {e.__class__.__name__}: {str(e)}")
        logger.exception("Full traceback:")
        return {"key_themes": [], "conclusion": f"Error extracting insights: {e.__class__.__name__}: {str(e)}"}

def parse_insights(text: str) -> dict:
    concepts = text.split('\n')
    
    structured_insights = {
        "key_themes": [],
        "conclusion": ""
    }

    for concept in concepts:
        if concept.strip():
            structured_insights["key_themes"].append(concept.strip())

    # Ensure we have exactly 3 concepts
    structured_insights["key_themes"] = structured_insights["key_themes"][:3]
    while len(structured_insights["key_themes"]) < 3:
        structured_insights["key_themes"].append("No additional concept identified.")

    # Add a conclusion
    structured_insights["conclusion"] = "These concepts represent the author's main beliefs, values, and experiences as reflected in their writing."

    return structured_insights

async def combine_concepts(all_concepts: list) -> dict:
    combined_text = "\n".join([f"Essay {i+1}:\n" + "\n".join(essay["key_themes"]) for i, essay in enumerate(all_concepts)])
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an experienced writing analyst. Analyze the given concepts from multiple essays and synthesize them into 3 overarching concepts that represent the author's personality fingerprint."},
                {"role": "user", "content": combined_text}
            ],
            temperature=0.1
        )

        if response and response.choices and len(response.choices) > 0:
            result = response.choices[0].message.content
            return parse_insights(result)
        else:
            logger.error("No choices returned in response for combined concepts.")
            return {"key_themes": [], "conclusion": "Error: No combined insights extracted."}

    except Exception as e:
        logger.error(f"Error in combine_concepts: {e.__class__.__name__}: {str(e)}")
        logger.exception("Full traceback:")
        return {"key_themes": [], "conclusion": f"Error extracting combined insights: {e.__class__.__name__}: {str(e)}"}