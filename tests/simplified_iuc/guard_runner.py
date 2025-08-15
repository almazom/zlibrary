"""
Guard Runner - Three-Tier Complexity Enforcement

Orchestrates complexity checking across the Three-Tier Framework.
Replaces monolithic test_complexity_guards.py with modular approach.
"""

import os
import sys
from typing import List, Dict, Any
from dataclasses import dataclass

from guard_rules import GuardRules, Tier, FORBIDDEN_PATTERNS
from complexity_analyzer import ComplexityAnalyzer, FileComplexity


@dataclass
class GuardViolation:
    """Represents a complexity guard violation"""
    filename: str
    tier: Tier
    violation_type: str
    current_value: Any
    limit_value: Any
    severity: str = "ERROR"
    
    def __str__(self):
        return (f"{self.severity}: {self.filename} ({self.tier.value}) - "
                f"{self.violation_type}: {self.current_value} > {self.limit_value}")


class GuardRunner:
    """
    Orchestrates complexity checking per ADR-001 Three-Tier Framework.
    
    Applies appropriate limits based on file tier assignments.
    """
    
    def __init__(self, directory: str = None):
        if directory is None:
            directory = "/home/almaz/microservices/zlibrary_api_module/tests/simplified_iuc"
        self.directory = directory
        self.violations: List[GuardViolation] = []
    
    def run_all_guards(self) -> Dict[str, Any]:
        """Run all complexity guards and return comprehensive report"""
        print("🛡️ RUNNING THREE-TIER COMPLEXITY GUARDS")
        print("=" * 50)
        
        # Get all Python files
        python_files = self._get_python_files()
        
        # Run tier-specific analysis
        results = {}
        for tier in Tier:
            tier_files = [f for f in python_files if GuardRules.get_tier_for_file(os.path.basename(f)) == tier]
            if tier_files:
                results[tier.value] = self._check_tier_files(tier, tier_files)
        
        # Generate summary
        summary = self._generate_summary(results)
        
        return {
            "summary": summary,
            "tier_results": results,
            "violations": [str(v) for v in self.violations],
            "total_violations": len(self.violations),
            "success": len(self.violations) == 0
        }
    
    def _get_python_files(self) -> List[str]:
        """Get all Python files in directory"""
        files = []
        try:
            for filename in os.listdir(self.directory):
                if filename.endswith('.py') and not filename.startswith('__'):
                    files.append(os.path.join(self.directory, filename))
        except Exception:
            pass
        return files
    
    def _check_tier_files(self, tier: Tier, files: List[str]) -> Dict[str, Any]:
        """Check all files in a specific tier"""
        print(f"\n🏷️ Checking {tier.value.upper()} tier ({len(files)} files)...")
        
        limits = GuardRules.TIER_LIMITS[tier]
        forbidden_patterns = FORBIDDEN_PATTERNS.get(tier, [])
        
        tier_violations = []
        analyses = []
        
        for file_path in files:
            filename = os.path.basename(file_path)
            print(f"  📄 {filename}")
            
            # Analyze file
            analysis = ComplexityAnalyzer.analyze_file(file_path, forbidden_patterns)
            analyses.append(analysis)
            
            # Check against tier limits
            file_violations = self._check_file_against_limits(analysis, limits, tier)
            tier_violations.extend(file_violations)
            self.violations.extend(file_violations)
            
            # Report status
            if file_violations:
                print(f"    ❌ {len(file_violations)} violations")
                for violation in file_violations:
                    print(f"      - {violation.violation_type}: {violation.current_value} > {violation.limit_value}")
            else:
                print(f"    ✅ Compliant")
        
        return {
            "tier": tier.value,
            "limits": str(limits),
            "files_checked": len(files),
            "violations": len(tier_violations),
            "analyses": analyses,
            "details": [str(v) for v in tier_violations]
        }
    
    def _check_file_against_limits(self, analysis: FileComplexity, limits, tier: Tier) -> List[GuardViolation]:
        """Check single file against its tier limits"""
        violations = []
        
        # Check line count
        if analysis.meaningful_lines > limits.max_lines:
            violations.append(GuardViolation(
                filename=analysis.filename,
                tier=tier,
                violation_type="Line count",
                current_value=analysis.meaningful_lines,
                limit_value=limits.max_lines
            ))
        
        # Check cyclomatic complexity
        if analysis.cyclomatic_complexity > limits.max_cyclomatic_complexity:
            violations.append(GuardViolation(
                filename=analysis.filename,
                tier=tier,
                violation_type="Cyclomatic complexity",
                current_value=analysis.cyclomatic_complexity,
                limit_value=limits.max_cyclomatic_complexity
            ))
        
        # Check function count
        if analysis.function_count > limits.max_functions:
            violations.append(GuardViolation(
                filename=analysis.filename,
                tier=tier,
                violation_type="Function count",
                current_value=analysis.function_count,
                limit_value=limits.max_functions
            ))
        
        # Check class count
        if analysis.class_count > limits.max_classes:
            violations.append(GuardViolation(
                filename=analysis.filename,
                tier=tier,
                violation_type="Class count",
                current_value=analysis.class_count,
                limit_value=limits.max_classes
            ))
        
        # Check forbidden patterns
        if analysis.has_forbidden_patterns:
            # Only violate if subprocess not allowed for this tier
            subprocess_patterns = ['subprocess.call', 'subprocess.run', 'subprocess.Popen']
            found_subprocess = any(p in analysis.has_forbidden_patterns for p in subprocess_patterns)
            
            if found_subprocess and not limits.allow_subprocess:
                violations.append(GuardViolation(
                    filename=analysis.filename,
                    tier=tier,
                    violation_type="Forbidden subprocess",
                    current_value=analysis.has_forbidden_patterns,
                    limit_value="None allowed"
                ))
            
            # Check other forbidden patterns
            other_patterns = [p for p in analysis.has_forbidden_patterns if p not in subprocess_patterns]
            if other_patterns:
                violations.append(GuardViolation(
                    filename=analysis.filename,
                    tier=tier,
                    violation_type="Forbidden patterns",
                    current_value=other_patterns,
                    limit_value="None allowed"
                ))
        
        return violations
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of all guard checks"""
        total_files = sum(r.get("files_checked", 0) for r in results.values())
        total_violations = len(self.violations)
        
        # Calculate overall complexity score (1-10, lower is better)
        if total_files > 0:
            violation_rate = total_violations / total_files
            complexity_score = min(10, max(1, int(violation_rate * 10) + 1))
        else:
            complexity_score = 1
        
        # Determine verdict
        if total_violations == 0:
            verdict = "✅ ALL GUARDS PASSED"
            status = "APPROVED"
        elif total_violations <= 2:
            verdict = "⚠️ MINOR VIOLATIONS"
            status = "CONDITIONAL"
        else:
            verdict = "❌ MAJOR VIOLATIONS"
            status = "REJECTED"
        
        return {
            "total_files_checked": total_files,
            "total_violations": total_violations,
            "complexity_score": complexity_score,
            "verdict": verdict,
            "status": status,
            "tier_breakdown": {tier: results[tier]["violations"] for tier in results.keys()}
        }
    
    def print_detailed_report(self, results: Dict[str, Any]):
        """Print human-readable detailed report"""
        summary = results["summary"]
        
        print("\n" + "=" * 60)
        print("🛡️ COMPLEXITY GUARD REPORT")
        print("=" * 60)
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"  Status: {summary['verdict']}")
        print(f"  Complexity Score: {summary['complexity_score']}/10")
        print(f"  Files Checked: {summary['total_files_checked']}")
        print(f"  Total Violations: {summary['total_violations']}")
        
        # Tier breakdown
        print(f"\n🏷️ TIER BREAKDOWN:")
        for tier_name, violation_count in summary["tier_breakdown"].items():
            status_icon = "✅" if violation_count == 0 else "❌"
            print(f"  {status_icon} {tier_name.upper()}: {violation_count} violations")
        
        # Violations detail
        if self.violations:
            print(f"\n🚨 VIOLATIONS ({len(self.violations)}):")
            for violation in self.violations:
                print(f"  - {violation}")
        else:
            print(f"\n✅ No violations detected!")
        
        # Guardian verdict
        print(f"\n🛡️ GUARDIAN VERDICT: {summary['status']}")
        if summary['status'] == "APPROVED":
            print("   All complexity guards passed. System remains simple.")
        elif summary['status'] == "CONDITIONAL":
            print("   Minor violations detected. Review and fix before production.")
        else:
            print("   Major violations detected. Immediate attention required.")
        
        print("\n" + "=" * 60)


def main():
    """Main entry point for guard runner"""
    print("🛡️ Three-Tier Complexity Guard System")
    print("Guardian-approved protection against complexity creep")
    print()
    
    # Initialize runner
    runner = GuardRunner()
    
    # Display tier configuration
    print(GuardRules.get_tier_summary())
    print()
    
    # Run all guards
    results = runner.run_all_guards()
    
    # Print detailed report
    runner.print_detailed_report(results)
    
    # Exit with appropriate code
    return 0 if results["summary"]["status"] == "APPROVED" else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)