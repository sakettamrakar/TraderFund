from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from ..connectors.base import BrokerConnector


class MCPBrokerConnector(BrokerConnector, ABC):
    connector_mode = "MCP"
    provenance_source = "mcp"

    @abstractmethod
    def connect_to_mcp(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def fetch_portfolio_summary(self) -> Dict[str, Any]:
        raise NotImplementedError
