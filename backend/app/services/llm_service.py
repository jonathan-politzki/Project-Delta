from openai import AsyncOpenAI
from app.core.config import LLM_PROVIDER, OPENAI_API_KEY
import logging

client = AsyncOpenAI(api_key=OPENAI_API_KEY)
logger = logging.getLogger(__name__)

async def generate_insights(text: str) -> str:
    if LLM_PROVIDER != "openai":
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")

    try:
        # Check if text is a string, if not, convert it to a string
        if not isinstance(text, str):
            text = str(text)
        
        logger.info(f"Generating insights for text: {text[:100]}...")  # Log first 100 chars

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an experienced writing analyst. Break down the text into its three core concepts."},
                {"role": "user", "content": text}
            ],
            temperature=0.1
        )

        if response and response.choices and len(response.choices) > 0:
            result = response.choices[0].message.content
            logger.info(f"LLM response received. First 100 chars: {result[:100]}...")
            return result
        else:
            logger.error("No choices returned in response.")
            return "Error: No insights generated."

    except Exception as e:
        logger.error(f"Error in generate_insights: {e.__class__.__name__}: {str(e)}")
        logger.exception("Full traceback:")
        return f"Error generating insights: {e.__class__.__name__}: {str(e)}"
