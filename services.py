import whisper
from transformers import pipeline
import pyttsx3, tempfile

from dotenv import load_dotenv
from huggingface_hub import login

from pyannote.audio import Pipeline
import os

# Load env
load_dotenv()
hf_token = os.getenv("HF_TOKEN")

# Authenticate with Hugging Face
if hf_token:
    login(token=hf_token)

os.environ["HF_TOKEN"] = hf_token
os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_token  # sometimes required

stt_model = whisper.load_model("base")
sentiment_model = pipeline("sentiment-analysis")
zero_shot = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Pretrained diarization pipeline (requires Hugging Face token)
diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=hf_token)

async def transcribe_audio(file, call_id: str):
    # Save uploaded file to a temp file so Whisper and pyannote can read it
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(file.read())
        tmp.flush()
        tmp_path = tmp.name

    # Step 1: Diarization (who spoke when)
    diarization_result = diarization_pipeline(tmp_path)

    diarization_segments = []
    for turn, _, speaker in diarization_result.itertracks(yield_label=True):
        diarization_segments.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker,
        })

    # Step 2: Transcribe with Whisper
    whisper_result = stt_model.transcribe(tmp_path)
    text = whisper_result["text"]

    # Step 3: Align Whisper segments with speaker segments
    diarization_output = []
    for seg in whisper_result["segments"]:
        start, end, seg_text = seg["start"], seg["end"], seg["text"]

        # Find matching speaker label
        speaker = "unknown"
        for d in diarization_segments:
            if d["start"] <= start and end <= d["end"]:
                speaker = d["speaker"]
                break

        diarization_output.append({
            "speaker": speaker,
            "start": start,
            "end": end,
            "text": seg_text.strip()
        })

    # Step 4: Sentiment on the full text
    sentiment = sentiment_model(text[:512])[0]

    return text, diarization_output, sentiment

def synthesize_speech(text: str):
    engine = pyttsx3.init()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    engine.save_to_file(text, tmp.name)
    engine.runAndWait()
    return tmp.name

def detect_coachable_moment_direct(transcript: str):
    keywords = ["price", "not sure", "concern"]
    for kw in keywords:
        if kw in transcript.lower():
            return f"Coachable moment: {kw} mentioned."
    return "No clear coachable moment."

def detect_coachable_moment(transcript: str):
    candidate_labels = ["customer objection", "buying signal", "greeting", "closing statement", "price", "not sure", "concern"]

    # Split transcript into sentences (naive split by '.')
    sentences = [s.strip() for s in transcript.split(".") if s.strip()]
    best_moment = None

    for sentence in sentences:
        result = zero_shot(sentence, candidate_labels)
        label = result["labels"][0]     # Top predicted label
        score = result["scores"][0]     # Confidence score

        # Focus on meaningful categories with good confidence
        if label in candidate_labels and score > 0.7:
            if not best_moment or score > best_moment["score"]:
                best_moment = {"sentence": sentence, "label": label, "score": score}

    return best_moment if best_moment else {"sentence": "", "label": "none", "score": 0.0}
