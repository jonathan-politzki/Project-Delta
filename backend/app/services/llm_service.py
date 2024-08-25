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
                {"role": "system", "content": "You are an AI model tasked with extracting the main ideas from a text. Take this text and extract the main 3 big concepts in a standalone way, describing only the ideas."},
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
            return {"insights": {"key_themes": [], "conclusion": "Error: No insights extracted.", "writing_style": "Unknown"}}

    except Exception as e:
        logger.error(f"Error in extract_concepts: {e.__class__.__name__}: {str(e)}")
        logger.exception("Full traceback:")
        return {"insights": {"key_themes": [], "conclusion": f"Error extracting insights: {e.__class__.__name__}: {str(e)}", "writing_style": "Unknown"}}

def parse_insights(text: str) -> dict:
    lines = text.split('\n')
    
    structured_insights = {
        "insights": {
            "key_themes": [],
            "conclusion": "",
            "writing_style": ""
        }
    }

    current_section = None
    for line in lines:
        line = line.strip()
        if line.startswith("Key Themes:"):
            current_section = "key_themes"
        elif line.startswith("Writing Style:"):
            current_section = "writing_style"
        elif line.startswith("Conclusion:"):
            current_section = "conclusion"
        elif line and current_section:
            if current_section == "key_themes":
                structured_insights["insights"]["key_themes"].append(line)
            elif current_section == "writing_style":
                structured_insights["insights"]["writing_style"] += line + " "
            elif current_section == "conclusion":
                structured_insights["insights"]["conclusion"] += line + " "

    # Ensure we have exactly 3 key themes
    structured_insights["insights"]["key_themes"] = structured_insights["insights"]["key_themes"][:3]
    while len(structured_insights["insights"]["key_themes"]) < 3:
        structured_insights["insights"]["key_themes"].append("No additional concept identified.")

    return structured_insights

async def combine_concepts(all_concepts: list) -> dict:
    combined_text = "\n".join([f"Essay {i+1}:\n" + "\n".join(essay["key_themes"]) for i, essay in enumerate(all_concepts)])
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI model that is trained to detect consistencies in ideas. Analyze the given concepts from multiple essays and synthesize them into 3 overarching trends in the type of ideas discussed. In this process, synthesize with the intent of comparing the ideas to traditional ideas or knowledge and finding the major differences in the ideas."},
                {"role": "user", "content": combined_text}
            ],
            temperature=0.1
        )

        if response and response.choices and len(response.choices) > 0:
            result = response.choices[0].message.content
            return parse_insights(result)
        else:
            logger.error("No choices returned in response for combined concepts.")
            return {"insights": {"key_themes": [], "conclusion": "Error: No combined insights extracted.", "writing_style": "Unknown"}}

    except Exception as e:
        logger.error(f"Error in combine_concepts: {e.__class__.__name__}: {str(e)}")
        logger.exception("Full traceback:")
        return {"insights": {"key_themes": [], "conclusion": f"Error extracting combined insights: {e.__class__.__name__}: {str(e)}", "writing_style": "Unknown"}}