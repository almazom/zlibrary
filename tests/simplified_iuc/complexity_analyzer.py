"""
Complexity Analyzer - Guardian-Approved AST Analysis

Provides sophisticated complexity analysis for the Three-Tier Framework.
Extracted from monolithic guard file to maintain modularity.
"""

import ast
import os
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class FileComplexity:
    """Complete complexity analysis for a single file"""
    filename: str
    line_count: int
    meaningful_lines: int
    cyclomatic_complexity: int
    function_count: int
    class_count: int
    import_count: int
    has_forbidden_patterns: List[str]
    

class ComplexityAnalyzer:
    """
    AST-based complexity analysis.
    
    Provides detailed metrics for complexity guard enforcement.
    """
    
    @staticmethod
    def count_meaningful_lines(file_path: str) -> int:
        """Count non-empty, non-comment lines"""
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            meaningful = 0
            in_multiline_string = False
            
            for line in lines:
                stripped = line.strip()
                
                # Skip empty lines
                if not stripped:
                    continue
                    
                # Handle multiline strings
                if '"""' in stripped or "'''" in stripped:
                    if stripped.count('"""') % 2 == 1 or stripped.count("'''") % 2 == 1:
                        in_multiline_string = not in_multiline_string
                    continue
                
                if in_multiline_string:
                    continue
                    
                # Skip single-line comments
                if stripped.startswith('#'):
                    continue
                    
                meaningful += 1
            
            return meaningful
        except Exception:
            return 0
    
    @staticmethod
    def calculate_cyclomatic_complexity(file_path: str) -> int:
        """Calculate cyclomatic complexity using AST"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            complexity = 1  # Base complexity
            
            for node in ast.walk(tree):
                # Decision points that increase complexity
                if isinstance(node, ast.If):
                    complexity += 1
                elif isinstance(node, ast.While):
                    complexity += 1
                elif isinstance(node, ast.For):
                    complexity += 1
                elif isinstance(node, ast.ExceptHandler):
                    complexity += 1
                elif isinstance(node, ast.With):
                    complexity += 1
                elif isinstance(node, ast.Assert):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    # Each additional boolean operation adds complexity
                    complexity += len(node.values) - 1
                elif isinstance(node, ast.Compare):
                    # Multiple comparisons in one statement
                    complexity += len(node.ops)
            
            return complexity
        except Exception:
            return 0
    
    @staticmethod
    def count_functions_and_classes(file_path: str) -> Dict[str, int]:
        """Count functions and classes using AST"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            functions = 0
            classes = 0
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions += 1
                elif isinstance(node, ast.AsyncFunctionDef):
                    functions += 1
                elif isinstance(node, ast.ClassDef):
                    classes += 1
            
            return {"functions": functions, "classes": classes}
        except Exception:
            return {"functions": 0, "classes": 0}
    
    @staticmethod
    def count_imports(file_path: str) -> int:
        """Count import statements"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            imports = 0
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports += 1
            
            return imports
        except Exception:
            return 0
    
    @staticmethod
    def find_forbidden_patterns(file_path: str, forbidden_patterns: List[str]) -> List[str]:
        """Find forbidden patterns in file content"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            found_patterns = []
            for pattern in forbidden_patterns:
                if pattern in content:
                    found_patterns.append(pattern)
            
            return found_patterns
        except Exception:
            return []
    
    @classmethod
    def analyze_file(cls, file_path: str, forbidden_patterns: List[str] = None) -> FileComplexity:
        """Complete complexity analysis of a single file"""
        if forbidden_patterns is None:
            forbidden_patterns = []
            
        filename = os.path.basename(file_path)
        
        # Get file size
        try:
            with open(file_path, 'r') as f:
                total_lines = len(f.readlines())
        except Exception:
            total_lines = 0
        
        # Analyze complexity
        meaningful_lines = cls.count_meaningful_lines(file_path)
        complexity = cls.calculate_cyclomatic_complexity(file_path)
        counts = cls.count_functions_and_classes(file_path)
        import_count = cls.count_imports(file_path)
        forbidden = cls.find_forbidden_patterns(file_path, forbidden_patterns)
        
        return FileComplexity(
            filename=filename,
            line_count=total_lines,
            meaningful_lines=meaningful_lines,
            cyclomatic_complexity=complexity,
            function_count=counts["functions"],
            class_count=counts["classes"],
            import_count=import_count,
            has_forbidden_patterns=forbidden
        )
    
    @classmethod
    def analyze_directory(cls, directory: str, forbidden_patterns: List[str] = None) -> List[FileComplexity]:
        """Analyze all Python files in a directory"""
        results = []
        
        try:
            for filename in os.listdir(directory):
                if filename.endswith('.py') and not filename.startswith('__'):
                    file_path = os.path.join(directory, filename)
                    analysis = cls.analyze_file(file_path, forbidden_patterns)
                    results.append(analysis)
        except Exception:
            pass
        
        return results
    
    @staticmethod
    def generate_complexity_report(analyses: List[FileComplexity]) -> str:
        """Generate human-readable complexity report"""
        if not analyses:
            return "No files analyzed"
        
        report = "📊 COMPLEXITY ANALYSIS REPORT\n"
        report += "=" * 50 + "\n\n"
        
        # Summary statistics
        total_files = len(analyses)
        total_lines = sum(a.meaningful_lines for a in analyses)
        avg_complexity = sum(a.cyclomatic_complexity for a in analyses) / total_files
        total_functions = sum(a.function_count for a in analyses)
        total_classes = sum(a.class_count for a in analyses)
        
        report += f"📈 SUMMARY:\n"
        report += f"  Files: {total_files}\n"
        report += f"  Total Lines: {total_lines}\n"
        report += f"  Average Complexity: {avg_complexity:.1f}\n"
        report += f"  Functions: {total_functions}\n"
        report += f"  Classes: {total_classes}\n\n"
        
        # Per-file breakdown
        report += "📄 PER-FILE BREAKDOWN:\n"
        for analysis in sorted(analyses, key=lambda x: x.cyclomatic_complexity, reverse=True):
            report += f"\n🔍 {analysis.filename}:\n"
            report += f"  Lines: {analysis.meaningful_lines} ({analysis.line_count} total)\n"
            report += f"  Complexity: {analysis.cyclomatic_complexity}\n"
            report += f"  Functions: {analysis.function_count}\n"
            report += f"  Classes: {analysis.class_count}\n"
            report += f"  Imports: {analysis.import_count}\n"
            
            if analysis.has_forbidden_patterns:
                report += f"  ⚠️ Forbidden patterns: {', '.join(analysis.has_forbidden_patterns)}\n"
        
        return report


if __name__ == "__main__":
    # Demo analysis of current directory
    analyzer = ComplexityAnalyzer()
    
    # Analyze simplified IUC directory
    iuc_dir = "/home/almaz/microservices/zlibrary_api_module/tests/simplified_iuc"
    analyses = analyzer.analyze_directory(iuc_dir)
    
    # Generate report
    report = analyzer.generate_complexity_report(analyses)
    print(report)