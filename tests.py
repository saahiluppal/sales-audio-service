from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_transcribe_upload():
    response = client.post("/transcribe", files={"file": open("sample.wav","rb")})
    assert response.status_code == 200
    assert "transcript" in response.json()
