"""Small LLM abstraction with offline deterministic default."""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass


class BaseLLM:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class MockLLM(BaseLLM):
    """Deterministic local LLM placeholder used by tests and demos."""

    def generate(self, prompt: str) -> str:
        preview = " ".join(prompt.strip().split())[:180]
        return f"[mock-llm] Deterministic response based on prompt: {preview}"


@dataclass
class OpenAICompatibleLLM(BaseLLM):
    """Minimal OpenAI-compatible chat completion client.

    This class is intentionally optional. The project default path uses
    deterministic local agents and never requires network access.
    """

    model: str = "gpt-4o-mini"
    api_key: str | None = None
    base_url: str | None = None

    def __post_init__(self) -> None:
        self.api_key = self.api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = (self.base_url or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")

    def generate(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set; use MockLLM for offline mode")
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        }
        request = urllib.request.Request(
            url=f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310 - optional user-configured endpoint
            data = json.loads(response.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]

