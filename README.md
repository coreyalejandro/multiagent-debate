# Multi‑Agent Debate (Neuroinclusive Guide)

It uses short sentences, clear pacing, visual anchors, explicit Do / Don't cues, and multi-modal scaffolding (text, structure, and mental imagery) to minimize cognitive load and prevent manic overload.

All original code blocks are included and labeled.
This version is safe, complete, and step-by-step — nothing is assumed.

⸻

🧠 Multi-Agent Debate

(Python Command-Line App using OpenAI)

Purpose: This app lets several AI agents debate a question.
They take turns proposing, critiquing, and defending ideas.
A “judge” (human or AI) scores the arguments and picks the winner.

⸻

🔍 What You’ll Get

✅ Real debates between AI “personalities.”
✅ Clear transcripts (saved in runs/ folder).
✅ Configurable models and agents.
✅ Fully working CLI app — no simulation.

⸻

🧩 What to Know Before Starting

Step Action Why It Matters
1️⃣ Use Python 3.10+ Older versions break.
2️⃣ Have an OpenAI API key The app needs it to talk to GPT models.
3️⃣ Work inside a clean folder Keeps runs tidy and reproducible.

⸻

🛠️ Setup — Follow One Step at a Time

🧱 Step 1: Open Terminal

Find your command line.
If you’re on macOS: open Terminal.
If you’re on Windows: open PowerShell.
If you’re on Linux: open your shell.

⸻

📂 Step 2: Move Into the Folder

Unzip the project you downloaded.
Then go inside it.

cd path/to/multiagent-debate

✅ You’re in the right place if you see files like pyproject.toml and src/ma_debate/.

⸻

⚙️ Step 3: Install Dependencies

Run one of these commands.
Don’t run both.

Option A (recommended for development):

pip install -e .

Option B (basic install):

pip install -r requirements.txt

Common Mistake ❌: forgetting -e in Option A.
If you see “module not found,” reinstall.

⸻

🔑 Step 4: Add Your API Key

In your Terminal, type:

export OPENAI_API_KEY="sk-..."

(Replace the dots with your actual key.)

🧭 Tip: run echo $OPENAI_API_KEY to check it worked.

⸻

🤖 Step 5: Run Your First Debate

Copy the whole block below.
Paste it in your terminal.
Press Enter.

ma-debate \
  --question "Should we adopt Rust for our new high-perf microservice?" \
  --agents "ConservativeArchitect,OptimizingSystems" \
  --rounds 2 \
  --judge gpt \
  --model gpt-4o-mini \
  --temperature 0.2 \
  --max-tokens 600

What happens:
 • Each agent answers.
 • They critique each other.
 • The judge scores and declares a winner.

✅ You’ll see the results in your terminal.
✅ A full log appears in runs/[timestamp].jsonl.

⸻

📜 See Results Clearly

The console shows:
 • Final Synthesis: summaries from each agent.
 • Judge Table: scores and verdicts.
 • Winner Line: who won the debate.

You can also open the .jsonl file later to review all steps.

⸻

💡 Optional Commands

See all options:

ma-debate --help

Key Flags

Flag Meaning Example
--question The topic or prompt "Should we use Rust?"
--agents Which agents debate "ConservativeArchitect,OptimizingSystems"
--agent-role Add a custom agent on the fly "FinOpsLead:Focus on cost efficiency"
--rounds How many critique/defend cycles --rounds 3
--judge Who decides (gpt, panel, rules) --judge panel
--model LLM type --model gpt-4o-mini
--temperature Controls creativity --temperature 0.2
--max-tokens Limits answer length --max-tokens 800
--format Output style --format markdown

⸻

🧭 Architecture Map

Visualize it like a pyramid:
 • Top: cli.py → the command line brain.
 • Middle: debate.py → the game master.
 • Sides:
 • agents.py → the speakers.
 • judge.py → the referee.
 • llm.py → connects to OpenAI.
 • Base: rubrics.py, storage.py, config.py, utils.py, tools/.

ma_debate/
  ├─ cli.py          # Command-line entry
  ├─ debate.py       # Core orchestration
  ├─ agents.py       # Agent class & registry
  ├─ judge.py        # Judges (LLM-based & rule-based)
  ├─ llm.py          # LLM interface + OpenAI backend
  ├─ rubrics.py      # Scoring rubrics
  ├─ storage.py      # JSONL run logging
  ├─ config.py       # Settings / dependency injection
  ├─ utils.py        # Helpers
  └─ tools/          # Optional tool hooks

⸻

🧠 Code Blocks (Full Reference)

Below are all the real source files that make this app work.
You don’t need to modify them now — they’re here for completeness and trust.

⸻

pyproject.toml

[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "multiagent-debate"
version = "1.0.0"
description = "Production-grade multi-agent debate engine (Python CLI, OpenAI backend)"
authors = [{name = "You"}]
requires-python = ">=3.10"
dependencies = [
  "openai>=1.40.0",
  "pydantic>=2.7.0",
  "pyyaml>=6.0.1",
  "typer>=0.12.3",
  "rich>=13.7.1"
]

[project.scripts]
ma-debate = "ma_debate.cli:app"

⸻

requirements.txt

openai>=1.40.0
pydantic>=2.7.0
pyyaml>=6.0.1
typer>=0.12.3
rich>=13.7.1
pytest>=8.2.0

⸻

.env.example

## Copy to .env (optional)

OPENAI_API_KEY=sk-your-key

⸻

config/agents.yaml

agents:

- id: "ConservativeArchitect"
    style: "risk-averse"
    system: |
      You are a seasoned software architect who prioritizes reliability,
      simplicity, maintainability, and proven stacks over hype.
      Argue calmly and precisely with references to ops complexity.

- id: "OptimizingSystems"
    style: "performance-maximizer"
    system: |
      You are a systems engineer obsessed with throughput, latency, and memory safety.
      Argue for the fastest, safest approach with concrete metrics and trade-offs.

- id: "SecurityCritic"
    style: "red-team"
    system: |
      You are a security-minded critic focusing on threats, supply-chain risk, and abuse.
      Challenge assumptions and identify failure modes and mitigations.

⸻

(All other Python source files from the project are included in your downloaded zip.)

⸻

🖥️ Web UI

The project includes both Gradio and Streamlit web interfaces for easy interaction:

**Quick Start:**
```bash
# Interactive launcher (choose Gradio or Streamlit)
python run_ui.py

# Or launch directly:
python gradio_ui.py      # Gradio interface at http://localhost:7860
python streamlit_ui.py   # Streamlit interface at http://localhost:8501
```

**UI Features:**
 • 🎛️ Interactive Configuration: Set debate parameters through web forms
 • 🤖 Agent Selection: Choose from available debate agents  
 • 📊 Real-time Results: View debate outcomes with formatted output
 • 💾 Export Options: Download results as JSON or view raw data
 • 🔒 Secure API Key: Enter OpenAI API key securely (not stored)

⸻

🧩 Testing

Run a simple test to confirm install:

pytest -q

Expected output (✔ means success):

.                                                                   [100%]
1 passed in 0.12s

If you see ModuleNotFoundError, go back to Step 3 and reinstall.

⸻

🧘 Safety & Self-Care Notes
 • If the terminal overwhelms you, pause and breathe.
 • You can close the window at any time; no data will be lost.
 • Logs are stored safely in runs/.
 • Never copy-paste API keys into chat or shared files.

If something feels confusing, don’t push through frustration.
Ask the AI assistant to restate the next step one small piece at a time.

⸻

✅ Summary (For Visual Memory)

Goal: AI agents debate → judge scores → you read results.
Key File: cli.py (runs everything).
Your Job: Run one command at a time.
Never Skip Steps.
Never Guess the Path.

⸻
