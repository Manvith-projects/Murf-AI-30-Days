import os
import requests
import logging
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

MURF_API_KEY = os.getenv("MURF_API_KEY")


def murf_tts(text: str) -> str | None:
    """Text to speech using Murf API."""
    if not MURF_API_KEY:
        logger.error("MURF Error: API key not found")
        return None
    headers = {"api-key": MURF_API_KEY}
    payload = {"text": text, "voiceId": "en-US-natalie"}
    try:
        res = requests.post("https://api.murf.ai/v1/speech/generate", headers=headers, json=payload)
        res.raise_for_status()
        data = res.json()
        audio_file = data.get("audioFile")
        if not audio_file:
            logger.error("MURF Error: No audioFile in response")
            return None
        return audio_file
    except Exception as e:
        logger.error(f"MURF TTS Error: {e}")
        return None
