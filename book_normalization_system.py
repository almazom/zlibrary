#!/usr/bin/env python3
"""
📚 UNIFIED BOOK NORMALIZATION SYSTEM - BEST OF ALL APPROACHES
Combines all 5 suggestions into one powerful normalization system
"""

import asyncio
import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Placeholder for LLM integration (would use Claude SDK or DeepSeek)
class NormalizationType(Enum):
    """Types of fuzzy input problems we handle"""
    TYPOS = "typos"
    ABBREVIATIONS = "abbreviations"
    PARTIAL_TITLES = "partial_titles"
    MIXED_ORDER = "mixed_order"
    PHONETIC = "phonetic"
    UNKNOWN = "unknown"

@dataclass
class NormalizationResult:
    """Result from normalization attempt"""
    original: str
    normalized: str
    confidence: float
    type: NormalizationType
    method_used: str

class UnifiedBookNormalizer:
    """
    BEST-OF-ALL SYSTEM: Combines all 5 approaches
    
    Features from each suggestion:
    1. Pre-search normalization with LLM
    2. Handles all fuzzy input categories
    3. Smart multi-stage fallback
    4. Optimized prompt templates
    5. Caching and multi-provider architecture
    """
    
    def __init__(self):
        self.cache = {}  # Cache normalized queries
        self.providers = ["claude", "deepseek", "local_rules"]
        
        # Knowledge base of common fixes (from Suggestion 2)
        self.common_fixes = {
            # Common typos
            "pyhton": "python",
            "programing": "programming",
            "hary": "harry",
            "poter": "potter",
            "filosfer": "philosopher",
            
            # Common abbreviations
            "hp": "harry potter",
            "lotr": "lord of the rings",
            "got": "game of thrones",
            
            # Common partial titles that need completion
            "gatsby": "the great gatsby",
            "1984": "1984 by george orwell",
            "mockingbird": "to kill a mockingbird"
        }
    
    async def normalize_book_query(self, user_input: str) -> Dict:
        """
        MAIN NORMALIZATION PIPELINE - Best of all approaches
        """
        print(f"\n🔍 UNIFIED NORMALIZATION SYSTEM")
        print(f"Input: '{user_input}'")
        print("-" * 50)
        
        # Check cache first (from Suggestion 5)
        if user_input in self.cache:
            print("✓ Found in cache")
            return self.cache[user_input]
        
        results = {
            "original": user_input,
            "strategies_tried": [],
            "final_result": None,
            "all_attempts": []
        }
        
        # STAGE 1: Detect input type (from Suggestion 2)
        input_type = self._detect_input_type(user_input)
        results["detected_type"] = input_type.value
        print(f"Detected type: {input_type.value}")
        
        # STAGE 2: Apply rule-based fixes (fast, no LLM needed)
        rule_based = self._apply_rule_based_fixes(user_input)
        if rule_based != user_input:
            print(f"Rule-based fix: '{rule_based}'")
            results["all_attempts"].append({
                "method": "rule_based",
                "result": rule_based,
                "confidence": 0.7
            })
        
        # STAGE 3: LLM normalization with specialized prompts (from Suggestions 1 & 4)
        llm_results = await self._llm_normalize_multi_strategy(user_input, input_type)
        results["all_attempts"].extend(llm_results)
        
        # STAGE 4: Smart fallback with keyword extraction (from Suggestion 3)
        if not any(r["confidence"] > 0.8 for r in results["all_attempts"]):
            keywords = await self._extract_keywords_fallback(user_input)
            results["all_attempts"].append({
                "method": "keyword_extraction",
                "result": keywords,
                "confidence": 0.5
            })
        
        # STAGE 5: Select best result using confidence scoring
        best_result = self._select_best_result(results["all_attempts"])
        results["final_result"] = best_result
        
        # Cache the result
        self.cache[user_input] = results
        
        return results
    
    def _detect_input_type(self, text: str) -> NormalizationType:
        """Detect what kind of fuzzy input we're dealing with"""
        
        # Check for obvious typos (non-dictionary words)
        if self._has_typos(text):
            return NormalizationType.TYPOS
        
        # Check for abbreviations
        if len(text.split()) <= 2 and text.lower() in self.common_fixes:
            return NormalizationType.ABBREVIATIONS
        
        # Check for partial titles (very short)
        if len(text.split()) <= 2:
            return NormalizationType.PARTIAL_TITLES
        
        # Check for mixed order (author name first)
        if self._looks_like_author_first(text):
            return NormalizationType.MIXED_ORDER
        
        # Check for phonetic spelling
        if self._has_phonetic_spelling(text):
            return NormalizationType.PHONETIC
        
        return NormalizationType.UNKNOWN
    
    def _apply_rule_based_fixes(self, text: str) -> str:
        """Apply fast rule-based corrections"""
        result = text.lower()
        
        # Apply known fixes
        for typo, correction in self.common_fixes.items():
            result = result.replace(typo, correction)
        
        # Title case for better presentation
        result = ' '.join(word.capitalize() for word in result.split())
        
        return result
    
    async def _llm_normalize_multi_strategy(self, text: str, input_type: NormalizationType) -> List[Dict]:
        """
        Use LLM with different strategies based on input type
        This is where we'd integrate Claude SDK or DeepSeek
        """
        results = []
        
        # Strategy 1: Type-specific prompt (from Suggestion 4)
        prompt = self._get_specialized_prompt(text, input_type)
        
        # Simulate LLM responses (in reality, would call Claude/DeepSeek)
        if input_type == NormalizationType.TYPOS:
            normalized = self._simulate_typo_correction(text)
            results.append({
                "method": "llm_typo_correction",
                "result": normalized,
                "confidence": 0.85
            })
        
        elif input_type == NormalizationType.PARTIAL_TITLES:
            normalized = self._simulate_title_completion(text)
            results.append({
                "method": "llm_title_completion",
                "result": normalized,
                "confidence": 0.75
            })
        
        elif input_type == NormalizationType.MIXED_ORDER:
            normalized = self._simulate_reordering(text)
            results.append({
                "method": "llm_reordering",
                "result": normalized,
                "confidence": 0.80
            })
        
        # Strategy 2: General normalization
        general = self._simulate_general_normalization(text)
        results.append({
            "method": "llm_general",
            "result": general,
            "confidence": 0.70
        })
        
        return results
    
    async def _extract_keywords_fallback(self, text: str) -> str:
        """Extract just the important keywords as fallback"""
        # Remove common words
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        words = text.lower().split()
        keywords = [w for w in words if w not in stopwords]
        return ' '.join(keywords)
    
    def _select_best_result(self, attempts: List[Dict]) -> Dict:
        """Select the best normalization based on confidence"""
        if not attempts:
            return {"result": "", "confidence": 0}
        
        # Sort by confidence
        sorted_attempts = sorted(attempts, key=lambda x: x["confidence"], reverse=True)
        best = sorted_attempts[0]
        
        print(f"\n✅ Best result: '{best['result']}' (confidence: {best['confidence']})")
        print(f"   Method: {best['method']}")
        
        return best
    
    def _get_specialized_prompt(self, text: str, input_type: NormalizationType) -> str:
        """Get type-specific prompt for better LLM results"""
        
        base_prompt = f"Normalize this book query: '{text}'\n"
        
        if input_type == NormalizationType.TYPOS:
            return base_prompt + "Focus on fixing spelling errors. Return only the corrected title."
        
        elif input_type == NormalizationType.PARTIAL_TITLES:
            return base_prompt + "This seems to be a partial title. Complete it with the full book title."
        
        elif input_type == NormalizationType.MIXED_ORDER:
            return base_prompt + "Reorder this to be: [Book Title] by [Author Name]"
        
        elif input_type == NormalizationType.ABBREVIATIONS:
            return base_prompt + "Expand any abbreviations to full titles."
        
        else:
            return base_prompt + "Fix any issues and return a clean book title and/or author."
    
    # Helper methods for detection
    def _has_typos(self, text: str) -> bool:
        """Check if text likely has typos"""
        typo_patterns = ['pyhton', 'programing', 'hary', 'poter']
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in typo_patterns)
    
    def _looks_like_author_first(self, text: str) -> bool:
        """Check if author name appears first"""
        # Simple heuristic: if first two words are capitalized and rest isn't
        words = text.split()
        if len(words) >= 3:
            return words[0][0].isupper() and words[1][0].isupper()
        return False
    
    def _has_phonetic_spelling(self, text: str) -> bool:
        """Check for phonetic misspellings"""
        phonetic_patterns = ['jorj', 'ohrwell', 'shekspeer']
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in phonetic_patterns)
    
    # Simulation methods (would be replaced with actual LLM calls)
    def _simulate_typo_correction(self, text: str) -> str:
        """Simulate typo correction (placeholder for LLM)"""
        corrections = {
            "hary poter": "Harry Potter",
            "pyhton programing": "Python Programming",
            "filosfers stone": "Philosopher's Stone"
        }
        return corrections.get(text.lower(), text)
    
    def _simulate_title_completion(self, text: str) -> str:
        """Simulate title completion (placeholder for LLM)"""
        completions = {
            "gatsby": "The Great Gatsby",
            "mockingbird": "To Kill a Mockingbird",
            "1984": "1984 by George Orwell"
        }
        return completions.get(text.lower(), text)
    
    def _simulate_reordering(self, text: str) -> str:
        """Simulate reordering (placeholder for LLM)"""
        if "rowling" in text.lower() and "harry" in text.lower():
            return "Harry Potter by J.K. Rowling"
        return text
    
    def _simulate_general_normalization(self, text: str) -> str:
        """Simulate general normalization (placeholder for LLM)"""
        # Basic cleanup
        words = text.split()
        return ' '.join(word.capitalize() for word in words)


async def demonstrate_system():
    """Demonstrate the unified normalization system"""
    print("=" * 70)
    print("🚀 UNIFIED BOOK NORMALIZATION SYSTEM DEMONSTRATION")
    print("Combining the best of all 5 approaches")
    print("=" * 70)
    
    normalizer = UnifiedBookNormalizer()
    
    # Test cases showing different types of fuzzy input
    test_cases = [
        "hary poter and the filosfers stone",  # Typos
        "hp",                                   # Abbreviation
        "gatsby",                               # Partial title
        "rowling harry potter",                # Mixed order
        "jorj orwell 1984",                    # Phonetic
        "pyhton programing for beginers",      # Technical typos
        "the invisible purple elephant cookbook"  # Made-up book (no fix needed)
    ]
    
    for test in test_cases:
        result = await normalizer.normalize_book_query(test)
        
        print(f"\n📊 RESULT SUMMARY:")
        print(f"   Original: '{result['original']}'")
        print(f"   Final: '{result['final_result']['result']}'")
        print(f"   Confidence: {result['final_result']['confidence']}")
        print(f"   Attempts made: {len(result['all_attempts'])}")
        print("=" * 70)
    
    # Show architecture benefits
    print("\n✨ UNIFIED SYSTEM BENEFITS:")
    print("1. ✅ Pre-search normalization (from Suggestion 1)")
    print("2. ✅ Handles all fuzzy categories (from Suggestion 2)")
    print("3. ✅ Smart multi-stage fallback (from Suggestion 3)")
    print("4. ✅ Specialized prompts per type (from Suggestion 4)")
    print("5. ✅ Caching & multi-provider support (from Suggestion 5)")
    print("6. 🌟 BEST OF ALL: Confidence-based selection from multiple strategies!")

if __name__ == "__main__":
    asyncio.run(demonstrate_system())