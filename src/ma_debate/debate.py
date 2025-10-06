from __future__ import annotations
import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .agents import Agent
from .judge import BaseJudge
from .storage import JSONLRunLogger
from .utils import now_iso

@dataclass
class DebateResult:
    winner_id: str
    final_synthesis: str
    answers: Dict[str, str]
    judge_details: Dict[str, dict]

class Debate:
    def __init__(self, agents: Dict[str, Agent], judge: BaseJudge, logger: JSONLRunLogger):
        self.agents = agents
        self.judge = judge
        self.logger = logger

    async def _propose_round(self, question: str, constraints: Optional[str], temperature: float, max_tokens: int, seed: Optional[int]) -> Dict[str, str]:
        async def run(aid: str, a: Agent) -> Tuple[str, str]:
            ans = a.propose(question, constraints, temperature, max_tokens, seed)
            self.logger.log({"ts": now_iso(), "phase": "propose", "agent": aid, "text": ans})
            return aid, ans
        tasks = [run(aid, a) for aid, a in self.agents.items()]
        results = await asyncio.gather(*tasks)
        return dict(results)

    async def _critique_round(self, answers: Dict[str, str], temperature: float, max_tokens: int, seed: Optional[int]) -> Dict[str, List[str]]:
        critiques: Dict[str, List[str]] = {aid: [] for aid in self.agents}
        for target_id, target_ans in answers.items():
            for aid, a in self.agents.items():
                if aid == target_id:
                    continue
                crit = a.critique(target_ans, temperature, max_tokens, seed)
                critiques[target_id].append(f"{aid}: {crit}")
                self.logger.log({"ts": now_iso(), "phase": "critique", "from": aid, "to": target_id, "text": crit})
        return critiques

    async def _defend_round(self, answers: Dict[str, str], critiques: Dict[str, List[str]], temperature: float, max_tokens: int, seed: Optional[int]) -> Dict[str, str]:
        async def run(aid: str, a: Agent) -> Tuple[str, str]:
            rev = a.defend(answers[aid], critiques[aid], temperature, max_tokens, seed)
            self.logger.log({"ts": now_iso(), "phase": "defend", "agent": aid, "text": rev})
            return aid, rev
        tasks = [run(aid, a) for aid, a in self.agents.items()]
        results = await asyncio.gather(*tasks)
        return dict(results)

    def _synthesize(self, answers: Dict[str, str]) -> str:
        parts = []
        for aid, text in answers.items():
            parts.append(f"### {aid}\n{text}\n")
        return "\n".join(parts)

    async def run(self, *, question: str, constraints: Optional[str], rounds: int, temperature: float, max_tokens: int, seed: Optional[int]):
        self.logger.log({"ts": now_iso(), "event": "start", "question": question, "constraints": constraints, "rounds": rounds})
        answers = await self._propose_round(question, constraints, temperature, max_tokens, seed)
        for _ in range(rounds):
            critiques = await self._critique_round(answers, temperature, max_tokens, seed)
            answers = await self._defend_round(answers, critiques, temperature, max_tokens, seed)
        winner_id, details = self.judge.judge(answers)
        synthesis = self._synthesize(answers)
        self.logger.log({"ts": now_iso(), "event": "end", "winner": winner_id})
        det = {k: {"total": v.total, "per_criterion": v.per_criterion, "verdict": v.verdict} for k, v in details.items()}
        return type("DebateResult", (), {"winner_id": winner_id, "final_synthesis": synthesis, "answers": answers, "judge_details": det})
