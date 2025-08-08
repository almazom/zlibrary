#!/usr/bin/env python3
"""
Cognitive Validation Layer - Smart Intent vs Reality Check
Compares user request with actual EPUB metadata for intelligent matching
"""
import zipfile
import xml.etree.ElementTree as ET
import subprocess
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
import re

class CognitiveValidator:
    """
    Smart validation layer that thinks about user satisfaction
    - Extracts real EPUB metadata
    - Compares with user intent
    - Calculates confidence scores
    - Provides intelligent recommendations
    """
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.last_validation = {}
    
    def extract_epub_metadata(self, epub_path: str) -> Dict[str, Any]:
        """
        Extract actual metadata from EPUB file
        """
        metadata = {
            "title": "",
            "author": "",
            "language": "",
            "publisher": "",
            "description": "",
            "subjects": [],
            "isbn": "",
            "publication_date": "",
            "extracted": False
        }
        
        try:
            with zipfile.ZipFile(epub_path, 'r') as epub:
                # Find OPF file (contains metadata)
                opf_path = None
                
                # First check container.xml for OPF location
                if 'META-INF/container.xml' in epub.namelist():
                    container = epub.read('META-INF/container.xml')
                    root = ET.fromstring(container)
                    
                    # Find rootfile element
                    for rootfile in root.iter('{urn:oasis:names:tc:opendocument:xmlns:container}rootfile'):
                        opf_path = rootfile.get('full-path')
                        break
                
                # Fallback: search for .opf file
                if not opf_path:
                    for file in epub.namelist():
                        if file.endswith('.opf'):
                            opf_path = file
                            break
                
                if opf_path and opf_path in epub.namelist():
                    opf_content = epub.read(opf_path)
                    opf_root = ET.fromstring(opf_content)
                    
                    # Extract metadata from Dublin Core elements
                    ns = {'dc': 'http://purl.org/dc/elements/1.1/'}
                    
                    # Title
                    title_elem = opf_root.find('.//dc:title', ns)
                    if title_elem is not None:
                        metadata["title"] = title_elem.text or ""
                    
                    # Author(s)
                    authors = []
                    for creator in opf_root.findall('.//dc:creator', ns):
                        if creator.text:
                            authors.append(creator.text)
                    metadata["author"] = ", ".join(authors)
                    
                    # Language
                    lang_elem = opf_root.find('.//dc:language', ns)
                    if lang_elem is not None:
                        metadata["language"] = lang_elem.text or ""
                    
                    # Publisher
                    pub_elem = opf_root.find('.//dc:publisher', ns)
                    if pub_elem is not None:
                        metadata["publisher"] = pub_elem.text or ""
                    
                    # Description
                    desc_elem = opf_root.find('.//dc:description', ns)
                    if desc_elem is not None:
                        metadata["description"] = desc_elem.text or ""
                    
                    # Subjects/Tags
                    for subject in opf_root.findall('.//dc:subject', ns):
                        if subject.text:
                            metadata["subjects"].append(subject.text)
                    
                    # ISBN
                    for identifier in opf_root.findall('.//dc:identifier', ns):
                        if identifier.text and 'isbn' in identifier.get('opf:scheme', '').lower():
                            metadata["isbn"] = identifier.text
                            break
                    
                    # Publication date
                    date_elem = opf_root.find('.//dc:date', ns)
                    if date_elem is not None:
                        metadata["publication_date"] = date_elem.text or ""
                    
                    metadata["extracted"] = True
                    
        except Exception as e:
            if self.verbose:
                print(f"⚠️ Metadata extraction error: {e}")
        
        return metadata
    
    def fast_smart_comparison(self, user_request: str, epub_path: str) -> Dict[str, Any]:
        """
        Fast and smart comparison - simple matching first, AI only for ambiguous cases
        """
        # Extract actual EPUB metadata
        metadata = self.extract_epub_metadata(epub_path)
        
        if not metadata["extracted"]:
            return {
                "confidence": 0.3,
                "match_quality": "unknown",
                "analysis": "Could not extract EPUB metadata",
                "recommendation": "manual_check"
            }
        
        # Fast path: Try simple comparison first
        validation = self.enhanced_simple_comparison(user_request, metadata)
        
        # If confidence is very high or very low, we're done (fast path)
        if validation["confidence"] >= 0.85 or validation["confidence"] <= 0.15:
            return validation
        
        # Ambiguous case (0.15 < confidence < 0.85) - use AI for better analysis
        # But only if not already clear from metadata
        if self.needs_ai_analysis(user_request, metadata):
            try:
                # Keep prompt minimal for speed
                comparison_prompt = f'Is "{metadata["title"]}" by {metadata["author"]} what user wants when searching for "{user_request}"? Reply: exact/good/partial/poor'
                
                result = subprocess.run([
                    "/home/almaz/.claude/local/claude",
                    "-p", comparison_prompt,
                    "--output-format", "json"
                ], capture_output=True, text=True, timeout=3)  # Fast 3 second timeout
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    content = data.get('result', '').lower()
                    
                    if 'exact' in content:
                        validation["match_quality"] = "exact"
                        validation["confidence"] = 0.95
                    elif 'good' in content:
                        validation["match_quality"] = "good"
                        validation["confidence"] = 0.75
                    elif 'partial' in content:
                        validation["match_quality"] = "partial"
                        validation["confidence"] = 0.5
                    elif 'poor' in content:
                        validation["match_quality"] = "poor"
                        validation["confidence"] = 0.2
                    
                    validation["intelligent_match"] = True
                    validation["recommendation"] = "download" if validation["confidence"] > 0.6 else "warn_user"
                    
            except Exception:
                pass  # Keep simple comparison result
        
        return validation
    
    def cognitive_comparison(self, user_request: str, epub_path: str) -> Dict[str, Any]:
        """
        Smart comparison with fast path optimization
        """
        return self.fast_smart_comparison(user_request, epub_path)
    
    def enhanced_simple_comparison(self, user_request: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced simple comparison - fast and smart without AI
        """
        user_lower = user_request.lower()
        title_lower = metadata.get("title", "").lower()
        author_lower = metadata.get("author", "").lower()
        
        # Clean and normalize for better matching
        import unicodedata
        def normalize(text):
            # Remove accents and normalize
            text = unicodedata.normalize('NFD', text)
            text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
            # Remove punctuation for matching
            text = re.sub(r'[^\w\s]', ' ', text)
            return text.lower().strip()
        
        user_norm = normalize(user_lower)
        title_norm = normalize(title_lower)
        author_norm = normalize(author_lower)
        
        confidence = 0.0
        exact_matches = 0
        partial_matches = 0
        
        # Split into meaningful words (skip short ones)
        user_words = [w for w in user_norm.split() if len(w) > 2]
        title_words = [w for w in title_norm.split() if len(w) > 2]
        author_words = [w for w in author_norm.split() if len(w) > 2]
        
        # Check for exact title match
        if title_norm and user_norm:
            if title_norm == user_norm:
                confidence = 0.95
                exact_matches += 1
            elif title_norm in user_norm or user_norm in title_norm:
                confidence = 0.8
                partial_matches += 1
        
        # Check author match (high weight)
        if author_words and user_words:
            author_match_count = sum(1 for w in author_words if w in user_words)
            if author_match_count >= len(author_words) * 0.8:  # 80% of author words match
                confidence += 0.4
                exact_matches += 1
            elif author_match_count > 0:
                confidence += 0.2 * (author_match_count / len(author_words))
                partial_matches += 1
        
        # Check title word matches
        if title_words and user_words and confidence < 0.8:
            title_match_count = sum(1 for w in title_words if w in user_words)
            if title_match_count >= len(title_words) * 0.7:  # 70% of title words match
                confidence += 0.3
                partial_matches += 1
            elif title_match_count > 0:
                confidence += 0.15 * (title_match_count / len(title_words))
                partial_matches += 1
        
        # Check reverse - are user words in title?
        if user_words and title_words and confidence < 0.7:
            user_in_title = sum(1 for w in user_words if w in title_words)
            if user_in_title >= len(user_words) * 0.8:
                confidence += 0.2
                partial_matches += 1
        
        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)
        
        # Determine match quality based on confidence and match types
        if exact_matches > 0 and confidence >= 0.8:
            match_quality = "exact"
        elif confidence >= 0.7:
            match_quality = "good"
        elif confidence >= 0.4:
            match_quality = "partial"
        else:
            match_quality = "poor"
        
        return {
            "confidence": confidence,
            "match_quality": match_quality,
            "analysis": f"Fast match: {confidence:.0%} confidence",
            "metadata": metadata,
            "user_request": user_request,
            "intelligent_match": False,
            "exact_matches": exact_matches,
            "partial_matches": partial_matches,
            "recommendation": "download" if confidence > 0.5 else "warn_user"
        }
    
    def needs_ai_analysis(self, user_request: str, metadata: Dict[str, Any]) -> bool:
        """
        Determine if we need AI for this comparison
        """
        # Skip AI if metadata is missing
        if not metadata.get("title") or not metadata.get("author"):
            return False
        
        # Skip AI if request is very short
        if len(user_request) < 5:
            return False
        
        # Need AI for complex requests with multiple authors or special characters
        if '&' in user_request or ',' in metadata.get("author", ""):
            return True
        
        # Need AI for requests that might be descriptions rather than titles
        if len(user_request.split()) > 7:
            return True
        
        return False
    
    def simple_comparison(self, user_request: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy simple comparison - redirects to enhanced version
        """
        return self.enhanced_simple_comparison(user_request, metadata)
    
    def validate_and_report(self, user_request: str, epub_path: str) -> Dict[str, Any]:
        """
        Complete validation with intelligent reporting
        """
        # Check if file exists
        if not Path(epub_path).exists():
            return {
                "valid": False,
                "error": "File not found",
                "confidence": 0.0
            }
        
        # Run cognitive comparison
        validation = self.cognitive_comparison(user_request, epub_path)
        
        # Generate smart feedback
        feedback = self.generate_smart_feedback(validation)
        validation["feedback"] = feedback
        
        self.last_validation = validation
        return validation
    
    def generate_smart_feedback(self, validation: Dict[str, Any]) -> str:
        """
        Generate intelligent user feedback based on validation
        """
        confidence = validation.get("confidence", 0)
        quality = validation.get("match_quality", "unknown")
        metadata = validation.get("metadata", {})
        
        if quality == "exact":
            return f"✅ Perfect match! Found exactly what you requested: {metadata.get('title', 'Book')}"
        
        elif quality == "good":
            return f"✅ Good match: {metadata.get('title', 'Book')} by {metadata.get('author', 'Author')}"
        
        elif quality == "partial":
            return f"⚠️ Partial match: Found '{metadata.get('title', 'Book')}' - may not be exactly what you wanted"
        
        elif quality == "poor":
            return f"⚠️ Poor match: '{metadata.get('title', 'Book')}' doesn't seem to match your request well"
        
        else:
            return f"❓ Uncertain match: Please verify this is the book you wanted"
    
    def print_validation_report(self, user_request: str, epub_path: str):
        """
        Print formatted validation report
        """
        validation = self.validate_and_report(user_request, epub_path)
        
        print("\n🧠 Cognitive Validation Report")
        print("=" * 50)
        print(f"User Request: {user_request}")
        print(f"File: {Path(epub_path).name}")
        
        metadata = validation.get("metadata", {})
        if metadata.get("extracted"):
            print("\n📚 EPUB Metadata:")
            print(f"  Title: {metadata.get('title', 'Unknown')}")
            print(f"  Author: {metadata.get('author', 'Unknown')}")
            print(f"  Language: {metadata.get('language', 'Unknown')}")
            
        print(f"\n🎯 Match Analysis:")
        print(f"  Confidence: {validation.get('confidence', 0):.0%}")
        print(f"  Quality: {validation.get('match_quality', 'unknown')}")
        print(f"  Method: {'Claude AI' if validation.get('intelligent_match') else 'Pattern matching'}")
        
        print(f"\n💡 Recommendation: {validation.get('recommendation', 'unknown')}")
        print(f"📝 Feedback: {validation.get('feedback', '')}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 2:
        validator = CognitiveValidator(verbose=True)
        user_request = sys.argv[1]
        epub_path = sys.argv[2]
        validator.print_validation_report(user_request, epub_path)