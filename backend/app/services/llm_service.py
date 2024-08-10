# llm_service.py

from openai import AsyncOpenAI
from app.core.config import LLM_PROVIDER, OPENAI_API_KEY
import logging

client = AsyncOpenAI(api_key=OPENAI_API_KEY)
logger = logging.getLogger(__name__)

async def generate_insights(text: str) -> str:
    if LLM_PROVIDER == "openai":
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a writing analyst. Provide insights on the writing style and key themes of the given text."},
                    {"role": "user", "content": text}
                ],
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in generate_insights: {str(e)}")
            return f"Error generating insights: {str(e)}"
    else:
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")

