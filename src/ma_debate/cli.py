from __future__ import annotations
import os, asyncio
import typer
from typing import List, Optional, Dict
from rich import print as rprint
from rich.table import Table

from .llm import llm_factory
from .agents import load_registry, Agent, AgentSpec
from .judge import judge_factory
from .storage import JSONLRunLogger
from .debate import Debate
from .utils import make_run_id, set_determinism

app = typer.Typer(no_args_is_help=True, add_completion=False)

def build_agents(agent_ids: List[str], llm_model: str, extra_roles: List[str]) -> Dict[str, Agent]:
    reg = load_registry(os.path.join(os.path.dirname(__file__), "config", "agents.yaml"))
    chosen: Dict[str, Agent] = {}
    llm = llm_factory("openai", llm_model)

    for aid in agent_ids:
        spec = reg.get(aid)
        if spec is None:
            raise typer.BadParameter(f"Unknown agent id: {aid}")
        chosen[aid] = Agent(spec, llm)

    for role in extra_roles:
        if ":" not in role:
            raise typer.BadParameter("Each --agent-role must look like 'Name:system prompt text'")
        name, system = role.split(":", 1)
        chosen[name] = Agent(AgentSpec(id=name, system=system.strip()), llm)

    return chosen

@app.command()
def run(
    question: str = typer.Option(..., "--question", "-q", help="Task/question to debate"),
    agents: str = typer.Option("ConservativeArchitect,OptimizingSystems", "--agents", "-a", help="Comma-separated agent IDs (see config/agents.yaml)"),
    agent_role: List[str] = typer.Option([], "--agent-role", help="Extra adhoc roles as 'Name:system prompt'"),
    rounds: int = typer.Option(2, "--rounds", "-r", min=1, max=6, help="Number of critique/defense rounds"),
    judge: str = typer.Option("gpt", "--judge", "-j", help="gpt | panel | rules"),
    model: str = typer.Option("gpt-4o-mini", "--model", "-m", help="LLM model for agents/judge"),
    temperature: float = typer.Option(0.2, "--temperature", "-t", min=0.0, max=2.0),
    max_tokens: int = typer.Option(800, "--max-tokens", "-k", min=64, max=8192),
    seed: Optional[int] = typer.Option(None, "--seed", help="Deterministic seed"),
    constraints: Optional[str] = typer.Option(None, "--constraints", help="Optional constraints/context"),
    output_dir: str = typer.Option("runs", "--output-dir", help="Where to write JSONL transcript"),
    fmt: str = typer.Option("json", "--format", help="Final output format: json | markdown")
):
    set_determinism(seed)

    agent_ids = [x.strip() for x in agents.split(",") if x.strip()]
    built_agents = build_agents(agent_ids, model, agent_role)

    judge_llm = None
    if judge.lower() in ("gpt", "panel"):
        judge_llm = llm_factory("openai", model)

    judge_inst = judge_factory(judge, judge_llm)

    run_id = make_run_id("debate")
    with JSONLRunLogger(output_dir=output_dir, run_id=run_id) as logger:
        debate = Debate(built_agents, judge_inst, logger)
        result = asyncio.run(debate.run(
            question=question,
            constraints=constraints,
            rounds=rounds,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed
        ))

    if fmt == "markdown":
        print("# Final Synthesis\n")
        print(result.final_synthesis)
        print(f"\n**Winner:** {result.winner_id}")
    else:
        table = Table(title="Judge Scores")
        table.add_column("Agent")
        table.add_column("Total")
        table.add_column("Verdict")
        for aid, det in result.judge_details.items():
            table.add_row(aid, f"{det['total']:.2f}", det.get("verdict",""))
        rprint(table)
        rprint({"winner": result.winner_id, "answers": result.answers})

if __name__ == "__main__":
    app()
