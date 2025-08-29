from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from models import TranscribeResponse, SpeakRequest
from services import transcribe_audio, synthesize_speech, detect_coachable_moment
from db import save_transcription, get_transcription
from db import list_call_ids
import uuid, os

app = FastAPI()

@app.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(file: UploadFile = File(...)):
    call_id = str(uuid.uuid4())
    text, diarization, sentiment = await transcribe_audio(file.file, call_id)
    save_transcription(call_id, text, diarization, sentiment)
    return {"call_id": call_id, "transcript": text, "diarization": diarization, "sentiment": sentiment}

@app.post("/speak")
async def speak(req: SpeakRequest):
    output_path = synthesize_speech(req.text)
    return FileResponse(output_path, media_type="audio/wav", filename="tts.wav")

# @app.post("/replay")
# async def replay(call_id: str):
#     transcript = get_transcription(call_id)
#     moment = detect_coachable_moment(transcript)
#     audio = synthesize_speech(moment)
#     return FileResponse(audio, media_type="audio/wav", filename="moment.wav")

@app.post("/replay")
async def replay(call_id: str):
    transcript = get_transcription(call_id)
    moment = detect_coachable_moment(transcript)
    if moment["label"] == "none":
        return JSONResponse({"message": "No clear coachable moment detected"})
    audio = synthesize_speech(moment["sentence"])
    return FileResponse(audio, media_type="audio/wav", filename="moment.wav")

@app.get("/calls")
def get_all_call_ids():
    """
    Returns a list of all stored call IDs.
    """
    return {"call_ids": list_call_ids()}