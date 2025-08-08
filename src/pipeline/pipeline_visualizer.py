#!/usr/bin/env python3
"""
🎨 PIPELINE VISUALIZER - Rich terminal UI for book search pipeline
Real-time monitoring with emojis and beautiful progress indicators
"""
import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.tree import Tree
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))

from pipeline.book_pipeline import BookSearchPipeline, PipelineConfig
from book_sources.base import SearchResult

console = Console()

@dataclass
class PipelineStep:
    """Represents a single step in the pipeline visualization"""
    name: str
    emoji: str
    status: str = "pending"  # pending, running, success, failed, skipped
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    details: str = ""
    metadata: Dict[str, Any] = None

class PipelineVisualizer:
    """
    🎨 Beautiful terminal visualization for the book search pipeline
    
    Features:
    - Real-time progress tracking with emojis
    - Step-by-step breakdown of all operations
    - Color-coded status indicators
    - Performance metrics display
    - Interactive fuzzy input demonstration
    """
    
    def __init__(self, pipeline: BookSearchPipeline):
        self.pipeline = pipeline
        self.console = Console()
        self.steps: List[PipelineStep] = []
        self.current_query = ""
        self.start_time = 0.0
        self.layout = Layout()
        
        # Initialize pipeline steps
        self._initialize_steps()
    
    def _initialize_steps(self):
        """Initialize all possible pipeline steps"""
        self.steps = [
            PipelineStep("input_validation", "🔍", details="Validate search query"),
            PipelineStep("query_normalization", "🤖", details="Claude AI normalization"),
            PipelineStep("chain_optimization", "🎯", details="Language-aware routing"),
            PipelineStep("zlibrary_search", "⚡", details="Z-Library search (Priority 1)"),
            PipelineStep("flibusta_search", "🇷🇺", details="Flibusta search (Priority 2)"),
            PipelineStep("result_compilation", "📊", details="Compile final results"),
        ]
    
    def _create_header(self) -> Panel:
        """Create beautiful header panel"""
        header_text = Text()
        header_text.append("🚀 ", style="bold blue")
        header_text.append("MULTI-SOURCE BOOK SEARCH PIPELINE", style="bold white")
        header_text.append(" 🚀", style="bold blue")
        
        subtitle = Text()
        subtitle.append("Real-time visualization with ", style="dim")
        subtitle.append("Z-Library", style="bold cyan")
        subtitle.append(" → ", style="dim")
        subtitle.append("Flibusta", style="bold red")
        subtitle.append(" fallback", style="dim")
        
        header_content = Align.center(
            Text.assemble(header_text, "\n", subtitle)
        )
        
        return Panel(
            header_content,
            style="bold blue",
            padding=(1, 2)
        )
    
    def _create_query_panel(self) -> Panel:
        """Create query display panel"""
        if not self.current_query:
            content = Text("Waiting for search query...", style="dim italic")
        else:
            content = Text()
            content.append("🔎 Query: ", style="bold")
            content.append(f'"{self.current_query}"', style="bold yellow")
            
            # Add fuzzy input indicator
            if any(char in self.current_query.lower() for char in ['malenkiy', 'hary', 'poter']):
                content.append("\n🌟 ", style="gold1")
                content.append("Fuzzy input detected - AI normalization active", style="gold1")
        
        return Panel(content, title="📝 Search Query", style="green")
    
    def _create_steps_panel(self) -> Panel:
        """Create pipeline steps visualization"""
        tree = Tree("🔄 Pipeline Steps", style="bold")
        
        for step in self.steps:
            # Status styling
            if step.status == "pending":
                status_icon = "⏳"
                style = "dim"
            elif step.status == "running":
                status_icon = "🔄"
                style = "bold yellow"
            elif step.status == "success":
                status_icon = "✅"
                style = "bold green"
            elif step.status == "failed":
                status_icon = "❌"
                style = "bold red"
            elif step.status == "skipped":
                status_icon = "⏭️"
                style = "dim blue"
            else:
                status_icon = "❓"
                style = "dim"
            
            # Create step text
            step_text = Text()
            step_text.append(f"{step.emoji} {step.name.replace('_', ' ').title()}", style=style)
            step_text.append(f" {status_icon}", style=style)
            
            if step.details:
                step_text.append(f"\n   {step.details}", style="dim")
            
            # Add timing info if available
            if step.start_time and step.end_time:
                duration = step.end_time - step.start_time
                step_text.append(f"\n   ⏱️ {duration:.2f}s", style="dim cyan")
            elif step.start_time and step.status == "running":
                current_duration = time.time() - step.start_time
                step_text.append(f"\n   ⏱️ {current_duration:.1f}s...", style="dim yellow")
            
            tree.add(step_text)
        
        return Panel(tree, title="🏗️ Pipeline Progress", style="blue")
    
    def _create_results_panel(self, result: Optional[SearchResult] = None) -> Panel:
        """Create results display panel"""
        if not result:
            content = Text("⏳ Waiting for results...", style="dim italic")
        elif result.found:
            content = Text()
            content.append("🎉 SUCCESS! ", style="bold green")
            content.append(f"Found via {result.source.upper()}\n\n", style="bold cyan")
            
            if result.title:
                content.append("📚 Title: ", style="bold")
                content.append(f"{result.title}\n", style="white")
            
            if result.author:
                content.append("👤 Author: ", style="bold")
                content.append(f"{result.author}\n", style="white")
            
            if hasattr(result, 'download_url') and result.download_url:
                content.append("📥 Download: ", style="bold")
                content.append("Available", style="bold green")
            
            content.append(f"\n⏱️ Response time: {result.response_time:.2f}s", style="dim")
        else:
            content = Text()
            content.append("😞 No results found\n", style="bold red")
            
            if result.metadata and 'sources_tried' in result.metadata:
                sources = result.metadata['sources_tried']
                content.append(f"🔍 Searched: {', '.join(sources)}\n", style="dim")
            
            content.append(f"⏱️ Total time: {result.response_time:.2f}s", style="dim")
        
        return Panel(content, title="📊 Results", style="magenta")
    
    def _create_stats_panel(self) -> Panel:
        """Create pipeline statistics panel"""
        stats = self.pipeline.get_stats()
        
        table = Table(show_header=True, header_style="bold")
        table.add_column("Source", style="cyan")
        table.add_column("Attempts", justify="right")
        table.add_column("Success Rate", justify="right")
        table.add_column("Avg Time", justify="right")
        
        for source, source_stats in stats.get("source_stats", {}).items():
            attempts = source_stats.get("attempts", 0)
            success_rate = source_stats.get("success_rate", 0.0) * 100
            avg_time = source_stats.get("average_response_time", 0.0)
            
            emoji = "⚡" if source == "zlibrary" else "🇷🇺" if source == "flibusta" else "📊"
            
            table.add_row(
                f"{emoji} {source.title()}",
                str(attempts),
                f"{success_rate:.1f}%",
                f"{avg_time:.2f}s"
            )
        
        # Add overall stats
        overall_rate = stats.get("overall_success_rate", 0.0) * 100
        avg_response = stats.get("average_response_time", 0.0)
        
        table.add_row(
            "🎯 Overall",
            str(stats.get("total_searches", 0)),
            f"{overall_rate:.1f}%",
            f"{avg_response:.2f}s",
            style="bold"
        )
        
        return Panel(table, title="📈 Performance Stats", style="yellow")
    
    def _update_step_status(self, step_name: str, status: str, details: str = ""):
        """Update step status and timing"""
        for step in self.steps:
            if step.name == step_name:
                if status == "running" and step.status == "pending":
                    step.start_time = time.time()
                elif status in ["success", "failed"] and step.start_time:
                    step.end_time = time.time()
                
                step.status = status
                if details:
                    step.details = details
                break
    
    async def visualize_search(self, query: str) -> SearchResult:
        """
        🎨 Main visualization method - search with beautiful real-time display
        """
        self.current_query = query
        self.start_time = time.time()
        
        # Reset all steps
        for step in self.steps:
            step.status = "pending"
            step.start_time = None
            step.end_time = None
        
        # Create layout
        self.layout.split_column(
            Layout(name="header", size=4),
            Layout(name="main"),
            Layout(name="stats", size=8)
        )
        
        self.layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        self.layout["left"].split_column(
            Layout(name="query", size=4),
            Layout(name="steps")
        )
        
        result = None
        
        with Live(self.layout, refresh_per_second=4, screen=True):
            # Update initial layout
            self.layout["header"].update(self._create_header())
            self.layout["query"].update(self._create_query_panel())
            self.layout["steps"].update(self._create_steps_panel())
            self.layout["right"].update(self._create_results_panel())
            self.layout["stats"].update(self._create_stats_panel())
            
            # Step 1: Input validation
            await asyncio.sleep(0.5)
            self._update_step_status("input_validation", "running")
            self.layout["steps"].update(self._create_steps_panel())
            
            await asyncio.sleep(1.0)
            try:
                self.pipeline._validate_query(query)
                self._update_step_status("input_validation", "success", "Query validated ✓")
            except ValueError as e:
                self._update_step_status("input_validation", "failed", f"Validation error: {e}")
                self.layout["steps"].update(self._create_steps_panel())
                return SearchResult(found=False, source="pipeline", metadata={"error": str(e)})
            
            self.layout["steps"].update(self._create_steps_panel())
            
            # Step 2: Query normalization
            await asyncio.sleep(0.3)
            self._update_step_status("query_normalization", "running")
            self.layout["steps"].update(self._create_steps_panel())
            
            normalized_queries = await self.pipeline._normalize_query(query)
            await asyncio.sleep(1.5)  # Simulate AI processing time
            
            if len(normalized_queries) > 1:
                norm_details = f"Generated {len(normalized_queries)} variants: {', '.join(normalized_queries[:2])}..."
            else:
                norm_details = "Using original query (normalization disabled/failed)"
            
            self._update_step_status("query_normalization", "success", norm_details)
            self.layout["steps"].update(self._create_steps_panel())
            
            # Step 3: Chain optimization
            await asyncio.sleep(0.3)
            self._update_step_status("chain_optimization", "running")
            self.layout["steps"].update(self._create_steps_panel())
            
            optimal_chain = self.pipeline._get_optimal_chain(query)
            await asyncio.sleep(0.5)
            
            lang_hint = "🇷🇺 Russian detected" if "ru" in str(optimal_chain) else "🇬🇧 Latin text"
            chain_details = f"{lang_hint} → Chain: {' → '.join(optimal_chain)}"
            self._update_step_status("chain_optimization", "success", chain_details)
            self.layout["steps"].update(self._create_steps_panel())
            
            # Step 4 & 5: Source searches
            for source_name in optimal_chain:
                step_name = f"{source_name}_search"
                
                await asyncio.sleep(0.5)
                self._update_step_status(step_name, "running")
                self.layout["steps"].update(self._create_steps_panel())
                
                # Simulate source search with real pipeline call
                if source_name in self.pipeline.sources:
                    source = self.pipeline.sources[source_name]
                    
                    for norm_query in normalized_queries:
                        try:
                            search_result = await self.pipeline._search_with_timeout(source, norm_query)
                            
                            if search_result.found:
                                result = search_result
                                success_details = f"✅ Found: {search_result.title[:30]}..." if search_result.title else "✅ Book found!"
                                self._update_step_status(step_name, "success", success_details)
                                
                                # Skip remaining sources
                                remaining_sources = optimal_chain[optimal_chain.index(source_name)+1:]
                                for skip_source in remaining_sources:
                                    skip_step = f"{skip_source}_search"
                                    self._update_step_status(skip_step, "skipped", "Skipped (already found)")
                                
                                break
                            
                        except Exception as e:
                            continue
                    
                    if not result:
                        fail_details = f"❌ No results found"
                        self._update_step_status(step_name, "failed", fail_details)
                else:
                    self._update_step_status(step_name, "failed", f"❌ Source not available")
                
                self.layout["steps"].update(self._create_steps_panel())
                
                # Update results panel if we found something
                if result:
                    self.layout["right"].update(self._create_results_panel(result))
                    break
            
            # Step 6: Result compilation
            await asyncio.sleep(0.3)
            self._update_step_status("result_compilation", "running")
            self.layout["steps"].update(self._create_steps_panel())
            
            await asyncio.sleep(0.5)
            
            if not result:
                # No results found anywhere
                total_time = time.time() - self.start_time
                result = SearchResult(
                    found=False,
                    source="pipeline",
                    response_time=total_time,
                    metadata={
                        "original_query": query,
                        "normalized_queries": normalized_queries,
                        "sources_tried": optimal_chain,
                        "total_time": total_time
                    }
                )
                self._update_step_status("result_compilation", "failed", "❌ No results from any source")
            else:
                self._update_step_status("result_compilation", "success", "📊 Results compiled successfully")
            
            # Final updates
            self.layout["steps"].update(self._create_steps_panel())
            self.layout["right"].update(self._create_results_panel(result))
            self.layout["stats"].update(self._create_stats_panel())
            
            # Show final result for a few seconds
            await asyncio.sleep(3.0)
        
        return result
    
    def print_summary(self, result: SearchResult):
        """Print beautiful summary after visualization"""
        console.print("\n" + "="*60, style="bold blue")
        console.print("🎯 SEARCH SUMMARY", style="bold white", justify="center")
        console.print("="*60, style="bold blue")
        
        if result.found:
            console.print(Panel(
                f"✅ SUCCESS!\n\n"
                f"📚 Title: {result.title}\n"
                f"👤 Author: {result.author}\n"
                f"🔍 Source: {result.source.upper()}\n"
                f"⏱️ Time: {result.response_time:.2f}s",
                title="🎉 Book Found",
                style="bold green"
            ))
        else:
            console.print(Panel(
                f"😞 No results found\n\n"
                f"🔍 Query: {self.current_query}\n"
                f"⏱️ Total time: {result.response_time:.2f}s\n"
                f"🔗 Sources tried: {len(result.metadata.get('sources_tried', []))}",
                title="❌ Search Failed",
                style="bold red"
            ))

async def demo_fuzzy_search():
    """
    🌟 Interactive demo with fuzzy inputs to showcase pipeline transparency
    """
    console.print(Panel(
        "🚀 FUZZY INPUT PIPELINE DEMONSTRATION\n\n"
        "Watch how the pipeline handles fuzzy/misspelled queries:\n"
        "• Input validation\n"
        "• AI normalization with Claude\n"
        "• Language-aware source routing\n"
        "• Real-time fallback visualization",
        title="🎨 Pipeline Visualizer Demo",
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
    
    # Demo queries with increasing fuzziness
    demo_queries = [
        "1984 Orwell",  # Clean query
        "hary poter filosofer stone",  # Fuzzy English
        "malenkiy prinz",  # Fuzzy Russian transliteration
        "dostoevsky преступление",  # Mixed language
        "voyna i mir tolstoy"  # Russian transliteration
    ]
    
    for i, query in enumerate(demo_queries, 1):
        console.print(f"\n🔄 Demo {i}/{len(demo_queries)}: Testing fuzzy input")
        console.print(f"Query: '{query}'", style="bold yellow")
        
        result = await visualizer.visualize_search(query)
        visualizer.print_summary(result)
        
        if i < len(demo_queries):
            console.print("\n⏳ Next demo in 3 seconds...", style="dim")
            await asyncio.sleep(3)
    
    # Final statistics
    console.print("\n" + "="*60, style="bold cyan")
    console.print("📊 FINAL PIPELINE STATISTICS", style="bold white", justify="center")
    console.print("="*60, style="bold cyan")
    
    stats = pipeline.get_stats()
    stats_table = Table(title="Performance Summary")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="bold white")
    
    stats_table.add_row("Total Searches", str(stats.get("total_searches", 0)))
    stats_table.add_row("Success Rate", f"{stats.get('overall_success_rate', 0) * 100:.1f}%")
    stats_table.add_row("Average Response Time", f"{stats.get('average_response_time', 0):.2f}s")
    
    console.print(stats_table, justify="center")

if __name__ == "__main__":
    console.print("🎨 Starting Pipeline Visualizer Demo...", style="bold green")
    asyncio.run(demo_fuzzy_search())