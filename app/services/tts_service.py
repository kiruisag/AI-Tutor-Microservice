from google.cloud import texttospeech
from app.core.config import settings

class TTSService:
    def __init__(self):
        self.client = texttospeech.TextToSpeechClient.from_service_account_json(
            settings.google_tts_credentials
        )

    async def synthesize(self, text: str) -> bytes:
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", name="en-US-Neural2-J"
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        return response.audio_content