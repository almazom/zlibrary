"""
Guardian-Approved Tier Configuration

Implements the Three-Tier Complexity Framework per ADR-001.
Each tier has appropriate complexity limits based on architectural responsibility.
"""

from dataclasses import dataclass
from typing import Dict, List, Set
from enum import Enum


class Tier(Enum):
    """Complexity tiers with escalating limits"""
    CORE = "core"           # Strictest limits - main functionality
    VALIDATION = "validation"  # Moderate limits - cross-implementation validation  
    META_GUARD = "meta_guard"  # Relaxed limits - protection systems


@dataclass
class ComplexityLimits:
    """Complexity limits for a specific tier"""
    max_lines: int
    max_cyclomatic_complexity: int
    max_functions: int
    max_classes: int
    allow_subprocess: bool
    tier_name: str
    
    def __str__(self):
        return (f"{self.tier_name}: {self.max_lines} lines, "
                f"{self.max_cyclomatic_complexity} complexity, "
                f"{self.max_functions} functions, "
                f"{self.max_classes} classes")


class GuardRules:
    """
    Guardian-approved complexity rules per tier.
    
    Based on architectural responsibilities and maintainability requirements.
    """
    
    # Tier definitions per ADR-001
    TIER_LIMITS = {
        Tier.CORE: ComplexityLimits(
            max_lines=200,
            max_cyclomatic_complexity=5,
            max_functions=10,
            max_classes=3,
            allow_subprocess=False,
            tier_name="Core Implementation"
        ),
        
        Tier.VALIDATION: ComplexityLimits(
            max_lines=300,
            max_cyclomatic_complexity=30,
            max_functions=15,
            max_classes=5,
            allow_subprocess=True,  # For comparing with original IUC
            tier_name="Validation Layer"
        ),
        
        Tier.META_GUARD: ComplexityLimits(
            max_lines=500,  # Per file when modular
            max_cyclomatic_complexity=60,
            max_functions=20,
            max_classes=8,
            allow_subprocess=False,
            tier_name="Meta-Guard System"
        )
    }
    
    # File tier assignments per ADR-001
    FILE_TIER_MAP = {
        # Tier 1: Core Implementation (Strictest)
        "telegram_bot_tester.py": Tier.CORE,
        "test_integration.py": Tier.CORE,
        
        # Tier 2: Validation Layer (Moderate)
        "validation_test.py": Tier.VALIDATION,
        
        # Tier 3: Meta-Guards (Relaxed)
        "test_complexity_guards.py": Tier.META_GUARD,
        "complexity_analyzer.py": Tier.META_GUARD,
        "guard_rules.py": Tier.META_GUARD,
        "guard_runner.py": Tier.META_GUARD,
        
        # Documentation and config (exempt from limits)
        "README.md": None,
        "requirements.txt": None,
        "ADR-001-LAYERED-COMPLEXITY.md": None,
    }
    
    @classmethod
    def get_limits_for_file(cls, filename: str) -> ComplexityLimits:
        """Get complexity limits for a specific file"""
        tier = cls.FILE_TIER_MAP.get(filename)
        
        if tier is None:
            # Default new files to Core tier (strictest)
            tier = Tier.CORE
            
        return cls.TIER_LIMITS[tier]
    
    @classmethod
    def get_tier_for_file(cls, filename: str) -> Tier:
        """Get tier assignment for a specific file"""
        return cls.FILE_TIER_MAP.get(filename, Tier.CORE)
    
    @classmethod
    def is_subprocess_allowed(cls, filename: str) -> bool:
        """Check if subprocess usage is allowed for this file"""
        limits = cls.get_limits_for_file(filename)
        return limits.allow_subprocess
    
    @classmethod
    def get_all_tiers(cls) -> Dict[Tier, List[str]]:
        """Get all files grouped by tier"""
        tiers = {tier: [] for tier in Tier}
        
        for filename, tier in cls.FILE_TIER_MAP.items():
            if tier is not None:
                tiers[tier].append(filename)
                
        return tiers
    
    @classmethod
    def validate_tier_assignments(cls) -> List[str]:
        """Validate that tier assignments make architectural sense"""
        issues = []
        
        # Check that core files are truly simple
        core_files = [f for f, t in cls.FILE_TIER_MAP.items() if t == Tier.CORE]
        if not core_files:
            issues.append("No core files defined - at least one required")
        
        # Check that we don't have too many meta-guard files
        guard_files = [f for f, t in cls.FILE_TIER_MAP.items() if t == Tier.META_GUARD]
        if len(guard_files) > 5:
            issues.append(f"Too many meta-guard files ({len(guard_files)}) - consider consolidation")
        
        # Check for tier creep (everything in validation/meta-guard)
        non_core_files = [f for f, t in cls.FILE_TIER_MAP.items() if t != Tier.CORE and t is not None]
        total_files = len([f for f in cls.FILE_TIER_MAP.values() if f is not None])
        
        if len(non_core_files) / total_files > 0.7:
            issues.append("Tier creep detected: >70% files not in core tier")
        
        return issues
    
    @classmethod
    def get_tier_summary(cls) -> str:
        """Get human-readable summary of tier assignments"""
        tiers = cls.get_all_tiers()
        
        summary = "📊 TIER ASSIGNMENTS:\n"
        summary += "=" * 40 + "\n"
        
        for tier in Tier:
            files = tiers[tier]
            limits = cls.TIER_LIMITS[tier]
            
            summary += f"\n🏷️ {limits.tier_name.upper()}:\n"
            summary += f"   Limits: {limits}\n"
            summary += f"   Files ({len(files)}):\n"
            
            for file in files:
                summary += f"   - {file}\n"
        
        # Validation warnings
        issues = cls.validate_tier_assignments()
        if issues:
            summary += "\n⚠️ TIER VALIDATION ISSUES:\n"
            for issue in issues:
                summary += f"   - {issue}\n"
        else:
            summary += "\n✅ All tier assignments valid\n"
        
        return summary


# Guardian-approved forbidden patterns per tier
FORBIDDEN_PATTERNS = {
    Tier.CORE: [
        # Strictest patterns for core implementation
        'subprocess.call',
        'subprocess.run',
        'os.system(',
        'subprocess.Popen',
        'shell=True',
        'eval(',
        'exec(',
        'import *',  # Wildcard imports
    ],
    
    Tier.VALIDATION: [
        # Some shell usage allowed for original IUC comparison
        'eval(',
        'exec(',
        'import *',
        'shell=True',  # Should use subprocess.run with specific args
    ],
    
    Tier.META_GUARD: [
        # Most relaxed but still safe
        'eval(',
        'exec(',
        'import *',
        'shell=True',
    ]
}


if __name__ == "__main__":
    # Display tier configuration
    print(GuardRules.get_tier_summary())
    
    # Test validation
    issues = GuardRules.validate_tier_assignments()
    if issues:
        print("\n🚨 Configuration Issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✅ Configuration Valid")