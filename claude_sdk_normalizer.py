#!/usr/bin/env python3
"""
CLAUDE SDK BOOK NORMALIZER - Real Claude SDK Integration with Feedback Loop
Uses subprocess to call Claude CLI directly with JSON structured output
"""
import subprocess
import json
import sys
import re
import yaml
import os
from typing import Dict, Any

class ClaudeSDKNormalizer:
    """Real Claude SDK integration for book title normalization"""
    
    def __init__(self):
        self.claude_command = "/home/almaz/.claude/local/claude"  # Full path to Claude CLI
        self.feedback_log = []  # Track normalization feedback
        self.prompts = self._load_prompts()  # Load prompts from YAML
        
    def normalize_book_title(self, fuzzy_input: str, language_hint: str = "auto") -> Dict[str, Any]:
        """
        Normalize book title using Claude SDK with structured JSON output
        
        Args:
            fuzzy_input: The fuzzy/incorrect book title
            language_hint: Language hint for better processing
            
        Returns:
            Dictionary with normalization results and feedback data
        """
        # Construct the prompt for Claude
        prompt = self._build_normalization_prompt(fuzzy_input, language_hint)
        
        try:
            # Call Claude CLI using subprocess
            result = subprocess.run([
                self.claude_command,
                "-p", prompt,
                "--output-format", "json"
            ], capture_output=True, text=True, timeout=self.prompts.get('timeout_settings', {}).get('default_timeout', 90))
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Claude CLI error: {result.stderr}",
                    "original": fuzzy_input
                }
            
            # Parse the Claude response
            response_data = json.loads(result.stdout)
            normalized_result = self._extract_normalization_result(response_data, fuzzy_input)
            
            # Add to feedback log
            self._log_feedback(fuzzy_input, normalized_result)
            
            return normalized_result
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Claude SDK timeout",
                "original": fuzzy_input
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {e}",
                "original": fuzzy_input
            }
    
    def _load_prompts(self) -> Dict[str, Any]:
        """Load prompts from YAML configuration file"""
        try:
            prompts_path = os.path.join(os.path.dirname(__file__), 'prompts', 'claude_normalization_prompts.yaml')
            with open(prompts_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Warning: Could not load prompts from YAML: {e}")
            # Fallback to minimal prompt
            return {
                "book_normalization": {
                    "main_prompt_template": "Normalize this book title: {fuzzy_input}",
                    "system_prompt": "You are a book normalizer."
                },
                "timeout_settings": {"default_timeout": 90}
            }
    
    def _build_normalization_prompt(self, fuzzy_input: str, language_hint: str) -> str:
        """Build the Claude normalization prompt from YAML configuration"""
        
        try:
            # Get the main prompt template from YAML
            main_template = self.prompts['book_normalization']['main_prompt_template']
            
            # Format the template with input parameters
            prompt = main_template.format(
                fuzzy_input=fuzzy_input,
                language_hint=language_hint
            )
            
            # Add language-specific instructions if needed
            if self._is_cyrillic(fuzzy_input):
                if 'language_specific' in self.prompts and 'russian' in self.prompts['language_specific']:
                    prompt += "\n\n" + self.prompts['language_specific']['russian'].get('additional_instructions', '')
            
            return prompt
            
        except Exception as e:
            print(f"Warning: Error building prompt from YAML: {e}")
            # Fallback to simple prompt
            return f"Normalize this book title and return JSON: '{fuzzy_input}'"

    def _extract_normalization_result(self, claude_response: Dict, original_input: str) -> Dict[str, Any]:
        """Extract and validate normalization result from Claude response"""
        
        try:
            # Claude returns result in 'result' field
            result_text = claude_response.get('result', '')
            
            # Extract JSON from markdown code blocks if present
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', result_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON without code blocks
                json_match = re.search(r'(\{.*\})', result_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    raise ValueError("No JSON found in Claude response")
            
            # Parse the JSON
            normalized_data = json.loads(json_str)
            
            # Validate required fields for new bilingual structure
            required_fields = ['original_input', 'normalized_query', 'confidence']
            for field in required_fields:
                if field not in normalized_data:
                    if field == 'original_input':
                        normalized_data[field] = original_input
                    elif field == 'normalized_query':
                        normalized_data[field] = original_input
                    else:
                        normalized_data[field] = 0.0
            
            # Ensure bilingual sections exist
            if 'original_language_version' not in normalized_data:
                normalized_data['original_language_version'] = {"title": "", "author": "", "language_code": "unknown"}
            if 'russian_language_version' not in normalized_data:
                normalized_data['russian_language_version'] = {"title": "", "author": "", "translation_available": False}
            
            # Add success flag and metadata
            normalized_data['success'] = True
            normalized_data['method'] = 'claude_sdk'
            normalized_data['timestamp'] = subprocess.run(['date', '-Iseconds'], 
                                                         capture_output=True, text=True).stdout.strip()
            
            return normalized_data
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to parse Claude response: {e}",
                "original": original_input,
                "raw_response": str(claude_response)
            }
    
    def _is_cyrillic(self, text: str) -> bool:
        """Check if text contains Cyrillic characters"""
        return bool(re.search(r'[а-яёА-ЯЁ]', text))
    
    def _log_feedback(self, original: str, result: Dict[str, Any]):
        """Log normalization feedback for development iteration"""
        
        feedback_entry = {
            "timestamp": result.get('timestamp', 'unknown'),
            "original": original,
            "normalized": result.get('normalized_query', ''),
            "confidence": result.get('confidence', 0.0),
            "problems_found": result.get('problems_found', []),
            "original_language_title": result.get('original_language_version', {}).get('title', ''),
            "russian_language_title": result.get('russian_language_version', {}).get('title', ''),
            "internet_research": result.get('internet_research', {}).get('found_book', False),
            "success": result.get('success', False)
        }
        
        self.feedback_log.append(feedback_entry)
        
        # Keep only last 100 entries
        if len(self.feedback_log) > 100:
            self.feedback_log = self.feedback_log[-100:]
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """Get feedback statistics for development iteration"""
        
        if not self.feedback_log:
            return {"total_normalizations": 0}
        
        successful = sum(1 for entry in self.feedback_log if entry['success'])
        total = len(self.feedback_log)
        avg_confidence = sum(entry['confidence'] for entry in self.feedback_log) / total
        
        # Most common problems
        all_problems = []
        for entry in self.feedback_log:
            all_problems.extend(entry.get('problems_found', []))
        
        problem_counts = {}
        for problem in all_problems:
            problem_counts[problem] = problem_counts.get(problem, 0) + 1
        
        return {
            "total_normalizations": total,
            "success_rate": successful / total if total > 0 else 0.0,
            "average_confidence": avg_confidence if total > 0 else 0.0,
            "common_problems": sorted(problem_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "recent_entries": self.feedback_log[-5:]  # Last 5 for review
        }
    
    def feedback_development_iteration(self, test_cases: list) -> Dict[str, Any]:
        """Run feedback development iteration on test cases"""
        
        print("\n🔄 FEEDBACK DEVELOPMENT ITERATION")
        print("="*60)
        
        results = []
        
        for test_case in test_cases:
            if isinstance(test_case, tuple):
                fuzzy_input, expected = test_case
            else:
                fuzzy_input, expected = test_case, None
            
            print(f"\n🧪 Testing: '{fuzzy_input}'")
            result = self.normalize_book_title(fuzzy_input)
            
            if result['success']:
                print(f"✅ Normalized: '{result.get('normalized_query', 'N/A')}'")
                print(f"📊 Confidence: {result['confidence']:.0%}")
                
                # Show bilingual results
                orig_lang = result.get('original_language_version', {})
                rus_lang = result.get('russian_language_version', {})
                
                if orig_lang.get('title'):
                    print(f"🌍 Original: {orig_lang['title']} - {orig_lang.get('author', 'Unknown')} ({orig_lang.get('language_code', 'unknown')})")
                if rus_lang.get('title'):
                    print(f"🇷🇺 Russian: {rus_lang['title']} - {rus_lang.get('author', 'Unknown')}")
                
                # Internet research info
                research = result.get('internet_research', {})
                if research.get('found_book'):
                    print(f"🔍 Internet research: Found book information")
                
                if expected and result.get('normalized_query', '').lower() == expected.lower():
                    print("🎯 Matches expected result!")
                elif expected:
                    print(f"⚠️  Expected: '{expected}', got: '{result.get('normalized_query', 'N/A')}'")
            else:
                print(f"❌ Failed: {result['error']}")
            
            results.append(result)
        
        # Generate feedback stats
        stats = self.get_feedback_stats()
        
        print(f"\n📈 FEEDBACK STATISTICS:")
        print(f"  • Total normalizations: {stats['total_normalizations']}")
        print(f"  • Success rate: {stats['success_rate']:.0%}")
        print(f"  • Average confidence: {stats['average_confidence']:.0%}")
        print(f"  • Common problems: {', '.join([p[0] for p in stats['common_problems'][:3]])}")
        
        return {
            "test_results": results,
            "feedback_stats": stats,
            "iteration_complete": True
        }


async def test_claude_sdk_normalization():
    """Test the Claude SDK normalizer with Russian examples"""
    
    normalizer = ClaudeSDKNormalizer()
    
    # Test cases focusing on Russian titles
    test_cases = [
        ("ведмак 3 дикая охота", "ведьмак 3: дикая охота"),
        ("метро2033 глуховски", "метро 2033 глуховский"),
        ("вайна и мир", "война и мир"),
        ("hary poter", "harry potter"),
        ("пелевин generation п", "generation п пелевин"),
        ("санкя прилепин", "санькя прилепин"),
    ]
    
    print("\n🚀 CLAUDE SDK BOOK NORMALIZER TEST")
    print("="*60)
    
    # Run feedback development iteration
    results = normalizer.feedback_development_iteration(test_cases)
    
    return results


if __name__ == "__main__":
    import asyncio
    
    if len(sys.argv) > 1:
        # Normalize single input from command line
        fuzzy_input = ' '.join(sys.argv[1:])
        normalizer = ClaudeSDKNormalizer()
        
        print(f"\n🔍 Normalizing: '{fuzzy_input}'")
        result = normalizer.normalize_book_title(fuzzy_input)
        
        print("\n📋 Result:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # Run test cases
        asyncio.run(test_claude_sdk_normalization())