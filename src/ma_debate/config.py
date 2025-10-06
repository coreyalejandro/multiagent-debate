from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional

class Settings(BaseModel):
    model: str = Field(default="gpt-4o-mini")
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: int = Field(default=800, ge=64, le=8192)
    seed: Optional[int] = None
    rounds: int = Field(default=2, ge=1, le=6)
    judge: str = Field(default="gpt")  # gpt | panel | rules
    output_dir: str = Field(default="runs")
    format: str = Field(default="json")  # json | markdown
    tools: List[str] = Field(default_factory=list)
