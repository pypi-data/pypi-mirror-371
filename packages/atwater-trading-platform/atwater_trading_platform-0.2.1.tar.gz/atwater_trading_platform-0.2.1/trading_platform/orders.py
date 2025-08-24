"""
Order management for the Trading Platform SDK
"""

import logging
from typing import Any, Optional

from .exceptions import OrderError

logger = logging.getLogger(__name__)


class OrdersManager:
    """
    Manages trading orders for the platform
    """

    def __init__(self, client):
        self.client = client

    async def create(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = 'market',
        price: Optional[float] = None,
        exchange: Optional[str] = None,
        time_in_force: str = 'GTC',
        **kwargs
    ) -> dict[str, Any]:
        """
        Place a new trading order
        Args:
            symbol: Trading symbol (e.g., 'SPY', 'BTC-USD')
            side: Order side ('buy' or 'sell')
            quantity: Order quantity
            order_type: Order type ('market', 'limit', 'stop', 'stop_limit')
            price: Limit price (required for limit orders)
            exchange: Target exchange (optional, will use smart routing if not specified)
            time_in_force: Time in force ('GTC', 'IOC', 'FOK')
            **kwargs: Additional order parameters
        Returns:
            Order confirmation data
        """
        # Validate inputs
        if side.lower() not in ['buy', 'sell']:
            raise OrderError(f"Invalid order side: {side}. Must be 'buy' or 'sell'")

        if quantity <= 0:
            raise OrderError(f"Invalid quantity: {quantity}. Must be positive")

        if order_type.lower() in ['limit', 'stop_limit'] and price is None:
            raise OrderError(f"Price required for {order_type} orders")

        # Prepare order data
        order_data = {
            'symbol': symbol.upper(),
            'side': side.upper(),
            'quantity': str(quantity),  # Use string to avoid floating point precision issues
            'order_type': order_type.upper(),
            'time_in_force': time_in_force.upper(),
            **kwargs
        }

        if price is not None:
            order_data['price'] = str(price)

        if exchange:
            order_data['exchange'] = exchange.upper()

        try:
            response = await self.client.request(
                'POST',
                'order_router',
                'orders',
                json=order_data
            )

            if not response.get('success'):
                message = response.get('message', 'Unknown error')
                raise OrderError(f"Order rejected: {message}")

            order_info = response.get('data', {})
            logger.info("Order placed successfully: %s", order_info.get('order_id'))

            return dict(order_info)

        except Exception as e:
            if isinstance(e, OrderError):
                raise
            raise OrderError(f"Failed to place order: {e}") from e

    async def cancel(self, order_id: str) -> dict[str, Any]:
        """
        Cancel an existing order
        Args:
            order_id: Order ID to cancel
        Returns:
            Cancellation confirmation
        """
        try:
            response = await self.client.request(
                'DELETE',
                'order_router',
                f'orders/{order_id}'
            )

            if not response.get('success'):
                message = response.get('message', 'Unknown error')
                raise OrderError(
                    f"Order cancellation failed: {message}"
                )

            logger.info("Order cancelled successfully: %s", order_id)
            return dict(response.get('data', {}))

        except Exception as e:
            if isinstance(e, OrderError):
                raise
            raise OrderError(f"Failed to cancel order {order_id}: {e}") from e

    async def get_order(self, order_id: str) -> dict[str, Any]:
        """
        Get details for a specific order
        Args:
            order_id: Order ID to retrieve
        Returns:
            Order details
        """
        try:
            response = await self.client.request(
                'GET',
                'order_router',
                f'orders/{order_id}'
            )

            if not response.get('success'):
                raise OrderError(f"Order not found: {order_id}")

            return dict(response.get('data', {}))

        except Exception as e:
            if isinstance(e, OrderError):
                raise
            raise OrderError(f"Failed to get order {order_id}: {e}") from e

    async def list_orders(
        self,
        status: Optional[str] = None,
        symbol: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[dict[str, Any]]:
        """
        List orders with optional filtering
        Args:
            status: Filter by order status ('pending', 'filled', 'cancelled', etc.)
            symbol: Filter by trading symbol
            limit: Maximum number of orders to return
            offset: Number of orders to skip
        Returns:
            List of order data
        """
        params: dict[str, int | str] = {
            'limit': limit,
            'offset': offset,
        }

        if status:
            params['status'] = status
        if symbol:
            params['symbol'] = symbol.upper()

        try:
            response = await self.client.request(
                'GET',
                'order_router',
                'orders',
                params=params
            )

            if not response.get('success'):
                message = response.get('message', 'Unknown error')
                raise OrderError(f"Failed to list orders: {message}")

            data = response.get('data', [])
            return list(data)

        except Exception as e:
            if isinstance(e, OrderError):
                raise
            raise OrderError(f"Failed to list orders: {e}") from e

    async def modify_order(
        self,
        order_id: str,
        quantity: Optional[float] = None,
        price: Optional[float] = None,
        **kwargs
    ) -> dict[str, Any]:
        """
        Modify an existing order
        Args:
            order_id: Order ID to modify
            quantity: New quantity (optional)
            price: New price (optional)
            **kwargs: Additional modification parameters
        Returns:
            Modified order data
        """
        modification_data = {}

        if quantity is not None:
            if quantity <= 0:
                raise OrderError(
                    f"Invalid quantity: {quantity}. Must be positive"
                )
            modification_data['quantity'] = str(quantity)

        if price is not None:
            modification_data['price'] = str(price)

        modification_data.update(kwargs)

        if not modification_data:
            raise OrderError("No modifications specified")

        try:
            response = await self.client.request(
                'PATCH',
                'order_router',
                f'orders/{order_id}',
                json=modification_data
            )

            if not response.get('success'):
                message = response.get('message', 'Unknown error')
                raise OrderError(
                    f"Order modification failed: {message}"
                )

            logger.info("Order modified successfully: %s", order_id)
            return dict(response.get('data', {}))

        except Exception as e:
            if isinstance(e, OrderError):
                raise
            raise OrderError(f"Failed to modify order {order_id}: {e}") from e

    async def get_order_status(self, order_id: str) -> str:
        """
        Get the current status of an order
        Args:
            order_id: Order ID to check
        Returns:
            Order status string
        """
        order_data = await self.get_order(order_id)
        status_value = order_data.get('status', 'unknown')
        return str(status_value)
