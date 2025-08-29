aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

import assemblyai as aai
import logging
import io
logger = logging.getLogger(__name__)

def transcribe_audio(audio_bytes: io.BytesIO, assembly_api_key: str) -> str | None:
    try:
        aai.settings.api_key = assembly_api_key
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_bytes)
        if transcript.error:
            logger.error(f"AssemblyAI transcription error: {transcript.error}")
            return None
        return transcript.text
    except Exception as e:
        logger.error(f"AssemblyAI STT Error: {e}")
        return None
