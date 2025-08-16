from pydantic import BaseModel
from typing import Optional

class AudioRequest(BaseModel):
    text: Optional[str] = None

class AudioResponse(BaseModel):
    audio_url: Optional[str] = None
    error: Optional[str] = None

class LLMQueryRequest(BaseModel):
    text: Optional[str] = None

class LLMQueryResponse(BaseModel):
    transcription: Optional[str] = None
    llm_response: Optional[str] = None
    audio_url: Optional[str] = None
    error: Optional[str] = None
