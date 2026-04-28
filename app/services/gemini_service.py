import google.generativeai as genai
from typing import AsyncGenerator, List, Dict, Optional
from app.core.config import settings

genai.configure(api_key=settings.gemini_api_key)

class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500,
        stop: Optional[list[str]] = None
    ) -> AsyncGenerator[str, None]:
        # Convert OpenAI-style messages to Gemini format
        gemini_messages = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            gemini_messages.append({"role": role, "parts": [msg["content"]]})
        
        response = await self.model.generate_content_async(
            gemini_messages,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                "stop_sequences": stop or []
            }
        )
        # Note: Gemini doesn't stream tokens in the same way, but returns whole response.
        # For true streaming, you'd need the streaming API (which yields chunks).
        # Simplified: yield whole response as one chunk
        yield response.text

    async def generate_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        gemini_messages = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            gemini_messages.append({"role": role, "parts": [msg["content"]]})
        response = await self.model.generate_content_async(gemini_messages, **kwargs)
        return response.text