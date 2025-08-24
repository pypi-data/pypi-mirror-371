"""
Exception classes for the Trading Platform SDK
"""

from typing import Any, Dict, Optional


class TradingPlatformError(Exception):
    """Base exception for all trading platform errors"""

    def __init__(self, message: str, error_code: Optional[str] = None,
                 request_id: Optional[str] = None, **kwargs):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.request_id = request_id
        self.details = kwargs


class AuthenticationError(TradingPlatformError):
    """Raised when authentication fails"""
    pass


class APIError(TradingPlatformError):
    """Raised when API requests fail"""

    def __init__(self, message: str, status_code: Optional[int] = None,
                 response_data: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.response_data = response_data


class ConnectionError(TradingPlatformError):
    """Raised when connection to services fails"""
    pass


class OrderError(TradingPlatformError):
    """Raised when order operations fail"""
    pass


class MarketDataError(TradingPlatformError):
    """Raised when market data operations fail"""
    pass
