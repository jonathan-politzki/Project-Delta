# embedding_service.py

import numpy as np
from anthropic import Anthropic
import openai
from app.core.config import LLM_PROVIDER, ANTHROPIC_API_KEY, OPENAI_API_KEY


anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
openai.api_key = OPENAI_API_KEY

def generate_embedding(text: str) -> list[float]:
    if LLM_PROVIDER == "anthropic":
        # Note: As of my knowledge cutoff, Anthropic doesn't provide a dedicated embedding API
        # This is a placeholder for when they do
        raise NotImplementedError("Anthropic embedding not yet implemented")
    elif LLM_PROVIDER == "openai":
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response['data'][0]['embedding']
    else:
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")