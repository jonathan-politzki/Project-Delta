# llm_service.py

from openai import AsyncOpenAI
from app.core.config import LLM_PROVIDER, OPENAI_API_KEY
import logging
import json
import re

client = AsyncOpenAI(api_key=OPENAI_API_KEY)
logger = logging.getLogger(__name__)

def parse_llm_response(response_text: str) -> dict:
    """
    Parse the LLM response, handling potential JSON formatting issues.
    """
    # Remove code block markers if present
    clean_text = re.sub(r'```json\s*|\s*```', '', response_text)
    try:
        return json.loads(clean_text)
    except json.JSONDecodeError:
        # If JSON parsing fails, attempt to extract key themes manually
        themes = re.findall(r'"theme":\s*"([^"]*)"', clean_text)
        return {"key_themes": themes if themes else []}

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
                {"role": "system", "content": "You are an AI model tasked with extracting the main concepts, ideas, and arguments from a text. Identify and summarize the 3 most important concepts or ideas presented in the text. Focus solely on the content and avoid commenting on writing style or structure."},
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
            return {"insights": {"key_themes": []}}

    except Exception as e:
        logger.error(f"Error in extract_concepts: {e.__class__.__name__}: {str(e)}")
        logger.exception("Full traceback:")
        return {"insights": {"key_themes": []}}

def parse_insights(text: str) -> dict:
    concepts = text.split('\n')
    key_themes = [concept.strip() for concept in concepts if concept.strip()]
    key_themes = key_themes[:3]
    while len(key_themes) < 3:
        key_themes.append("No additional concept identified.")
    
    return {"insights": {"key_themes": key_themes}}

async def combine_concepts(all_concepts: list) -> dict:
    combined_text = "\n".join([f"Essay {i+1}:\n" + "\n".join(essay) for i, essay in enumerate(all_concepts)])
    
    logger.info(f"Combining concepts from {len(all_concepts)} essays")
    logger.info(f"Combined text: {combined_text}")

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI model that is trained to detect consistencies in ideas. Analyze the given concepts from multiple essays and synthesize them into 3 overarching trends in the type of ideas discussed. In this process, synthesize with the intent of comparing the ideas to traditional ideas or knowledge and finding the major differences in the ideas. Format your response as a JSON object with a 'key_themes' array containing these 3 overarching trends."},
                {"role": "user", "content": combined_text}
            ],
            temperature=0.1
        )

        logger.info(f"Raw OpenAI API response for combined concepts: {response}")

        if response and response.choices and len(response.choices) > 0:
            result = response.choices[0].message.content
            logger.info(f"Raw LLM result for combined concepts: {result}")
            parsed_result = parse_llm_response(result)
            logger.info(f"Parsed insights for combined concepts: {parsed_result}")
            return {"insights": parsed_result}
        else:
            logger.error("No choices returned in response for combined concepts.")
            return {"insights": {"key_themes": []}}

    except Exception as e:
        logger.error(f"Error in combine_concepts: {e.__class__.__name__}: {str(e)}")
        logger.exception("Full traceback:")
        return {"insights": {"key_themes": []}}