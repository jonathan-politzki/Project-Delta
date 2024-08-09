# llm_service.py

from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import openai
from app.core.config import LLM_PROVIDER, ANTHROPIC_API_KEY, OPENAI_API_KEY

anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
openai.api_key = OPENAI_API_KEY

async def generate_insights(text: str) -> str: # added some logic in acreate to make openai asynchronous. may need to do this with anthrpoic if we end up using it
    if LLM_PROVIDER == "anthropic":
        response = anthropic.completions.create(
            model="claude-3-5-sonnet-20240620",
            prompt=f"{HUMAN_PROMPT}You are a writing analyst. Provide insights on the writing style and key themes of the given text:\n\n{text}{AI_PROMPT}",
            max_tokens_to_sample=300
        )
        return response.completion
    if LLM_PROVIDER == "openai": 
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a writing analyst. Provide insights on the writing style and key themes of the given text."},
                    {"role": "user", "content": text}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in generate_insights: {str(e)}")
            return f"Error generating insights: {str(e)}"

    else:
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")