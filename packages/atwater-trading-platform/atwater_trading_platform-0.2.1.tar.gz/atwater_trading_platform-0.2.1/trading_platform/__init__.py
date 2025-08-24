"""
AtwaterFinancial Trading Platform Python SDK

A high-performance async client library for the AtwaterFinancial HFT trading platform.
Provides access to market data streaming, order management, and PnL tracking.
"""

__version__ = "0.2.1"
__author__ = "Atwater Financial"

from .client import TradingClient
from .exceptions import (
    APIError,
    AuthenticationError,
    ConnectionError,
    MarketDataError,
    OrderError,
    TradingPlatformError,
)

__all__ = [
    "TradingClient",
    "TradingPlatformError",
    "AuthenticationError",
    "APIError",
    "ConnectionError",
    "OrderError",
    "MarketDataError",
]
