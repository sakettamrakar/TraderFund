"""Universe Expansion - Models"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class SymbolMaster:
    symbol: str
    exchange: str
    instrument_type: str
    listing_status: str
    sector: Optional[str]
    industry: Optional[str]
    country: str
    currency: str
    market_cap: Optional[float]
    market_cap_bucket: str
    eligibility_hint: str
    data_source: str
    ingestion_timestamp: str
    version: str
    
    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "exchange": self.exchange,
            "instrument_type": self.instrument_type,
            "listing_status": self.listing_status,
            "sector": self.sector,
            "industry": self.industry,
            "country": self.country,
            "currency": self.currency,
            "market_cap": self.market_cap,
            "market_cap_bucket": self.market_cap_bucket,
            "eligibility_hint": self.eligibility_hint,
            "data_source": self.data_source,
            "ingestion_timestamp": self.ingestion_timestamp,
            "version": self.version,
        }
    
    @classmethod
    def from_csv_row(cls, row: dict, version: str = "1.0.0"):
        """Create from symbols.csv row."""
        from . import config
        
        # Market cap bucket (unknown without API data)
        market_cap_bucket = "unknown"
        
        # Eligibility hint based on exchange and type
        exchange = row.get("exchange", "")
        asset_type = row.get("assetType", "Stock")
        status = row.get("status", "Active")
        
        if exchange in config.VALID_EXCHANGES and asset_type in config.VALID_ASSET_TYPES:
            eligibility_hint = "likely"
        else:
            eligibility_hint = "unlikely"
        
        if status in config.EXCLUDED_STATUS:
            eligibility_hint = "unlikely"
        
        return cls(
            symbol=row.get("symbol", ""),
            exchange=exchange,
            instrument_type=asset_type,
            listing_status=status,
            sector=row.get("sector") if row.get("sector") else None,
            industry=row.get("industry") if row.get("industry") else None,
            country="USA",
            currency="USD",
            market_cap=None,
            market_cap_bucket=market_cap_bucket,
            eligibility_hint=eligibility_hint,
            data_source="alpha_vantage_listing",
            ingestion_timestamp=datetime.utcnow().isoformat(),
            version=version,
        )
