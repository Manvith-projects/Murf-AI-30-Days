import os
import requests
import logging
import base64
from dotenv import load_dotenv
           
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


MURF_API_KEY = os.getenv("MURF_API_KEY")
print(f"[DEBUG] MURF_API_KEY loaded in app: {MURF_API_KEY!r}")


def murf_tts(text: str) -> str | None:
    """Text to speech using Murf API. Returns the base64-encoded audio file content."""
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
        # Download the audio file and return base64-encoded content
        audio_res = requests.get(audio_file)
        audio_res.raise_for_status()
        b64_full = base64.b64encode(audio_res.content).decode('utf-8')
        return b64_full
    except Exception as e:
        logger.error(f"MURF TTS Error: {e}")
        return None

def murf_tts_chunked(text: str):
    """
    Fetch the Murf audio URL, download the full audio, and yield base64-encoded file as a single chunk.
    """
    audio_url = murf_tts(text)
    if not audio_url:
        return
    try:
        r = requests.get(audio_url)
        r.raise_for_status()
        b64_full = base64.b64encode(r.content).decode('utf-8')
        yield b64_full
    except Exception as e:
        logger.error(f"Murf TTS chunked fetch error: {e}")
