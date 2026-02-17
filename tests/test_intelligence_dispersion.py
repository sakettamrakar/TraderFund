import unittest
from unittest.mock import MagicMock, patch
from intelligence.engine import IntelligenceEngine
from intelligence.contracts import AttentionSignal
from pathlib import Path
from datetime import datetime

class TestIntelligenceDispersion(unittest.TestCase):
    def test_score_dispersion(self):
        # Use a temporary directory for output to avoid clutter
        engine = IntelligenceEngine(Path("/tmp/test_output"))

        # Create signals with variance 0.16
        # Values: 1.0, 1.8. Mean=1.4. Var=((0.4^2 + 0.4^2)/2) = 0.16.
        sig1 = AttentionSignal(
            symbol="A", signal_type="TEST", domain="TEST", metric_label="Test",
            metric_value=1.0, unit="x", baseline="0", reason="Test",
            explanation={}, timestamp=datetime.now().isoformat(), market="US"
        )
        sig2 = AttentionSignal(
            symbol="B", signal_type="TEST", domain="TEST", metric_label="Test",
            metric_value=1.8, unit="x", baseline="0", reason="Test",
            explanation={}, timestamp=datetime.now().isoformat(), market="US"
        )

        # Mock _run_generators to return these signals
        with patch.object(engine, '_run_generators', return_value=[sig1, sig2]):
            # Mock _persist_snapshot to avoid file I/O and directory creation
            with patch.object(engine, '_persist_snapshot'):
                # Mock universe builder to return dummy symbols
                engine.universe_builder.get_symbols = MagicMock(return_value=["A", "B"])

                # Run cycle
                snapshot = engine.run_cycle("US", {}, {})

                # Assert that signals are preserved
                # Current threshold is 0.21, so 0.16 should fail (signals cleared).
                # New threshold is 0.15, so 0.16 should pass (signals preserved).
                self.assertTrue(len(snapshot.signals) > 0, "Signals were cleared due to dispersion check")

if __name__ == '__main__':
    unittest.main()
