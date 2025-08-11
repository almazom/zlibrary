#!/usr/bin/env python3
"""
Claude-powered URL content extractor for book information
Uses Claude SDK to fetch and extract structured book data from URLs
"""

import json
import sys
import yaml
import subprocess
from urllib.parse import urlparse
from pathlib import Path

def load_prompts():
    """Load extraction prompts from YAML config"""
    config_path = Path(__file__).parent.parent / "config" / "extraction_prompts.yaml"
    
    if not config_path.exists():
        return {}
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_prompt_for_url(url, prompts_config):
    """Select appropriate prompt based on URL domain"""
    parsed = urlparse(url)
    domain = parsed.netloc.lower().replace('www.', '')
    
    # Check each configured service
    for service, config in prompts_config.items():
        if service == 'generic':
            continue
        if 'domains' in config:
            for configured_domain in config['domains']:
                if configured_domain in domain:
                    return config['prompt']
    
    # Fallback to generic prompt
    return prompts_config.get('generic', {}).get('prompt', 
        'Extract book information: title, author, year, description. Return as JSON.')

def extract_with_claude(url, prompt):
    """Use Claude CLI to extract information from URL"""
    try:
        # Build the Claude command
        # Using claude -p to pass the prompt and URL
        cmd = [
            'claude', '-p',
            f'Fetch this URL and extract book information: {url}\n\n{prompt}'
        ]
        
        # Execute Claude CLI
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return {
                "error": "claude_cli_failed",
                "message": result.stderr or "Failed to run Claude CLI"
            }
        
        # Parse the response
        response = result.stdout.strip()
        
        # Try to extract JSON from the response
        # Claude might return markdown code blocks
        if '```json' in response:
            start = response.find('```json') + 7
            end = response.find('```', start)
            response = response[start:end].strip()
        elif '```' in response:
            start = response.find('```') + 3
            end = response.find('```', start)
            response = response[start:end].strip()
        
        # Parse JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON object in the response
            import re
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {
                "error": "json_parse_failed",
                "message": "Could not parse JSON from Claude response",
                "raw_response": response[:500]
            }
            
    except subprocess.TimeoutExpired:
        return {
            "error": "timeout",
            "message": "Claude CLI timed out"
        }
    except FileNotFoundError:
        return {
            "error": "claude_not_found",
            "message": "Claude CLI not found. Please install: npm install -g @anthropic-ai/claude-cli"
        }
    except Exception as e:
        return {
            "error": "extraction_failed",
            "message": str(e)
        }

def extract_with_direct_api(url, prompt):
    """Alternative: Use direct API call if Claude CLI is not available"""
    import os
    import requests
    
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return {
            "error": "no_api_key",
            "message": "ANTHROPIC_API_KEY not set"
        }
    
    try:
        # First fetch the webpage content
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; BookExtractor/1.0)'
        })
        response.raise_for_status()
        
        # Send to Claude API
        api_response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json'
            },
            json={
                'model': 'claude-3-haiku-20240307',
                'max_tokens': 1000,
                'messages': [{
                    'role': 'user',
                    'content': f"Here is a webpage content:\n\n{response.text[:10000]}\n\n{prompt}"
                }]
            },
            timeout=30
        )
        api_response.raise_for_status()
        
        result = api_response.json()
        content = result['content'][0]['text']
        
        # Parse JSON from response
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {
                "error": "json_parse_failed",
                "message": "Could not parse JSON from API response"
            }
            
    except Exception as e:
        return {
            "error": "api_failed",
            "message": str(e)
        }

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "no_url",
            "message": "Usage: claude_url_extractor.py <URL>"
        }))
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Load prompts configuration
    prompts = load_prompts()
    
    # Get appropriate prompt for URL
    prompt = get_prompt_for_url(url, prompts)
    
    # Try Claude CLI first
    result = extract_with_claude(url, prompt)
    
    # If CLI fails, try direct API
    if result.get('error') == 'claude_not_found':
        result = extract_with_direct_api(url, prompt)
    
    # Output result
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()