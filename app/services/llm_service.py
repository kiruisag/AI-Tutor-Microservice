import logging
import asyncio
from typing import AsyncGenerator, List, Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    STRICT PROVIDER SERVICE
    - Uses ONLY LLM_PROVIDER from .env
    - Falls back to MOCK ONLY when all providers fail
    - Returns structured error reasons for debugging
    """

    def __init__(self):
        self.provider = settings.llm_provider.lower()

        self._openai_client = None
        self._gemini_client = None

        logger.info(f"LLM Service initialized with provider={self.provider}")

    # ----------------------------
    # CLIENTS (LAZY LOADING)
    # ----------------------------
    def _get_openai_client(self):
        if self._openai_client is None:
            from openai import AsyncOpenAI

            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY missing")

            self._openai_client = AsyncOpenAI(
                api_key=settings.openai_api_key
            )

        return self._openai_client

    def _get_gemini_client(self):
        if self._gemini_client is None:
            from google import genai

            if not settings.gemini_api_key:
                raise ValueError("GEMINI_API_KEY missing")

            self._gemini_client = genai.Client(
                api_key=settings.gemini_api_key
            )

        return self._gemini_client

    # ----------------------------
    # PROVIDER CHAIN (STRICT)
    # ----------------------------
    def _get_provider_chain(self) -> List[str]:
        if self.provider == "openai":
            return ["openai", "mock"]

        if self.provider == "gemini":
            return ["gemini", "mock"]

        if self.provider == "vertex":
            return ["gemini", "mock"]

        return ["mock"]

    # ----------------------------
    # OPENAI
    # ----------------------------
    async def _openai_completion(self, messages, **kwargs):
        client = self._get_openai_client()

        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            **kwargs
        )

        return response.choices[0].message.content

    async def _openai_stream(self, messages, temperature, max_tokens, stop):
        client = self._get_openai_client()

        stream = await client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    # ----------------------------
    # GEMINI
    # ----------------------------
    async def _gemini_completion(self, messages, **kwargs):
        client = self._get_gemini_client()

        system_instruction = None
        user_content = messages[-1]["content"]

        for m in messages:
            if m.get("role") == "system":
                system_instruction = m.get("content")

        from google.genai import types

        config = types.GenerateContentConfig(
            system_instruction=system_instruction
        )

        response = await client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_content,
            config=config,
        )

        return response.text

    async def _gemini_stream(self, messages, temperature, max_tokens, stop):
        client = self._get_gemini_client()

        user_content = messages[-1]["content"]

        from google.genai import types

        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            stop_sequences=stop,
        )

        stream = await client.aio.models.generate_content_stream(
            model="gemini-2.0-flash",
            contents=user_content,
            config=config,
        )

        async for chunk in stream:
            if chunk.text:
                yield chunk.text

    # ----------------------------
    # MOCK (FALLBACK ONLY)
    # ----------------------------
    async def _mock_completion(self, messages, reason: Optional[Dict[str, Any]] = None):
        return {
            "answer": "Mock response: AI service unavailable",
            "reason": reason or {
                "error": "All LLM providers failed",
                "hint": "Check API keys, quota, network, or provider config",
                "provider": self.provider
            }
        }

    async def _mock_stream(self, messages, **kwargs):
        yield "Mock streaming response..."

    # ----------------------------
    # SAFE COMPLETION (WITH ERROR REPORTING)
    # ----------------------------
    async def _safe_completion(self, messages, **kwargs):
        providers = self._get_provider_chain()

        last_error = None

        for provider in providers:
            try:
                if provider == "openai":
                    result = await self._openai_completion(messages, **kwargs)
                    return {
                        "answer": result,
                        "provider": "openai",
                        "failed_over": False
                    }

                if provider == "gemini":
                    result = await self._gemini_completion(messages, **kwargs)
                    return {
                        "answer": result,
                        "provider": "gemini",
                        "failed_over": False
                    }

                return await self._mock_completion(messages)

            except Exception as e:
                last_error = {
                    "provider": provider,
                    "error": str(e)
                }

                logger.warning(f"{provider} failed: {e}")
                await asyncio.sleep(0.3)

        # FINAL FALLBACK
        return await self._mock_completion(messages, reason=last_error)

    # ----------------------------
    # SAFE STREAMING
    # ----------------------------
    async def _safe_stream(self, messages, temperature, max_tokens, stop):
        providers = self._get_provider_chain()

        for provider in providers:
            try:
                if provider == "openai":
                    stream = self._openai_stream(messages, temperature, max_tokens, stop)

                elif provider == "gemini":
                    stream = self._gemini_stream(messages, temperature, max_tokens, stop)

                else:
                    stream = self._mock_stream(messages)

                async for chunk in stream:
                    yield chunk

                return

            except Exception as e:
                logger.warning(f"{provider} stream failed: {e}")
                continue

        yield "AI service temporarily unavailable"

    # ----------------------------
    # PUBLIC API
    # ----------------------------
    async def generate_completion(self, messages, **kwargs):
        return await self._safe_completion(messages, **kwargs)

    async def generate_stream(
        self,
        messages,
        temperature=0.7,
        max_tokens=500,
        stop=None
    ) -> AsyncGenerator[str, None]:

        async for chunk in self._safe_stream(messages, temperature, max_tokens, stop):
            yield chunk