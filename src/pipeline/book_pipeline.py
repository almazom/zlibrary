#!/usr/bin/env python3
"""
BOOK SEARCH PIPELINE - Multi-source orchestrator with intelligent fallback
TDD Implementation: Configurable fallback chains with Claude normalization
"""
import asyncio
import time
import re
import json
import subprocess
import yaml
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))

from book_sources.base import BookSourceInterface, SearchResult
from book_sources.zlibrary_source import ZLibrarySource
from book_sources.flibusta_source import FlibustaSource
# Import ClaudeSDKNormalizer from project root
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from claude_sdk_normalizer import ClaudeSDKNormalizer
except ImportError:
    # Fallback mock for demo
    class ClaudeSDKNormalizer:
        def normalize_book_title(self, query):
            return {"success": False, "error": "Normalizer not available"}

@dataclass
class PipelineConfig:
    """Configuration for the book search pipeline"""
    fallback_chain: List[str] = field(default_factory=lambda: ["zlibrary", "flibusta"])
    timeout_per_source: int = 30
    max_total_timeout: int = 120
    cache_enabled: bool = True
    parallel_search: bool = False
    enable_claude_normalization: bool = True
    language_aware_routing: bool = True

class BookSearchPipeline:
    """
    Multi-source book search pipeline with intelligent fallback
    
    Features:
    - Configurable source chains
    - Claude SDK normalization
    - Language-aware routing
    - Performance monitoring
    - Graceful error handling
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """
        Initialize the book search pipeline
        
        Args:
            config: Pipeline configuration
        """
        self.config = config or PipelineConfig()
        self.sources: Dict[str, BookSourceInterface] = {}
        self.normalizer = None
        self.web_prompts = self._load_web_research_prompts()
        self.stats = {
            "total_searches": 0,
            "successful_searches": 0,
            "source_stats": {},
            "average_response_time": 0.0
        }
        
        # Initialize components
        self._initialize_sources()
        self._initialize_normalizer()
    
    def _load_web_research_prompts(self) -> Dict[str, Any]:
        """Load web research prompts with force keywords from YAML"""
        try:
            prompts_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'prompts', 'claude_web_research_prompts.yaml')
            with open(prompts_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Warning: Could not load web research prompts: {e}")
            return {}
    
    def _initialize_sources(self):
        """Initialize all available book sources"""
        # Initialize Z-Library
        if "zlibrary" in self.config.fallback_chain:
            try:
                self.sources["zlibrary"] = ZLibrarySource()
            except Exception as e:
                print(f"Warning: Failed to initialize Z-Library: {e}")
        
        # Initialize Flibusta
        if "flibusta" in self.config.fallback_chain:
            try:
                self.sources["flibusta"] = FlibustaSource()
            except Exception as e:
                print(f"Warning: Failed to initialize Flibusta: {e}")
    
    def _initialize_normalizer(self):
        """Initialize Claude SDK normalizer if enabled"""
        if self.config.enable_claude_normalization:
            try:
                self.normalizer = ClaudeSDKNormalizer()
            except Exception as e:
                print(f"Warning: Failed to initialize Claude normalizer: {e}")
                self.normalizer = None
    
    async def search_book(self, query: str, **kwargs) -> SearchResult:
        """
        Main search method with full pipeline
        
        Args:
            query: Book search query (can be fuzzy)
            **kwargs: Additional parameters
            
        Returns:
            SearchResult: Best result from available sources
        """
        start_time = time.time()
        self.stats["total_searches"] += 1
        
        try:
            # Validate input
            self._validate_query(query)
            
            # Step 0: URL DETECTION - If input is URL, extract book information first
            if self._is_url(query):
                print(f"🔗 URL detected: Extracting book information from webpage")
                url_book_info = await self._extract_book_from_url(query)
                if url_book_info.get("extraction_success"):
                    # Use extracted information as enhanced query
                    extracted_title = url_book_info.get("title", "")
                    extracted_author = url_book_info.get("author", "")
                    if extracted_title and extracted_author:
                        query = f"{extracted_author} {extracted_title}"
                        print(f"📖 Extracted: {query}")
                    elif extracted_title:
                        query = extracted_title
                        print(f"📖 Extracted title: {query}")
            
            # Step 1: AUTHOR EXTRACTION - Find the author first for better searches
            author_info = await self._extract_author_with_web_research(query)
            
            # Step 1.2: Normalize query with Claude if enabled
            normalized_queries = await self._normalize_query(query, author_info)
            
            # Step 1.5: PREDICTIVE INTENT ANALYSIS - What does user REALLY want?
            user_intent_prediction = await self._predict_user_intent_with_web_research(query)
            
            # Step 1.6: Enhance queries with intent predictions
            if user_intent_prediction.get("research_performed"):
                enhanced_queries = self._enhance_queries_with_intent(normalized_queries, user_intent_prediction)
                normalized_queries = enhanced_queries
            
            # Step 2: Determine optimal fallback chain
            optimal_chain = self._get_optimal_chain(query, **kwargs)
            
            # Step 3: Search through sources in order
            for source_name in optimal_chain:
                if source_name not in self.sources:
                    continue
                
                source = self.sources[source_name]
                
                # Try each normalized query
                for norm_query in normalized_queries:
                    try:
                        result = await self._search_with_timeout(source, norm_query, **kwargs)
                        
                        if result.found:
                            # Success! But validate if this matches user intent
                            validation = self._validate_result_matches_intent(query, result, **kwargs)
                            result.metadata["intent_validation"] = validation
                            
                            self._update_stats(source_name, result, time.time() - start_time)
                            return result
                        
                    except Exception as e:
                        print(f"Source {source_name} failed for query '{norm_query}': {e}")
                        continue
            
            # No sources found the book
            total_time = time.time() - start_time
            return SearchResult(
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
            
        except ValueError as e:
            # Input validation error
            return SearchResult(
                found=False,
                source="pipeline",
                response_time=time.time() - start_time,
                metadata={
                    "error": f"Invalid input: {e}",
                    "original_query": query
                }
            )
        
        except Exception as e:
            # Unexpected error
            return SearchResult(
                found=False,
                source="pipeline",
                response_time=time.time() - start_time,
                metadata={
                    "error": f"Pipeline error: {e}",
                    "original_query": query
                }
            )
    
    def _validate_query(self, query: str):
        """Validate search query"""
        if not query:
            raise ValueError("Query cannot be empty")
        
        query = query.strip()
        if not query:
            raise ValueError("Query cannot be empty or whitespace only")
        
        if len(query) < 2:
            raise ValueError("Query too short (minimum 2 characters)")
        
        if len(query) > 500:
            raise ValueError("Query too long (maximum 500 characters)")
        
        # Check for potentially invalid patterns
        if re.match(r'^[!@#$%^&*()_+\-=\[\]{}|;\':",./<>?`~]+$', query):
            raise ValueError("Query contains only special characters")
    
    async def _normalize_query(self, query: str, author_info: Dict[str, Any] = None) -> List[str]:
        """
        Normalize query using Claude SDK
        
        Returns:
            List[str]: List of normalized queries to try
        """
        queries = [query]  # Always include original
        
        if not self.normalizer:
            return queries
        
        try:
            # Enhanced normalization with author information
            normalization_input = query
            if author_info and author_info.get("author_extraction_performed"):
                # Include author context in normalization
                author_analysis = author_info.get("claude_analysis", "")
                if "author_name" in author_analysis.lower():
                    print(f"🎯 Using author context for enhanced normalization")
                    normalization_input = f"{query} (with author context: {author_analysis[:100]})"
            
            result = self.normalizer.normalize_book_title(normalization_input)
            
            if result.get("success"):
                search_strings = result.get("search_strings", {})
                
                # Add normalized strings
                if "original" in search_strings and search_strings["original"]:
                    queries.append(search_strings["original"])
                
                if "russian" in search_strings and search_strings["russian"]:
                    queries.append(search_strings["russian"])
                
                # Add main normalized query if available
                if "normalized_query" in result and result["normalized_query"]:
                    queries.append(result["normalized_query"])
                    
                # If author was extracted, try author + title combinations
                if author_info and author_info.get("author_extraction_performed"):
                    author_analysis = author_info.get("claude_analysis", "")
                    # Extract potential author name and add as search variant
                    if "author_name" in author_analysis.lower():
                        print(f"📝 Adding author-enhanced search variants")
                        # Add original query as author-title search
                        queries.insert(0, query)  # Prioritize with author context
        
        except Exception as e:
            print(f"Query normalization failed: {e}")
        
        # Remove duplicates while preserving order
        unique_queries = []
        seen = set()
        for q in queries:
            if q and q.lower() not in seen:
                unique_queries.append(q)
                seen.add(q.lower())
        
        return unique_queries
    
    def _get_optimal_chain(self, query: str, **kwargs) -> List[str]:
        """
        Determine optimal fallback chain based on query and context
        
        Args:
            query: Search query
            **kwargs: Additional context (language_hint, time_limit, etc.)
            
        Returns:
            List[str]: Ordered list of source names to try
        """
        # Start with configured chain
        chain = self.config.fallback_chain.copy()
        
        if not self.config.language_aware_routing:
            return chain
        
        # Enhanced language-aware routing with Claude normalization feedback
        detected_language = self._detect_language(query)
        russian_author_detected = self._detect_russian_author_in_query(query)
        
        if (detected_language == "ru" or russian_author_detected) and "flibusta" in chain and "zlibrary" in chain:
            # Russian text OR Russian author name detected - prioritize Flibusta
            # Flibusta specializes in Russian books and translations
            chain = ["flibusta", "zlibrary"]
            print(f"🇷🇺 Language routing: Detected Russian content, prioritizing Flibusta -> Z-Library")
            
        elif detected_language == "en" and "zlibrary" in chain and "flibusta" in chain:
            # English text - prioritize Z-Library (broader international collection)
            chain = ["zlibrary", "flibusta"]
            print(f"🌍 Language routing: Detected English content, prioritizing Z-Library -> Flibusta")
        
        # Time constraint routing
        time_limit = kwargs.get("max_time", 0)
        if time_limit > 0 and time_limit < 15:
            # Fast search - only fast sources
            chain = [s for s in chain if s == "zlibrary"]
        
        return [s for s in chain if s in self.sources]
    
    def _detect_language(self, text: str) -> str:
        """Language detection - use Claude for complex cases, simple for obvious ones"""
        # Quick check for obvious cases
        cyrillic_chars = len(re.findall(r'[а-яёА-ЯЁ]', text))
        latin_chars = len(re.findall(r'[a-zA-Z]', text))
        
        # Obvious cases - no need for AI
        if cyrillic_chars > latin_chars * 2:
            return "ru"
        elif latin_chars > cyrillic_chars * 2:
            return "en"
        
        # Mixed/unclear cases - use Claude SDK -p with YAML prompt
        try:
            # Use YAML web research prompt for complex language detection
            prompt_template = self.web_prompts.get('language_detection_web', {})
            
            if prompt_template:
                web_language_prompt = prompt_template['main_prompt'].format(text=text)
            else:
                # Fallback prompt with force keywords
                web_language_prompt = f'Web search and research online the language of: "{text}". Look up online for language identification. Return: ru, en, or mixed'
            
            result = subprocess.run([
                "/home/almaz/.claude/local/claude",
                "-p", web_language_prompt,
                "--output-format", "json"
            ], capture_output=True, text=True, timeout=8)  # Fast timeout
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                content = data.get('result', '').lower()
                if 'ru' in content:
                    print(f"🌐 Language detection via web research: Russian")
                    return "ru"
                elif 'en' in content:
                    print(f"🌐 Language detection via web research: English")
                    return "en"
        except:
            pass
        
        return "mixed"
    
    def _detect_russian_author_in_query(self, text: str) -> bool:
        """Detect Russian author names using Claude SDK -p power with web research"""
        try:
            # Use YAML web research prompt for Russian author detection
            prompt_template = self.web_prompts.get('russian_author_research', {})
            
            if prompt_template:
                russian_research_prompt = prompt_template['main_prompt'].format(author_text=text)
            else:
                # Fallback with force web search keywords
                russian_research_prompt = f'Search the web to verify: Is "{text}" Russian author/content? Web search for author nationality and Russian translations. Return JSON: {{"is_russian": true/false, "confidence": 0.0-1.0}}'
            
            result = subprocess.run([
                "/home/almaz/.claude/local/claude",
                "-p", russian_research_prompt,
                "--output-format", "json"
            ], capture_output=True, text=True, timeout=8)  # Fast timeout
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                # Extract from Claude response
                content = data.get('result', '')
                if 'true' in content.lower() and ('0.7' in content or '0.8' in content or '0.9' in content):
                    print(f"🎯 Claude SDK Web Research: Russian author/content detected")
                    return True
                    
        except:
            pass
        
        # Simple fallback
        return bool(re.search(r'[а-яёА-ЯЁ]', text)) and len(text.split()) >= 2
    
    def _fallback_cyrillic_check(self, text: str) -> bool:
        """Simple fallback when Claude SDK is unavailable"""
        return bool(re.search(r'[а-яёА-ЯЁ]', text)) and len(text.split()) >= 2
    
    def _validate_result_matches_intent(self, original_query: str, result, **kwargs) -> Dict[str, Any]:
        """
        COGNITIVE VALIDATION LAYER - Does this book match what user actually wanted?
        Uses Claude SDK with web research to analyze user satisfaction potential
        """
        try:
            # Extract book metadata
            book_title = getattr(result, 'title', 'Unknown')
            book_author = getattr(result, 'author', 'Unknown') 
            book_metadata = getattr(result, 'metadata', {})
            
            # Use YAML web research prompt for validation
            prompt_template = self.web_prompts.get('book_intent_validation', {})
            
            if prompt_template:
                validation_prompt = prompt_template['main_prompt'].format(
                    book_title=book_title, 
                    author=book_author, 
                    user_query=original_query
                )
            else:
                # Fallback with web research force keywords
                validation_prompt = f'''
Look up online: Does book "{book_title}" by {book_author} match user search "{original_query}"?

Web research validation tasks:
- Check if this is author's popular work
- Look up user reviews and satisfaction online
- Verify genre and content match via web search
- Research online user expectations for this query

Analyze via web research if this book matches user intent. Return JSON:
{{
    "intent_match": true/false,
    "confidence": 0.0-1.0,
    "match_quality": "excellent|good|partial|poor|mismatch",
    "reasoning": "based on web research findings",
    "user_satisfaction_prediction": 0.0-1.0,
    "recommendation": "download|search_alternative|clarify_request"
}}

IMPORTANT: Use web search to get current data about book popularity and user satisfaction.
'''

            claude_result = subprocess.run([
                "/home/almaz/.claude/local/claude",
                "-p", validation_prompt,
                "--output-format", "json"
            ], capture_output=True, text=True, timeout=8)
            
            if claude_result.returncode == 0:
                data = json.loads(claude_result.stdout)
                content = data.get('result', '')
                
                # Extract validation analysis
                if 'intent_match' in content.lower():
                    match_quality = "good" if "good" in content else "partial" if "partial" in content else "excellent"
                    confidence = 0.8 if "true" in content.lower() else 0.3
                    
                    validation_result = {
                        "analysis_method": "claude_sdk",
                        "intent_match_detected": "true" in content.lower(),
                        "confidence": confidence,
                        "match_quality": match_quality,
                        "claude_analysis": content[:300],  # First 300 chars
                        "validation_timestamp": time.time()
                    }
                    
                    # Print validation feedback
                    if validation_result["intent_match_detected"]:
                        print(f"✅ Intent Validation: Good match (confidence: {confidence:.1%})")
                    else:
                        print(f"⚠️ Intent Validation: Potential mismatch (confidence: {confidence:.1%})")
                        print(f"📋 Analysis: {content[:150]}...")
                    
                    return validation_result
                    
        except Exception as e:
            print(f"Intent validation failed: {e}")
        
        # Fallback validation
        return {
            "analysis_method": "fallback",
            "intent_match_detected": True,  # Assume good if we can't analyze
            "confidence": 0.5,
            "match_quality": "unknown",
            "note": "Claude SDK validation unavailable"
        }
    
    async def _predict_user_intent_with_web_research(self, query: str) -> Dict[str, Any]:
        """
        PREDICTIVE INTENT LAYER - Use Claude SDK web research to predict what user REALLY wants
        
        Before searching our sources, let's understand:
        1. What is the most popular book by this author?
        2. What book would give 80%+ user satisfaction?
        3. What are users typically looking for with this query?
        """
        try:
            # Use YAML quick web research for faster analysis
            quick_template = self.web_prompts.get('quick_web_research', {})
            
            if quick_template:
                web_research_prompt = quick_template['main_prompt'].format(query=query)
            else:
                # Use standard predictive research template
                prompt_template = self.web_prompts.get('predictive_intent_research', {})
                
                if prompt_template:
                    web_research_prompt = prompt_template['main_prompt'].format(author_query=query)
                else:
                    # Fallback with simple web search
                    web_research_prompt = f'''
Search web for "{query}" information

Quick web research:
- Find author's popular books
- Look up basic ratings  
- Get key information

Return brief analysis based on web findings.
'''

            # Execute Claude SDK with web research capability
            claude_result = subprocess.run([
                "/home/almaz/.claude/local/claude",
                "-p", web_research_prompt,
                "--output-format", "json"
            ], capture_output=True, text=True, timeout=10)  # Fast timeout for web research
            
            if claude_result.returncode == 0:
                data = json.loads(claude_result.stdout)
                content = data.get('result', '')
                
                # Parse web research results
                if 'predicted_intent' in content.lower() or 'popular' in content.lower():
                    intent_prediction = {
                        "analysis_method": "claude_web_research",
                        "research_performed": True,
                        "claude_analysis": content[:500],  # First 500 chars
                        "confidence": 0.8 if "confident" in content.lower() else 0.6,
                        "timestamp": time.time()
                    }
                    
                    print(f"🔍 Predictive Intent Research:")
                    print(f"   {content[:200]}...")
                    
                    # Extract specific predictions if possible
                    if "most_likely" in content.lower():
                        print(f"🎯 Most Likely Intent: Detected via web research")
                    
                    return intent_prediction
                    
        except Exception as e:
            print(f"Web research intent prediction failed: {e}")
        
        # Fallback - basic intent analysis without web research
        return {
            "analysis_method": "fallback",
            "research_performed": False,
            "confidence": 0.3,
            "note": "Web research unavailable, using basic analysis"
        }
    
    def _enhance_queries_with_intent(self, normalized_queries: List[str], intent_prediction: Dict[str, Any]) -> List[str]:
        """
        Enhance search queries with web research insights
        Prioritize queries most likely to satisfy user intent
        """
        enhanced_queries = normalized_queries.copy()
        
        # Extract predicted popular books from Claude web research
        analysis = intent_prediction.get("claude_analysis", "")
        
        # Look for specific book titles mentioned in the analysis
        if "most_likely" in analysis.lower() or "popular" in analysis.lower():
            # Use Claude SDK to extract specific search terms
            try:
                extract_prompt = f'From this analysis: "{analysis[:300]}", extract the most likely book titles/queries user wants. Return comma-separated list of 2-3 search terms.'
                
                result = subprocess.run([
                    "/home/almaz/.claude/local/claude",
                    "-p", extract_prompt,
                    "--output-format", "json"
                ], capture_output=True, text=True, timeout=8)
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    content = data.get('result', '')
                    
                    # Add extracted high-confidence queries to front of list
                    if content and len(content) > 10:
                        print(f"🎯 Intent-enhanced queries: {content[:100]}...")
                        # Add the high-confidence predictions first
                        enhanced_queries.insert(0, content.split(',')[0].strip(' "'))
                        
            except Exception as e:
                print(f"Query enhancement failed: {e}")
        
        return enhanced_queries
    
    async def _extract_author_with_web_research(self, query: str) -> Dict[str, Any]:
        """
        AUTHOR EXTRACTION LAYER - Find the author first for better book searches
        Uses Claude SDK web research to identify author before searching
        """
        try:
            # Use YAML author extraction prompt
            prompt_template = self.web_prompts.get('author_extraction_research', {})
            
            if prompt_template:
                author_research_prompt = prompt_template['main_prompt'].format(book_query=query)
            else:
                # Fallback with web search force keywords
                author_research_prompt = f'''
Search the web to find the author of book: "{query}"

FORCE WEB SEARCH - Find author information online:
- Look up the book title online
- Search for author information  
- Find publication details
- Research book bibliography

Return JSON with author information:
{{
  "author_found": true/false,
  "author_name": "Author Name",
  "confidence": 0.0-1.0,
  "book_title_normalized": "Clean title",
  "publication_year": "YYYY"
}}

Use web search to find accurate author information.
'''

            # Execute Claude SDK with web research
            claude_result = subprocess.run([
                "/home/almaz/.claude/local/claude",
                "-p", author_research_prompt,
                "--output-format", "json"
            ], capture_output=True, text=True, timeout=8)  # Fast timeout for author extraction
            
            if claude_result.returncode == 0:
                data = json.loads(claude_result.stdout)
                content = data.get('result', '')
                
                # Parse author extraction results
                if 'author_found' in content.lower() and 'true' in content.lower():
                    author_info = {
                        "analysis_method": "claude_web_research",
                        "author_extraction_performed": True,
                        "claude_analysis": content[:400],
                        "confidence": 0.8 if "confidence" in content.lower() else 0.6,
                        "timestamp": time.time()
                    }
                    
                    print(f"👤 Author Extraction: Found author info via web research")
                    print(f"   📝 Analysis: {content[:150]}...")
                    
                    return author_info
                    
        except Exception as e:
            print(f"Author extraction failed: {e}")
        
        # Fallback - no author extraction
        return {
            "analysis_method": "fallback",
            "author_extraction_performed": False,
            "confidence": 0.0,
            "note": "Author extraction unavailable"
        }
    
    def _is_url(self, text: str) -> bool:
        """Check if input is a URL"""
        return text.strip().startswith(('http://', 'https://'))
    
    async def _extract_book_from_url(self, url: str) -> Dict[str, Any]:
        """
        URL BOOK EXTRACTION LAYER - Extract book info directly from URL using Claude SDK
        Uses Claude -p to fetch and analyze the webpage content
        """
        try:
            # Use YAML URL extraction prompt
            prompt_template = self.web_prompts.get('url_book_extraction', {})
            
            if prompt_template:
                url_extraction_prompt = prompt_template['main_prompt'].format(book_url=url)
            else:
                # Fallback with focused URL extraction
                url_extraction_prompt = f'''
Visit this URL and extract book information: {url}

Look for:
- Book title (main heading, h1, or prominent text)
- Author name (byline, author field, or credits)

Return ONLY this exact JSON structure:
{{
  "title": "Book Title Here",
  "author": "Author Name Here", 
  "success": true
}}

IMPORTANT: Visit the actual webpage to get real data.
'''

            print(f"🔗 Using Claude SDK to extract from: {url}")
            
            # Execute Claude SDK with URL fetching capability
            claude_result = subprocess.run([
                "/home/almaz/.claude/local/claude",
                "-p", url_extraction_prompt,
                "--output-format", "json"
            ], capture_output=True, text=True, timeout=12)  # Fast URL fetching timeout
            
            if claude_result.returncode == 0:
                data = json.loads(claude_result.stdout)
                content = data.get('result', '')
                
                # Parse JSON response from Claude
                try:
                    # Try to parse as JSON first
                    import json as json_parser
                    json_data = json_parser.loads(content)
                    
                    if json_data.get("success") and json_data.get("title") and json_data.get("author"):
                        url_info = {
                            "analysis_method": "claude_url_extraction",
                            "extraction_success": True,
                            "title": json_data["title"],
                            "author": json_data["author"],
                            "confidence": 0.9,
                            "timestamp": time.time(),
                            "original_url": url
                        }
                        
                        print(f"✅ URL Extraction: {json_data['title']} by {json_data['author']}")
                        return url_info
                        
                except json_parser.JSONDecodeError:
                    # Fallback to text parsing if JSON fails
                    if 'title' in content.lower() and 'author' in content.lower():
                        url_info = {
                            "analysis_method": "claude_url_extraction",
                            "extraction_success": True,
                            "claude_analysis": content[:500],
                            "confidence": 0.8,
                            "timestamp": time.time(),
                            "original_url": url
                        }
                        
                        # Try to extract specific fields from text
                        try:
                            if '"title"' in content:
                                title_start = content.find('"title"') + 9
                                title_end = content.find('"', title_start + 1)
                                if title_end > title_start:
                                    url_info["title"] = content[title_start:title_end]
                            
                            if '"author"' in content:
                                author_start = content.find('"author"') + 10
                                author_end = content.find('"', author_start + 1)
                                if author_end > author_start:
                                    url_info["author"] = content[author_start:author_end]
                        except:
                            pass
                        
                        print(f"✅ URL Extraction: Successfully extracted book information")
                        print(f"   📝 Analysis: {content[:150]}...")
                        
                        return url_info
                    
        except Exception as e:
            print(f"URL extraction failed: {e}")
        
        # Fallback - no URL extraction
        return {
            "analysis_method": "fallback",
            "extraction_success": False,
            "confidence": 0.0,
            "note": "URL extraction unavailable",
            "original_url": url
        }
    
    def _is_cyrillic(self, text: str) -> bool:
        """Check if text contains Cyrillic characters"""
        return bool(re.search(r'[а-яёА-ЯЁ]', text))
    
    async def _search_with_timeout(self, source: BookSourceInterface, query: str, **kwargs) -> SearchResult:
        """Search with source-specific timeout"""
        timeout = min(source.get_timeout(), self.config.timeout_per_source)
        
        try:
            return await asyncio.wait_for(source.search(query, **kwargs), timeout=timeout)
        except asyncio.TimeoutError:
            return SearchResult(
                found=False,
                source=source.get_source_name(),
                response_time=timeout,
                metadata={
                    "error": f"Timeout after {timeout} seconds",
                    "query": query
                }
            )
    
    def _update_stats(self, source_name: str, result: SearchResult, total_time: float):
        """Update pipeline statistics"""
        if result.found:
            self.stats["successful_searches"] += 1
        
        if source_name not in self.stats["source_stats"]:
            self.stats["source_stats"][source_name] = {
                "attempts": 0,
                "successes": 0,
                "total_time": 0.0
            }
        
        stats = self.stats["source_stats"][source_name]
        stats["attempts"] += 1
        if result.found:
            stats["successes"] += 1
        stats["total_time"] += result.response_time
        
        # Update average response time
        total_searches = self.stats["total_searches"]
        if total_searches > 1:
            prev_avg = self.stats["average_response_time"]
            self.stats["average_response_time"] = (prev_avg * (total_searches - 1) + total_time) / total_searches
        else:
            self.stats["average_response_time"] = total_time
    
    def get_fallback_chain(self) -> List[str]:
        """Get current fallback chain configuration"""
        return self.config.fallback_chain.copy()
    
    def get_optimal_chain_for_query(self, query: str) -> List[str]:
        """Get optimal chain for specific query (for testing)"""
        return self._get_optimal_chain(query)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline performance statistics"""
        stats = self.stats.copy()
        
        # Calculate success rates
        for source_name, source_stats in stats["source_stats"].items():
            if source_stats["attempts"] > 0:
                source_stats["success_rate"] = source_stats["successes"] / source_stats["attempts"]
                source_stats["average_response_time"] = source_stats["total_time"] / source_stats["attempts"]
            else:
                source_stats["success_rate"] = 0.0
                source_stats["average_response_time"] = 0.0
        
        # Overall success rate
        if stats["total_searches"] > 0:
            stats["overall_success_rate"] = stats["successful_searches"] / stats["total_searches"]
        else:
            stats["overall_success_rate"] = 0.0
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all sources"""
        health_status = {"pipeline": "healthy", "sources": {}}
        
        for source_name, source in self.sources.items():
            try:
                is_healthy = await source.health_check()
                health_status["sources"][source_name] = "healthy" if is_healthy else "unhealthy"
            except Exception as e:
                health_status["sources"][source_name] = f"error: {e}"
        
        # Check if normalizer is working
        if self.normalizer:
            try:
                test_result = self.normalizer.normalize_book_title("test")
                health_status["claude_normalizer"] = "healthy" if test_result else "unhealthy"
            except:
                health_status["claude_normalizer"] = "unhealthy"
        else:
            health_status["claude_normalizer"] = "disabled"
        
        return health_status
    
    async def cleanup(self):
        """Clean up resources"""
        for source in self.sources.values():
            if hasattr(source, 'cleanup'):
                try:
                    await source.cleanup()
                except:
                    pass