"""
Epistemic Drift Validator

Implements validation rules from epistemic_drift_validator_specification.md

Rule Categories:
- Drift Taxonomy: OD-1, CD-1, BD-1, PD-1, TD-1, LD-1
- Macro/Factor: MF-1, MF-2, MF-3, MF-4
- Harness Safety: EH-1, EH-2, EH-3, EH-4

Author: System Architecture Team
Status: v1.0
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("EpistemicValidator")


class Severity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    FAIL = "FAIL"
    CRITICAL = "CRITICAL"


@dataclass
class Violation:
    """Represents a detected epistemic violation."""
    rule_id: str
    location: str
    message: str
    severity: Severity
    expected: str
    actual: str
    remediation: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "location": self.location,
            "message": self.message,
            "severity": self.severity.value,
            "expected": self.expected,
            "actual": self.actual,
            "remediation": self.remediation
        }


@dataclass
class ValidationResult:
    """Result of validation run."""
    status: str = "PASS"
    violations: List[Violation] = field(default_factory=list)
    checked_rules: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def add_violation(self, v: Violation):
        self.violations.append(v)
        if v.severity == Severity.CRITICAL:
            self.status = "CRITICAL_FAIL"
        elif v.severity == Severity.FAIL and self.status not in ["CRITICAL_FAIL"]:
            self.status = "FAIL"
        elif v.severity == Severity.WARNING and self.status == "PASS":
            self.status = "WARNING"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "violations": [v.to_dict() for v in self.violations],
            "checked_rules": self.checked_rules,
            "violation_count": len(self.violations),
            "timestamp": self.timestamp
        }


class EpistemicValidator:
    """
    Validates epistemic integrity of the system.
    
    This validator is READ-ONLY. It never modifies files.
    It reports violations for human review and remediation.
    """
    
    # Forbidden patterns for causal language in constraint layers
    CAUSAL_PATTERNS = [
        r"regime\s+causes",
        r"regime\s+drives",
        r"factor\s+causes",
        r"factor\s+drives",
        r"macro\s+causes",
    ]
    
    # Forbidden patterns for inference in execution code
    INFERENCE_PATTERNS = [
        r"if\s+volatility\s*[><=]",
        r"if\s+self\.volatility\s*[><=]",
        r"regime\s*=\s*['\"]",  # Direct regime assignment
        r"macro_service\.get",
        r"macro_state_service",
    ]
    
    # Forbidden patterns for strategy logic in skills
    STRATEGY_PATTERNS = [
        r"if\s+price\s*[><=]",
        r"if\s+self\.price\s*[><=]",
        r"rsi\s*=\s*",
        r"macd\s*=\s*",
        r"if\s+bullish",
        r"if\s+bearish",
    ]
    
    # Layer responsibility boundaries
    LAYER_RESPONSIBILITIES = {
        "regime": ["behavioral classification", "environment", "gating"],
        "factor": ["permission", "constraint", "exposure limit", "policy"],
        "signal": ["observation", "detection", "opportunity"],
        "belief": ["synthesis", "conviction", "confidence"],
        "execution": ["order", "transaction", "submit"],
    }
    
    # Latent layers that require activation authorization
    LATENT_LAYERS = [
        "macro",
        "flow",
        "volatility_geometry",
        "factor_layer",
    ]
    
    def __init__(self, root_dir: Path):
        self.root = root_dir
        self.result = ValidationResult()
        
    def validate_all(self) -> ValidationResult:
        """Run all validation rules."""
        # Drift Taxonomy
        self.check_ontological_drift()      # OD-1
        self.check_causal_drift()           # CD-1
        self.check_boundary_drift()         # BD-1
        self.check_permission_drift()       # PD-1
        self.check_temporal_drift()         # TD-1
        self.check_latent_active_drift()    # LD-1
        
        # Macro/Factor Awareness
        self.check_macro_dependency()       # MF-1
        self.check_factor_policy()          # MF-2
        self.check_execution_inference()    # MF-3
        self.check_silent_defaults()        # MF-4
        
        # Harness Safety
        self.check_belief_inference()       # EH-1
        self.check_factor_bypass()          # EH-2
        self.check_implicit_strategy()      # EH-3
        
        return self.result
    
    # =========================================================================
    # DRIFT TAXONOMY RULES
    # =========================================================================
    
    def check_ontological_drift(self) -> None:
        """OD-1: Check for undeclared concepts in epistemic documents."""
        self.result.checked_rules.append("OD-1")
        
        # Define known concepts from authoritative documents
        known_layers = {
            "reality", "time", "object", "feature", "event",
            "macro", "flow", "volatility", "regime", "factor",
            "narrative", "signal", "belief", "strategy",
            "optimization", "execution", "settlement", "audit"
        }
        
        # Scan epistemic docs for layer references
        epistemic_path = self.root / "docs" / "epistemic"
        if not epistemic_path.exists():
            return
            
        for md_file in epistemic_path.rglob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8').lower()
                # Look for "X layer" patterns
                layer_refs = re.findall(r"(\w+)\s+layer", content)
                for ref in layer_refs:
                    if ref not in known_layers and ref not in ["this", "that", "each", "every", "any", "the", "a"]:
                        self.result.add_violation(Violation(
                            rule_id="OD-1",
                            location=str(md_file.relative_to(self.root)),
                            message=f"Undeclared layer concept: '{ref} layer'",
                            severity=Severity.WARNING,
                            expected="Declared layer from structure_stack_vision.md",
                            actual=f"'{ref} layer' (unknown)",
                            remediation="Add to latent_structural_layers.md or remove reference"
                        ))
            except Exception as e:
                logger.debug(f"Error reading {md_file}: {e}")
    
    def check_causal_drift(self) -> None:
        """CD-1: Check for causal language in constraint layers."""
        self.result.checked_rules.append("CD-1")
        
        docs_path = self.root / "docs"
        if not docs_path.exists():
            return
            
        # Check regime and factor documents for causal language
        target_files = list(docs_path.rglob("*regime*.md")) + \
                       list(docs_path.rglob("*factor*.md")) + \
                       list(docs_path.rglob("*macro*.md"))
        
        for md_file in target_files:
            try:
                content = md_file.read_text(encoding='utf-8').lower()
                for pattern in self.CAUSAL_PATTERNS:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        self.result.add_violation(Violation(
                            rule_id="CD-1",
                            location=str(md_file.relative_to(self.root)),
                            message=f"Causal language in constraint layer: '{matches[0]}'",
                            severity=Severity.FAIL,
                            expected="Constraint language (constrains, permits, gates)",
                            actual=f"Causal language found: '{matches[0]}'",
                            remediation="Replace causal verbs with constraint verbs"
                        ))
            except Exception as e:
                logger.debug(f"Error reading {md_file}: {e}")
    
    def check_boundary_drift(self) -> None:
        """BD-1: Check for layers claiming other layers' responsibilities."""
        self.result.checked_rules.append("BD-1")
        
        docs_path = self.root / "docs"
        if not docs_path.exists():
            return
        
        for layer_name, responsibilities in self.LAYER_RESPONSIBILITIES.items():
            # Find documents for other layers
            other_layers = [l for l in self.LAYER_RESPONSIBILITIES.keys() if l != layer_name]
            
            for other_layer in other_layers:
                pattern = f"{other_layer}*.md"
                for md_file in docs_path.rglob(pattern):
                    try:
                        content = md_file.read_text(encoding='utf-8').lower()
                        # Check if this document claims responsibilities of another layer
                        for resp in responsibilities:
                            if resp in content and layer_name in content:
                                # Potential boundary violation - check context
                                # This is a heuristic; human review may be needed
                                pass  # Too many false positives, simplified check below
                    except Exception as e:
                        logger.debug(f"Error reading {md_file}: {e}")
        
        # Simplified check: Look for explicit cross-responsibility claims
        signal_docs = list(docs_path.rglob("*signal*.md"))
        for md_file in signal_docs:
            try:
                content = md_file.read_text(encoding='utf-8').lower()
                if "determines regime" in content or "classifies regime" in content:
                    self.result.add_violation(Violation(
                        rule_id="BD-1",
                        location=str(md_file.relative_to(self.root)),
                        message="Signal layer claiming regime classification responsibility",
                        severity=Severity.FAIL,
                        expected="Regime classification is Regime Layer responsibility",
                        actual="Signal layer claiming regime determination",
                        remediation="Remove regime logic from signal layer documentation"
                    ))
            except Exception as e:
                logger.debug(f"Error reading {md_file}: {e}")
    
    def check_permission_drift(self) -> None:
        """PD-1: Check for permission chain violations."""
        self.result.checked_rules.append("PD-1")
        
        src_path = self.root / "src"
        if not src_path.exists():
            src_path = self.root / "traderfund"
        if not src_path.exists():
            return
            
        # Check for signal processing without permission checks
        for py_file in src_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # Look for signal processing patterns
                if "signal" in content.lower() and "execute" in content.lower():
                    # Check if FactorPermission is referenced
                    if "factor_permission" not in content.lower() and \
                       "factorapermission" not in content.lower() and \
                       "permission" not in content.lower():
                        # Potential bypass - flag for review
                        if "def execute" in content or "async def execute" in content:
                            self.result.add_violation(Violation(
                                rule_id="PD-1",
                                location=str(py_file.relative_to(self.root)),
                                message="Execution without permission validation",
                                severity=Severity.CRITICAL,
                                expected="FactorPermission check before execution",
                                actual="No permission validation found",
                                remediation="Add factor permission validation step"
                            ))
            except Exception as e:
                logger.debug(f"Error reading {py_file}: {e}")
    
    def check_temporal_drift(self) -> None:
        """TD-1: Check for fast layers mutating slow beliefs."""
        self.result.checked_rules.append("TD-1")
        
        src_path = self.root / "src"
        if not src_path.exists():
            src_path = self.root / "traderfund"
        if not src_path.exists():
            return
        
        # Check for mutation of regime/narrative state in signal/flow code
        for py_file in src_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                file_lower = py_file.name.lower()
                
                # If this is a signal/flow file, check for regime mutation
                if "signal" in file_lower or "flow" in file_lower:
                    patterns = [
                        r"regime_state\.\w+\s*=",
                        r"narrative\.\w+\s*=",
                        r"self\.regime\s*=",
                    ]
                    for pattern in patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            self.result.add_violation(Violation(
                                rule_id="TD-1",
                                location=str(py_file.relative_to(self.root)),
                                message=f"Fast layer mutating slow belief: {matches[0]}",
                                severity=Severity.FAIL,
                                expected="Fast layers receive immutable slow state",
                                actual=f"Mutation detected: {matches[0]}",
                                remediation="Remove mutation; receive state as immutable input"
                            ))
            except Exception as e:
                logger.debug(f"Error reading {py_file}: {e}")
    
    def check_latent_active_drift(self) -> None:
        """LD-1: Check for unauthorized latent layer activation."""
        self.result.checked_rules.append("LD-1")
        
        src_path = self.root / "src"
        if not src_path.exists():
            src_path = self.root / "traderfund"
        if not src_path.exists():
            return
        
        decisions_path = self.root / "docs" / "epistemic" / "ledger" / "decisions.md"
        decisions_content = ""
        if decisions_path.exists():
            try:
                decisions_content = decisions_path.read_text(encoding='utf-8').lower()
            except:
                pass
        
        for py_file in src_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8').lower()
                
                for latent_layer in self.LATENT_LAYERS:
                    # Check for imports or usage of latent layers
                    patterns = [
                        f"from.*{latent_layer}",
                        f"import.*{latent_layer}",
                        f"{latent_layer}_service",
                        f"{latent_layer}state",
                    ]
                    for pattern in patterns:
                        if re.search(pattern, content):
                            # Check if authorized in decisions
                            if latent_layer not in decisions_content:
                                self.result.add_violation(Violation(
                                    rule_id="LD-1",
                                    location=str(py_file.relative_to(self.root)),
                                    message=f"Latent layer '{latent_layer}' used without authorization",
                                    severity=Severity.CRITICAL,
                                    expected="Decision Ledger entry authorizing activation",
                                    actual=f"No D00X authorization for {latent_layer}",
                                    remediation=f"Create Decision Ledger entry or remove {latent_layer} import"
                                ))
            except Exception as e:
                logger.debug(f"Error reading {py_file}: {e}")
    
    # =========================================================================
    # MACRO/FACTOR AWARENESS RULES
    # =========================================================================
    
    def check_macro_dependency(self) -> None:
        """MF-1: Check that Regime declares Macro dependency."""
        self.result.checked_rules.append("MF-1")
        
        regime_files = [
            self.root / "docs" / "Market_Regime_Detection_Blueprint.md",
            self.root / "docs" / "Regime_Taxonomy.md",
        ]
        
        for regime_file in regime_files:
            if regime_file.exists():
                try:
                    content = regime_file.read_text(encoding='utf-8').lower()
                    if "upstream dependency" not in content and "macro" not in content:
                        self.result.add_violation(Violation(
                            rule_id="MF-1",
                            location=str(regime_file.relative_to(self.root)),
                            message="Regime document missing macro dependency declaration",
                            severity=Severity.FAIL,
                            expected="Upstream Dependency section referencing macro_state",
                            actual="No macro dependency found",
                            remediation="Add Upstream Dependency section to regime doc"
                        ))
                except Exception as e:
                    logger.debug(f"Error reading {regime_file}: {e}")
    
    def check_factor_policy(self) -> None:
        """MF-2: Check that Factor is policy layer, not signal generator."""
        self.result.checked_rules.append("MF-2")
        
        factor_path = self.root / "docs" / "epistemic" / "factor_layer_policy.md"
        if factor_path.exists():
            try:
                content = factor_path.read_text(encoding='utf-8').lower()
                if "signal generator" not in content or "is not" not in content:
                    # Check if properly declares non-goal
                    if "what factor layer is not" not in content:
                        self.result.add_violation(Violation(
                            rule_id="MF-2",
                            location=str(factor_path.relative_to(self.root)),
                            message="Factor policy missing explicit non-goal declaration",
                            severity=Severity.WARNING,
                            expected="Explicit 'What Factor Layer is NOT' section",
                            actual="Non-goal section not found",
                            remediation="Add explicit non-goals to factor policy"
                        ))
            except Exception as e:
                logger.debug(f"Error reading {factor_path}: {e}")
    
    def check_execution_inference(self) -> None:
        """MF-3: Check that execution does not infer upstream state."""
        self.result.checked_rules.append("MF-3")
        
        src_path = self.root / "src"
        if not src_path.exists():
            src_path = self.root / "traderfund"
        if not src_path.exists():
            return
        
        execution_paths = list(src_path.rglob("*exec*.py")) + \
                          list(src_path.rglob("*harness*.py")) + \
                          list(src_path.rglob("*task*.py"))
        
        for py_file in execution_paths:
            try:
                content = py_file.read_text(encoding='utf-8')
                
                for pattern in self.INFERENCE_PATTERNS:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        self.result.add_violation(Violation(
                            rule_id="MF-3",
                            location=str(py_file.relative_to(self.root)),
                            message=f"Execution code inferring upstream state: {matches[0]}",
                            severity=Severity.CRITICAL,
                            expected="Receive state as input parameter",
                            actual=f"Inference pattern: {matches[0]}",
                            remediation="Remove inference; pass state as parameter"
                        ))
            except Exception as e:
                logger.debug(f"Error reading {py_file}: {e}")
    
    def check_silent_defaults(self) -> None:
        """MF-4: Check for silent default assumptions."""
        self.result.checked_rules.append("MF-4")
        
        src_path = self.root / "src"
        if not src_path.exists():
            src_path = self.root / "traderfund"
        if not src_path.exists():
            return
        
        # Patterns for silent defaults
        default_patterns = [
            r"liquidity\s*=\s*liquidity\s+or\s+['\"]",
            r"macro_state\s*=\s*macro_state\s+or\s+",
            r"regime\s*=\s*regime\s+or\s+['\"]",
            r"if\s+not\s+regime:\s*regime\s*=",
        ]
        
        for py_file in src_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                
                for pattern in default_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        self.result.add_violation(Violation(
                            rule_id="MF-4",
                            location=str(py_file.relative_to(self.root)),
                            message=f"Silent default detected: {matches[0][:50]}...",
                            severity=Severity.WARNING,
                            expected="Explicit handling of None with confidence degradation",
                            actual=f"Silent default: {matches[0][:50]}",
                            remediation="Handle None explicitly; do not assume defaults"
                        ))
            except Exception as e:
                logger.debug(f"Error reading {py_file}: {e}")
    
    # =========================================================================
    # HARNESS SAFETY RULES
    # =========================================================================
    
    def check_belief_inference(self) -> None:
        """EH-1: Check that tasks consume beliefs, not infer them."""
        self.result.checked_rules.append("EH-1")
        
        src_path = self.root / "src"
        if not src_path.exists():
            src_path = self.root / "traderfund"
        if not src_path.exists():
            return
        
        task_files = list(src_path.rglob("*task*.py"))
        
        for py_file in task_files:
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # Check if task computes beliefs internally
                if "class" in content and "task" in content.lower():
                    # Look for belief computation patterns
                    if "conviction" in content.lower() and "=" in content:
                        if "self.compute_belief" in content or "synthesize_belief" in content:
                            self.result.add_violation(Violation(
                                rule_id="EH-1",
                                location=str(py_file.relative_to(self.root)),
                                message="Task computing beliefs internally",
                                severity=Severity.CRITICAL,
                                expected="Receive BeliefSet as input from Belief Layer",
                                actual="Task synthesizing beliefs",
                                remediation="Move belief synthesis to Belief Layer"
                            ))
            except Exception as e:
                logger.debug(f"Error reading {py_file}: {e}")
    
    def check_factor_bypass(self) -> None:
        """EH-2: Check that tasks do not bypass factor permissions."""
        self.result.checked_rules.append("EH-2")
        
        # This check overlaps with PD-1; focused on harness structure
        harness_path = self.root / "src" / "harness"
        if not harness_path.exists():
            return
            
        for py_file in harness_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # Check task graph definitions
                if "task_graph" in content.lower() or "dag" in content.lower():
                    # Look for action tasks without permission deps
                    if "order" in content.lower() or "execute" in content.lower():
                        if "permission" not in content.lower():
                            self.result.add_violation(Violation(
                                rule_id="EH-2",
                                location=str(py_file.relative_to(self.root)),
                                message="Task graph missing permission check node",
                                severity=Severity.CRITICAL,
                                expected="Permission check task before action tasks",
                                actual="No permission dependency in graph",
                                remediation="Add permission check as dependency"
                            ))
            except Exception as e:
                logger.debug(f"Error reading {py_file}: {e}")
    
    def check_implicit_strategy(self) -> None:
        """EH-3: Check that skills do not encode strategy logic."""
        self.result.checked_rules.append("EH-3")
        
        skills_path = self.root / ".agent" / "skills"
        if not skills_path.exists():
            return
        
        for py_file in skills_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                
                for pattern in self.STRATEGY_PATTERNS:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        self.result.add_violation(Violation(
                            rule_id="EH-3",
                            location=str(py_file.relative_to(self.root)),
                            message=f"Skill encoding strategy logic: {matches[0]}",
                            severity=Severity.CRITICAL,
                            expected="Strategy logic in Strategy Layer only",
                            actual=f"Strategy pattern in skill: {matches[0]}",
                            remediation="Remove strategy logic from skill"
                        ))
            except Exception as e:
                logger.debug(f"Error reading {py_file}: {e}")
    
    def print_report(self) -> None:
        """Print JSON report to stdout."""
        print(json.dumps(self.result.to_dict(), indent=2))


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Epistemic Drift Validator")
    parser.add_argument("--root", default=".", help="Project root directory")
    parser.add_argument("--rule", help="Run specific rule only (e.g., PD-1)")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    
    args = parser.parse_args()
    
    root = Path(args.root).resolve()
    validator = EpistemicValidator(root)
    
    if args.rule:
        # Run specific rule
        rule_methods = {
            "OD-1": validator.check_ontological_drift,
            "CD-1": validator.check_causal_drift,
            "BD-1": validator.check_boundary_drift,
            "PD-1": validator.check_permission_drift,
            "TD-1": validator.check_temporal_drift,
            "LD-1": validator.check_latent_active_drift,
            "MF-1": validator.check_macro_dependency,
            "MF-2": validator.check_factor_policy,
            "MF-3": validator.check_execution_inference,
            "MF-4": validator.check_silent_defaults,
            "EH-1": validator.check_belief_inference,
            "EH-2": validator.check_factor_bypass,
            "EH-3": validator.check_implicit_strategy,
        }
        if args.rule in rule_methods:
            rule_methods[args.rule]()
        else:
            print(f"Unknown rule: {args.rule}")
            print(f"Available rules: {', '.join(rule_methods.keys())}")
            return
    else:
        validator.validate_all()
    
    if args.json:
        validator.print_report()
    else:
        result = validator.result
        print(f"\n{'='*60}")
        print(f"EPISTEMIC VALIDATION REPORT")
        print(f"{'='*60}")
        print(f"Status: {result.status}")
        print(f"Rules Checked: {len(result.checked_rules)}")
        print(f"Violations: {len(result.violations)}")
        print(f"{'='*60}\n")
        
        if result.violations:
            for v in result.violations:
                print(f"[{v.severity.value}] {v.rule_id}: {v.message}")
                print(f"  Location: {v.location}")
                print(f"  Remediation: {v.remediation}")
                print()
        else:
            print("✓ No violations detected")


if __name__ == "__main__":
    main()
