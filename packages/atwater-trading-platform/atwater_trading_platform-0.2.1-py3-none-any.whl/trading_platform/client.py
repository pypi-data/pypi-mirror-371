"""
Main TradingClient class for the Trading Platform SDK
"""

import asyncio
import logging
from typing import Any, Optional, cast
from urllib.parse import urljoin, urlparse

import aiohttp

from .auth import AuthManager
from .exceptions import ConnectionError as SDKConnectionError
from .market_data import MarketDataManager
from .orders import OrdersManager
from .pnl import PnLManager

logger = logging.getLogger(__name__)


class TradingClient:
    """
    Async client for the AtwaterFinancial HFT Trading Platform
    Provides access to:
    - Authentication and JWT token management
    - Market data streaming via WebSocket
    - Order placement and management
    - Position and PnL tracking

    Example:
        client = TradingClient(
            base_url='https://trading.atwater.financial',
            jwt_token='your-jwt-token'
        )

        # Place an order
        order = await client.orders.create(
            symbol='SPY',
            side='buy',
            quantity=100,
            order_type='limit',
            price=450.50
        )

        # Get positions
        positions = await client.pnl.get_positions()

        # Subscribe to market data
        await client.market_data.subscribe(['SPY', 'QQQ'])
    """

    def __init__(
        self,
        base_url: str = "http://localhost",
        jwt_token: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        **kwargs
    ):
        """
        Initialize the trading client

        Args:
            base_url: Base URL for the trading platform APIs
            jwt_token: JWT authentication token (if available)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            **kwargs: Additional configuration options
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self._extra_config = kwargs

        # Parse service URLs from base URL
        parsed = urlparse(self.base_url)
        self.service_urls = {
            'auth': f"{parsed.scheme}://{parsed.hostname}:8080",
            'symbol_server': f"{parsed.scheme}://{parsed.hostname}:8003",
            'order_router': f"{parsed.scheme}://{parsed.hostname}:8083",
            'pnl_monitor': f"{parsed.scheme}://{parsed.hostname}:8084",
            'market_data': f"ws{'s' if parsed.scheme == 'https' else ''}://{parsed.hostname}:8081/ws",
        }

        # Initialize HTTP session
        self._session: Optional[aiohttp.ClientSession] = None

        # Initialize service managers
        self.auth = AuthManager(self)
        self.orders = OrdersManager(self)
        self.market_data = MarketDataManager(self)
        self.pnl = PnLManager(self)

        # Set initial JWT token if provided
        if jwt_token:
            self.auth.set_jwt_token(jwt_token)

    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def _ensure_session(self):
        """Ensure aiohttp session is created"""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=30,
                ttl_dns_cache=300,
                use_dns_cache=True,
            )

            timeout = aiohttp.ClientTimeout(total=self.timeout)

            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': 'TradingPlatform-Python-SDK/0.1.0',
                    'Content-Type': 'application/json',
                }
            )

    async def close(self):
        """Close the client and cleanup resources"""
        if self.market_data:
            await self.market_data.close()

        if self._session and not self._session.closed:
            await self._session.close()

    @property
    def session(self) -> aiohttp.ClientSession:
        """Get the aiohttp session, creating it if necessary"""
        if self._session is None or self._session.closed:
            raise SDKConnectionError(

                    "Client session not initialized. "
                    "Use async context manager or call _ensure_session()"

            )
        return self._session

    def get_service_url(self, service: str) -> str:
        """Get the URL for a specific service"""
        if service not in self.service_urls:
            raise ValueError(f"Unknown service: {service}")
        return self.service_urls[service]

    async def request(
        self,
        method: str,
        service: str,
        path: str,
        auth_required: bool = True,
        **kwargs
    ) -> dict[str, Any]:
        """
        Make an authenticated HTTP request to a service

        Args:
            method: HTTP method (GET, POST, etc.)
            service: Service name (auth, symbol_server, order_router, etc.)
            path: API path (without leading slash)
            auth_required: Whether authentication is required
            **kwargs: Additional arguments passed to aiohttp

        Returns:
            JSON response data

        Raises:
            TradingPlatformError: On API errors
            ConnectionError: On connection issues
        """
        await self._ensure_session()

        url = urljoin(self.get_service_url(service) + '/', path.lstrip('/'))

        # Add authentication headers if required
        headers = kwargs.pop('headers', {})
        if auth_required and self.auth.jwt_token:
            headers['Authorization'] = f'Bearer {self.auth.jwt_token}'

        # Retry logic for requests
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                async with self.session.request(method, url, headers=headers, **kwargs) as response:
                    response_data = cast(dict[str, Any], await response.json())

                    if response.status >= 400:
                        error_msg = response_data.get('message', f'HTTP {response.status}')
                        error_code = response_data.get('error', 'API_ERROR')
                        request_id = response_data.get('request_id')

                        from .exceptions import APIError
                        raise APIError(
                            error_msg,
                            status_code=response.status,
                            error_code=error_code,
                            request_id=request_id,
                            response_data=response_data
                        )

                    return response_data

            except aiohttp.ClientError as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(
                        "Request failed (attempt %s/%s): %s. Retrying in %ss...",
                        attempt + 1,
                        self.max_retries + 1,
                        e,
                        wait_time,
                    )
                    await asyncio.sleep(wait_time)
                    continue
                break

        # If all retries failed, raise the last exception
        if last_exception:
            raise SDKConnectionError(
                f"Request failed after {self.max_retries + 1} attempts: {last_exception}"
            )

        raise SDKConnectionError("Request failed with no exception captured")

    async def health_check(self) -> dict[str, Any]:
        """
        Check the health of all services

        Returns:
            Dict with health status of each service
        """
        services = ['auth', 'symbol_server', 'order_router', 'pnl_monitor']
        health_status = {}

        for service in services:
            try:
                response = await self.request('GET', service, 'health', auth_required=False)
                health_status[service] = {
                    'status': 'healthy',
                    'response': response
                }
            except Exception as e:
                health_status[service] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }

        return health_status
