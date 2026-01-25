from dataclasses import dataclass

class VisualStyles:
    # Color Palette (Safe, Neutral)
    # No Bright Green/Red implying "Go/Stop".
    # Use HSL/Hex for subtleties.
    
    COLOR_BULLISH = "#4A90E2" # Soft Blue
    COLOR_BEARISH = "#E2904A" # Soft Orange
    COLOR_NEUTRAL = "#9B9B9B" # Grey
    
    # Opacity Rules for Confidence
    # Opacity = Confidence / 100
    
    @staticmethod
    def get_color_for_direction(direction: str) -> str:
        if direction == "BULLISH": return VisualStyles.COLOR_BULLISH
        if direction == "BEARISH": return VisualStyles.COLOR_BEARISH
        return VisualStyles.COLOR_NEUTRAL

    @staticmethod
    def get_confidence_style(confidence: float) -> str:
        """Returns CSS style string for confidence visualization."""
        opacity = max(0.3, confidence / 100.0)
        return f"opacity: {opacity};"

    APP_TITLE = "TraderFund Intelligence Layer"
    APP_ICON = "🧠"
    
    WARNING_BANNER = """
    **RESEARCH ONLY**: This dashboard visualizes historical data and statistical patterns.
    High confidence does NOT imply future profitability.
    """
