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
                {"role": "system", "content": "You are an experienced writing analyst. Analyze the given text and provide: 1) Writing style analysis. 2) Key themes analysis. 3) A brief conclusion."},
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
            return {"writing_style": [], "key_themes": [], "conclusion": "Error: No insights extracted."}

    except Exception as e:
        logger.error(f"Error in extract_concepts: {e.__class__.__name__}: {str(e)}")
        logger.exception("Full traceback:")
        return {"writing_style": [], "key_themes": [], "conclusion": f"Error extracting insights: {e.__class__.__name__}: {str(e)}"}

def parse_insights(text: str) -> dict:
    sections = text.split('###')
    
    structured_insights = {
        "writing_style": [],
        "key_themes": [],
        "conclusion": ""
    }

    for section in sections:
        if "Writing Style:" in section:
            style_points = section.split('\n')[1:]  # Skip the title
            structured_insights["writing_style"] = [point.strip().strip('1234567890. ') for point in style_points if point.strip()]
        elif "Key Themes:" in section:
            theme_points = section.split('\n')[1:]  # Skip the title
            structured_insights["key_themes"] = [point.strip().strip('1234567890. ') for point in theme_points if point.strip()]
        elif "Conclusion:" in section:
            structured_insights["conclusion"] = section.replace("Conclusion:", "").strip()

    # If any section is empty, add a default message
    if not structured_insights["writing_style"]:
        structured_insights["writing_style"] = ["No writing style analysis available."]
    if not structured_insights["key_themes"]:
        structured_insights["key_themes"] = ["No key themes identified."]
    if not structured_insights["conclusion"]:
        structured_insights["conclusion"] = "No conclusion available."

    return structured_insights

