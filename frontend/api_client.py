import requests
from typing import List, Dict

class MedicalChatAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def send_message(self, message: str, history: List[Dict[str, str]]) -> Dict:
        """Sends a text query to the RAG backend."""
        payload = {"message": message, "history": history}
        response = requests.post(f"{self.base_url}/api/v1/chat/query", json=payload, timeout=60)
        response.raise_for_status()
        return response.json()

    def transcribe_audio(self, audio_bytes: bytes) -> str:
        """Sends microphone data to Groq Whisper for FREE transcription."""
        files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
        response = requests.post(f"{self.base_url}/api/v1/chat/transcribe", files=files, timeout=30)
        response.raise_for_status()
        return response.json().get("text", "")

    def get_text_to_speech(self, text: str) -> str:
        """Requests a Base64 MP3 of the text using Edge-TTS (Free)."""
        payload = {"text": text}
        response = requests.post(f"{self.base_url}/api/v1/chat/text-to-speech", json=payload, timeout=30)
        response.raise_for_status()
        return response.json().get("audio_base64", "")