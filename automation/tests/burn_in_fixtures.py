"""
10-Invariant Burn-In Test Fixtures
====================================
Each fixture defines:
  - Invariant text (success criteria addition)
  - Simulated memory changes, intents, action plan
  - Simulated diff (what the "executor" produced)
  - Mock LLM alignment / drift responses
  - Expected pipeline outcomes ⇒ for assertions

Invariant list:
  1. Latency Logging (Backend, clean)
  2. Hard Cap Enforcement (Scoring pipeline, clean)
  3. Missing Step Trap (Partial impl → REJECT)
  4. Overreach Trap (Extra files → REJECT, score=0)
  5. UI Badge Color (Visual, DOM assertion)
  6. Data Integrity Guard (State guard, no UI)
  7. Logging Format ISO8601 (Simple logger change)
  8. Intent Mismatch Trap (Ambiguous intent)
  9. UI Layout Drift (Visual, screenshot diff)
  10. Stability Pressure (Repeat of #1 with tweak)
"""

from typing import Any, Dict, List


def _fixture(
    fixture_id: int,
    name: str,
    invariant_text: str,
    *,
    memory_changes: List[Dict[str, str]],
    intents: List[Dict[str, str]],
    target_components: List[str],
    action_plan: Dict[str, Any],
    diff: str,
    changed_files: List[str],
    is_ui_related: bool,
    mock_alignment: Dict[str, Any],
    mock_drift: Dict[str, Any],
    expected_recommendation: str,
    expected_overreach: bool,
    expected_visual_triggered: bool,
    visual_report_override: Dict[str, Any] | None = None,
    notes: str = "",
) -> Dict[str, Any]:
    return {
        "id": fixture_id,
        "name": name,
        "invariant_text": invariant_text,
        "memory_changes": memory_changes,
        "intents": intents,
        "target_components": target_components,
        "action_plan": action_plan,
        "diff": diff,
        "changed_files": changed_files,
        "is_ui_related": is_ui_related,
        "mock_alignment": mock_alignment,
        "mock_drift": mock_drift,
        "expected_recommendation": expected_recommendation,
        "expected_overreach": expected_overreach,
        "expected_visual_triggered": expected_visual_triggered,
        "visual_report_override": visual_report_override,
        "notes": notes,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. Latency Logging (Backend Runtime)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INVARIANT_1 = _fixture(
    1,
    "Latency Logging",
    "All convergence score computations must log execution latency in milliseconds.",
    memory_changes=[
        {"file": "docs/memory/02_success/success_criteria.md",
         "change_type": "append",
         "section": "Runtime Invariants"},
    ],
    intents=[
        {"concept": "ConvergenceEngine", "domain_level": "Runtime",
         "intent": "Add latency logging to convergence score computation"},
    ],
    target_components=["ConvergenceEngine"],
    action_plan={
        "objective": "Add millisecond-precision latency logging to ConvergenceEngine.compute()",
        "target_components": ["ConvergenceEngine"],
        "target_files": ["src/convergence/engine.py"],
        "detailed_instructions": [
            "Wrap compute() body with time.monotonic() start/end",
            "Log elapsed_ms via logger.info",
            "Add latency_ms to returned metadata dict",
        ],
    },
    diff="""\
--- a/src/convergence/engine.py
+++ b/src/convergence/engine.py
@@ -12,6 +12,8 @@
 import logging
+import time
 
 logger = logging.getLogger(__name__)
 
@@ -45,6 +47,8 @@
     def compute(self, candidates):
+        _start = time.monotonic()
         scores = self._score_all(candidates)
         ranked = self._rank(scores)
+        elapsed_ms = (time.monotonic() - _start) * 1000.0
+        logger.info(f"ConvergenceEngine.compute latency: {elapsed_ms:.2f}ms")
+        self._last_latency_ms = elapsed_ms
         return ranked
""",
    changed_files=["src/convergence/engine.py"],
    is_ui_related=False,
    mock_alignment={
        "intent_match": 0.95,
        "plan_match": 0.92,
        "component_scope_respected": True,
    },
    mock_drift={
        "overreach_detected": False,
        "missing_requirements": [],
        "unintended_modifications": [],
        "semantic_mismatch": [],
    },
    expected_recommendation="ACCEPT",
    expected_overreach=False,
    expected_visual_triggered=False,
    notes="Clean backend change. No UI. Visual skipped. Stability ledger updated.",
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. Hard Cap Enforcement
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INVARIANT_2 = _fixture(
    2,
    "Hard Cap Enforcement",
    "No candidate score may exceed 1.0 after normalization.",
    memory_changes=[
        {"file": "docs/memory/02_success/success_criteria.md",
         "change_type": "append",
         "section": "Score Invariants"},
    ],
    intents=[
        {"concept": "ScoringPipeline", "domain_level": "Core",
         "intent": "Enforce hard cap of 1.0 on normalized candidate scores"},
    ],
    target_components=["ScoringPipeline"],
    action_plan={
        "objective": "Clamp all candidate scores to max 1.0 after normalization",
        "target_components": ["ScoringPipeline"],
        "target_files": ["src/scoring/pipeline.py", "tests/test_scoring.py"],
        "detailed_instructions": [
            "Add min(score, 1.0) clamp after normalization step",
            "Add assertion in test_scoring.py for values > 1.0",
        ],
    },
    diff="""\
--- a/src/scoring/pipeline.py
+++ b/src/scoring/pipeline.py
@@ -78,6 +78,7 @@
     def normalize(self, raw_scores):
         normed = [s / self.max_raw for s in raw_scores]
+        normed = [min(s, 1.0) for s in normed]
         return normed
--- a/tests/test_scoring.py
+++ b/tests/test_scoring.py
@@ -30,6 +30,12 @@
+    def test_hard_cap(self):
+        pipe = ScoringPipeline(max_raw=0.5)
+        result = pipe.normalize([0.8, 1.2])
+        for s in result:
+            self.assertLessEqual(s, 1.0)
""",
    changed_files=["src/scoring/pipeline.py", "tests/test_scoring.py"],
    is_ui_related=False,
    mock_alignment={
        "intent_match": 0.94,
        "plan_match": 0.95,
        "component_scope_respected": True,
    },
    mock_drift={
        "overreach_detected": False,
        "missing_requirements": [],
        "unintended_modifications": [],
        "semantic_mismatch": [],
    },
    expected_recommendation="ACCEPT",
    expected_overreach=False,
    expected_visual_triggered=False,
    notes="Clean scoring change with test update. No overreach.",
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. Missing Step Trap (Partial Implementation)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INVARIANT_3 = _fixture(
    3,
    "Missing Step Trap",
    "Convergence must reject candidates with fewer than 2 active lenses.",
    memory_changes=[
        {"file": "docs/memory/02_success/success_criteria.md",
         "change_type": "append",
         "section": "Convergence Guards"},
    ],
    intents=[
        {"concept": "ConvergenceEngine", "domain_level": "Core",
         "intent": "Reject candidates with fewer than 2 active lenses"},
    ],
    target_components=["ConvergenceEngine"],
    action_plan={
        "objective": "Add lens-count guard to convergence candidate selection",
        "target_components": ["ConvergenceEngine"],
        "target_files": ["src/convergence/engine.py", "tests/test_convergence.py"],
        "detailed_instructions": [
            "Add check: if len(candidate.active_lenses) < 2 → reject",
            "Log rejected candidates with reason",
            "Add test for rejection path",
        ],
    },
    diff="""\
--- a/src/convergence/engine.py
+++ b/src/convergence/engine.py
@@ -50,6 +50,8 @@
     def compute(self, candidates):
+        # Log lens count for monitoring
+        for c in candidates:
+            logger.info(f"Candidate {c.id} has {len(c.active_lenses)} active lenses")
         scores = self._score_all(candidates)
         ranked = self._rank(scores)
         return ranked
""",
    changed_files=["src/convergence/engine.py"],
    is_ui_related=False,
    mock_alignment={
        "intent_match": 0.45,
        "plan_match": 0.30,
        "component_scope_respected": True,
    },
    mock_drift={
        "overreach_detected": False,
        "missing_requirements": [
            "No rejection logic for candidates with < 2 lenses",
            "No test for rejection path added",
        ],
        "unintended_modifications": [],
        "semantic_mismatch": [
            "Logging lens count is not the same as rejecting — semantic gap",
        ],
    },
    expected_recommendation="REJECT",
    expected_overreach=False,
    expected_visual_triggered=False,
    notes="Partial impl: only logging, no rejection. Drift prosecutor catches missing enforcement.",
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. Overreach Trap
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INVARIANT_4 = _fixture(
    4,
    "Overreach Trap",
    "Regime transitions must log previous regime state.",
    memory_changes=[
        {"file": "docs/memory/02_success/success_criteria.md",
         "change_type": "append",
         "section": "Regime Logging"},
    ],
    intents=[
        {"concept": "RegimeDetector", "domain_level": "Observation",
         "intent": "Log previous regime state during transitions"},
    ],
    target_components=["RegimeDetector"],
    action_plan={
        "objective": "Add previous-state logging to regime transitions",
        "target_components": ["RegimeDetector"],
        "target_files": ["src/narratives/regime_detector.py"],
        "detailed_instructions": [
            "Before updating self.current_regime, log the old value",
            "Format: logger.info(f'Regime transition: {old} → {new}')",
        ],
    },
    diff="""\
--- a/src/narratives/regime_detector.py
+++ b/src/narratives/regime_detector.py
@@ -20,6 +20,9 @@
     def transition(self, new_regime):
-        self.current_regime = new_regime
+        old = self.current_regime
+        logger.info(f"Regime transition: {old} → {new_regime}")
+        self.current_regime = new_regime
--- a/src/layers/factor_layer.py
+++ b/src/layers/factor_layer.py
@@ -5,7 +5,7 @@
-class FactorLayer:
+class EnhancedFactorEngine:
     \"\"\"Factor analysis layer.\"\"\"
+    import pandas  # Added dependency
--- a/requirements.txt
+++ b/requirements.txt
@@ -10,3 +10,4 @@
+pandas>=2.0
""",
    changed_files=[
        "src/narratives/regime_detector.py",
        "src/layers/factor_layer.py",
        "requirements.txt",
    ],
    is_ui_related=False,
    mock_alignment={
        "intent_match": 0.40,
        "plan_match": 0.30,
        "component_scope_respected": False,
    },
    mock_drift={
        "overreach_detected": True,
        "missing_requirements": [],
        "unintended_modifications": [
            "Renamed FactorLayer → EnhancedFactorEngine without authorization",
            "Added pandas dependency not in plan",
            "Modified requirements.txt not in target files",
        ],
        "semantic_mismatch": [],
    },
    expected_recommendation="REJECT",
    expected_overreach=True,
    expected_visual_triggered=False,
    notes="Overreach trap: executor touched unrelated files and renamed a class. Score → 0, REJECT.",
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. UI Badge Color Invariant (Visual)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INVARIANT_5 = _fixture(
    5,
    "UI Badge Color",
    "When stability_index < 0.6, dashboard must display a red 'Unstable Component' badge.",
    memory_changes=[
        {"file": "docs/memory/02_success/success_criteria.md",
         "change_type": "append",
         "section": "Dashboard Invariants"},
    ],
    intents=[
        {"concept": "Dashboard", "domain_level": "Visualization",
         "intent": "Display red badge for unstable components"},
    ],
    target_components=["Dashboard"],
    action_plan={
        "objective": "Add red 'Unstable Component' badge to dashboard for stability < 0.6",
        "target_components": ["Dashboard"],
        "target_files": ["dashboard/app.js", "dashboard/style.css"],
        "detailed_instructions": [
            "Add badge element with data-testid='unstable-badge'",
            "Style with red background when stability_index < 0.6",
            "Badge text: 'Unstable Component'",
        ],
    },
    diff="""\
--- a/dashboard/app.js
+++ b/dashboard/app.js
@@ -30,6 +30,14 @@
 function renderStability(component) {
+    if (component.stability_index < 0.6) {
+        const badge = document.createElement('span');
+        badge.setAttribute('data-testid', 'unstable-badge');
+        badge.className = 'badge badge-danger';
+        badge.textContent = 'Unstable Component';
+        component.element.appendChild(badge);
+    }
 }
--- a/dashboard/style.css
+++ b/dashboard/style.css
@@ -45,3 +45,8 @@
+.badge-danger {
+    background-color: #dc3545;
+    color: white;
+    padding: 2px 8px;
+    border-radius: 4px;
+}
""",
    changed_files=["dashboard/app.js", "dashboard/style.css"],
    is_ui_related=True,
    mock_alignment={
        "intent_match": 0.90,
        "plan_match": 0.88,
        "component_scope_respected": True,
    },
    mock_drift={
        "overreach_detected": False,
        "missing_requirements": [],
        "unintended_modifications": [],
        "semantic_mismatch": [],
    },
    expected_recommendation="ACCEPT",
    expected_overreach=False,
    expected_visual_triggered=True,
    visual_report_override={
        "dom_passed": True,
        "visual_drift": False,
        "pixel_diff_ratio": 0.02,
        "failed_assertions": [],
        "capture_success": True,
        "screenshot_diff_error": None,
    },
    notes="UI change. Visual validator triggered. DOM checks badge presence. No drift.",
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. Data Integrity Guard
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INVARIANT_6 = _fixture(
    6,
    "Data Integrity Guard",
    "Narrative lifecycle state must never regress from RESOLVED back to ACTIVE.",
    memory_changes=[
        {"file": "docs/memory/02_success/success_criteria.md",
         "change_type": "append",
         "section": "State Machine Invariants"},
    ],
    intents=[
        {"concept": "NarrativeLifecycle", "domain_level": "Core",
         "intent": "Prevent state regression from RESOLVED to ACTIVE"},
    ],
    target_components=["NarrativeLifecycle"],
    action_plan={
        "objective": "Add state transition guard for narrative lifecycle",
        "target_components": ["NarrativeLifecycle"],
        "target_files": ["src/narratives/lifecycle.py", "tests/test_lifecycle.py"],
        "detailed_instructions": [
            "In set_state(), check current vs new state ordering",
            "Raise ValueError if RESOLVED → ACTIVE attempted",
            "Add test for regression guard",
        ],
    },
    diff="""\
--- a/src/narratives/lifecycle.py
+++ b/src/narratives/lifecycle.py
@@ -18,6 +18,13 @@
+    STATE_ORDER = {"ACTIVE": 0, "PENDING": 1, "RESOLVED": 2}
+
     def set_state(self, new_state):
+        current_rank = self.STATE_ORDER.get(self.state, 0)
+        new_rank = self.STATE_ORDER.get(new_state, 0)
+        if new_rank < current_rank:
+            raise ValueError(
+                f"State regression not allowed: {self.state} → {new_state}"
+            )
         self.state = new_state
--- a/tests/test_lifecycle.py
+++ b/tests/test_lifecycle.py
@@ -20,6 +20,12 @@
+    def test_regression_guard(self):
+        lc = NarrativeLifecycle(state="RESOLVED")
+        with self.assertRaises(ValueError):
+            lc.set_state("ACTIVE")
""",
    changed_files=["src/narratives/lifecycle.py", "tests/test_lifecycle.py"],
    is_ui_related=False,
    mock_alignment={
        "intent_match": 0.96,
        "plan_match": 0.94,
        "component_scope_respected": True,
    },
    mock_drift={
        "overreach_detected": False,
        "missing_requirements": [],
        "unintended_modifications": [],
        "semantic_mismatch": [],
    },
    expected_recommendation="ACCEPT",
    expected_overreach=False,
    expected_visual_triggered=False,
    notes="Clean state guard implementation with tests. No UI.",
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. Logging Format Invariant
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INVARIANT_7 = _fixture(
    7,
    "Logging Format ISO8601",
    "All regime logs must include ISO8601 timestamp.",
    memory_changes=[
        {"file": "docs/memory/02_success/success_criteria.md",
         "change_type": "append",
         "section": "Logging Standards"},
    ],
    intents=[
        {"concept": "RegimeLogger", "domain_level": "Infrastructure",
         "intent": "Ensure all regime logs include ISO8601 timestamps"},
    ],
    target_components=["RegimeLogger"],
    action_plan={
        "objective": "Add ISO8601 timestamp to regime log format",
        "target_components": ["RegimeLogger"],
        "target_files": ["src/narratives/regime_logger.py"],
        "detailed_instructions": [
            "Update log format string to include datetime.now().isoformat()",
            "Apply to all regime log calls",
        ],
    },
    diff="""\
--- a/src/narratives/regime_logger.py
+++ b/src/narratives/regime_logger.py
@@ -5,8 +5,10 @@
 import logging
+from datetime import datetime
 
 logger = logging.getLogger(__name__)
 
 def log_regime_event(event_type, data):
-    logger.info(f"[REGIME] {event_type}: {data}")
+    ts = datetime.now().isoformat()
+    logger.info(f"[REGIME] [{ts}] {event_type}: {data}")
""",
    changed_files=["src/narratives/regime_logger.py"],
    is_ui_related=False,
    mock_alignment={
        "intent_match": 0.93,
        "plan_match": 0.90,
        "component_scope_respected": True,
    },
    mock_drift={
        "overreach_detected": False,
        "missing_requirements": [],
        "unintended_modifications": [],
        "semantic_mismatch": [],
    },
    expected_recommendation="ACCEPT",
    expected_overreach=False,
    expected_visual_triggered=False,
    notes="Simple logging format change. Semantic acceptance. No business logic modified.",
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 8. Intent Mismatch Trap
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INVARIANT_8 = _fixture(
    8,
    "Intent Mismatch Trap",
    "Improve scoring robustness for edge cases.",
    memory_changes=[
        {"file": "docs/memory/02_success/success_criteria.md",
         "change_type": "append",
         "section": "Scoring"},
    ],
    intents=[
        # Intentionally vague — low domain specificity
        {"concept": "Unknown", "domain_level": "Unknown",
         "intent": "Improve scoring robustness for edge cases"},
    ],
    target_components=["ScoringPipeline"],
    action_plan={
        "objective": "Improve scoring robustness for edge cases",
        "target_components": ["ScoringPipeline"],
        "target_files": ["src/scoring/pipeline.py"],
        "detailed_instructions": [
            "Investigate edge cases in scoring pipeline",
            "TBD — exact changes unclear",
        ],
    },
    diff="""\
--- a/src/scoring/pipeline.py
+++ b/src/scoring/pipeline.py
@@ -80,6 +80,10 @@
     def normalize(self, raw_scores):
         normed = [s / self.max_raw for s in raw_scores]
+        # Handle edge cases
+        normed = [max(0.0, min(s, 1.0)) for s in normed]
+        if not normed:
+            logger.warning("Empty score list after normalization")
         return normed
""",
    changed_files=["src/scoring/pipeline.py"],
    is_ui_related=False,
    mock_alignment={
        "intent_match": 0.55,
        "plan_match": 0.50,
        "component_scope_respected": True,
    },
    mock_drift={
        "overreach_detected": False,
        "missing_requirements": [
            "No specific edge cases identified or tested",
        ],
        "unintended_modifications": [],
        "semantic_mismatch": [
            "Vague intent makes it impossible to verify completeness",
        ],
    },
    expected_recommendation="REJECT",
    expected_overreach=False,
    expected_visual_triggered=False,
    notes="Ambiguous invariant. Intent extractor confidence low. "
          "Plan has TBD. Router may flag ambiguity.",
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 9. UI Layout Drift Test
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INVARIANT_9 = _fixture(
    9,
    "UI Layout Drift",
    "Score dispersion metric must be visible on dashboard header.",
    memory_changes=[
        {"file": "docs/memory/02_success/success_criteria.md",
         "change_type": "append",
         "section": "Dashboard Layout"},
    ],
    intents=[
        {"concept": "Dashboard", "domain_level": "Visualization",
         "intent": "Add score dispersion metric to dashboard header"},
    ],
    target_components=["Dashboard"],
    action_plan={
        "objective": "Add score dispersion metric to dashboard header area",
        "target_components": ["Dashboard"],
        "target_files": ["dashboard/app.js", "dashboard/index.html"],
        "detailed_instructions": [
            "Add <span data-testid='dispersion-metric'> in header section",
            "Compute dispersion from score data and bind to element",
            "Format as percentage with 2 decimals",
        ],
    },
    diff="""\
--- a/dashboard/index.html
+++ b/dashboard/index.html
@@ -12,6 +12,9 @@
     <header>
         <h1>TraderFund Dashboard</h1>
+        <span data-testid="dispersion-metric" class="header-metric">
+            Dispersion: <span id="dispersion-value">--</span>%
+        </span>
     </header>
--- a/dashboard/app.js
+++ b/dashboard/app.js
@@ -55,6 +55,12 @@
 function updateDashboard(data) {
+    // Compute score dispersion
+    const scores = data.candidates.map(c => c.score);
+    const mean = scores.reduce((a, b) => a + b, 0) / scores.length;
+    const variance = scores.reduce((a, s) => a + (s - mean) ** 2, 0) / scores.length;
+    const dispersion = (Math.sqrt(variance) / mean * 100).toFixed(2);
+    document.getElementById('dispersion-value').textContent = dispersion;
     renderTable(data);
 }
""",
    changed_files=["dashboard/index.html", "dashboard/app.js"],
    is_ui_related=True,
    mock_alignment={
        "intent_match": 0.92,
        "plan_match": 0.90,
        "component_scope_respected": True,
    },
    mock_drift={
        "overreach_detected": False,
        "missing_requirements": [],
        "unintended_modifications": [],
        "semantic_mismatch": [],
    },
    expected_recommendation="REVIEW",
    expected_overreach=False,
    expected_visual_triggered=True,
    visual_report_override={
        "dom_passed": True,
        "visual_drift": True,
        "pixel_diff_ratio": 0.08,
        "failed_assertions": [],
        "capture_success": True,
        "screenshot_diff_error": None,
    },
    notes="UI layout change. Visual drift detected (pixel diff > 5%). "
          "Score penalized -0.15 for visual_drift → REVIEW.",
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 10. Stability Pressure Test
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INVARIANT_10 = _fixture(
    10,
    "Stability Pressure (Repeat)",
    "All convergence scores must log computation latency.",
    memory_changes=[
        {"file": "docs/memory/02_success/success_criteria.md",
         "change_type": "modify",
         "section": "Runtime Invariants"},
    ],
    intents=[
        {"concept": "ConvergenceEngine", "domain_level": "Runtime",
         "intent": "Ensure all convergence scores log computation latency"},
    ],
    target_components=["ConvergenceEngine"],
    action_plan={
        "objective": "Verify and tighten latency logging — add threshold warning",
        "target_components": ["ConvergenceEngine"],
        "target_files": ["src/convergence/engine.py"],
        "detailed_instructions": [
            "Verify existing latency logging is present",
            "Add warning if latency > 500ms",
            "Add latency_ms to convergence metadata output",
        ],
    },
    diff="""\
--- a/src/convergence/engine.py
+++ b/src/convergence/engine.py
@@ -47,8 +47,12 @@
     def compute(self, candidates):
         _start = time.monotonic()
         scores = self._score_all(candidates)
         ranked = self._rank(scores)
         elapsed_ms = (time.monotonic() - _start) * 1000.0
         logger.info(f"ConvergenceEngine.compute latency: {elapsed_ms:.2f}ms")
+        if elapsed_ms > 500.0:
+            logger.warning(f"ConvergenceEngine.compute SLOW: {elapsed_ms:.2f}ms > 500ms threshold")
         self._last_latency_ms = elapsed_ms
+        ranked.metadata["latency_ms"] = elapsed_ms
         return ranked
""",
    changed_files=["src/convergence/engine.py"],
    is_ui_related=False,
    mock_alignment={
        "intent_match": 0.91,
        "plan_match": 0.89,
        "component_scope_respected": True,
    },
    mock_drift={
        "overreach_detected": False,
        "missing_requirements": [],
        "unintended_modifications": [],
        "semantic_mismatch": [],
    },
    expected_recommendation="ACCEPT",
    expected_overreach=False,
    expected_visual_triggered=False,
    notes="Repeat target (ConvergenceEngine). Drift memory should recognize component. "
          "Stability index may shift. Router behaviour may adjust based on history.",
)


# ── All fixtures in order ────────────────────────────────────
ALL_INVARIANTS = [
    INVARIANT_1,
    INVARIANT_2,
    INVARIANT_3,
    INVARIANT_4,
    INVARIANT_5,
    INVARIANT_6,
    INVARIANT_7,
    INVARIANT_8,
    INVARIANT_9,
    INVARIANT_10,
]
