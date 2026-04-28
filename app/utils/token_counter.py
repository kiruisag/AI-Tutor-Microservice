# app/utils/token_counter.py
"""
Token counting utilities for LLM quota estimation.
"""
from typing import Optional

try:
    import tiktoken
except ImportError:
    tiktoken = None

# Estimate token count for a given text (OpenAI/Gemini compatible)
def count_tokens(text: str, model: Optional[str] = None) -> int:
    if tiktoken and model:
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))
    # Fallback: rough estimate (1 token ≈ 4 chars)
    return max(1, len(text) // 4)

# Cache token counts (simple in-memory cache for demonstration)
_token_cache = {}

def cached_count_tokens(text: str, model: Optional[str] = None) -> int:
    key = (text, model)
    if key in _token_cache:
        return _token_cache[key]
    count = count_tokens(text, model)
    _token_cache[key] = count
    return count
