from src.portfolio_intelligence.analytics import analyze_portfolio
from src.portfolio_intelligence.config import PortfolioIntelligenceConfig
from src.portfolio_intelligence.connectors.base import BrokerConnector
from src.portfolio_intelligence.enrichment import enrich_portfolio
from src.portfolio_intelligence.models import (
    BrokerAuthResult,
    InstrumentRecord,
    RawBrokerHolding,
    RawBrokerOrder,
    RawBrokerPosition,
)
from src.portfolio_intelligence.normalization import normalize_portfolio
from src.portfolio_intelligence.service import PortfolioIntelligenceService, PortfolioRefreshService
from src.portfolio_intelligence.validation import PortfolioSystemValidator


class FakeMCPConnector(BrokerConnector):
    broker_name = "ZERODHA"
    market = "INDIA"
    connector_mode = "MCP"
    provenance_source = "kite_mcp"

    def __init__(self, *, authenticated: bool, holdings=None, positions=None, orders=None, instruments=None):
        super().__init__()
        self._authenticated = authenticated
        self._holdings = holdings or []
        self._positions = positions or []
        self._orders = orders or []
        self._instruments = instruments or []

    def connect_to_mcp(self):
        return {"reachable": True, "url": "https://mcp.kite.trade/mcp"}

    def authenticate(self) -> BrokerAuthResult:
        if self._authenticated:
            return BrokerAuthResult(
                broker=self.broker_name,
                authenticated=True,
                message="Authenticated against Kite MCP in read-only mode.",
                login_url=None,
                missing_credentials=[],
                account_id="AB1234",
                account_name="MCP Account",
            )
        return BrokerAuthResult(
            broker=self.broker_name,
            authenticated=False,
            message="Kite MCP login required for read-only portfolio ingestion.",
            login_url="https://kite.zerodha.com/connect/login?api_key=kitemcp",
            missing_credentials=["KITE_MCP_INTERACTIVE_LOGIN"],
        )

    def fetch_holdings(self):
        return self._holdings

    def fetch_positions(self):
        return self._positions

    def fetch_orders(self):
        return self._orders

    def fetch_instruments(self):
        return self._instruments

    def fetch_portfolio_summary(self):
        return {"holding_count": len(self._holdings), "position_count": len(self._positions)}


class FakeAPIConnector(BrokerConnector):
    broker_name = "ZERODHA"
    market = "INDIA"
    provenance_source = "kite_connect_api"

    def __init__(self, *, authenticated: bool, holdings=None, positions=None, orders=None, instruments=None):
        super().__init__()
        self._authenticated = authenticated
        self._holdings = holdings or []
        self._positions = positions or []
        self._orders = orders or []
        self._instruments = instruments or []

    def authenticate(self) -> BrokerAuthResult:
        if self._authenticated:
            return BrokerAuthResult(
                broker=self.broker_name,
                authenticated=True,
                message="Authenticated against Zerodha in read-only mode.",
                login_url=None,
                missing_credentials=[],
                account_id="ZX1234",
                account_name="API Account",
            )
        return BrokerAuthResult(
            broker=self.broker_name,
            authenticated=False,
            message="Missing Zerodha credentials for read-only portfolio ingestion.",
            login_url=None,
            missing_credentials=["KITE_ACCESS_TOKEN or KITE_REQUEST_TOKEN"],
        )

    def fetch_holdings(self):
        return self._holdings

    def fetch_positions(self):
        return self._positions

    def fetch_orders(self):
        return self._orders

    def fetch_instruments(self):
        return self._instruments


def test_portfolio_validator_reports_mcp_and_api_statuses(tmp_path):
    config = PortfolioIntelligenceConfig(base_dir=tmp_path / "portfolio")
    service = PortfolioIntelligenceService(config=config)
    service.build_kite_mcp_connector = lambda: FakeMCPConnector(authenticated=False)
    service.build_zerodha_connector = lambda: FakeAPIConnector(authenticated=False)

    validator = PortfolioSystemValidator(service, PortfolioRefreshService(service))
    report = validator.run()

    assert report["truth_epoch"] == "TRUTH_EPOCH_2026-03-06_01"
    assert report["statuses"]["connectivity"] == "CONNECTIVITY_OK"
    assert report["statuses"]["mcp_connectivity"] == "MCP_CONNECTIVITY_OK"
    assert report["statuses"]["api_fallback"] == "API_FALLBACK_AUTH_REQUIRED"
    assert report["details"]["mcp_auth"]["message"] == "Kite MCP login required for read-only portfolio ingestion."


def test_portfolio_refresh_falls_back_to_api_when_mcp_auth_required(tmp_path):
    config = PortfolioIntelligenceConfig(base_dir=tmp_path / "portfolio")
    service = PortfolioIntelligenceService(config=config)
    service.build_kite_mcp_connector = lambda: FakeMCPConnector(authenticated=False)
    service.build_zerodha_connector = lambda: FakeAPIConnector(
        authenticated=True,
        holdings=[
            RawBrokerHolding(
                symbol="RELIANCE",
                exchange="NSE",
                quantity=10,
                average_price=1250.0,
                last_price=1300.0,
                pnl=500.0,
                product="CNC",
                instrument_token=738561,
                raw={"tradingsymbol": "RELIANCE"},
            )
        ],
        positions=[],
        orders=[
            RawBrokerOrder(
                order_id="1",
                symbol="RELIANCE",
                exchange="NSE",
                transaction_type="BUY",
                quantity=10,
                status="COMPLETE",
                product="CNC",
                variety="regular",
                order_timestamp="2026-03-11T00:00:00Z",
                raw={},
            )
        ],
        instruments=[
            InstrumentRecord(
                symbol="RELIANCE",
                exchange="NSE",
                instrument_token=738561,
                name="Reliance Industries",
                instrument_type="EQ",
                segment="NSE",
                tick_size=0.05,
                lot_size=1,
                raw={},
            )
        ],
    )

    analytics = PortfolioRefreshService(service).refresh_zerodha_portfolio(
        portfolio_id="zerodha_primary",
        account_name="Primary",
        market="INDIA",
    )

    assert analytics["portfolio_data_source"] == "API"
    assert analytics["refresh_diagnostics"]["mcp"]["connectivity_status"] == "MCP_CONNECTIVITY_OK"
    assert analytics["refresh_diagnostics"]["api_fallback"]["status"] == "API_FALLBACK_IN_USE"


def test_portfolio_refresh_uses_mcp_when_valid(tmp_path):
    config = PortfolioIntelligenceConfig(base_dir=tmp_path / "portfolio")
    service = PortfolioIntelligenceService(config=config)
    service.build_kite_mcp_connector = lambda: FakeMCPConnector(
        authenticated=True,
        holdings=[
            RawBrokerHolding(
                symbol="RELIANCE",
                exchange="NSE",
                quantity=10,
                average_price=1250.0,
                last_price=1300.0,
                pnl=500.0,
                product="CNC",
                instrument_token=738561,
                raw={"tradingsymbol": "RELIANCE"},
            )
        ],
        positions=[
            RawBrokerPosition(
                symbol="RELIANCE",
                exchange="NSE",
                quantity=10,
                average_price=1250.0,
                last_price=1300.0,
                pnl=500.0,
                product="CNC",
                instrument_token=738561,
                raw={},
            )
        ],
        orders=[],
        instruments=[
            InstrumentRecord(
                symbol="RELIANCE",
                exchange="NSE",
                instrument_token=738561,
                name="Reliance Industries",
                instrument_type="EQ",
                segment="NSE",
                tick_size=0.05,
                lot_size=1,
                raw={},
            )
        ],
    )
    service.build_zerodha_connector = lambda: FakeAPIConnector(authenticated=False)

    analytics = PortfolioRefreshService(service).refresh_zerodha_portfolio(
        portfolio_id="zerodha_primary",
        account_name="Primary",
        market="INDIA",
    )

    assert analytics["portfolio_data_source"] == "MCP"
    assert analytics["refresh_diagnostics"]["mcp"]["schema_status"] == "MCP_SCHEMA_VALID"
    assert analytics["refresh_diagnostics"]["api_fallback"]["status"] == "API_FALLBACK_NOT_REQUIRED"


def test_portfolio_pipeline_computes_india_holding_analytics():
    normalized = normalize_portfolio(
        holdings=[
            RawBrokerHolding(
                symbol="RELIANCE",
                exchange="NSE",
                quantity=10,
                average_price=1250.0,
                last_price=1300.0,
                pnl=500.0,
                product="CNC",
                instrument_token=738561,
                raw={"tradingsymbol": "RELIANCE"},
            )
        ],
        positions=[],
        instruments=[
            InstrumentRecord(
                symbol="RELIANCE",
                exchange="NSE",
                instrument_token=738561,
                name="Reliance Industries",
                instrument_type="EQ",
                segment="NSE",
                tick_size=0.05,
                lot_size=1,
                raw={},
            )
        ],
        portfolio_id="test_india",
        broker="ZERODHA",
        market="INDIA",
        account_name="Test India",
        truth_epoch="TRUTH_EPOCH_2026-03-06_01",
        data_as_of="2026-03-11T00:00:00Z",
    )

    enriched = enrich_portfolio(normalized, config=PortfolioIntelligenceConfig())
    analytics = analyze_portfolio(enriched)

    assert analytics["overview"]["holding_count"] == 1
    assert analytics["holdings"][0]["ticker"] == "RELIANCE"
    assert analytics["holdings"][0]["sector"] == "Energy"
    assert analytics["holdings"][0]["conviction_score"] >= 0.0
    assert analytics["diversification"]["sector_allocation"]["Energy"] == 100.0
