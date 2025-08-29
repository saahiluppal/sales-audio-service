# Sales Call Analytics Microservice

A modular **Python microservice** for analyzing sales-call audio snippets.
The system provides:

* **Speech-to-Text (STT)** transcription with **speaker diarization**.
* **Sentiment analysis** of utterances.
* **Text-to-Speech (TTS)** synthesis.
* Detection and **replay of coachable moments**.
* RESTful API built on **FastAPI**.
* Persistent storage in **SQLite**.
* **Dockerized deployment**.

---

## Demo & Samples

- **Sample audio file**: [audio.wav](./assets/audio.wav)  
- **Video demo (prototype in action)**: [demo.mp4](./assets/ScreenRecordDemo.mp4)

---

## 🚀 Features Implemented

1. **Transcription**

   * Upload audio (WAV/MP3).
   * Returns transcript, diarization (who spoke & when), and sentiment.

2. **Text-to-Speech**

   * Input text → synthesized audio (WAV).

3. **Coachable Moments**

   * Detects objections, buying signals, or concerns using zero-shot classification.
   * Replay specific moments via TTS.

4. **Data Storage**

   * Persists transcripts, diarization, and sentiment in **SQLite**.
   * Query stored call IDs.

5. **Dockerized Deployment**

   * Dockerfile included for reproducible builds.

---

## 🛠️ Tech Stack

* **FastAPI** – REST API framework
* **Whisper** – Speech-to-Text (STT)
* **Pyannote** – Speaker diarization
* **Hugging Face Transformers** – Sentiment & zero-shot classification
* **pyttsx3** – Text-to-Speech
* **SQLAlchemy + SQLite** – Persistent storage
* **Docker** – Containerization

---

## 📦 Setup & Installation

### 1. Clone Repo

```bash
git clone https://github.com/<your-username>/sales-call-microservice.git
cd sales-call-microservice
```

### 2. Environment Setup

* Create a `.env` file in the root directory:

```env
HF_TOKEN=your_huggingface_token
```

* Install dependencies (if running locally):

```bash
pip install -r requirements.txt
```

### 3. Run with Docker

```bash
docker build -t sales-call-service .
docker run -p 8000:8000 --env-file .env sales-call-service
```

API will be available at:
👉 `http://localhost:8000`

Interactive docs:
👉 `http://localhost:8000/docs`

---

## 🎤 API Endpoints

### 1. **Transcribe Audio**

```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@sample.wav"
```

**Response:**

```json
{
  "call_id": "123e4567-e89b-12d3-a456-426614174000",
  "transcript": "Hello, thanks for calling...",
  "diarization": [
    {"speaker": "SPEAKER_0", "start": 0.0, "end": 4.2, "text": "Hello"},
    {"speaker": "SPEAKER_1", "start": 4.3, "end": 7.5, "text": "I’m not sure about the price"}
  ],
  "sentiment": {"label": "NEGATIVE", "score": 0.91}
}
```

### 2. **Text-to-Speech**

```bash
curl -X POST "http://localhost:8000/speak" \
  -H "Content-Type: application/json" \
  -d '{"text": "Let us move forward with this plan."}' \
  --output tts.wav
```

### 3. **Replay Coachable Moment**

```bash
curl -X POST "http://localhost:8000/replay?call_id=<call_id>" \
  --output moment.wav
```

If no coachable moment is detected:

```json
{ "message": "No clear coachable moment detected" }
```

### 4. **List Stored Calls**

```bash
curl http://localhost:8000/calls
```

**Response:**

```json
{ "call_ids": ["abc-123", "def-456"] }
```

---

## 🏗️ Architecture

* **API Layer (FastAPI):** Exposes `/transcribe`, `/speak`, `/replay`, `/calls`.
* **Audio Processing Service:** Whisper for STT, Pyannote for diarization, Hugging Face for sentiment & zero-shot coachable moment detection.
* **Data Layer (SQLite + SQLAlchemy):** Persists transcripts, diarization, and sentiment.

---

## 📄 Design Brief

The system is structured into modular components **API layer, audio processing service, and persistence layer** to ensure separation of concerns.
**Horizontal scalability** is possible as the service is stateless and containerized. With a queue (Celery/RabbitMQ), it could handle concurrent audio clips.
**Fault tolerance** is addressed by temporary file handling and database transactions.

---
