FROM python:3.10-slim

WORKDIR /app

# Install system dependencies: ffmpeg + espeak-ng
RUN apt-get update && apt-get install -y ffmpeg espeak-ng && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
