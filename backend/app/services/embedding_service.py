import openai
import numpy as np

openai.api_key = "your-api-key-here"

def generate_embedding(text: str) -> list[float]:
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response['data'][0]['embedding']
