#!/usr/bin/env python3
"""
Gradio UI for Multi-Agent Debate System
"""

import gradio as gr
import asyncio
import os
import json
from typing import Dict, Any

# Import the debate system components
from src.ma_debate.cli import build_agents, llm_factory, judge_factory
from src.ma_debate.debate import Debate
from src.ma_debate.storage import JSONLRunLogger
from src.ma_debate.utils import make_run_id


class DebateUI:
    def __init__(self):
        self.current_result = None
        
    def run_debate(
        self,
        question: str,
        agents: str,
        rounds: int,
        judge_type: str,
        model: str,
        temperature: float,
        max_tokens: int,
        api_key: str
    ) -> tuple[str, str, str]:
        """Run the debate and return formatted results"""
        
        if not question.strip():
            return "❌ Please enter a question for the debate.", "", ""
            
        if not agents.strip():
            return "❌ Please specify at least one agent.", "", ""
            
        if not api_key.strip():
            return "❌ Please enter your OpenAI API key.", "", ""
        
        try:
            # Set the API key
            os.environ["OPENAI_API_KEY"] = api_key
            
            # Parse agents
            agent_ids = [x.strip() for x in agents.split(",") if x.strip()]
            
            # Build agents
            built_agents = build_agents(agent_ids, model, [])
            
            # Create judge
            judge_llm = None
            if judge_type.lower() in ("gpt", "panel"):
                judge_llm = llm_factory("openai", model)
            judge_inst = judge_factory(judge_type, judge_llm)
            
            # Create output directory
            output_dir = "runs"
            os.makedirs(output_dir, exist_ok=True)
            
            # Run debate
            run_id = make_run_id("debate")
            with JSONLRunLogger(output_dir=output_dir, run_id=run_id) as logger:
                debate = Debate(built_agents, judge_inst, logger)
                result = asyncio.run(debate.run(
                    question=question,
                    constraints=None,
                    rounds=rounds,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    seed=None
                ))
            
            self.current_result = result
            
            # Format results for display
            console_output = self._format_console_output(result)
            json_output = json.dumps(result, indent=2)
            summary = self._format_summary(result)
            
            return console_output, json_output, summary
            
        except Exception as e:
            error_msg = f"❌ Error running debate: {str(e)}"
            return error_msg, "", error_msg
    
    def _format_console_output(self, result: Dict[str, Any]) -> str:
        """Format the result for console-like display"""
        output = []
        output.append("🏆 DEBATE RESULTS")
        output.append("=" * 50)
        
        if 'winner' in result:
            output.append(f"🥇 Winner: {result['winner']}")
            output.append("")
        
        if 'answers' in result:
            output.append("📝 Agent Responses:")
            output.append("-" * 30)
            for agent, response in result['answers'].items():
                output.append(f"\n🤖 {agent}:")
                # Truncate very long responses
                if len(response) > 500:
                    response = response[:500] + "... [truncated]"
                output.append(response)
                output.append("")
        
        return "\n".join(output)
    
    def _format_summary(self, result: Dict[str, Any]) -> str:
        """Create a brief summary of the debate"""
        summary = []
        
        if 'winner' in result:
            summary.append(f"🏆 Winner: {result['winner']}")
        
        if 'answers' in result:
            summary.append(f"📊 Participants: {len(result['answers'])} agents")
            summary.append(f"💬 Responses: {len([r for r in result['answers'].values() if r])} submitted")
        
        return "\n".join(summary)


def create_gradio_interface():
    """Create and configure the Gradio interface"""
    
    debate_ui = DebateUI()
    
    with gr.Blocks(
        title="Multi-Agent Debate System",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        .debate-header {
            text-align: center;
            margin-bottom: 20px;
        }
        """
    ) as interface:
        
        gr.Markdown(
            """
            # 🗣️ Multi-Agent Debate System
            
            Engage AI agents in structured debates on any topic. Configure agents, set parameters, and watch them argue their cases!
            """,
            elem_classes=["debate-header"]
        )
        
        with gr.Row():
            with gr.Column(scale=2):
                # Input Section
                gr.Markdown("## ⚙️ Debate Configuration")
                
                question = gr.Textbox(
                    label="🤔 Debate Question",
                    placeholder="What is the best programming language for web development?",
                    lines=2,
                    value="What is the best agentic framework?"
                )
                
                agents = gr.Textbox(
                    label="🤖 Agents (comma-separated)",
                    placeholder="ConservativeArchitect,OptimizingSystems",
                    value="ConservativeArchitect,OptimizingSystems",
                    info="Available: ConservativeArchitect, OptimizingSystems, SecurityCritic"
                )
                
                with gr.Row():
                    rounds = gr.Slider(
                        minimum=1,
                        maximum=5,
                        value=2,
                        step=1,
                        label="🔄 Debate Rounds"
                    )
                    
                    temperature = gr.Slider(
                        minimum=0.0,
                        maximum=1.0,
                        value=0.2,
                        step=0.1,
                        label="🌡️ Temperature"
                    )
                
                with gr.Row():
                    model = gr.Dropdown(
                        choices=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
                        value="gpt-4o-mini",
                        label="🧠 Model"
                    )
                    
                    judge_type = gr.Dropdown(
                        choices=["gpt", "panel", "rules"],
                        value="gpt",
                        label="⚖️ Judge Type"
                    )
                
                max_tokens = gr.Slider(
                    minimum=100,
                    maximum=2000,
                    value=600,
                    step=100,
                    label="📝 Max Tokens per Response"
                )
                
                api_key = gr.Textbox(
                    label="🔑 OpenAI API Key",
                    type="password",
                    placeholder="sk-...",
                    info="Your OpenAI API key (not stored)"
                )
                
                run_button = gr.Button(
                    "🚀 Start Debate",
                    variant="primary",
                    size="lg"
                )
            
            with gr.Column(scale=3):
                # Output Section
                gr.Markdown("## 📊 Debate Results")
                
                with gr.Tabs():
                    with gr.Tab("📋 Summary"):
                        summary_output = gr.Textbox(
                            label="Quick Summary",
                            lines=4,
                            interactive=False
                        )
                    
                    with gr.Tab("💬 Console View"):
                        console_output = gr.Textbox(
                            label="Debate Transcript",
                            lines=20,
                            interactive=False,
                            show_copy_button=True
                        )
                    
                    with gr.Tab("🔧 JSON Data"):
                        json_output = gr.JSON(
                            label="Raw Results"
                        )
        
        # Event handlers
        run_button.click(
            fn=debate_ui.run_debate,
            inputs=[
                question, agents, rounds, judge_type, model,
                temperature, max_tokens, api_key
            ],
            outputs=[console_output, json_output, summary_output]
        )
        
        # Example buttons
        gr.Markdown("## 💡 Example Questions")
        with gr.Row():
            gr.Examples(
                examples=[
                    ["What is the best programming language for AI development?"],
                    ["Should companies prioritize remote work or return to office?"],
                    ["What is the most effective approach to climate change?"],
                    ["Is open source or proprietary software better for enterprise?"]
                ],
                inputs=[question]
            )
    
    return interface


if __name__ == "__main__":
    # Create and launch the interface
    interface = create_gradio_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
