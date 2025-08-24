"""
Market data streaming and subscription management for the Trading Platform SDK
"""

import asyncio
import contextlib
import json
import logging
from typing import Any, Callable, Optional, cast

import aiohttp

from .exceptions import MarketDataError

logger = logging.getLogger(__name__)


class MarketDataManager:
    """
    Manages real-time market data subscriptions and streaming
    """

    def __init__(self, client):
        self.client = client
        self._ws_connection: Optional[aiohttp.ClientWebSocketResponse] = None
        self._subscriptions: set[str] = set()
        self._callbacks: dict[str, list[Callable]] = {}
        self._running = False
        self._reconnect_task: Optional[asyncio.Task] = None
        self._listen_task: Optional[asyncio.Task] = None

    async def connect(self) -> bool:
        """
        Connect to the market data WebSocket

        Returns:
            True if connection successful
        """
        if self._ws_connection and not self._ws_connection.closed:
            return True

        try:
            ws_url = self.client.get_service_url('market_data')

            # Add authentication if token is available
            headers = {}
            if self.client.auth.jwt_token:
                headers['Authorization'] = f'Bearer {self.client.auth.jwt_token}'

            session = self.client.session
            self._ws_connection = await session.ws_connect(
                ws_url + '/market-data',
                headers=headers,
                heartbeat=30,
                timeout=30
            )

            # Authenticate WebSocket connection
            if self.client.auth.jwt_token:
                await self._send_message(
                    {
                        'type': 'auth',
                        'token': self.client.auth.jwt_token,
                    }
                )

            logger.info("Connected to market data WebSocket")
            return True

        except Exception as e:
            logger.error("Failed to connect to market data WebSocket: %s", e)
            return False

    async def disconnect(self):
        """Disconnect from the market data WebSocket"""
        self._running = False

        if self._listen_task and not self._listen_task.done():
            self._listen_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._listen_task

        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._reconnect_task

        if self._ws_connection and not self._ws_connection.closed:
            await self._ws_connection.close()

        logger.info("Disconnected from market data WebSocket")

    async def subscribe(
        self, symbols: list[str], data_types: Optional[list[str]] = None, callback: Optional[Callable] = None
    ) -> None:
        """
        Subscribe to market data for symbols

        Args:
            symbols: List of trading symbols to subscribe to
            data_types: Types of data to subscribe to ('trades', 'quotes', 'depth')
            callback: Optional callback function for received data
        """
        if data_types is None:
            data_types = ['trades', 'quotes']

        # Ensure connection is established
        if not await self.connect():
            raise MarketDataError("Failed to connect to market data service")

        # Start listening if not already running
        if not self._running:
            self._running = True
            self._listen_task = asyncio.create_task(self._listen_loop())

        # Register callback if provided
        if callback:
            for symbol in symbols:
                if symbol not in self._callbacks:
                    self._callbacks[symbol] = []
                self._callbacks[symbol].append(callback)

        # Send subscription message
        subscription_msg: dict[str, Any] = {
            'type': 'subscribe',
            'symbols': [s.upper() for s in symbols],
            'data_types': data_types,
        }

        await self._send_message(subscription_msg)

        # Track subscriptions
        self._subscriptions.update(s.upper() for s in symbols)

        logger.info("Subscribed to market data for symbols: %s", symbols)

    async def unsubscribe(self, symbols: list[str]) -> None:
        """
        Unsubscribe from market data for symbols

        Args:
            symbols: List of trading symbols to unsubscribe from
        """
        if not self._ws_connection or self._ws_connection.closed:
            return

        unsubscribe_msg: dict[str, Any] = {
            'type': 'unsubscribe',
            'symbols': [s.upper() for s in symbols],
        }

        await self._send_message(unsubscribe_msg)

        # Remove from tracked subscriptions and callbacks
        for symbol in symbols:
            symbol_upper = symbol.upper()
            self._subscriptions.discard(symbol_upper)
            if symbol_upper in self._callbacks:
                del self._callbacks[symbol_upper]

        logger.info("Unsubscribed from market data for symbols: %s", symbols)

    def add_callback(self, symbol: str, callback: Callable) -> None:
        """
        Add a callback function for a specific symbol

        Args:
            symbol: Trading symbol
            callback: Callback function that receives market data
        """
        symbol_upper = symbol.upper()
        if symbol_upper not in self._callbacks:
            self._callbacks[symbol_upper] = []
        self._callbacks[symbol_upper].append(callback)

    def remove_callback(self, symbol: str, callback: Callable) -> None:
        """
        Remove a callback function for a specific symbol

        Args:
            symbol: Trading symbol
            callback: Callback function to remove
        """
        symbol_upper = symbol.upper()
        if symbol_upper in self._callbacks:
            try:
                self._callbacks[symbol_upper].remove(callback)
                if not self._callbacks[symbol_upper]:
                    del self._callbacks[symbol_upper]
            except ValueError:
                pass

    async def get_symbols(self) -> list[dict[str, Any]]:
        """
        Get list of available trading symbols

        Returns:
            List of symbol information
        """
        try:
            response = await self.client.request(
                'GET',
                'symbol_server',
                'symbols',
                auth_required=False
            )

            if not response.get('success'):
                message = response.get('message', 'Unknown error')
                raise MarketDataError(
                    f"Failed to get symbols: {message}"
                )

            return cast(list[dict[str, Any]], response.get('data', []))

        except Exception as e:
            if isinstance(e, MarketDataError):
                raise
            raise MarketDataError(f"Failed to get symbols: {e}") from e

    async def search_symbols(self, query: str) -> list[dict[str, Any]]:
        """
        Search for symbols matching a query

        Args:
            query: Search query string

        Returns:
            List of matching symbols
        """
        try:
            response = await self.client.request(
                'GET',
                'symbol_server',
                'symbols/search',
                params={'q': query},
                auth_required=False
            )

            if not response.get('success'):
                message = response.get('message', 'Unknown error')
                raise MarketDataError(
                    f"Symbol search failed: {message}"
                )

            return cast(list[dict[str, Any]], response.get('data', []))

        except Exception as e:
            if isinstance(e, MarketDataError):
                raise
            raise MarketDataError(f"Symbol search failed: {e}") from e

    async def get_symbol_info(self, symbol: str, exchange: Optional[str] = None) -> dict[str, Any]:
        """
        Get detailed information about a specific symbol

        Args:
            symbol: Trading symbol
            exchange: Specific exchange (optional)

        Returns:
            Symbol information
        """
        try:
            path = f'symbols/{symbol.upper()}'
            if exchange:
                path += f'/{exchange.upper()}'

            response = await self.client.request(
                'GET',
                'symbol_server',
                path,
                auth_required=False
            )

            if not response.get('success'):
                raise MarketDataError(f"Symbol not found: {symbol}")

            return cast(dict[str, Any], response.get('data', {}))

        except Exception as e:
            if isinstance(e, MarketDataError):
                raise
            raise MarketDataError(f"Failed to get symbol info for {symbol}: {e}") from e

    async def _send_message(self, message: dict[str, Any]) -> None:
        """Send a message to the WebSocket"""
        if not self._ws_connection or self._ws_connection.closed:
            raise MarketDataError("WebSocket not connected")

        try:
            await self._ws_connection.send_str(json.dumps(message))
        except Exception as e:
            logger.error("Failed to send WebSocket message: %s", e)
            raise MarketDataError(f"Failed to send message: {e}") from e

    async def _listen_loop(self) -> None:
        """Main listening loop for WebSocket messages"""
        while self._running:
            try:
                if (self._ws_connection is None) or self._ws_connection.closed:
                    if not await self._reconnect():
                        await asyncio.sleep(5)
                        continue

                assert self._ws_connection is not None
                async for msg in self._ws_connection:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        try:
                            data = json.loads(msg.data)
                            await self._handle_message(data)
                        except json.JSONDecodeError:
                            logger.warning("Invalid JSON received: %s", msg.data)
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        logger.error("WebSocket error: %s", self._ws_connection.exception())
                        break
                    elif msg.type == aiohttp.WSMsgType.CLOSE:
                        logger.info("WebSocket connection closed")
                        break

            except Exception as e:
                logger.error("Error in WebSocket listen loop: %s", e)
                await asyncio.sleep(1)

    async def _handle_message(self, data: dict[str, Any]) -> None:
        """Handle incoming WebSocket messages"""
        msg_type = data.get('type')

        if msg_type == 'market_data':
            symbol = data.get('symbol')
            if symbol and symbol in self._callbacks:
                # Call all registered callbacks for this symbol
                for callback in self._callbacks[symbol]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(data)
                        else:
                            callback(data)
                    except Exception as e:
                        logger.error("Error in market data callback: %s", e)

        elif msg_type == 'error':
            logger.error("Market data error: %s", data.get('message', 'Unknown error'))

        elif msg_type == 'subscription_confirmed':
            logger.info("Subscription confirmed for: %s", data.get('symbols', []))

        else:
            logger.debug(f"Unhandled message type: {msg_type}")

    async def _reconnect(self) -> bool:
        """Attempt to reconnect to WebSocket"""
        logger.info("Attempting to reconnect to market data WebSocket...")

        if await self.connect():
            # Resubscribe to previous subscriptions
            if self._subscriptions:
                subscription_msg: dict[str, Any] = {
                    'type': 'subscribe',
                    'symbols': list(self._subscriptions),
                    'data_types': ['trades', 'quotes'],
                }
                await self._send_message(subscription_msg)

            return True

        return False

    async def close(self) -> None:
        """Close the market data manager and cleanup resources"""
        await self.disconnect()
