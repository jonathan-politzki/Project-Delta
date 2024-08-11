# embedding_service.py

from openai import AsyncOpenAI
from app.core.config import LLM_PROVIDER, OPENAI_API_KEY
import logging

client = AsyncOpenAI(api_key=OPENAI_API_KEY)
logger = logging.getLogger(__name__)

async def generate_embedding(text: str) -> list[float]:
    if LLM_PROVIDER == "openai":
        try:
            response = await client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            embedding = response.data[0].embedding
            if len(embedding) != 1536:  # OpenAI's text-embedding-3-small model produces 1536-dimensional embeddings
                raise ValueError(f"Expected embedding dimension 1536, but got {len(embedding)}")
            logger.info(f"Generated embedding of length: {len(embedding)}")
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return []
    else:
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")