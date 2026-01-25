
import pandas as pd
from typing import Any, Dict
from datetime import datetime, timedelta

from traderfund.regime.providers.base import IEventPressureProvider

class CalendarEventProvider(IEventPressureProvider):
    """
    Simulates event pressure based on time-to-impact logic.
    In a real system, this connects to an Economic Calendar.
    For Phase 1 stateless implementation, we'll perform a basic check 
    against a passed 'external_events' list or assume 0 pressure if no events.
    """
    def __init__(self, max_lookahead_minutes: int = 60, lock_window_minutes: int = 15):
        self.max_lookahead_minutes = max_lookahead_minutes
        self.lock_window_minutes = lock_window_minutes

    def get_pressure(self, data: Any) -> Dict[str, Any]:
        """
        Calculates pressure from event proximity.
        Expects data to contain a 'timestamp' and optionally a list of 'upcoming_events'.
        """
        # For pure OHLCV dataframe input in Phase 1, we often lack event data.
        # We will check if 'upcoming_events' is attached to the dataframe metadata 
        # or if passed as a separate arg (Base interface says 'data: Any').
        # Design decision: If valid event data is missing, return 0.0 safe state.
        
        current_time = None
        events = []

        if isinstance(data, pd.DataFrame):
            if not data.empty and 'timestamp' in data.columns:
                current_time = pd.to_datetime(data['timestamp'].iloc[-1])
            elif not data.empty and isinstance(data.index, pd.DatetimeIndex):
                current_time = data.index[-1]
            
            # Simulated: In a real app, we'd look up a calendar service here.
            # For stateless provider, we check if events are injected.
            if hasattr(data, 'attrs') and 'events' in data.attrs:
                events = data.attrs['events']
        
        if current_time is None:
            return {'pressure': 0.0, 'is_lock_window': False}

        max_pressure = 0.0
        is_locked = False

        for event in events:
            # Event structure expected: {'time': datetime, 'impact': float (0-1)}
            event_time = pd.to_datetime(event['time'])
            impact = event.get('impact', 1.0)
            
            delta = (event_time - current_time).total_seconds() / 60.0
            
            if 0 <= delta <= self.lock_window_minutes:
                is_locked = True
                max_pressure = 1.0
            elif 0 < delta <= self.max_lookahead_minutes:
                # Linear decay: 1.0 at lock_window boundary, 0.0 at max_lookahead
                # Distance from lock window:
                dist = delta - self.lock_window_minutes
                range_span = self.max_lookahead_minutes - self.lock_window_minutes
                pressure = 1.0 - (dist / range_span)
                normalized = max(0.0, min(1.0, pressure * impact))
                max_pressure = max(max_pressure, normalized)
                
        return {
            'pressure': float(max_pressure),
            'is_lock_window': is_locked
        }
