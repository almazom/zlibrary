#!/usr/bin/env python3
"""
🎨 INTERACTIVE PIPELINE VISUALIZATION DEMO
Beautiful terminal UI showing all layers of the book search pipeline

Usage:
    python3 demo_pipeline_visual.py                    # Run full demo
    python3 demo_pipeline_visual.py "your query"       # Single query
    python3 demo_pipeline_visual.py --interactive      # Interactive mode
"""
import asyncio
import sys
import argparse
import os

# Add paths for imports
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pipeline.pipeline_visualizer import PipelineVisualizer, demo_fuzzy_search
from pipeline.book_pipeline import BookSearchPipeline, PipelineConfig
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

console = Console()

async def single_query_demo(query: str):
    """Demo with a single query"""
    console.print(Panel(
        f"🔍 Single Query Demonstration\n\n"
        f"Query: '{query}'\n\n"
        f"Watch the pipeline process your search through:\n"
        f"• Input validation\n"
        f"• Claude AI normalization\n"
        f"• Language-aware routing\n"
        f"• Z-Library search (⚡ fast)\n"
        f"• Flibusta fallback (🇷🇺 comprehensive)\n"
        f"• Result compilation",
        title="🎨 Pipeline Visualizer",
        style="bold blue"
    ))
    
    # Initialize pipeline with visual configuration
    config = PipelineConfig(
        fallback_chain=["zlibrary", "flibusta"],
        enable_claude_normalization=True,
        language_aware_routing=True,
        timeout_per_source=30
    )
    
    pipeline = BookSearchPipeline(config)
    visualizer = PipelineVisualizer(pipeline)
    
    # Run visualization
    result = await visualizer.visualize_search(query)
    visualizer.print_summary(result)
    
    return result

async def interactive_mode():
    """Interactive mode for multiple queries"""
    console.print(Panel(
        "🎮 INTERACTIVE PIPELINE VISUALIZATION\n\n"
        "Enter fuzzy/misspelled book queries to see how the pipeline:\n"
        "• Validates and normalizes your input\n"
        "• Routes to the best sources\n" 
        "• Handles fallback scenarios\n"
        "• Provides transparent progress tracking\n\n"
        "Try queries like:\n"
        "• 'hary poter' (fuzzy English)\n"
        "• 'malenkiy prinz' (fuzzy Russian)\n"
        "• 'dostoevsky crime punishment'\n"
        "• 'tolstoy war peace'\n\n"
        "Type 'quit' to exit",
        title="🎨 Interactive Demo",
        style="bold magenta"
    ))
    
    # Initialize pipeline
    config = PipelineConfig(
        fallback_chain=["zlibrary", "flibusta"],
        enable_claude_normalization=True,
        language_aware_routing=True
    )
    
    pipeline = BookSearchPipeline(config)
    visualizer = PipelineVisualizer(pipeline)
    
    query_count = 0
    
    while True:
        try:
            # Get user input
            console.print("\n" + "─" * 60, style="dim")
            query = Prompt.ask(
                "🔍 Enter your book search query",
                default="",
                show_default=False
            ).strip()
            
            if not query or query.lower() in ['quit', 'exit', 'q']:
                break
            
            query_count += 1
            console.print(f"\n🎬 Query #{query_count}: '{query}'", style="bold yellow")
            
            # Run visualization
            result = await visualizer.visualize_search(query)
            visualizer.print_summary(result)
            
            # Show option to continue
            console.print("\n⏳ Ready for next search...", style="dim green")
            
        except KeyboardInterrupt:
            console.print("\n\n👋 Goodbye! Thanks for trying the pipeline visualizer!", style="bold blue")
            break
        except Exception as e:
            console.print(f"\n❌ Error: {e}", style="bold red")
            continue
    
    # Final stats
    if query_count > 0:
        console.print(Panel(
            f"📊 Session Summary\n\n"
            f"• Queries processed: {query_count}\n"
            f"• Pipeline transparency: 100%\n"
            f"• Visual feedback: Real-time\n\n"
            f"Thanks for exploring the pipeline! 🚀",
            title="✨ Session Complete",
            style="bold green"
        ))

def print_help():
    """Print help information"""
    help_text = Text()
    help_text.append("🎨 PIPELINE VISUALIZER - ", style="bold blue")
    help_text.append("Book Search Pipeline Transparency Tool\n\n", style="bold")
    
    help_text.append("FEATURES:\n", style="bold yellow")
    help_text.append("• 🔍 Real-time step visualization\n", style="green")
    help_text.append("• 🤖 Claude AI normalization tracking\n", style="green") 
    help_text.append("• 🌍 Language-aware routing display\n", style="green")
    help_text.append("• ⚡ Z-Library → 🇷🇺 Flibusta fallback\n", style="green")
    help_text.append("• 📊 Performance metrics\n", style="green")
    help_text.append("• 🎨 Beautiful terminal UI\n\n", style="green")
    
    help_text.append("USAGE EXAMPLES:\n", style="bold yellow")
    help_text.append("# Run full demo with fuzzy inputs\n", style="dim")
    help_text.append("python3 demo_pipeline_visual.py\n\n", style="cyan")
    
    help_text.append("# Test single query\n", style="dim") 
    help_text.append("python3 demo_pipeline_visual.py \"hary poter\"\n\n", style="cyan")
    
    help_text.append("# Interactive mode\n", style="dim")
    help_text.append("python3 demo_pipeline_visual.py --interactive\n\n", style="cyan")
    
    help_text.append("FUZZY INPUT EXAMPLES:\n", style="bold yellow")
    help_text.append("• \"hary poter filosofer stone\" → Harry Potter\n", style="blue")
    help_text.append("• \"malenkiy prinz\" → Маленький принц\n", style="blue") 
    help_text.append("• \"dostoevsky преступление\" → Crime and Punishment\n", style="blue")
    help_text.append("• \"voyna i mir tolstoy\" → War and Peace\n", style="blue")
    
    console.print(Panel(help_text, title="📖 Help", style="bold"))

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="🎨 Pipeline Visualizer - Book Search Transparency Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "query", 
        nargs="?", 
        help="Book search query to visualize"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode for multiple queries"
    )
    
    parser.add_argument(
        "--demo", "-d",
        action="store_true", 
        help="Run full fuzzy input demo"
    )
    
    parser.add_argument(
        "--help-extended",
        action="store_true",
        help="Show extended help with examples"
    )
    
    args = parser.parse_args()
    
    # Handle help
    if args.help_extended:
        print_help()
        return
    
    # Handle different modes
    if args.interactive:
        await interactive_mode()
    elif args.demo or not args.query:
        console.print("🌟 Starting full fuzzy input demonstration...", style="bold green")
        await demo_fuzzy_search()
    else:
        await single_query_demo(args.query)
    
    console.print("\n🎨 Pipeline visualization complete! ✨", style="bold blue")

if __name__ == "__main__":
    try:
        # Check for rich dependency
        import rich
        asyncio.run(main())
    except ImportError:
        print("❌ Error: 'rich' library required for visualization")
        print("📦 Install with: pip install rich")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)