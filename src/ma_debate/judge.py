from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Dict, Tuple, Any

from .llm import LLM
from .rubrics import Rubric, DEFAULT_RUBRIC, rubric_instructions

@dataclass
class Judgement:
    total: float
    per_criterion: Dict[str, Dict[str, Any]]  # name -> {score, weight, note}
    verdict: str

class BaseJudge:
    def judge(self, answers: Dict[str, str]) -> Tuple[str, Dict[str, "Judgement"]]:
        """Return (winner_id, details per agent)."""
        raise NotImplementedError

class GPTJudge(BaseJudge):
    def __init__(self, llm: LLM, rubric: Rubric = DEFAULT_RUBRIC):
        self.llm = llm
        self.rubric = rubric

    def _score_one(self, agent_id: str, answer: str) -> Judgement:
        prompt = f"{rubric_instructions(self.rubric)}\n\nSubmission from {agent_id}:\n{answer}\n"
        resp = self.llm.chat(
            messages=[
                {"role": "system", "content": "You are a strict but fair debate judge."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=600,
            seed=None
        )
        try:
            start = resp.find("{")
            end = resp.rfind("}")
            data = json.loads(resp[start:end+1])
        except Exception:
            return Judgement(total=0.0, per_criterion={}, verdict="Parsing failed")
        total = 0.0
        per = {}
        for crit, weight in self.rubric.criteria.items():
            info = data.get(crit, {})
            score = float(info.get("score", 0.0))
            note = info.get("note", "")
            per[crit] = {"score": score, "weight": weight, "note": note}
            total += score * weight
        verdict = data.get("verdict", "")
        return Judgement(total=total, per_criterion=per, verdict=verdict)

    def judge(self, answers: Dict[str, str]) -> Tuple[str, Dict[str, Judgement]]:
        details = {aid: self._score_one(aid, ans) for aid, ans in answers.items()}
        winner = max(details.items(), key=lambda kv: kv[1].total)[0]
        return winner, details

class PanelJudge(BaseJudge):
    def __init__(self, llm: LLM, rubric: Rubric = DEFAULT_RUBRIC, n: int = 3):
        self.llm = llm
        self.rubric = rubric
        self.n = n

    def judge(self, answers: Dict[str, str]) -> Tuple[str, Dict[str, Judgement]]:
        members = [GPTJudge(self.llm, self.rubric) for _ in range(self.n)]
        panels = []
        for m in members:
            w, d = m.judge(answers)
            panels.append((w, d))
        agg: Dict[str, float] = {aid: 0.0 for aid in answers}
        for _, d in panels:
            for aid, j in d.items():
                agg[aid] += j.total
        winner = max(agg.items(), key=lambda kv: kv[1])[0]
        return winner, panels[0][1]

class RulesJudge(BaseJudge):
    def __init__(self):
        pass

    def _score(self, text: str) -> float:
        score = 0.0
        score += text.count("\n- ") * 1.0
        if "##" in text or "###" in text:
            score += 1.0
        for kw in ["risk", "mitigat", "trade-off", "constraint", "latency", "throughput", "security", "safety"]:
            if kw in text.lower():
                score += 1.5
        if len(text) > 3000:
            score -= 2.0
        return score

    def judge(self, answers: Dict[str, str]) -> Tuple[str, Dict[str, Judgement]]:
        details = {}
        for aid, ans in answers.items():
            s = self._score(ans)
            details[aid] = Judgement(total=s, per_criterion={}, verdict="Heuristic score")
        winner = max(details.items(), key=lambda kv: kv[1].total)[0]
        return winner, details

def judge_factory(kind: str, llm: LLM | None) -> BaseJudge:
    k = (kind or "gpt").lower()
    if k == "gpt":
        assert llm is not None, "LLM required for GPT judge"
        return GPTJudge(llm)
    if k == "panel":
        assert llm is not None, "LLM required for Panel judge"
        return PanelJudge(llm)
    if k == "rules":
        return RulesJudge()
    raise ValueError(f"Unknown judge kind: {kind}")
