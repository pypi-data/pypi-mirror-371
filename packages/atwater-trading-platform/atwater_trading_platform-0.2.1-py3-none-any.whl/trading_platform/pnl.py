"""
PnL and position management for the Trading Platform SDK
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Optional, cast

from .exceptions import TradingPlatformError

logger = logging.getLogger(__name__)


class PnLManager:
    """
    Manages positions, PnL tracking, and related analytics
    """

    def __init__(self, client):
        self.client = client

    async def get_positions(
        self,
        symbol: Optional[str] = None,
        exchange: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """
        Get current positions
        Args:
            symbol: Filter by specific symbol (optional)
            exchange: Filter by specific exchange (optional)
        Returns:
            List of position data
        """
        params = {}
        if symbol:
            params['symbol'] = symbol.upper()
        if exchange:
            params['exchange'] = exchange.upper()

        try:
            response = await self.client.request(
                'GET',
                'pnl_monitor',
                'positions',
                params=params if params else None
            )

            if not response.get('success'):
                message = response.get('message', 'Unknown error')
                raise TradingPlatformError(
                    f"Failed to get positions: {message}"
                )

            return cast(list[dict[str, Any]], response.get('data', []))

        except Exception as e:
            if isinstance(e, TradingPlatformError):
                raise
            raise TradingPlatformError(f"Failed to get positions: {e}") from e

    async def get_position(self, symbol: str, exchange: Optional[str] = None) -> dict[str, Any]:
        """
        Get position for a specific symbol
        Args:
            symbol: Trading symbol
            exchange: Specific exchange (optional)
        Returns:
            Position data for the symbol
        """
        positions = await self.get_positions(symbol=symbol, exchange=exchange)

        if not positions:
            return {
                'symbol': symbol.upper(),
                'quantity': 0,
                'market_value': 0,
                'unrealized_pnl': 0,
                'realized_pnl': 0,
                'average_cost': 0
            }

        # If multiple positions (different exchanges), aggregate them
        if len(positions) == 1:
            return positions[0]

        # Aggregate multiple positions
        total_quantity = sum(float(pos.get('quantity', 0)) for pos in positions)
        total_market_value = sum(float(pos.get('market_value', 0)) for pos in positions)
        total_unrealized_pnl = sum(float(pos.get('unrealized_pnl', 0)) for pos in positions)
        total_realized_pnl = sum(float(pos.get('realized_pnl', 0)) for pos in positions)

        # Calculate weighted average cost
        total_cost_basis = sum(
            float(pos.get('quantity', 0)) * float(pos.get('average_cost', 0))
            for pos in positions
        )
        avg_cost = total_cost_basis / total_quantity if total_quantity != 0 else 0

        return {
            'symbol': symbol.upper(),
            'quantity': total_quantity,
            'market_value': total_market_value,
            'unrealized_pnl': total_unrealized_pnl,
            'realized_pnl': total_realized_pnl,
            'average_cost': avg_cost,
            'exchanges': [pos.get('exchange') for pos in positions]
        }

    async def get_pnl_summary(self) -> dict[str, Any]:
        """
        Get overall PnL summary across all positions
        Returns:
            Aggregated PnL summary
        """
        try:
            response = await self.client.request(
                'GET',
                'pnl_monitor',
                'pnl/summary'
            )

            if not response.get('success'):
                message = response.get('message', 'Unknown error')
                raise TradingPlatformError(
                    f"Failed to get PnL summary: {message}"
                )

            return cast(dict[str, Any], response.get('data', {}))

        except Exception as e:
            if isinstance(e, TradingPlatformError):
                raise
            raise TradingPlatformError(f"Failed to get PnL summary: {e}") from e

    async def get_historical_pnl(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        symbol: Optional[str] = None,
        granularity: str = 'daily'
    ) -> list[dict[str, Any]]:
        """
        Get historical PnL data
        Args:
            start_date: Start date for historical data (defaults to 30 days ago)
            end_date: End date for historical data (defaults to now)
            symbol: Filter by specific symbol (optional)
            granularity: Data granularity ('daily', 'hourly', 'minute')
        Returns:
            List of historical PnL data points
        """
        if start_date is None:
            start_date = datetime.utcnow() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.utcnow()

        params: dict[str, str] = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'granularity': granularity,
        }

        if symbol:
            params['symbol'] = symbol.upper()

        try:
            response = await self.client.request(
                'GET',
                'pnl_monitor',
                'pnl/historical',
                params=params
            )

            if not response.get('success'):
                message = response.get('message', 'Unknown error')
                raise TradingPlatformError(
                    f"Failed to get historical PnL: {message}"
                )

            return cast(list[dict[str, Any]], response.get('data', []))

        except Exception as e:
            if isinstance(e, TradingPlatformError):
                raise
            raise TradingPlatformError(f"Failed to get historical PnL: {e}") from e

    async def get_trade_history(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[dict[str, Any]]:
        """
        Get trade history
        Args:
            symbol: Filter by specific symbol (optional)
            start_date: Start date for trade history
            end_date: End date for trade history
            limit: Maximum number of trades to return
            offset: Number of trades to skip
        Returns:
            List of trade data
        """
        params: dict[str, int | str] = {
            'limit': limit,
            'offset': offset,
        }

        if symbol:
            params['symbol'] = symbol.upper()
        if start_date:
            params['start_date'] = start_date.isoformat()
        if end_date:
            params['end_date'] = end_date.isoformat()

        try:
            response = await self.client.request(
                'GET',
                'pnl_monitor',
                'trades',
                params=params
            )

            if not response.get('success'):
                message = response.get('message', 'Unknown error')
                raise TradingPlatformError(
                    f"Failed to get trade history: {message}"
                )

            return cast(list[dict[str, Any]], response.get('data', []))

        except Exception as e:
            if isinstance(e, TradingPlatformError):
                raise
            raise TradingPlatformError(f"Failed to get trade history: {e}") from e

    async def get_performance_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict[str, Any]:
        """
        Get performance metrics and analytics
        Args:
            start_date: Start date for metrics calculation
            end_date: End date for metrics calculation
        Returns:
            Performance metrics including Sharpe ratio, max drawdown, etc.
        """
        params: dict[str, str] = {}
        if start_date:
            params['start_date'] = start_date.isoformat()
        if end_date:
            params['end_date'] = end_date.isoformat()

        try:
            response = await self.client.request(
                'GET',
                'pnl_monitor',
                'analytics/performance',
                params=params if params else None
            )

            if not response.get('success'):
                message = response.get('message', 'Unknown error')
                raise TradingPlatformError(
                    f"Failed to get performance metrics: {message}"
                )

            return cast(dict[str, Any], response.get('data', {}))

        except Exception as e:
            if isinstance(e, TradingPlatformError):
                raise
            raise TradingPlatformError(f"Failed to get performance metrics: {e}") from e

    async def get_risk_metrics(self) -> dict[str, Any]:
        """
        Get current risk metrics
        Returns:
            Risk metrics including VaR, exposure, concentration, etc.
        """
        try:
            response = await self.client.request(
                'GET',
                'pnl_monitor',
                'analytics/risk'
            )

            if not response.get('success'):
                message = response.get('message', 'Unknown error')
                raise TradingPlatformError(
                    f"Failed to get risk metrics: {message}"
                )

            return cast(dict[str, Any], response.get('data', {}))

        except Exception as e:
            if isinstance(e, TradingPlatformError):
                raise
            raise TradingPlatformError(f"Failed to get risk metrics: {e}") from e

    async def export_data(
        self,
        data_type: str,
        format: str = 'csv',
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        **kwargs
    ) -> str:
        """
        Export PnL or trade data to file
        Args:
            data_type: Type of data to export ('trades', 'pnl', 'positions')
            format: Export format ('csv', 'json', 'excel')
            start_date: Start date for export
            end_date: End date for export
            **kwargs: Additional export parameters
        Returns:
            Download URL or file path for the exported data
        """
        export_params = {
            'data_type': data_type,
            'format': format,
            **kwargs
        }

        if start_date:
            export_params['start_date'] = start_date.isoformat()
        if end_date:
            export_params['end_date'] = end_date.isoformat()

        try:
            response = await self.client.request(
                'POST',
                'pnl_monitor',
                'export',
                json=export_params
            )

            if not response.get('success'):
                message = response.get('message', 'Unknown error')
                raise TradingPlatformError(
                    f"Failed to export data: {message}"
                )

            download_url = response.get('download_url')
            if isinstance(download_url, str) and download_url:
                return download_url
            file_path = response.get('file_path', '')
            return cast(str, file_path)

        except Exception as e:
            if isinstance(e, TradingPlatformError):
                raise
            raise TradingPlatformError(f"Failed to export data: {e}") from e
