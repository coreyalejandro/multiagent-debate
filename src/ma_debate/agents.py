from __future__ import annotations
import yaml
from dataclasses import dataclass
from typing import Dict, List, Optional

from .llm import LLM

@dataclass
class AgentSpec:
    id: str
    system: str
    style: str = "generalist"

class Agent:
    def __init__(self, spec: AgentSpec, llm: LLM):
        self.spec = spec
        self.llm = llm

    def propose(self, question: str, constraints: Optional[str], temperature: float, max_tokens: int, seed: Optional[int]) -> str:
        msgs = [
            {"role": "system", "content": self.spec.system},
            {"role": "user", "content": f"Question: {question}\nConstraints: {constraints or 'None'}\n\nProduce an initial, high-quality proposal. Use structured reasoning and cite assumptions."}
        ]
        return self.llm.chat(msgs, temperature=temperature, max_tokens=max_tokens, seed=seed)

    def critique(self, opponent_answer: str, temperature: float, max_tokens: int, seed: Optional[int]) -> str:
        msgs = [
            {"role": "system", "content": self.spec.system},
            {"role": "user", "content": f"Opponent's answer:\n{opponent_answer}\n\nCritique this answer: identify flaws, missing evidence, risky assumptions, and constraints violations. Be specific and constructive."}
        ]
        return self.llm.chat(msgs, temperature=temperature, max_tokens=max_tokens, seed=seed)

    def defend(self, own_answer: str, critiques: List[str], temperature: float, max_tokens: int, seed: Optional[int]) -> str:
        joined = "\n- ".join(critiques) if critiques else "None"
        msgs = [
            {"role": "system", "content": self.spec.system},
            {"role": "user", "content": f"Your previous answer:\n{own_answer}\n\nCritiques received:\n- " + joined + "\n\nRevise your answer addressing valid points and strengthening the proposal. Keep what holds, fix what doesn't."}
        ]
        return self.llm.chat(msgs, temperature=temperature, max_tokens=max_tokens, seed=seed)

def load_registry(path: str) -> Dict[str, AgentSpec]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    registry: Dict[str, AgentSpec] = {}
    for a in data.get("agents", []):
        registry[a["id"]] = AgentSpec(id=a["id"], system=a["system"], style=a.get("style","generalist"))
    return registry
