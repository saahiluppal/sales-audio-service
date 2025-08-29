import whisper
from transformers import pipeline
import pyttsx3, tempfile

stt_model = whisper.load_model("base")
sentiment_model = pipeline("sentiment-analysis")
zero_shot = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

async def transcribe_audio(file, call_id: str):
    # Save uploaded file to a temp file so Whisper can read it
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(file.read())
        tmp.flush()
        tmp_path = tmp.name

    print(tmp_path)
    result = stt_model.transcribe(tmp_path)
    text = result["text"]

    diarization = [{"speaker": "agent", "text": text}]  # Fake diarization for MVP
    sentiment = sentiment_model(text[:512])[0]
    return text, diarization, sentiment

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
