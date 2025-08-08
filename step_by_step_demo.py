#!/usr/bin/env python3
"""
🔍 STEP-BY-STEP PIPELINE DEMO
Shows each pipeline layer individually with detailed explanations
"""
import asyncio
import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import track

console = Console()

class StepByStepDemo:
    def __init__(self, query):
        self.query = query
        
    async def run_demo(self):
        """Run step-by-step demonstration"""
        console.print(Panel(
            f"🔍 STEP-BY-STEP PIPELINE DEMONSTRATION\n\n"
            f"Query: '{self.query}'\n"
            f"Following each layer of the pipeline...",
            title="🎨 Pipeline Breakdown",
            style="bold blue"
        ))
        
        await asyncio.sleep(1)
        
        # Step 1: Input Validation
        console.print("\n" + "="*60)
        console.print("🔍 STEP 1: INPUT VALIDATION", style="bold cyan")
        console.print("="*60)
        
        await asyncio.sleep(0.5)
        console.print(f"📝 Original input: '{self.query}'")
        await asyncio.sleep(0.5)
        console.print("✅ Length check: OK (2+ characters)")
        await asyncio.sleep(0.5)
        console.print("✅ Character validation: Contains valid characters")
        await asyncio.sleep(0.5)
        console.print("✅ Sanitization: Input cleaned and prepared")
        await asyncio.sleep(1)
        console.print("🎯 Result: Query validated successfully", style="bold green")
        
        # Step 2: Claude AI Normalization
        console.print("\n" + "="*60)
        console.print("🤖 STEP 2: CLAUDE AI NORMALIZATION", style="bold cyan")
        console.print("="*60)
        
        await asyncio.sleep(0.5)
        console.print("🔄 Processing fuzzy input with AI...")
        
        # Simulate AI processing
        for i in track(range(3), description="🤖 AI processing..."):
            await asyncio.sleep(0.5)
        
        # Show normalization results
        normalizations = self.simulate_normalization(self.query)
        console.print(f"✅ Generated {len(normalizations)} query variants:")
        for i, variant in enumerate(normalizations, 1):
            console.print(f"   {i}. '{variant}'", style="yellow")
        
        await asyncio.sleep(1)
        console.print("🎯 Result: Fuzzy input normalized to clean queries", style="bold green")
        
        # Step 3: Language Detection & Routing
        console.print("\n" + "="*60)
        console.print("🌍 STEP 3: LANGUAGE DETECTION & ROUTING", style="bold cyan")
        console.print("="*60)
        
        await asyncio.sleep(0.5)
        lang, lang_desc = self.detect_language(self.query)
        console.print(f"🔍 Analyzing query characters...")
        await asyncio.sleep(0.5)
        console.print(f"📊 Language detected: {lang_desc}")
        await asyncio.sleep(0.5)
        
        if lang == "ru":
            routing = "🇷🇺 Flibusta → Z-Library (Russian priority)"
        else:
            routing = "⚡ Z-Library → 🇷🇺 Flibusta (Speed priority)"
        
        console.print(f"🎯 Routing decision: {routing}")
        await asyncio.sleep(1)
        console.print("🎯 Result: Optimal source chain determined", style="bold green")
        
        # Step 4: Primary Source Search
        console.print("\n" + "="*60)
        console.print("⚡ STEP 4: PRIMARY SOURCE SEARCH (Z-LIBRARY)", style="bold cyan")
        console.print("="*60)
        
        await asyncio.sleep(0.5)
        console.print("🔍 Searching Z-Library database...")
        console.print("📊 Database: 22M+ books, 9 formats, 50+ languages")
        
        # Simulate search
        for i in track(range(4), description="⚡ Z-Library search..."):
            await asyncio.sleep(0.5)
        
        # Check if we find it in Z-Library
        zlib_result = self.simulate_search("zlibrary", normalizations)
        if zlib_result:
            console.print(f"✅ FOUND in Z-Library!")
            console.print(f"📚 Title: {zlib_result['title']}")
            console.print(f"👤 Author: {zlib_result['author']}")
            console.print("📥 Download: Available")
            console.print("🎯 Result: Book found in primary source", style="bold green")
            
            # Skip fallback
            console.print("\n" + "="*60)
            console.print("🇷🇺 STEP 5: FALLBACK SEARCH (SKIPPED)", style="bold cyan")
            console.print("="*60)
            console.print("⏭️ Skipping Flibusta search - book already found")
            console.print("🎯 Result: Fallback not needed", style="bold green")
            
            final_result = zlib_result
        else:
            console.print("❌ Not found in Z-Library")
            console.print("🔄 Proceeding to fallback source...")
            console.print("🎯 Result: Moving to Flibusta fallback", style="bold yellow")
            
            # Step 5: Fallback Search
            console.print("\n" + "="*60)
            console.print("🇷🇺 STEP 5: FALLBACK SEARCH (FLIBUSTA)", style="bold cyan")
            console.print("="*60)
            
            await asyncio.sleep(0.5)
            console.print("🔍 Searching Flibusta with AI enhancement...")
            console.print("📊 Specialties: Russian books, EPUB format, AI normalization")
            
            # Simulate longer search
            for i in track(range(6), description="🇷🇺 Flibusta AI search..."):
                await asyncio.sleep(0.5)
            
            flibusta_result = self.simulate_search("flibusta", normalizations)
            if flibusta_result:
                console.print(f"✅ FOUND in Flibusta!")
                console.print(f"📚 Title: {flibusta_result['title']}")
                console.print(f"👤 Author: {flibusta_result['author']}")
                console.print("📥 Download: Available (EPUB)")
                console.print("🎯 Result: Book found in fallback source", style="bold green")
                final_result = flibusta_result
            else:
                console.print("❌ Not found in Flibusta either")
                console.print("🎯 Result: No results from any source", style="bold red")
                final_result = None
        
        # Step 6: Result Compilation
        console.print("\n" + "="*60)
        console.print("📊 STEP 6: RESULT COMPILATION", style="bold cyan")
        console.print("="*60)
        
        await asyncio.sleep(0.5)
        console.print("📋 Compiling final results...")
        await asyncio.sleep(0.5)
        console.print("📈 Calculating performance metrics...")
        await asyncio.sleep(0.5)
        console.print("🎨 Formatting response...")
        await asyncio.sleep(0.5)
        console.print("🎯 Result: Pipeline execution complete", style="bold green")
        
        # Final Summary
        console.print("\n" + "="*60)
        console.print("🎯 FINAL PIPELINE SUMMARY", style="bold white")
        console.print("="*60)
        
        if final_result:
            console.print(Panel(
                f"✅ SUCCESS! Book found and ready for download\n\n"
                f"📚 Final Title: {final_result['title']}\n"
                f"👤 Final Author: {final_result['author']}\n"
                f"🔍 Found via: {final_result['source'].upper()}\n"
                f"🤖 AI Processing: Fuzzy input successfully normalized\n"
                f"🌍 Language Routing: {lang_desc}\n"
                f"⏱️ Total Pipeline Time: ~8.3 seconds\n"
                f"📋 Steps Completed: 6/6",
                title="🎉 Pipeline Success",
                style="bold green"
            ))
        else:
            console.print(Panel(
                f"😞 No results found in any source\n\n"
                f"🔍 Original Query: '{self.query}'\n"
                f"🤖 Normalized Variants: {len(normalizations)} tried\n"
                f"🔗 Sources Searched: Z-Library + Flibusta\n"
                f"🌍 Language Processing: {lang_desc}\n"
                f"⏱️ Total Pipeline Time: ~11.8 seconds\n"
                f"📋 Steps Completed: 6/6",
                title="❌ Pipeline Complete (No Results)",
                style="bold red"
            ))
        
        console.print(f"\n🎨 Step-by-step demonstration complete! ✨", style="bold blue")
    
    def simulate_normalization(self, query):
        """Simulate Claude normalization with detailed variants"""
        normalizations = {
            "hary poter": ["hary poter", "Harry Potter", "Гарри Поттер"],
            "filosofer stone": ["filosofer stone", "Philosopher's Stone", "философский камень"],
            "malenkiy prinz": ["malenkiy prinz", "The Little Prince", "Маленький принц"],
            "dostoevsky": ["dostoevsky", "Dostoevsky", "Достоевский"],
            "voyna i mir": ["voyna i mir", "War and Peace", "Война и мир"],
            "tolken": ["tolken", "Tolkien", "Толкиен"],
            "shakesbeer": ["shakesbeer", "Shakespeare", "Шекспир"]
        }
        
        query_lower = query.lower()
        
        for key, variants in normalizations.items():
            if key in query_lower:
                return variants
        
        # Default normalization
        return [query, query.title()]
    
    def detect_language(self, query):
        """Language detection with explanation"""
        import re
        cyrillic = len(re.findall(r'[а-яёА-ЯЁ]', query))
        latin = len(re.findall(r'[a-zA-Z]', query))
        
        if cyrillic > latin:
            return "ru", "Russian (Cyrillic characters detected)"
        elif latin > cyrillic:
            return "en", "English (Latin characters detected)"
        else:
            return "mixed", "Mixed/Unknown language"
    
    def simulate_search(self, source, normalized_queries):
        """Simulate book search with detailed logic"""
        books = {
            "harry potter": {"title": "Harry Potter and the Philosopher's Stone", "author": "J.K. Rowling", "source": "zlibrary"},
            "hary poter": {"title": "Harry Potter and the Philosopher's Stone", "author": "J.K. Rowling", "source": "zlibrary"},
            "malenkiy prinz": {"title": "The Little Prince", "author": "Antoine de Saint-Exupéry", "source": "zlibrary"},
            "little prince": {"title": "The Little Prince", "author": "Antoine de Saint-Exupéry", "source": "zlibrary"},
            "маленький принц": {"title": "Маленький принц", "author": "Антуан де Сент-Экзюпери", "source": "flibusta"},
            "dostoevsky": {"title": "Crime and Punishment", "author": "Fyodor Dostoevsky", "source": "zlibrary"},
            "1984": {"title": "1984", "author": "George Orwell", "source": "zlibrary"},
            "orwell": {"title": "1984", "author": "George Orwell", "source": "zlibrary"},
            "tolkien": {"title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "source": "zlibrary"},
            "tolken": {"title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "source": "zlibrary"},
            "shakespeare": {"title": "Hamlet", "author": "William Shakespeare", "source": "zlibrary"},
            "shakesbeer": {"title": "Hamlet", "author": "William Shakespeare", "source": "zlibrary"}
        }
        
        # Try each normalized query
        for norm_query in normalized_queries:
            query_key = norm_query.lower()
            for book_key, book_data in books.items():
                if book_key in query_key or any(word in query_key for word in book_key.split()):
                    # Check if source matches
                    if book_data["source"] == source:
                        return book_data
                    elif source == "flibusta":  # Flibusta can find most books
                        return book_data
        
        return None

async def main():
    import sys
    
    # Get query from command line or use default
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "hary poter filosofer stone"
    
    demo = StepByStepDemo(query)
    await demo.run_demo()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n👋 Demo interrupted. Goodbye!", style="bold yellow")