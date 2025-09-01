# MetaTrader 5 Integration

This document describes how to use the MetaTrader 5 (MT5) integration with the TradingView Webhooks Bot.

## Overview

The MT5Demo action allows you to execute trades on MetaTrader 5 demo accounts via TradingView webhooks. This is perfect for testing trading strategies without risking real money.

## Prerequisites

1. **MetaTrader 5 Terminal**: Download and install from [MetaQuotes website](https://www.metatrader5.com/)
2. **Demo Account**: Create a demo account through your MT5 terminal
3. **Python Environment**: Ensure you have the required dependencies installed

## Installation

1. Install the required Python packages:
```bash
pip install -r src/requirements.txt
```

2. Set up your environment variables in `.env` file or system environment:
```env
MT5_LOGIN=51234567              # Your demo account number
MT5_PASSWORD=demo_password      # Your demo account password
MT5_SERVER=MetaQuotes-Demo      # Demo server name
MT5_ENVIRONMENT=demo            # Environment (demo/live)
```

## Configuration

The MT5Demo action is automatically registered when the application starts. It will attempt to connect to your demo account using the provided credentials.

### Default Settings

- **Login**: 51234567 (demo account)
- **Password**: demo_password
- **Server**: MetaQuotes-Demo
- **Environment**: demo

## Webhook Usage

Send POST requests to your webhook endpoint with JSON payloads to trigger trades.

### Supported Actions

#### 1. Account Information
```json
{
    "action": "info"
}
```
Returns account balance, equity, margin, etc.

#### 2. Get Positions
```json
{
    "action": "positions",
    "symbol": "EURUSD"  // Optional: specific symbol, or "ALL" for all positions
}
```
Returns all open positions.

#### 3. Buy Order
```json
{
    "action": "buy",
    "symbol": "EURUSD",
    "volume": "0.01",
    "order_type": "market",     // Optional: "market", "limit", "stop"
    "price": "1.1000",          // Required for limit/stop orders
    "stop_loss": "1.0950",      // Optional
    "take_profit": "1.1050",    // Optional
    "comment": "Webhook trade"  // Optional
}
```

#### 4. Sell Order
```json
{
    "action": "sell",
    "symbol": "EURUSD",
    "volume": "0.01",
    "order_type": "market",
    "price": "1.1000",          // Required for limit/stop orders
    "stop_loss": "1.1050",      // Optional
    "take_profit": "1.0950",    // Optional
    "comment": "Webhook trade"  // Optional
}
```

#### 5. Close Position
```json
{
    "action": "close",
    "ticket": "12345"           // Position ticket number (required)
}
```

### TradingView Alert Setup

1. In TradingView, create an alert on your chart
2. Set the webhook URL to your bot's endpoint (e.g., `https://your-domain.com/webhook`)
3. Use the JSON payload format in the alert message:

```json
{
    "action": "buy",
    "symbol": "{{ticker}}",
    "volume": "0.01",
    "comment": "TradingView Alert: {{strategy.order.action}}"
}
```

## Testing

Run the test script to verify your setup:

```bash
python test_mt5_demo.py
```

This will test:
- Account connection
- Account information retrieval
- Position queries
- Sample trade execution

## Common Currency Pairs

The action supports all currency pairs available in your MT5 terminal:

- **Major Pairs**: EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, AUDUSD, NZDUSD
- **Minor Pairs**: EURGBP, EURJPY, EURCHF, GBPJPY, GBPCHF, AUDJPY
- **Exotic Pairs**: USDTRY, USDZAR, USDMXN, USDRUB

## Risk Management

### Demo Account Safety
- Always use demo accounts for testing
- Demo accounts use virtual money only
- No real financial risk involved

### Production Considerations
- Never use live accounts without thorough testing
- Implement proper risk management rules
- Set appropriate stop losses and take profits
- Monitor positions regularly

## Troubleshooting

### Connection Issues
- Ensure MT5 terminal is running
- Check demo account credentials
- Verify server name is correct
- Check firewall/antivirus settings

### Common Errors
- `MT5 initialize failed`: MT5 terminal not running or not installed
- `MT5 login failed`: Invalid credentials or server name
- `Symbol not found`: Currency pair not available in your account type
- `Invalid volume`: Volume outside min/max limits for the symbol

### Logs
Check the application logs for detailed error messages:
```bash
tail -f logs/app.log
```

## API Reference

### Volume Constraints
- Minimum volume varies by symbol (usually 0.01 lots)
- Maximum volume varies by account type
- Volume must be in steps (usually 0.01)

### Order Types
- `market`: Immediate execution at current price
- `limit`: Execution when price reaches specified level
- `stop`: Stop order (stop loss/take profit)

### Position Management
- Each position has a unique ticket number
- Use ticket numbers to close specific positions
- Multiple positions can be open for the same symbol

## Support

For issues specific to the MT5 integration:
1. Check MT5 terminal logs
2. Verify demo account access through MT5 directly
3. Review webhook bot application logs
4. Test with the provided test script

For general webhook bot issues, refer to the main README.md file.
