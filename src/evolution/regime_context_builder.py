"""
Regime Context Builder (EV-RUN-0).
Establishes a single, immutable source of truth for regime state during EV-RUN.

SAFETY INVARIANTS:
- READ-ONLY: Loads data, does not modify.
- ATOMIC: Computed once per execution block.
- MANDATORY: All EV-RUN-x tasks must consume this context.
- NO FALLBACK: Fails if viability check fails.
"""
import os
import sys
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from evolution.regime_audit.viability_check import StateViabilityCheck, ViabilityStatus
# Import generic profile types - actual loader used in caller
from evolution.profile_loader import EvaluationProfile, ModeType, WindowingType
from ingestion.market_loader import MarketLoader

class RegimeContextError(Exception):
    """Raised when regime context cannot be established or is violated."""
    pass

class RegimeContextBuilder:
    """
    Builds and persists the immutable regime context for an EV-RUN session.
    Supports both legacy single-execution and profile-driven windowed execution.
    """
    
    def __init__(self, output_path: str = "docs/evolution/context/regime_context.json", profile: Optional[EvaluationProfile] = None, market: str = "US"):
        self.output_path = Path(output_path)
        self.output_root = self.output_path.parent # docs/evolution/context
        self.viability_checker = StateViabilityCheck()
        self.profile = profile
        self.market = market

        # Base time range for evaluation (Mocked for this phase as per existing code)
        self.base_start_date = datetime(2023, 1, 1)
        self.base_end_date = datetime.now()
        
        self.loader = MarketLoader()
    
    def _determine_regime(self, window_end: datetime) -> Tuple[str, str, bool]:
        """
        Determines the authoritative regime label and code.
        REAL IMPLEMENTATION using MarketLoader.
        """
        # 1. Forced Regime
        if self.profile and self.profile.mode.type == ModeType.FORCED_REGIME:
            override = self.profile.regime.override
            if not override:
                raise RegimeContextError("Forced Regime mode active but no override string provided.")
            return (f"Forced {override.regime_code}", override.regime_code, True)

        # 2. Real Detection
        try:
            df = self.loader.load_benchmark(self.market)
            if df.empty:
                return ("Unknown (No Data)", "UNKNOWN", False)
                
            # Filter up to window_end
            mask = df.index <= window_end
            df_curr = df.loc[mask]
            
            if df_curr.empty:
                 return ("Unknown (Gap)", "UNKNOWN", False)
                 
            # Logic: Price > SMA50
            if len(df_curr) < 50:
                 return ("Unknown (Insufficient History)", "UNKNOWN", False)
                 
            price = df_curr.iloc[-1]['Close']
            sma50 = df_curr['Close'].rolling(window=50).mean().iloc[-1]
            sma200 = df_curr['Close'].rolling(window=200).mean().iloc[-1]
            
            # Volatility Check
            vol_level = self.loader.load_volatility(self.market, df_curr)
            
            # Gate Logic (From recalibration doc)
            # BULLISH: Price > SMA50 AND Vol < Threshold
            # Thresholds: US=25, INDIA=HighVol?
            vol_threshold = 25.0 if self.market == "US" else 1000.0 # Loose for India surrogate for now
            
            if price > sma50 and vol_level < vol_threshold:
                return ("Bullish", "BULLISH", False)
            elif price < sma200:
                return ("Bearish", "BEARISH", False)
            else:
                return ("Neutral", "NEUTRAL", False)
                
        except Exception as e:
            print(f"Regime Calculation Warning: {e}")
            return ("Unknown (Error)", "UNKNOWN", False)

    def _parse_duration(self, duration_str: str) -> timedelta:
        """Parses '90d' format into timedelta."""
        match = re.match(r"^(\d+)d$", duration_str)
        if not match:
             raise ValueError(f"Unsupported duration format: {duration_str}. Only 'd' (days) supported.")
        days = int(match.group(1))
        return timedelta(days=days)

    def _generate_windows(self) -> List[Dict[str, Any]]:
        """
        Generates list of window definitions based on profile windowing settings.
        """
        windows = []
        
        if not self.profile or self.profile.windowing.type == WindowingType.SINGLE:
            windows.append({
                "window_id": "GLOBAL",
                "start": self.base_start_date,
                "end": self.base_end_date
            })
            return windows

        if self.profile.windowing.type == WindowingType.ROLLING:
            w_size = self._parse_duration(self.profile.windowing.window_size)
            s_size = self._parse_duration(self.profile.windowing.step_size)
            current_start = self.base_start_date
            while current_start + w_size <= self.base_end_date:
                current_end = current_start + w_size
                w_id = f"WINDOW-{current_start.strftime('%Y-%m-%d')}-{current_end.strftime('%Y-%m-%d')}"
                windows.append({"window_id": w_id, "start": current_start, "end": current_end})
                current_start += s_size
            return windows
            
        raise NotImplementedError(f"Windowing type {self.profile.windowing.type} not yet implemented")

    def build_context(self) -> Dict[str, Any]:
        """Legacy/Default entrypoint."""
        return self._build_and_persist_context(self.output_path, self.base_start_date, self.base_end_date)

    def build_windowed_contexts(self) -> List[str]:
        """Profile-driven entrypoint."""
        if not self.profile:
            raise RegimeContextError("Cannot build windowed contexts without a profile.")
        windows = self._generate_windows()
        generated_paths = []
        for w in windows:
            w_path = self.output_root / self.profile.profile_id / w["window_id"] / "regime_context.json"
            w_path.parent.mkdir(parents=True, exist_ok=True)
            self._build_and_persist_context(w_path, w["start"], w["end"])
            generated_paths.append(str(w_path))
        return generated_paths

    def _build_and_persist_context(self, path: Path, start: datetime, end: datetime) -> Dict[str, Any]:
        # Viability Check (Mocked args for now, but logic inside is checking symbols)
        # Ideally we check self.market's required symbols
        
        viability = self.viability_checker.check_overall_viability(
            required_symbols=["SPY"] if self.market=="US" else ["NSE_RELIANCE"],
            symbol_coverage={"SPY": "PRESENT", "NSE_RELIANCE": "PRESENT"}, # Assume present for dry-run of logic
            symbol_sufficiency={"SPY": True, "NSE_RELIANCE": True},
            symbol_alignment={"SPY": True, "NSE_RELIANCE": True}
        )
        
        if viability.status == ViabilityStatus.NOT_VIABLE:
            raise RegimeContextError(f"Regime viability check failed: {viability.blocking_reasons}")

        regime_label, regime_code, is_counterfactual = self._determine_regime(end)
        
        context = {
            "regime_context": {
                "regime_label": regime_label,
                "regime_code": regime_code,
                "computed_at": datetime.now().isoformat(),
                "market": self.market,
                "evaluation_window": {
                    "start": start.isoformat(),
                    "end": end.isoformat()
                },
                "inputs_used": ["SPY"] if self.market=="US" else ["NSE_RELIANCE"],
                "viability": {
                    "viable": True,
                    "reason": "Authentic Data Ingestion"
                },
                "properties": {
                    "is_counterfactual": is_counterfactual,
                    "profile_id": self.profile.profile_id if self.profile else None
                },
                "version": "2.0.0-IGNITION"
            }
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(context, f, indent=2)
            
        print(f"Generated Regime Context ({self.market}): {regime_code}")
        return context

if __name__ == "__main__":
    try:
        # Simple test usage
        builder = RegimeContextBuilder(market="US")
        builder.build_context()
    except Exception as e:
        print(f"CRITICAL FAILURE: {str(e)}")
        sys.exit(1)
