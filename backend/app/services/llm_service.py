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
                {"role": "system", "content": "You are an experienced writing analyst. Analyze the given text and provide: 1) Three to five core concepts, each with a title and a brief description. 2) One overarching concept that encompasses all the core concepts."},
                {"role": "user", "content": text}
            ],
            temperature=0.1
        )

        if response and response.choices and len(response.choices) > 0:
            result = response.choices[0].message.content
            # Parse the result into core concepts and overarching concept
            concepts = parse_concepts(result)
            logger.info(f"Extracted concepts: {concepts}")
            return concepts
        else:
            logger.error("No choices returned in response.")
            return {"core_concepts": [], "overarching_concept": "Error: No concepts extracted."}

    except Exception as e:
        logger.error(f"Error in extract_concepts: {e.__class__.__name__}: {str(e)}")
        logger.exception("Full traceback:")
        return {"core_concepts": [], "overarching_concept": f"Error extracting concepts: {e.__class__.__name__}: {str(e)}"}

def parse_concepts(text: str) -> dict:
    lines = text.split('\n')
    core_concepts = []
    overarching_concept = ""
    current_concept = {}

    for line in lines:
        if line.startswith("Core Concepts"):
            continue
        elif line.startswith("1.") or line.startswith("2.") or line.startswith("3.") or line.startswith("4.") or line.startswith("5."):
            if current_concept:
                core_concepts.append(current_concept)
            current_concept = {"title": line.split(":")[0].strip(), "description": line.split(":")[1].strip()}
        elif line.startswith("Overarching Concept:"):
            if current_concept:
                core_concepts.append(current_concept)
            overarching_concept = line.split(":")[1].strip()

    if current_concept:
        core_concepts.append(current_concept)

    return {"core_concepts": core_concepts, "overarching_concept": overarching_concept}