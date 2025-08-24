# AtwaterFinancial Trading Platform Python SDK

A high-performance async client library for the AtwaterFinancial HFT trading platform. This SDK provides easy access to market data streaming, order management, and PnL tracking capabilities.

## Features

- **Async/Await Support**: Built with asyncio for high-performance concurrent operations
- **Market Data Streaming**: Real-time market data via WebSocket connections
- **Order Management**: Place, modify, and cancel orders across multiple exchanges
- **Position & PnL Tracking**: Monitor positions and profit/loss in real-time
- **Authentication**: JWT-based authentication with Google OAuth2 support
- **Error Handling**: Comprehensive error handling with retry logic
- **Type Hints**: Full type annotation support for better development experience

## Installation

```bash
pip install trading-platform
```

Or install from source:

```bash
git clone https://github.com/AtwaterFinancial/AtwaterFinancial.git
cd AtwaterFinancial/sdks/python
pip install -e .
```

## Quick Start

```python
import asyncio
from trading_platform import TradingClient

async def main():
    # Initialize the client
    async with TradingClient(
        base_url='https://trading.atwater.financial',
        jwt_token='your-jwt-token'
    ) as client:
        
        # Check service health
        health = await client.health_check()
        print("Service health:", health)
        
        # Place an order
        order = await client.orders.create(
            symbol='SPY',
            side='buy',
            quantity=100,
            order_type='limit',
            price=450.50
        )
        print("Order placed:", order)
        
        # Get positions
        positions = await client.pnl.get_positions()
        print("Current positions:", positions)
        
        # Subscribe to market data
        def on_market_data(data):
            print(f"Market data: {data}")
        
        await client.market_data.subscribe(
            symbols=['SPY', 'QQQ'],
            callback=on_market_data
        )
        
        # Keep receiving data for 30 seconds
        await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())
```

## Authentication

The SDK supports JWT token authentication. You can either provide a token directly or use the OAuth2 flow:

### Using JWT Token

```python
client = TradingClient(
    base_url='https://trading.atwater.financial',
    jwt_token='your-jwt-token'
)
```

### Using OAuth2 Flow

```python
async with TradingClient(base_url='https://trading.atwater.financial') as client:
    # Get OAuth2 authorization URL
    auth_url = await client.auth.login_with_google('http://localhost:3000/callback')
    print(f"Please visit: {auth_url}")
    
    # After user authorization, handle the callback
    # (authorization_code and state come from the callback URL)
    profile = await client.auth.handle_oauth_callback(authorization_code, state)
    print("Logged in:", profile)
```

## API Reference

### TradingClient

The main client class that provides access to all trading platform services.

#### Methods

- `health_check()`: Check the health status of all services
- `close()`: Close the client and cleanup resources

### AuthManager (`client.auth`)

Handles authentication and token management.

#### Methods

- `login_with_google(redirect_uri)`: Initiate Google OAuth2 login
- `handle_oauth_callback(code, state)`: Handle OAuth2 callback
- `validate_token()`: Validate current JWT token
- `get_profile()`: Get user profile information
- `logout()`: Logout and clear authentication state

### OrdersManager (`client.orders`)

Manages trading orders.

#### Methods

- `create(symbol, side, quantity, order_type, price=None, ...)`: Place a new order
- `cancel(order_id)`: Cancel an existing order
- `get_order(order_id)`: Get order details
- `list_orders(status=None, symbol=None, ...)`: List orders with filtering
- `modify_order(order_id, quantity=None, price=None, ...)`: Modify an existing order

### MarketDataManager (`client.market_data`)

Handles real-time market data streaming and symbol information.

#### Methods

- `subscribe(symbols, data_types=None, callback=None)`: Subscribe to market data
- `unsubscribe(symbols)`: Unsubscribe from market data
- `get_symbols()`: Get list of available symbols
- `search_symbols(query)`: Search for symbols
- `get_symbol_info(symbol, exchange=None)`: Get symbol information

### PnLManager (`client.pnl`)

Tracks positions, profit/loss, and performance metrics.

#### Methods

- `get_positions(symbol=None, exchange=None)`: Get current positions
- `get_position(symbol, exchange=None)`: Get position for specific symbol
- `get_pnl_summary()`: Get overall PnL summary
- `get_historical_pnl(start_date=None, end_date=None, ...)`: Get historical PnL data
- `get_trade_history(...)`: Get trade history
- `get_performance_metrics(...)`: Get performance analytics
- `export_data(data_type, format='csv', ...)`: Export data to file

## Error Handling

The SDK provides comprehensive error handling with specific exception types:

```python
from trading_platform import (
    TradingPlatformError,
    AuthenticationError,
    APIError,
    ConnectionError,
    OrderError,
    MarketDataError
)

try:
    order = await client.orders.create(
        symbol='INVALID',
        side='buy',
        quantity=100
    )
except OrderError as e:
    print(f"Order failed: {e.message}")
    print(f"Error code: {e.error_code}")
except APIError as e:
    print(f"API error: {e.message}")
    print(f"Status code: {e.status_code}")
```

## Configuration

### Service URLs

By default, the SDK connects to services on localhost with standard ports:

- Auth Gateway: `:8080`
- Symbol Server: `:8003`
- Order Router: `:8083`
- PnL Monitor: `:8084`
- Market Data: `:8081/ws`

You can customize the base URL:

```python
client = TradingClient(base_url='https://your-trading-platform.com')
```

### Timeouts and Retries

```python
client = TradingClient(
    base_url='https://trading.atwater.financial',
    timeout=60.0,  # Request timeout in seconds
    max_retries=5  # Maximum retry attempts
)
```

## Examples

See the `examples/` directory for more comprehensive examples:

- `basic_trading.py`: Basic order placement and management
- `market_data_streaming.py`: Real-time market data streaming
- `portfolio_monitoring.py`: Position and PnL tracking
- `advanced_strategy.py`: Complete trading strategy implementation

## Development

To set up for development:

```bash
git clone https://github.com/AtwaterFinancial/AtwaterFinancial.git
cd AtwaterFinancial/sdks/python

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black trading_platform/
isort trading_platform/

# Type checking
mypy trading_platform/
```

## License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## Support

For questions and support:

- GitHub Issues: [https://github.com/AtwaterFinancial/AtwaterFinancial/issues](https://github.com/AtwaterFinancial/AtwaterFinancial/issues)
- Documentation: [https://docs.atwater.financial](https://docs.atwater.financial)
- Email: dev@atwater.financial