"""
Test suite for the Trading Platform SDK
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from trading_platform import TradingClient
from trading_platform.exceptions import (
    APIError, 
    AuthenticationError, 
    OrderError, 
    MarketDataError
)


@pytest.fixture
def client():
    """Create a test client"""
    return TradingClient(
        base_url='http://localhost',
        jwt_token='test-token'
    )


@pytest.mark.asyncio
class TestTradingClient:
    """Test cases for TradingClient"""
    
    async def test_client_initialization(self):
        """Test client initialization"""
        client = TradingClient(
            base_url='https://test.example.com',
            jwt_token='test-token',
            timeout=60.0,
            max_retries=5
        )
        
        assert client.base_url == 'https://test.example.com'
        assert client.timeout == 60.0
        assert client.max_retries == 5
        assert client.auth.jwt_token == 'test-token'
    
    async def test_service_url_generation(self):
        """Test service URL generation"""
        client = TradingClient(base_url='https://example.com')
        
        assert client.get_service_url('auth') == 'https://example.com:8080'
        assert client.get_service_url('symbol_server') == 'https://example.com:8003'
        assert client.get_service_url('order_router') == 'https://example.com:8083'
        assert client.get_service_url('market_data') == 'wss://example.com:8081/ws'
    
    async def test_context_manager(self):
        """Test async context manager"""
        client = TradingClient()
        
        async with client:
            assert client._session is not None
            assert not client._session.closed
        
        assert client._session.closed


@pytest.mark.asyncio
class TestAuthManager:
    """Test cases for AuthManager"""
    
    async def test_set_jwt_token(self, client):
        """Test setting JWT token"""
        client.auth.set_jwt_token('new-token', expires_in=3600)
        
        assert client.auth.jwt_token == 'new-token'
        assert client.auth.token_expires_at is not None
    
    async def test_token_expiration_check(self, client):
        """Test token expiration checking"""
        # Clear any existing token first
        client.auth.jwt_token = None
        client.auth.token_expires_at = None
        
        # Test with no token
        assert client.auth.is_token_expired() == True
        
        # Test with valid token
        client.auth.set_jwt_token('test-token', expires_in=3600)
        assert client.auth.is_token_expired() == False
        
        # Test with expired token
        client.auth.set_jwt_token('test-token', expires_in=-1)
        assert client.auth.is_token_expired() == True


@pytest.mark.asyncio
class TestOrdersManager:
    """Test cases for OrdersManager"""
    
    async def test_order_validation(self, client):
        """Test order input validation"""
        with pytest.raises(OrderError, match="Invalid order side"):
            await client.orders.create('SPY', 'invalid', 100)
        
        with pytest.raises(OrderError, match="Invalid quantity"):
            await client.orders.create('SPY', 'buy', -100)
        
        with pytest.raises(OrderError, match="Price required"):
            await client.orders.create('SPY', 'buy', 100, 'limit')
    
    @patch('trading_platform.client.TradingClient.request')
    async def test_create_order_success(self, mock_request, client):
        """Test successful order creation"""
        mock_request.return_value = {
            'success': True,
            'data': {
                'order_id': 'order-123',
                'symbol': 'SPY',
                'side': 'BUY',
                'quantity': '100',
                'status': 'pending'
            }
        }
        
        result = await client.orders.create(
            symbol='SPY',
            side='buy',
            quantity=100,
            order_type='market'
        )
        
        assert result['order_id'] == 'order-123'
        assert result['symbol'] == 'SPY'
        
        # Verify request was called correctly
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        assert args[0] == 'POST'
        assert args[1] == 'order_router'
        assert args[2] == 'orders'
        
        order_data = kwargs['json']
        assert order_data['symbol'] == 'SPY'
        assert order_data['side'] == 'BUY'
        assert order_data['quantity'] == '100'


@pytest.mark.asyncio 
class TestMarketDataManager:
    """Test cases for MarketDataManager"""
    
    @patch('trading_platform.client.TradingClient.request')
    async def test_get_symbols(self, mock_request, client):
        """Test getting symbols"""
        mock_request.return_value = {
            'success': True,
            'data': [
                {'symbol': 'SPY', 'name': 'SPDR S&P 500 ETF'},
                {'symbol': 'QQQ', 'name': 'Invesco QQQ ETF'}
            ]
        }
        
        symbols = await client.market_data.get_symbols()
        
        assert len(symbols) == 2
        assert symbols[0]['symbol'] == 'SPY'
        assert symbols[1]['symbol'] == 'QQQ'
    
    @patch('trading_platform.client.TradingClient.request')
    async def test_search_symbols(self, mock_request, client):
        """Test symbol search"""
        mock_request.return_value = {
            'success': True,
            'data': [
                {'symbol': 'SPY', 'name': 'SPDR S&P 500 ETF'}
            ]
        }
        
        results = await client.market_data.search_symbols('SPY')
        
        assert len(results) == 1
        assert results[0]['symbol'] == 'SPY'
        
        # Verify request parameters
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        assert kwargs['params'] == {'q': 'SPY'}


@pytest.mark.asyncio
class TestPnLManager:
    """Test cases for PnLManager"""
    
    @patch('trading_platform.client.TradingClient.request')
    async def test_get_positions(self, mock_request, client):
        """Test getting positions"""
        mock_request.return_value = {
            'success': True,
            'data': [
                {
                    'symbol': 'SPY',
                    'quantity': 100,
                    'market_value': 45000.0,
                    'unrealized_pnl': 500.0,
                    'average_cost': 445.0
                }
            ]
        }
        
        positions = await client.pnl.get_positions()
        
        assert len(positions) == 1
        assert positions[0]['symbol'] == 'SPY'
        assert positions[0]['quantity'] == 100
    
    @patch('trading_platform.client.TradingClient.request')
    async def test_get_position_for_symbol(self, mock_request, client):
        """Test getting position for specific symbol"""
        mock_request.return_value = {
            'success': True,
            'data': [
                {
                    'symbol': 'SPY',
                    'quantity': 100,
                    'market_value': 45000.0,
                    'unrealized_pnl': 500.0,
                    'average_cost': 445.0
                }
            ]
        }
        
        position = await client.pnl.get_position('SPY')
        
        assert position['symbol'] == 'SPY'
        assert position['quantity'] == 100


@pytest.mark.asyncio
class TestExceptionHandling:
    """Test exception handling"""
    
    @patch('trading_platform.client.TradingClient.request')
    async def test_api_error_handling(self, mock_request, client):
        """Test API error handling"""
        mock_request.side_effect = APIError(
            "Order rejected", 
            status_code=400,
            error_code="INVALID_ORDER"
        )
        
        with pytest.raises(OrderError) as exc_info:
            await client.orders.create('SPY', 'buy', 100)
        
        # The OrderError should wrap the APIError
        assert "Order rejected" in str(exc_info.value)
    
    async def test_invalid_service_url(self, client):
        """Test invalid service URL handling"""
        with pytest.raises(ValueError, match="Unknown service"):
            client.get_service_url('invalid_service')


# Fixtures and helpers for integration tests
@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket connection"""
    ws = AsyncMock()
    ws.closed = False
    return ws


@pytest.fixture 
def mock_aiohttp_session():
    """Create a mock aiohttp session"""
    session = AsyncMock()
    session.closed = False
    return session


if __name__ == "__main__":
    pytest.main([__file__])