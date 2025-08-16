#!/usr/bin/env python3
"""
🎨 SIMPLE VISUAL PIPELINE DEMO
Demonstrates all pipeline steps without requiring real authentication
"""
import asyncio
import time
import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.layout import Layout

# Add paths for imports
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

console = Console()

class SimpleVisualDemo:
    """Simple visual demonstration of pipeline steps"""
    
    def __init__(self, query: str):
        self.query = query
        self.steps = [
            {"name": "🔍 Input Validation", "status": "pending", "time": 0.5},
            {"name": "🤖 Claude Normalization", "status": "pending", "time": 1.5},
            {"name": "🎯 Language Detection", "status": "pending", "time": 0.3},
            {"name": "⚡ Z-Library Search", "status": "pending", "time": 2.0},
            {"name": "🇷🇺 Flibusta Fallback", "status": "pending", "time": 3.0},
            {"name": "📊 Result Compilation", "status": "pending", "time": 0.5}
        ]
        
    def create_header(self):
        """Create demo header"""
        return Panel(
            f"🎨 PIPELINE VISUALIZATION DEMO\n\nQuery: '{self.query}'\nShowing: All pipeline layers with real-time progress",
            style="bold blue",
            padding=(1, 2)
        )
    
    def create_steps_display(self):
        """Create steps progress display"""
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Step", style="white")
        table.add_column("Status", justify="center")
        table.add_column("Details", style="dim")
        
        for step in self.steps:
            # Status emoji and style
            if step["status"] == "pending":
                status_icon = "⏳"
                style = "dim"
            elif step["status"] == "running":
                status_icon = "🔄"
                style = "bold yellow"
            elif step["status"] == "success":
                status_icon = "✅"
                style = "bold green"
            elif step["status"] == "failed":
                status_icon = "❌"
                style = "bold red"
            else:
                status_icon = "❓"
                style = "dim"
            
            # Add timing if available
            details = step.get("details", "")
            if step.get("duration"):
                details += f" ({step['duration']:.2f}s)"
            
            table.add_row(
                step["name"],
                status_icon,
                details,
                style=style
            )
        
        return Panel(table, title="📋 Pipeline Progress", style="green")
    
    def simulate_normalization(self, query):
        """Simulate Claude normalization"""
        normalizations = {
            "hary poter": ["Harry Potter", "Гарри Поттер"],
            "filosofer stone": ["Philosopher's Stone", "философский камень"],
            "malenkiy prinz": ["The Little Prince", "Маленький принц"],
            "dostoevsky": ["Dostoevsky", "Достоевский"],
            "voyna i mir": ["War and Peace", "Война и мир"],
            "tolken": ["Tolkien", "Толкиен"],
            "shakesbeer": ["Shakespeare", "Шекспир"]
        }
        
        query_lower = query.lower()
        normalized = [query]  # Original
        
        for key, variants in normalizations.items():
            if key in query_lower:
                normalized.extend(variants)
                break
        
        return normalized[:3]  # Limit to 3 variants
    
    def detect_language(self, query):
        """Simple language detection"""
        import re
        cyrillic = len(re.findall(r'[а-яёА-ЯЁ]', query))
        latin = len(re.findall(r'[a-zA-Z]', query))
        
        if cyrillic > latin:
            return "ru", "🇷🇺 Russian detected → Flibusta priority"
        elif latin > cyrillic:
            return "en", "🇬🇧 English detected → Z-Library priority"
        else:
            return "mixed", "🌍 Mixed language → Standard chain"
    
    def simulate_search(self, source, query, normalized_queries):
        """Simulate book search"""
        # Demo book database
        books = {
            "harry potter": {"title": "Harry Potter and the Philosopher's Stone", "author": "J.K. Rowling", "source": "zlibrary"},
            "hary poter": {"title": "Harry Potter and the Philosopher's Stone", "author": "J.K. Rowling", "source": "zlibrary"},
            "malenkiy prinz": {"title": "Маленький принц", "author": "Антуан де Сент-Экзюпери", "source": "flibusta"},
            "little prince": {"title": "The Little Prince", "author": "Antoine de Saint-Exupéry", "source": "zlibrary"},
            "dostoevsky": {"title": "Crime and Punishment", "author": "Fyodor Dostoevsky", "source": "zlibrary"},
            "1984": {"title": "1984", "author": "George Orwell", "source": "zlibrary"},
            "orwell": {"title": "1984", "author": "George Orwell", "source": "zlibrary"},
            "tolkien": {"title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "source": "zlibrary"},
            "tolken": {"title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "source": "zlibrary"},
            "shakespeare": {"title": "Hamlet", "author": "William Shakespeare", "source": "zlibrary"},
            "shakesbeer": {"title": "Hamlet", "author": "William Shakespeare", "source": "zlibrary"}
        }
        
        # Try to find book
        for norm_query in normalized_queries:
            query_key = norm_query.lower()
            for book_key, book_data in books.items():
                if book_key in query_key or any(word in query_key for word in book_key.split()):
                    if book_data["source"] == source or source == "flibusta":  # Flibusta can find most books
                        return book_data
        
        return None
    
    async def run_demo(self):
        """Run the visual demo"""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=6),
            Layout(name="steps")
        )
        
        with Live(layout, refresh_per_second=4, screen=True):
            # Initialize display
            layout["header"].update(self.create_header())
            layout["steps"].update(self.create_steps_display())
            
            # Step 1: Input Validation
            self.steps[0]["status"] = "running"
            self.steps[0]["details"] = f"Validating '{self.query}'"
            layout["steps"].update(self.create_steps_display())
            await asyncio.sleep(self.steps[0]["time"])
            
            self.steps[0]["status"] = "success"
            self.steps[0]["details"] = "✓ Query validated and sanitized"
            self.steps[0]["duration"] = self.steps[0]["time"]
            layout["steps"].update(self.create_steps_display())
            
            # Step 2: Claude Normalization
            self.steps[1]["status"] = "running"
            self.steps[1]["details"] = "Processing fuzzy input with AI..."
            layout["steps"].update(self.create_steps_display())
            await asyncio.sleep(self.steps[1]["time"])
            
            normalized_queries = self.simulate_normalization(self.query)
            self.steps[1]["status"] = "success"
            self.steps[1]["details"] = f"✓ Generated {len(normalized_queries)} variants: {', '.join(normalized_queries[:2])}..."
            self.steps[1]["duration"] = self.steps[1]["time"]
            layout["steps"].update(self.create_steps_display())
            
            # Step 3: Language Detection
            self.steps[2]["status"] = "running"
            self.steps[2]["details"] = "Analyzing query language..."
            layout["steps"].update(self.create_steps_display())
            await asyncio.sleep(self.steps[2]["time"])
            
            lang, lang_desc = self.detect_language(self.query)
            self.steps[2]["status"] = "success"
            self.steps[2]["details"] = f"✓ {lang_desc}"
            self.steps[2]["duration"] = self.steps[2]["time"]
            layout["steps"].update(self.create_steps_display())
            
            # Step 4: Z-Library Search
            self.steps[3]["status"] = "running"
            self.steps[3]["details"] = "Searching Z-Library database..."
            layout["steps"].update(self.create_steps_display())
            await asyncio.sleep(self.steps[3]["time"])
            
            zlib_result = self.simulate_search("zlibrary", self.query, normalized_queries)
            if zlib_result:
                self.steps[3]["status"] = "success"
                self.steps[3]["details"] = f"✓ Found: {zlib_result['title']}"
                self.steps[3]["duration"] = self.steps[3]["time"]
                
                # Skip Flibusta since we found it
                self.steps[4]["status"] = "success"
                self.steps[4]["details"] = "⏭️ Skipped (book already found)"
                self.steps[4]["duration"] = 0
                
                final_result = zlib_result
            else:
                self.steps[3]["status"] = "failed"
                self.steps[3]["details"] = "❌ No results in Z-Library"
                self.steps[3]["duration"] = self.steps[3]["time"]
                layout["steps"].update(self.create_steps_display())
                
                # Step 5: Flibusta Fallback
                self.steps[4]["status"] = "running"
                self.steps[4]["details"] = "Searching Flibusta with AI enhancement..."
                layout["steps"].update(self.create_steps_display())
                await asyncio.sleep(self.steps[4]["time"])
                
                flibusta_result = self.simulate_search("flibusta", self.query, normalized_queries)
                if flibusta_result:
                    self.steps[4]["status"] = "success"
                    self.steps[4]["details"] = f"✓ Found: {flibusta_result['title']}"
                    self.steps[4]["duration"] = self.steps[4]["time"]
                    final_result = flibusta_result
                else:
                    self.steps[4]["status"] = "failed"
                    self.steps[4]["details"] = "❌ No results in Flibusta"
                    self.steps[4]["duration"] = self.steps[4]["time"]
                    final_result = None
            
            layout["steps"].update(self.create_steps_display())
            
            # Step 6: Result Compilation
            self.steps[5]["status"] = "running"
            self.steps[5]["details"] = "Compiling final results..."
            layout["steps"].update(self.create_steps_display())
            await asyncio.sleep(self.steps[5]["time"])
            
            self.steps[5]["status"] = "success"
            self.steps[5]["details"] = "✓ Results compiled and formatted"
            self.steps[5]["duration"] = self.steps[5]["time"]
            layout["steps"].update(self.create_steps_display())
            
            # Show final results for 3 seconds
            await asyncio.sleep(3)
        
        # Display final results
        self.show_results(final_result, normalized_queries)
    
    def show_results(self, result, normalized_queries):
        """Show final search results"""
        console.print("\n" + "="*60, style="bold blue")
        console.print("🎯 SEARCH RESULTS", style="bold white", justify="center")
        console.print("="*60, style="bold blue")
        
        if result:
            console.print(Panel(
                f"✅ SUCCESS!\n\n"
                f"📚 Title: {result['title']}\n"
                f"👤 Author: {result['author']}\n"
                f"🔍 Found via: {result['source'].upper()}\n"
                f"📥 Download: Available\n\n"
                f"🤖 Normalized queries: {', '.join(normalized_queries)}\n"
                f"⏱️ Total pipeline time: ~8.3 seconds",
                title="🎉 Book Found",
                style="bold green"
            ))
        else:
            console.print(Panel(
                f"😞 No results found\n\n"
                f"🔍 Original query: {self.query}\n"
                f"🤖 Tried variants: {', '.join(normalized_queries)}\n"
                f"🔗 Sources searched: Z-Library, Flibusta\n"
                f"⏱️ Total pipeline time: ~8.3 seconds",
                title="❌ Search Failed",
                style="bold red"
            ))

async def main():
    """Main demo function"""
    import sys
    
    # Get query from command line or use default
    if len(sys.argv) > 1:
        query = sys.argv[1]
    else:
        query = "hary poter filosofer stone"
    
    console.print(Panel(
        f"🎨 VISUAL PIPELINE DEMONSTRATION\n\n"
        f"This demo shows all layers of the book search pipeline:\n"
        f"• Input validation and sanitization\n"
        f"• Claude AI normalization (fuzzy → clean)\n"
        f"• Language detection and smart routing\n"
        f"• Z-Library search (primary source)\n"
        f"• Flibusta fallback search (secondary)\n"
        f"• Result compilation and formatting\n\n"
        f"Query: '{query}'\n"
        f"Mode: Visual demonstration (no real API calls)",
        title="🚀 Pipeline Visualizer",
        style="bold magenta"
    ))
    
    demo = SimpleVisualDemo(query)
    await demo.run_demo()
    
    console.print(f"\n🎨 Visual demonstration complete! ✨", style="bold blue")
    console.print(f"💡 Try different fuzzy queries:", style="dim")
    console.print(f"   • 'malenkiy prinz' (Russian transliteration)", style="dim")
    console.print(f"   • 'shakesbeer hamlet' (misspelled author)", style="dim")
    console.print(f"   • 'tolken lord rings' (fuzzy fantasy)", style="dim")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n👋 Demo interrupted. Goodbye!", style="bold yellow")
    except Exception as e:
        console.print(f"\n❌ Demo error: {e}", style="bold red")