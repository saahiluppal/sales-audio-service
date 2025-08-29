from pydantic import BaseModel
from typing import List, Dict

class TranscribeResponse(BaseModel):
    call_id: str
    transcript: str
    diarization: List[Dict]
    sentiment: Dict

class SpeakRequest(BaseModel):
    text: str
