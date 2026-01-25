"""
Evaluation Profile Loader.
Responsible for loading, validating, and typing Evaluation Profile definitions.

Invariants:
- Profiles are immutable inputs.
- Schema validation is strict (HARD FAILURE on violation).
- Invariants must be explicitly TRUE.
"""
import os
import sys
import yaml
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pathlib import Path

class ProfileValidationError(Exception):
    """Raised when an evaluation profile fails schema or invariant validation."""
    pass

class ModeType(str, Enum):
    HISTORICAL = "historical"
    FORCED_REGIME = "forced_regime"

class WindowingType(str, Enum):
    SINGLE = "single"
    ROLLING = "rolling"
    ANCHORED = "anchored"

class FactorObservationType(str, Enum):
    OBSERVE = "observe"
    DISABLE = "disable"

@dataclass
class ProfileMode:
    type: ModeType

@dataclass
class ProfileRegimeOverride:
    regime_code: str
    rationale: str

@dataclass
class ProfileRegime:
    detection: bool
    override: Optional[ProfileRegimeOverride]

@dataclass
class ProfileWindowing:
    type: WindowingType
    window_size: str
    step_size: Optional[str] = None
    anchor_dates: Optional[List[str]] = None

@dataclass
class ProfileFactor:
    observation: FactorObservationType
    override: None # Must be None per schema

@dataclass
class ProfileExecution:
    shadow_only: bool
    allow_replay: bool
    allow_parallel_windows: bool

@dataclass
class ProfileOutputs:
    artifact_namespace: str
    persist_intermediate: bool

@dataclass
class ProfileGovernance:
    decision_ref: str
    ledger_required: bool
    did_required: bool

@dataclass
class ProfileInvariants:
    forbid_real_execution: bool
    forbid_strategy_mutation: bool
    forbid_regime_fallback: bool

@dataclass
class EvaluationProfile:
    profile_id: str
    version: str
    description: str
    mode: ProfileMode
    windowing: ProfileWindowing
    regime: ProfileRegime
    factor: ProfileFactor
    execution: ProfileExecution
    outputs: ProfileOutputs
    governance: ProfileGovernance
    invariants: ProfileInvariants

def load_profile(path: str) -> EvaluationProfile:
    """
    Load and validate an Evaluation Profile from a YAML file.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Profile not found at: {path}")

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ProfileValidationError(f"Invalid YAML in profile: {e}")

    try:
        # 1. Parse Sections
        mode_data = data.get('mode', {})
        windowing_data = data.get('windowing', {})
        regime_data = data.get('regime', {})
        factor_data = data.get('factor', {})
        exec_data = data.get('execution', {})
        outputs_data = data.get('outputs', {})
        gov_data = data.get('governance', {})
        inv_data = data.get('invariants', {})

        # 2. Build Objects & Validate Enums
        
        # Mode
        mode = ProfileMode(type=ModeType(mode_data.get('type')))

        # Windowing
        windowing = ProfileWindowing(
            type=WindowingType(windowing_data.get('type')),
            window_size=windowing_data.get('window_size'),
            step_size=windowing_data.get('step_size'),
            anchor_dates=windowing_data.get('anchor_dates')
        )

        # Regime
        override_data = regime_data.get('override')
        override = None
        if override_data:
            override = ProfileRegimeOverride(
                regime_code=override_data.get('regime_code'),
                rationale=override_data.get('rationale')
            )
        regime = ProfileRegime(
            detection=regime_data.get('detection'),
            override=override
        )

        # Factor
        if factor_data.get('override') is not None:
             raise ProfileValidationError("factor.override must be null (Factor forcing is FORBIDDEN)")
        
        factor = ProfileFactor(
            observation=FactorObservationType(factor_data.get('observation')),
            override=None
        )

        # Execution
        execution = ProfileExecution(
            shadow_only=exec_data.get('shadow_only'),
            allow_replay=exec_data.get('allow_replay'),
            allow_parallel_windows=exec_data.get('allow_parallel_windows')
        )

        # Outputs
        outputs = ProfileOutputs(
            artifact_namespace=outputs_data.get('artifact_namespace'),
            persist_intermediate=outputs_data.get('persist_intermediate')
        )

        # Governance
        governance = ProfileGovernance(
            decision_ref=gov_data.get('decision_ref'),
            ledger_required=gov_data.get('ledger_required'),
            did_required=gov_data.get('did_required')
        )

        # Invariants
        invariants = ProfileInvariants(
            forbid_real_execution=inv_data.get('forbid_real_execution'),
            forbid_strategy_mutation=inv_data.get('forbid_strategy_mutation'),
            forbid_regime_fallback=inv_data.get('forbid_regime_fallback')
        )

        # 3. Construct Profile
        profile = EvaluationProfile(
            profile_id=data.get('profile_id'),
            version=data.get('version'),
            description=data.get('description'),
            mode=mode,
            windowing=windowing,
            regime=regime,
            factor=factor,
            execution=execution,
            outputs=outputs,
            governance=governance,
            invariants=invariants
        )

        # 4. Logical Validation
        _validate_profile_logic(profile)
        
        return profile

    except (ValueError, KeyError, TypeError) as e:
        raise ProfileValidationError(f"Structure validation failed: {str(e)}")

def _validate_profile_logic(profile: EvaluationProfile):
    """
    Enforce business logic constraints and invariants.
    """
    # Invariant checks
    if not profile.execution.shadow_only:
        raise ProfileValidationError("Invariant Violation: execution.shadow_only must be True")
    if not profile.invariants.forbid_real_execution:
        raise ProfileValidationError("Invariant Violation: forbid_real_execution must be True")
    if not profile.invariants.forbid_strategy_mutation:
        raise ProfileValidationError("Invariant Violation: forbid_strategy_mutation must be True")
    if not profile.invariants.forbid_regime_fallback:
        raise ProfileValidationError("Invariant Violation: forbid_regime_fallback must be True")
    
    # Governance checks
    if not profile.governance.ledger_required:
        raise ProfileValidationError("Governance Violation: ledger_required must be True")
    if not profile.governance.did_required:
        raise ProfileValidationError("Governance Violation: did_required must be True")
    if profile.governance.decision_ref != "D013":
        # We might allow newer decisions later, but for now strict check on authorization
        raise ProfileValidationError("Governance Violation: decision_ref must be D013")

    # Mode consistency
    if profile.mode.type == ModeType.HISTORICAL:
        if not profile.regime.detection:
             raise ProfileValidationError("Configuration Error: Historical mode requires regime.detection=True")
        if profile.regime.override is not None:
             raise ProfileValidationError("Configuration Error: Historical mode forbids regime.override")

    if profile.mode.type == ModeType.FORCED_REGIME:
        if profile.regime.detection:
             raise ProfileValidationError("Configuration Error: Forced Regime mode requires regime.detection=False")
        if profile.regime.override is None:
             raise ProfileValidationError("Configuration Error: Forced Regime mode requires regime.override")
        if not profile.regime.override.regime_code:
             raise ProfileValidationError("Configuration Error: Forced Regime mode requires valid regime_code")

    # Windowing consistency
    if profile.windowing.type == WindowingType.ROLLING:
        if not profile.windowing.step_size:
            raise ProfileValidationError("Configuration Error: Rolling window requires step_size")

    if profile.windowing.type == WindowingType.ANCHORED:
        if not profile.windowing.anchor_dates:
            raise ProfileValidationError("Configuration Error: Anchored window requires anchor_dates")

    if profile.windowing.type == WindowingType.SINGLE:
        if profile.windowing.step_size or profile.windowing.anchor_dates:
             raise ProfileValidationError("Configuration Error: Single window should not have step_size or anchor_dates")

if __name__ == "__main__":
    # Quick test if run as script
    if len(sys.argv) > 1:
        try:
            p = load_profile(sys.argv[1])
            print(f"SUCCESS: Loaded profile {p.profile_id} (v{p.version})")
            print(f"Mode: {p.mode.type}")
            print(f"Namespace: {p.outputs.artifact_namespace}")
        except Exception as e:
            print(f"FAILURE: {e}")
            sys.exit(1)
    else:
        print("Usage: python profile_loader.py <path_to_profile.yaml>")
