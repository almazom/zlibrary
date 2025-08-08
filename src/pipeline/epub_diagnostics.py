#!/usr/bin/env python3
"""
EPUB Diagnostics & Smart Renaming Pipeline Layer
Validates EPUBs and creates Linux-friendly filenames
"""
import os
import zipfile
import hashlib
import re
from typing import Dict, Any, Optional
from pathlib import Path

class EPUBDiagnostics:
    """
    Diagnostic layer for EPUB validation and smart renaming
    Features:
    - EPUB structure validation
    - Cyrillic to Latin transliteration 
    - Linux-safe filename generation
    - Quality reporting
    """
    
    # Cyrillic to Latin mapping
    TRANSLIT_MAP = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
        'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '',
        'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D',
        'Е': 'E', 'Ё': 'Yo', 'Ж': 'Zh', 'З': 'Z', 'И': 'I',
        'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
        'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T',
        'У': 'U', 'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch',
        'Ш': 'Sh', 'Щ': 'Sch', 'Ъ': '', 'Ы': 'Y', 'Ь': '',
        'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.last_diagnostic = {}
    
    def validate_epub(self, filepath: str) -> Dict[str, Any]:
        """
        Validate EPUB file structure and content
        
        Returns:
            Dict with validation results
        """
        diagnostic = {
            "valid": False,
            "is_epub": False,
            "is_html_error": False,
            "size": 0,
            "error": None,
            "structure": {},
            "quality_score": 0.0
        }
        
        try:
            filepath = Path(filepath)
            if not filepath.exists():
                diagnostic["error"] = "File not found"
                return diagnostic
            
            diagnostic["size"] = filepath.stat().st_size
            
            # Check if it's a ZIP (EPUB)
            try:
                with zipfile.ZipFile(filepath, 'r') as epub:
                    files = epub.namelist()
                    diagnostic["is_epub"] = True
                    
                    # Check essential EPUB files
                    has_container = 'META-INF/container.xml' in files
                    has_mimetype = 'mimetype' in files
                    
                    # Check mimetype content
                    valid_mimetype = False
                    if has_mimetype:
                        mimetype = epub.read('mimetype').decode('utf-8').strip()
                        valid_mimetype = (mimetype == 'application/epub+zip')
                    
                    # Count content types
                    html_files = len([f for f in files if f.endswith(('.html', '.xhtml', '.htm'))])
                    image_files = len([f for f in files if f.endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg'))])
                    css_files = len([f for f in files if f.endswith('.css')])
                    
                    diagnostic["structure"] = {
                        "total_files": len(files),
                        "has_container": has_container,
                        "has_mimetype": has_mimetype,
                        "valid_mimetype": valid_mimetype,
                        "html_files": html_files,
                        "image_files": image_files,
                        "css_files": css_files
                    }
                    
                    # Calculate quality score
                    score = 0.0
                    if has_container: score += 0.25
                    if has_mimetype: score += 0.25
                    if valid_mimetype: score += 0.25
                    if html_files > 0: score += 0.15
                    if css_files > 0: score += 0.10
                    
                    diagnostic["quality_score"] = score
                    diagnostic["valid"] = score >= 0.75
                    
            except zipfile.BadZipFile:
                # Not a ZIP file - check if HTML error page
                with open(filepath, 'rb') as f:
                    content = f.read(1000)
                    if b'<!DOCTYPE html' in content or b'<html' in content:
                        diagnostic["is_html_error"] = True
                        diagnostic["error"] = "HTML error page instead of EPUB"
                        
                        # Check for common error messages
                        if b'daily limit' in content.lower() or b'limit reached' in content.lower():
                            diagnostic["error"] = "Download limit reached"
                        elif b'not found' in content.lower() or b'404' in content:
                            diagnostic["error"] = "Book not found"
                    else:
                        diagnostic["error"] = "Invalid file format"
            
        except Exception as e:
            diagnostic["error"] = str(e)
        
        self.last_diagnostic = diagnostic
        return diagnostic
    
    def transliterate(self, text: str) -> str:
        """
        Transliterate Cyrillic to Latin for Linux-safe filenames
        
        Args:
            text: Original text with possible Cyrillic
            
        Returns:
            Latin-only text
        """
        result = []
        for char in text:
            if char in self.TRANSLIT_MAP:
                result.append(self.TRANSLIT_MAP[char])
            else:
                result.append(char)
        return ''.join(result)
    
    def create_safe_filename(self, original_name: str, keep_extension: bool = True) -> str:
        """
        Create download-friendly filename following best practices:
        
        BEST PRACTICES:
        1. Replace spaces with underscores (URL/download safe)
        2. Transliterate non-ASCII characters (Cyrillic, accents, etc.)
        3. Remove special characters that cause issues in URLs/shells
        4. Avoid dots except for extension (prevents hidden files)
        5. Limit length to prevent filesystem issues
        6. Ensure web-safe and shell-safe naming
        
        Args:
            original_name: Original filename (may contain spaces, Cyrillic, etc.)
            keep_extension: Preserve file extension
            
        Returns:
            Download-friendly filename for web, Linux, Windows
        """
        # Extract extension if needed
        extension = ''
        if keep_extension and '.' in original_name:
            name, extension = os.path.splitext(original_name)
        else:
            name = original_name
        
        # Transliterate Cyrillic and other non-ASCII
        safe_name = self.transliterate(name)
        
        # BEST PRACTICE #1: Replace ALL spaces with underscores
        # Spaces cause issues in URLs, downloads, and command lines
        safe_name = safe_name.replace(' ', '_')
        
        # Remove dots to prevent hidden files and confusion
        safe_name = safe_name.replace('.', '_')
        
        # Remove special characters (keep only alphanumeric, underscore, dash)
        # This ensures compatibility with URLs, shells, and filesystems
        safe_name = re.sub(r'[^\w\-]', '_', safe_name)
        
        # Clean up multiple underscores
        safe_name = re.sub(r'_+', '_', safe_name)
        
        # Trim underscores and dashes from ends
        safe_name = safe_name.strip('_-')
        
        # Limit length (100 chars is safe for most systems)
        if len(safe_name) > 100:
            safe_name = safe_name[:100].rstrip('_-')
        
        # If name is empty after cleaning, generate one
        if not safe_name:
            safe_name = f"book_{hashlib.md5(original_name.encode()).hexdigest()[:8]}"
        
        # Add extension back
        if extension:
            safe_name += extension
        
        return safe_name
    
    def rename_if_needed(self, filepath: str, force: bool = False) -> Optional[str]:
        """
        Rename file following best practices for download-friendly names
        
        BEST PRACTICES CHECKED:
        - Spaces in filename (causes URL/download issues)
        - Non-ASCII characters (causes encoding issues)
        - Special characters (causes shell/filesystem issues)
        - Multiple dots (can create hidden files)
        
        Args:
            filepath: Current file path
            force: Force rename even if already safe
            
        Returns:
            New filepath if renamed, None if not needed
        """
        filepath = Path(filepath)
        original_name = filepath.name
        
        # BEST PRACTICE CHECKS - Always rename if:
        has_spaces = ' ' in original_name  # Spaces break URLs and downloads
        has_cyrillic = any(c in original_name for c in self.TRANSLIT_MAP.keys())
        has_non_ascii = any(ord(c) > 127 for c in original_name)
        has_unsafe = bool(re.search(r'[^\w\s\-\.]', original_name))
        has_multiple_dots = original_name.count('.') > 1  # Can cause confusion
        
        # Always rename files with spaces or problematic characters
        needs_rename = has_spaces or has_cyrillic or has_non_ascii or has_unsafe or has_multiple_dots
        
        if not force and not needs_rename:
            return None
        
        # Create safe name following best practices
        safe_name = self.create_safe_filename(original_name)
        
        # Don't rename if result is the same
        if safe_name == original_name:
            return None
        
        # Create new path
        new_path = filepath.parent / safe_name
        
        # Handle conflicts
        counter = 1
        while new_path.exists():
            name, ext = os.path.splitext(safe_name)
            new_path = filepath.parent / f"{name}_{counter}{ext}"
            counter += 1
        
        # Rename file
        filepath.rename(new_path)
        
        if self.verbose:
            reasons = []
            if has_spaces: reasons.append("spaces→underscores")
            if has_cyrillic or has_non_ascii: reasons.append("transliterated")
            if has_unsafe: reasons.append("special chars removed")
            reason_str = f" ({', '.join(reasons)})" if reasons else ""
            print(f"📝 Renamed{reason_str}: {original_name} → {new_path.name}")
        
        return str(new_path)
    
    def process_download(self, filepath: str) -> Dict[str, Any]:
        """
        Complete diagnostic and renaming pipeline
        
        Args:
            filepath: Downloaded file path
            
        Returns:
            Processing results with diagnostics and new path
        """
        result = {
            "original_path": filepath,
            "new_path": filepath,
            "renamed": False,
            "diagnostic": {},
            "success": False,
            "recommendations": []
        }
        
        # Run diagnostics
        diagnostic = self.validate_epub(filepath)
        result["diagnostic"] = diagnostic
        
        # Check if valid EPUB
        if diagnostic["valid"]:
            result["success"] = True
            
            # Rename if needed
            new_path = self.rename_if_needed(filepath)
            if new_path:
                result["new_path"] = new_path
                result["renamed"] = True
            
            # Add quality recommendations
            if diagnostic["quality_score"] < 1.0:
                if not diagnostic["structure"].get("css_files"):
                    result["recommendations"].append("Missing CSS styling")
                if not diagnostic["structure"].get("image_files"):
                    result["recommendations"].append("No images found")
        
        elif diagnostic["is_html_error"]:
            result["recommendations"].append(f"Error: {diagnostic['error']}")
            if "limit" in diagnostic["error"].lower():
                result["recommendations"].append("Wait for daily limit reset or use different account")
        
        else:
            result["recommendations"].append("Invalid EPUB format")
        
        return result
    
    def print_diagnostic_report(self, filepath: str):
        """
        Print formatted diagnostic report
        """
        result = self.process_download(filepath)
        
        print("\n📚 EPUB Diagnostic Report")
        print("=" * 50)
        print(f"File: {Path(filepath).name}")
        print(f"Size: {result['diagnostic']['size']:,} bytes")
        
        if result["success"]:
            print("✅ Status: Valid EPUB")
            print(f"📊 Quality Score: {result['diagnostic']['quality_score']:.0%}")
            
            structure = result['diagnostic']['structure']
            print("\n📁 Structure:")
            print(f"  • Total Files: {structure['total_files']}")
            print(f"  • HTML Content: {structure['html_files']}")
            print(f"  • Images: {structure['image_files']}")
            print(f"  • CSS Styles: {structure['css_files']}")
            
            if result["renamed"]:
                print(f"\n📝 Renamed to: {Path(result['new_path']).name}")
        
        else:
            print(f"❌ Status: {result['diagnostic']['error']}")
        
        if result["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in result["recommendations"]:
                print(f"  • {rec}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        diagnostics = EPUBDiagnostics(verbose=True)
        for filepath in sys.argv[1:]:
            diagnostics.print_diagnostic_report(filepath)