from __future__ import annotations
import os
from typing import List, Dict, Optional, Protocol

class LLM(Protocol):
    def chat(self, messages: List[Dict[str, str]], *, temperature: float, max_tokens: int, seed: Optional[int] = None) -> str: ...

class OpenAIChat(LLM):
    def __init__(self, model: str = "gpt-4o-mini"):
        from openai import OpenAI  # lazy import
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    def chat(self, messages: List[Dict[str, str]], *, temperature: float, max_tokens: int, seed: Optional[int] = None) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed
        )
        return resp.choices[0].message.content or ""

def llm_factory(backend: str | None, model: str) -> LLM:
    backend = (backend or "openai").lower()
    if backend == "openai":
        return OpenAIChat(model=model)
    raise ValueError(f"Unknown LLM backend: {backend}")
