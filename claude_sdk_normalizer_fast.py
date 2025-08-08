#!/usr/bin/env python3
"""
CLAUDE SDK BOOK NORMALIZER - Fast Optimized Version
Removes ultra-thinking prompts while keeping cognitive intelligence
"""
import subprocess
import json
import sys
import re
import os
from typing import Dict, Any, Optional

class ClaudeSDKNormalizerFast:
    """Fast Claude SDK integration for book title normalization"""
    
    def __init__(self, use_cognitive=True, timeout=10):
        """
        Initialize fast normalizer
        
        Args:
            use_cognitive: Enable cognitive layer (default: True)
            timeout: Timeout in seconds (default: 10)
        """
        self.claude_command = "claude"  # Use claude from PATH
        self.use_cognitive = use_cognitive
        self.timeout = timeout
        
    def normalize_book_title(self, fuzzy_input: str, language_hint: str = "auto") -> Dict[str, Any]:
        """
        Fast normalization without internet searches
        
        Args:
            fuzzy_input: The fuzzy/incorrect book title
            language_hint: Language hint for better processing
            
        Returns:
            Dictionary with normalization results
        """
        
        # Quick local normalization first (no Claude needed)
        quick_result = self._quick_normalize(fuzzy_input)
        
        # If cognitive layer is disabled, return quick result
        if not self.use_cognitive:
            return quick_result
        
        # Build fast cognitive prompt (no internet search)
        prompt = self._build_fast_prompt(fuzzy_input, language_hint)
        
        try:
            # Call Claude with short timeout
            result = subprocess.run([
                self.claude_command,
                "-p", prompt
            ], capture_output=True, text=True, timeout=self.timeout)
            
            if result.returncode != 0:
                # Fallback to quick normalization
                return quick_result
            
            # Parse Claude response
            return self._parse_fast_response(result.stdout, fuzzy_input, quick_result)
            
        except subprocess.TimeoutExpired:
            # On timeout, return quick normalization
            quick_result["timeout"] = True
            return quick_result
        except Exception as e:
            # On any error, return quick normalization
            quick_result["error"] = str(e)
            return quick_result
    
    def _quick_normalize(self, fuzzy_input: str) -> Dict[str, Any]:
        """Quick local normalization without Claude"""
        
        # Basic cleaning
        normalized = fuzzy_input.strip()
        
        # Fix common misspellings
        replacements = {
            'poter': 'potter',
            'hary': 'harry',
            'filosofer': "philosopher's",
            'teh': 'the',
            'grate': 'great',
            'programing': 'programming',
            'beginers': 'beginners',
            'jorj': 'george',
            'orwell': 'orwell',
            'malenkiy': 'маленький',
            'prinz': 'принц',
            'norvegski': 'норвежский',
            'les': 'лес'
        }
        
        words = normalized.lower().split()
        fixed_words = []
        problems_found = []
        
        for word in words:
            if word in replacements:
                fixed_words.append(replacements[word])
                problems_found.append(f"Fixed: {word} -> {replacements[word]}")
            else:
                fixed_words.append(word)
        
        # Capitalize properly
        normalized_title = ' '.join(fixed_words).title()
        
        # Detect language
        has_cyrillic = any(ord(c) >= 0x0400 and ord(c) <= 0x04FF for c in fuzzy_input)
        language = "russian" if has_cyrillic else "english"
        
        return {
            "success": True,
            "original": fuzzy_input,
            "normalized_title": normalized_title,
            "language": language,
            "confidence": 0.6 if problems_found else 0.8,
            "problems_found": problems_found,
            "method": "quick_local"
        }
    
    def _build_fast_prompt(self, fuzzy_input: str, language_hint: str) -> str:
        """Build fast cognitive prompt without internet search"""
        
        return f"""Fix this book title and author. Return ONLY valid JSON.

Input: "{fuzzy_input}"

Fix ONLY these issues (DO NOT search internet):
- Spelling errors
- Missing punctuation
- Capitalization
- Complete the author name if partially given

Return this JSON:
{{
  "title": "corrected title",
  "author": "author name if detected",
  "language": "detected language",
  "confidence": 0.0-1.0,
  "fixes": ["list of corrections made"]
}}

Examples:
"hary poter" -> {{"title": "Harry Potter", "author": "", "language": "english", "confidence": 0.9, "fixes": ["Fixed spelling: hary->harry, poter->potter"]}}
"1984 orwell" -> {{"title": "1984", "author": "George Orwell", "language": "english", "confidence": 0.95, "fixes": ["Completed author name"]}}"""
    
    def _parse_fast_response(self, response: str, original: str, fallback: Dict) -> Dict[str, Any]:
        """Parse Claude's fast response"""
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                
                # Build result
                result = {
                    "success": True,
                    "original": original,
                    "normalized_title": data.get("title", original),
                    "author": data.get("author", ""),
                    "language": data.get("language", "unknown"),
                    "confidence": float(data.get("confidence", 0.5)),
                    "problems_found": data.get("fixes", []),
                    "method": "claude_cognitive_fast"
                }
                
                # Combine title and author for search string
                if result["author"]:
                    result["search_string"] = f"{result['normalized_title']} {result['author']}"
                else:
                    result["search_string"] = result["normalized_title"]
                
                return result
        except:
            pass
        
        # If parsing fails, return fallback
        fallback["parse_error"] = True
        return fallback


class SimpleNormalizer:
    """Ultra-fast normalizer without any Claude calls"""
    
    @staticmethod
    def normalize(text: str) -> Dict[str, Any]:
        """Instant normalization using only local rules"""
        
        # Common book title corrections
        corrections = {
            # Harry Potter
            r'\bhary\b': 'harry',
            r'\bpoter\b': 'potter',
            r'\bfilosofer\b': "philosopher's",
            r'\bsorcerers?\b': "sorcerer's",
            
            # Common words
            r'\bteh\b': 'the',
            r'\bgrate\b': 'great',
            r'\bprograming\b': 'programming',
            r'\bbeginers?\b': 'beginners',
            r'\bpyton\b': 'python',
            
            # Authors
            r'\bjk\s*rowling\b': 'J.K. Rowling',
            r'\borwell\b': 'George Orwell',
            r'\bmartin\b': 'Robert Martin',
            
            # Russian transliterations
            r'\bmalenkiy\b': 'маленький',
            r'\bprinz\b': 'принц',
            r'\bvedmak\b': 'ведьмак',
        }
        
        normalized = text.strip()
        fixes = []
        
        # Apply corrections
        for pattern, replacement in corrections.items():
            if re.search(pattern, normalized, re.IGNORECASE):
                normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
                fixes.append(f"{pattern} -> {replacement}")
        
        # Proper capitalization
        words = normalized.split()
        capitalized = []
        for i, word in enumerate(words):
            if i == 0 or len(word) > 2:
                capitalized.append(word.capitalize())
            else:
                capitalized.append(word.lower())
        
        final = ' '.join(capitalized)
        
        return {
            "success": True,
            "original": text,
            "normalized": final,
            "confidence": 0.7 if fixes else 0.9,
            "fixes": fixes,
            "method": "local_rules_only"
        }


# Convenience function for fast normalization
def fast_normalize(text: str, use_cognitive: bool = True, timeout: int = 5) -> str:
    """
    Convenience function for quick normalization
    
    Args:
        text: Text to normalize
        use_cognitive: Use Claude cognitive layer (default: True)
        timeout: Timeout in seconds (default: 5)
    
    Returns:
        Normalized string
    """
    if use_cognitive:
        normalizer = ClaudeSDKNormalizerFast(use_cognitive=True, timeout=timeout)
        result = normalizer.normalize_book_title(text)
        return result.get("normalized_title", text) if result.get("success") else text
    else:
        result = SimpleNormalizer.normalize(text)
        return result.get("normalized", text)


if __name__ == "__main__":
    # Test examples
    import time
    
    test_cases = [
        "hary poter and filosofer stone",
        "teh grate gatsby",
        "1984 orwell",
        "python programing for beginers",
        "clean code robert martin",
        "malenkiy prinz",
        "vedmak sapkovski"
    ]
    
    print("=" * 80)
    print("FAST NORMALIZATION TESTS")
    print("=" * 80)
    
    # Test with cognitive layer
    print("\n1. WITH COGNITIVE LAYER (Claude):")
    print("-" * 40)
    normalizer = ClaudeSDKNormalizerFast(use_cognitive=True, timeout=5)
    
    for test in test_cases[:3]:  # Test first 3 with Claude
        start = time.time()
        result = normalizer.normalize_book_title(test)
        elapsed = time.time() - start
        
        print(f"\nInput: {test}")
        print(f"Output: {result.get('normalized_title', test)}")
        print(f"Method: {result.get('method', 'unknown')}")
        print(f"Confidence: {result.get('confidence', 0):.1%}")
        print(f"Time: {elapsed:.2f}s")
    
    # Test without cognitive layer (instant)
    print("\n\n2. WITHOUT COGNITIVE LAYER (Local only):")
    print("-" * 40)
    normalizer_fast = ClaudeSDKNormalizerFast(use_cognitive=False)
    
    for test in test_cases:
        start = time.time()
        result = normalizer_fast.normalize_book_title(test)
        elapsed = time.time() - start
        
        print(f"\nInput: {test}")
        print(f"Output: {result.get('normalized_title', test)}")
        print(f"Confidence: {result.get('confidence', 0):.1%}")
        print(f"Time: {elapsed:.4f}s")
    
    # Test ultra-fast local-only
    print("\n\n3. ULTRA-FAST (SimpleNormalizer):")
    print("-" * 40)
    
    for test in test_cases:
        start = time.time()
        result = SimpleNormalizer.normalize(test)
        elapsed = time.time() - start
        
        print(f"\nInput: {test}")
        print(f"Output: {result.get('normalized', test)}")
        print(f"Time: {elapsed:.6f}s")