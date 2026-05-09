"""
Unified async model client — Anthropic, OpenAI, Google Gemini, Ollama.
Each client returns a normalized ModelResponse.
"""
from __future__ import annotations
import asyncio
import time
from dataclasses import dataclass
from typing import Optional

from loguru import logger


@dataclass
class ModelResponse:
    model: str
    provider: str
    content: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int
    seed: Optional[int]
    temperature: float
    error: Optional[str] = None

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    def to_dict(self) -> dict:
        return {
            "model": self.model,
            "provider": self.provider,
            "content": self.content,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "latency_ms": self.latency_ms,
            "seed": self.seed,
            "temperature": self.temperature,
            "error": self.error,
        }


PROVIDER_MAP = {
    "claude": "anthropic",
    "gpt": "openai",
    "o1": "openai",
    "o3": "openai",
    "gemini": "google",
    "grok": "xai",
    "llama": "ollama",
    "mistral": "ollama",
    "qwen": "ollama",
}


def detect_provider(model_id: str) -> str:
    model_lower = model_id.lower()
    for prefix, provider in PROVIDER_MAP.items():
        if model_lower.startswith(prefix):
            return provider
    return "ollama"


async def call_model(
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    seed: Optional[int] = None,
    api_key: str = "",
) -> ModelResponse:
    """Unified entry point — routes to appropriate provider client."""
    provider = detect_provider(model)
    t0 = time.monotonic()

    try:
        if provider == "anthropic":
            return await _call_anthropic(model, system_prompt, user_prompt, temperature, max_tokens, seed, api_key, t0)
        elif provider == "openai":
            return await _call_openai(model, system_prompt, user_prompt, temperature, max_tokens, seed, api_key, t0)
        elif provider == "google":
            return await _call_google(model, system_prompt, user_prompt, temperature, max_tokens, seed, api_key, t0)
        else:
            return await _call_ollama(model, system_prompt, user_prompt, temperature, max_tokens, seed, t0)
    except Exception as e:
        latency_ms = int((time.monotonic() - t0) * 1000)
        logger.error(f"Model call failed [{provider}/{model}]: {e}")
        return ModelResponse(
            model=model, provider=provider, content="",
            prompt_tokens=0, completion_tokens=0,
            latency_ms=latency_ms, seed=seed, temperature=temperature,
            error=str(e),
        )


async def _call_anthropic(
    model, system_prompt, user_prompt, temperature, max_tokens, seed, api_key, t0
) -> ModelResponse:
    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=api_key)
        kwargs = dict(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        # Anthropic supports top_k for pseudo-determinism but not seed directly
        response = await client.messages.create(**kwargs)
        latency_ms = int((time.monotonic() - t0) * 1000)
        content = response.content[0].text if response.content else ""
        return ModelResponse(
            model=model, provider="anthropic", content=content,
            prompt_tokens=response.usage.input_tokens,
            completion_tokens=response.usage.output_tokens,
            latency_ms=latency_ms, seed=seed, temperature=temperature,
        )
    except ImportError:
        raise RuntimeError("anthropic package not installed. Run: pip install anthropic")


async def _call_openai(
    model, system_prompt, user_prompt, temperature, max_tokens, seed, api_key, t0
) -> ModelResponse:
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=api_key)
        kwargs = dict(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        if seed is not None:
            kwargs["seed"] = seed
        response = await client.chat.completions.create(**kwargs)
        latency_ms = int((time.monotonic() - t0) * 1000)
        content = response.choices[0].message.content or ""
        return ModelResponse(
            model=model, provider="openai", content=content,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            latency_ms=latency_ms, seed=seed, temperature=temperature,
        )
    except ImportError:
        raise RuntimeError("openai package not installed. Run: pip install openai")


async def _call_google(
    model, system_prompt, user_prompt, temperature, max_tokens, seed, api_key, t0
) -> ModelResponse:
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        full_prompt = f"{system_prompt}\n\n{user_prompt}" if system_prompt else user_prompt
        gen_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        model_obj = genai.GenerativeModel(model_name=model, generation_config=gen_config)
        response = await asyncio.to_thread(model_obj.generate_content, full_prompt)
        latency_ms = int((time.monotonic() - t0) * 1000)
        content = response.text if hasattr(response, "text") else ""
        return ModelResponse(
            model=model, provider="google", content=content,
            prompt_tokens=0, completion_tokens=0,
            latency_ms=latency_ms, seed=seed, temperature=temperature,
        )
    except ImportError:
        raise RuntimeError("google-generativeai not installed. Run: pip install google-generativeai")


async def _call_ollama(
    model, system_prompt, user_prompt, temperature, max_tokens, seed, t0
) -> ModelResponse:
    try:
        import httpx
        payload = {
            "model": model,
            "prompt": user_prompt,
            "system": system_prompt,
            "options": {"temperature": temperature, "num_predict": max_tokens},
            "stream": False,
        }
        if seed is not None:
            payload["options"]["seed"] = seed

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post("http://localhost:11434/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()

        latency_ms = int((time.monotonic() - t0) * 1000)
        return ModelResponse(
            model=model, provider="ollama", content=data.get("response", ""),
            prompt_tokens=data.get("prompt_eval_count", 0),
            completion_tokens=data.get("eval_count", 0),
            latency_ms=latency_ms, seed=seed, temperature=temperature,
        )
    except ImportError:
        raise RuntimeError("httpx not installed. Run: pip install httpx")
