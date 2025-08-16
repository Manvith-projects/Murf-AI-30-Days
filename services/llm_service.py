import os
from google import genai
import logging

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
logger = logging.getLogger(__name__)

def query_llm(text: str) -> str | None:
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=text
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini LLM Error: {e}")
        return None
