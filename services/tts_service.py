
import requests
import logging
import base64
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def murf_tts(text: str, murf_api_key: str) -> str | None:
    """Text to speech using Murf API. Returns the base64-encoded audio file content."""
    if not murf_api_key:
        logger.error("MURF Error: API key not found")
        return None
    headers = {"api-key": murf_api_key}
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
def murf_tts_chunked(text: str, murf_api_key: str):
    """
    Fetch the Murf audio URL, download the full audio, and yield base64-encoded file as a single chunk.
    """
    audio_url = murf_tts(text, murf_api_key)
    if not audio_url:
        return
    try:
        r = requests.get(audio_url)
        r.raise_for_status()
        b64_full = base64.b64encode(r.content).decode('utf-8')
        yield b64_full
    except Exception as e:
        logger.error(f"Murf TTS chunked fetch error: {e}")
