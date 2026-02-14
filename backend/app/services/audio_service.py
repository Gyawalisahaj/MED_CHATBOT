import os
import edge_tts
import asyncio
from groq import Groq
from app.core.config import settings

class AudioService:
    def __init__(self):
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
        self.voice = "en-US-AndrewNeural" # High-quality male neural voice

    async def transcribe(self, audio_bytes):
        """Transcribe mic input to text for FREE."""
        temp_file = "temp_mic.wav"
        with open(temp_file, "wb") as f:
            f.write(audio_bytes)
        
        with open(temp_file, "rb") as file:
            transcription = self.groq_client.audio.transcriptions.create(
                file=(temp_file, file.read()),
                model="whisper-large-v3-turbo",
                response_format="text"
            )
        os.remove(temp_file)
        return transcription

    async def generate_speech(self, text: str) -> bytes:
        """Generate audio bytes for the 'Read Aloud' button."""
        communicate = edge_tts.Communicate(text, self.voice)
        # Use a temporary buffer or file
        temp_out = "temp_speech.mp3"
        await communicate.save(temp_out)
        with open(temp_out, "rb") as f:
            audio_data = f.read()
        os.remove(temp_out)
        return audio_data