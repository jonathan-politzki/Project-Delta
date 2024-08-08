# backend/app/core/config.py

import os
from dotenv import load_dotenv
load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # Default to Anthropic, can be changed to "openai" or others
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "your-anthropic-api-key-here")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")