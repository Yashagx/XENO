import json
import re
import asyncio
from groq import Groq, AsyncGroq
from app.config import settings
from typing import Any, Optional
import logging
import os

logger = logging.getLogger(__name__)

# Groq async client
_client: Optional[AsyncGroq] = None
_cached_api_key: Optional[str] = None


def get_client() -> AsyncGroq:
    global _client, _cached_api_key
    current_key = os.getenv("GROQ_API_KEY") or settings.GROQ_API_KEY
    # Reset client if API key changed (e.g. loaded from AWS Secrets Manager at startup)
    if _client is None or _cached_api_key != current_key:
        _cached_api_key = current_key
        _client = AsyncGroq(api_key=current_key)
    return _client


async def call_llm(prompt: str, system: str = "", temperature: float = 0.7) -> dict:
    """Call Groq LLM and parse JSON response."""
    try:
        client = get_client()
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = await client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=4096,
            response_format={"type": "json_object"},
        )
        text = response.choices[0].message.content.strip()
        # Strip markdown code blocks if present
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}, response: {text[:500]}")
        return {"error": str(e), "raw": text[:500]}
    except Exception as e:
        logger.error(f"LLM call error: {e}")
        return {"error": str(e)}


async def embed_text(text: str) -> list[float]:
    """
    Groq doesn't provide embeddings — return a simple hash-based pseudo-embedding
    for dev/SQLite mode. In production, replace with OpenAI/Cohere embeddings.
    """
    try:
        import hashlib
        import struct
        # Deterministic 768-dim float vector from text hash (dev fallback)
        h = hashlib.sha256(text.encode()).digest()
        # Repeat hash to fill 768 floats (32 bytes -> 8 floats, need 96 repeats)
        extended = (h * 96)[:768 * 4]
        floats = list(struct.unpack(f'{768}f', extended[:768 * 4]))
        # Normalize to [-1, 1]
        mx = max(abs(f) for f in floats) or 1.0
        return [f / mx for f in floats]
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        return [0.0] * settings.EMBEDDING_DIMENSION
