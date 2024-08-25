# llm_service.py

from openai import AsyncOpenAI
from app.core.config import LLM_PROVIDER, OPENAI_API_KEY
import logging
import json

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
                {"role": "system", "content": "You are an AI model tasked with extracting the main ideas from a text. Take this text and extract the main 3 big concepts in a standalone way, describing only the ideas. Format your response as a JSON object with a 'key_themes' array containing these 3 concepts."},
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
    try:
        # Attempt to parse the text as JSON
        insights = json.loads(text)
        if not isinstance(insights, dict) or 'key_themes' not in insights:
            raise ValueError("Invalid JSON structure")
        
        # Ensure we have exactly 3 key themes
        key_themes = insights['key_themes'][:3]
        while len(key_themes) < 3:
            key_themes.append("No additional concept identified.")
        
        return {"insights": {"key_themes": key_themes}}
    except json.JSONDecodeError:
        # If JSON parsing fails, fall back to text parsing
        lines = text.split('\n')
        key_themes = []
        for line in lines:
            if line.strip().startswith('-'):
                key_themes.append(line.strip()[1:].strip())
            if len(key_themes) == 3:
                break
        
        while len(key_themes) < 3:
            key_themes.append("No additional concept identified.")
        
        return {"insights": {"key_themes": key_themes}}

async def combine_concepts(all_concepts: list) -> dict:
    combined_text = "\n".join([f"Essay {i+1}:\n" + "\n".join(essay["insights"]["key_themes"]) for i, essay in enumerate(all_concepts)])
    
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
            parsed_result = parse_insights(result)
            logger.info(f"Parsed insights for combined concepts: {parsed_result}")
            return parsed_result
        else:
            logger.error("No choices returned in response for combined concepts.")
            return {"insights": {"key_themes": []}}

    except Exception as e:
        logger.error(f"Error in combine_concepts: {e.__class__.__name__}: {str(e)}")
        logger.exception("Full traceback:")
        return {"insights": {"key_themes": []}}