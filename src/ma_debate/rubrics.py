from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

@dataclass
class Rubric:
    name: str
    criteria: Dict[str, int]  # criterion -> weight

DEFAULT_RUBRIC = Rubric(
    name="GeneralReasoningV1",
    criteria={
        "soundness": 3,
        "evidence": 2,
        "constraints": 2,
        "safety": 1,
        "clarity": 1
    }
)

def rubric_instructions(r: Rubric) -> str:
    desc = "\n".join([f"- {k}: weight {w}" for k, w in r.criteria.items()])
    return f"You are a judge. Score each submission 0-10 per criterion, multiply by weight, sum to total. Criteria:\n{desc}\nRespond as JSON with per-criterion scores and brief justifications, plus a one-sentence verdict."
