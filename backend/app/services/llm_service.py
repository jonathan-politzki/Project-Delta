import openai

# set up openai key

openai.api_key = "your-api-key-here"

async def generate_insights(text: str) -> str:
    response = await openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a writing analyst. Provide insights on the writing style and key themes of the given text."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content
