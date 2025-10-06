#!/usr/bin/env python3
"""
Launcher script for Multi-Agent Debate UI
Choose between Gradio and Streamlit interfaces
"""

import sys
import subprocess
import argparse


def run_gradio():
    """Launch the Gradio interface"""
    print("🚀 Starting Gradio UI...")
    print("📱 Interface will be available at: http://localhost:7860")
    subprocess.run([sys.executable, "gradio_ui.py"])


def run_streamlit():
    """Launch the Streamlit interface"""
    print("🚀 Starting Streamlit UI...")
    print("📱 Interface will be available at: http://localhost:8501")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_ui.py"])


def main():
    parser = argparse.ArgumentParser(
        description="Launch Multi-Agent Debate UI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_ui.py --gradio     # Launch Gradio interface
  python run_ui.py --streamlit  # Launch Streamlit interface
  python run_ui.py              # Interactive menu
        """
    )
    
    parser.add_argument(
        "--gradio", 
        action="store_true", 
        help="Launch Gradio interface"
    )
    parser.add_argument(
        "--streamlit", 
        action="store_true", 
        help="Launch Streamlit interface"
    )
    
    args = parser.parse_args()
    
    if args.gradio:
        run_gradio()
    elif args.streamlit:
        run_streamlit()
    else:
        # Interactive menu
        print("🗣️ Multi-Agent Debate UI Launcher")
        print("=" * 40)
        print("Choose your preferred interface:")
        print("1. Gradio (Modern, feature-rich)")
        print("2. Streamlit (Simple, clean)")
        print("3. Exit")
        
        while True:
            try:
                choice = input("\nEnter your choice (1-3): ").strip()
                
                if choice == "1":
                    run_gradio()
                    break
                elif choice == "2":
                    run_streamlit()
                    break
                elif choice == "3":
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1, 2, or 3.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break


if __name__ == "__main__":
    main()
