#!/usr/bin/env python3
"""
Streamlit UI for Multi-Agent Debate System
"""

import streamlit as st
import asyncio
import os
from typing import Dict, Any

# Import the debate system components
from src.ma_debate.cli import build_agents, llm_factory, judge_factory
from src.ma_debate.debate import Debate
from src.ma_debate.storage import JSONLRunLogger, make_run_id


def run_debate(
    question: str,
    agents: str,
    rounds: int,
    judge_type: str,
    model: str,
    temperature: float,
    max_tokens: int,
    api_key: str
) -> Dict[str, Any]:
    """Run the debate and return results"""
    
    if not question.strip():
        st.error("Please enter a question for the debate.")
        return {}
        
    if not agents.strip():
        st.error("Please specify at least one agent.")
        return {}
        
    if not api_key.strip():
        st.error("Please enter your OpenAI API key.")
        return {}
    
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
        
        return result
        
    except Exception as e:
        st.error(f"Error running debate: {str(e)}")
        return {}


def display_results(result: Dict[str, Any]):
    """Display debate results in Streamlit"""
    
    if not result:
        return
    
    st.success("✅ Debate completed successfully!")
    
    # Winner section
    if 'winner' in result:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"### 🏆 Winner: {result['winner']}")
    
    # Agent responses
    if 'answers' in result:
        st.markdown("### 🤖 Agent Responses")
        
        for agent, response in result['answers'].items():
            with st.expander(f"Agent: {agent}", expanded=True):
                st.markdown(response)
    
    # JSON data
    if st.checkbox("Show raw JSON data"):
        st.json(result)


def main():
    """Main Streamlit app"""
    
    # Page configuration
    st.set_page_config(
        page_title="Multi-Agent Debate System",
        page_icon="🗣️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Title and description
    st.markdown("# 🗣️ Multi-Agent Debate System")
    st.markdown("Engage AI agents in structured debates on any topic. Configure agents, set parameters, and watch them argue their cases!")
    
    # Sidebar for configuration
    with st.sidebar:
        st.markdown("## ⚙️ Debate Configuration")
        
        # API Key
        api_key = st.text_input(
            "🔑 OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="Your OpenAI API key (not stored)"
        )
        
        # Question
        question = st.text_area(
            "🤔 Debate Question",
            value="What is the best agentic framework?",
            height=100,
            help="The question that agents will debate about"
        )
        
        # Agents
        agents = st.text_input(
            "🤖 Agents (comma-separated)",
            value="ConservativeArchitect,OptimizingSystems",
            help="Available: ConservativeArchitect, OptimizingSystems, SecurityCritic"
        )
        
        # Parameters
        col1, col2 = st.columns(2)
        with col1:
            rounds = st.slider("🔄 Rounds", 1, 5, 2)
            temperature = st.slider("🌡️ Temperature", 0.0, 1.0, 0.2, 0.1)
        
        with col2:
            model = st.selectbox(
                "🧠 Model",
                ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
                index=0
            )
            judge_type = st.selectbox(
                "⚖️ Judge Type",
                ["gpt", "panel", "rules"],
                index=0
            )
        
        max_tokens = st.slider("📝 Max Tokens", 100, 2000, 600, 100)
        
        # Run button
        run_button = st.button(
            "🚀 Start Debate",
            type="primary",
            use_container_width=True
        )
    
    # Main content area
    if run_button:
        with st.spinner("🤖 Running debate... This may take a moment."):
            result = run_debate(
                question=question,
                agents=agents,
                rounds=rounds,
                judge_type=judge_type,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key
            )
            
            if result:
                display_results(result)
    
    # Example questions section
    st.markdown("---")
    st.markdown("## 💡 Example Questions")
    
    examples = [
        "What is the best programming language for AI development?",
        "Should companies prioritize remote work or return to office?",
        "What is the most effective approach to climate change?",
        "Is open source or proprietary software better for enterprise?",
        "What is the future of artificial intelligence in healthcare?"
    ]
    
    cols = st.columns(len(examples))
    for i, example in enumerate(examples):
        with cols[i]:
            if st.button(f"Example {i+1}", help=example, use_container_width=True):
                st.session_state.example_question = example
                st.rerun()
    
    # Handle example selection
    if hasattr(st.session_state, 'example_question'):
        st.text_area("Selected example:", value=st.session_state.example_question, disabled=True)
        if st.button("Use this question"):
            st.session_state.question = st.session_state.example_question
            del st.session_state.example_question
            st.rerun()
    
    # Instructions
    with st.expander("📖 How to Use"):
        st.markdown("""
        ### Getting Started
        
        1. **Enter your OpenAI API key** in the sidebar
        2. **Write a debate question** or choose from examples
        3. **Select agents** to participate (comma-separated)
        4. **Adjust parameters** like rounds, temperature, and model
        5. **Click "Start Debate"** and wait for results
        
        ### Available Agents
        
        - **ConservativeArchitect**: Prioritizes reliability, simplicity, and proven technologies
        - **OptimizingSystems**: Focuses on performance, throughput, and memory safety
        - **SecurityCritic**: Emphasizes security, threats, and risk assessment
        
        ### Tips
        
        - Use specific, debatable questions for best results
        - More rounds = deeper analysis but longer runtime
        - Lower temperature = more focused responses
        - Higher max tokens = longer, more detailed responses
        """)


if __name__ == "__main__":
    main()
