# MetaTrader 5 Integration - Deployment Guide

## Overview

This guide explains how to deploy the MetaTrader 5 integration in different environments, addressing the architectural challenges of running MT5 (a Windows application) in various deployment scenarios.

## Architecture Understanding

### The Challenge
- **MetaTrader 5** is a Windows-only application
- **MetaTrader5 Python package** only works on Windows (it's a wrapper around the MT5 terminal)
- **Docker/Linux** cannot run MT5 directly without Wine emulation
- **macOS/ARM64** cannot run the MetaTrader5 Python package

### Our Solution
We provide two implementations:
1. **MT5Demo** - Real MetaTrader 5 integration (Windows only)
2. **MT5DemoMock** - Mock implementation for development/testing (cross-platform)

## Deployment Options

### Option 1: Development/Testing (Current Setup)
**Platform**: macOS, Linux, Docker
**Implementation**: MT5DemoMock
**Use Case**: Development, testing webhook logic, CI/CD

```bash
# Current configuration uses mock implementation
REGISTERED_ACTIONS = ['BitsoSpot', 'MT5DemoMock']
```

**Benefits**:
- ✅ Works on any platform
- ✅ No MetaTrader 5 installation required
- ✅ Perfect for testing webhook integration
- ✅ Simulates real MT5 responses

**Limitations**:
- ❌ No actual trading (mock only)
- ❌ No real market data

### Option 2: Windows VPS Production
**Platform**: Windows Server/VPS
**Implementation**: MT5Demo
**Use Case**: Live trading with real MetaTrader 5

#### Setup Steps:

1. **Provision Windows VPS**
   ```
   - Windows Server 2019/2022
   - Minimum 2GB RAM, 2 CPU cores
   - RDP access enabled
   ```

2. **Install MetaTrader 5**
   ```
   - Download from MetaQuotes website
   - Install MT5 terminal
   - Create demo account or configure live account
   - Ensure terminal stays logged in
   ```

3. **Install Python Environment**
   ```powershell
   # Install Python 3.11+
   # Install dependencies
   pip install -r requirements.txt
   # Note: MetaTrader5 package will install on Windows
   ```

4. **Configure for Production**
   ```python
   # Update settings.py for production
   REGISTERED_ACTIONS = ['BitsoSpot', 'MT5Demo']  # Use real MT5Demo
   ```

5. **Environment Variables**
   ```env
   MT5_LOGIN=your_mt5_account_number
   MT5_PASSWORD=your_mt5_password
   MT5_SERVER=your_mt5_server
   MT5_ENVIRONMENT=demo  # or 'live' for real trading
   ```

### Option 3: Hybrid Architecture (Recommended)
**Setup**: Webhook bot on Linux/Docker + MT5 on Windows
**Communication**: REST API or message queue

#### Architecture:
```
TradingView → Linux Webhook Bot → Windows MT5 Service
             (Docker)              (VPS/Local)
```

#### Implementation:

1. **Webhook Bot (Linux/Docker)**
   - Receives TradingView webhooks
   - Validates and processes signals
   - Forwards trading commands to MT5 service

2. **MT5 Service (Windows)**
   - Small Windows service running MT5Demo
   - Exposes REST API for trade execution
   - Handles actual MetaTrader 5 communication

3. **Communication**
   ```python
   # Webhook bot sends HTTP requests to MT5 service
   import requests

   mt5_service_url = "http://windows-vps:8080"
   trade_data = {"action": "buy", "symbol": "EURUSD", "volume": 0.01}

   response = requests.post(f"{mt5_service_url}/trade", json=trade_data)
   ```

### Option 4: Docker with Wine (Complex)
**Platform**: Docker with Wine emulation
**Implementation**: MT5Demo in Wine container
**Use Case**: Containerized production (advanced users)

This approach requires:
- Wine configuration for MT5
- X11 forwarding for GUI
- Complex networking setup
- Platform specification (linux/amd64)

## Current Configuration

### Environment Variables Required
```env
# Required for both mock and real implementations
MT5_LOGIN=5039692049
MT5_PASSWORD=B_S8BmRn
MT5_SERVER=MetaQuotes-Demo
MT5_ENVIRONMENT=demo
```

### Testing the Current Setup
```bash
# Test mock implementation (works on any platform)
cd src
python3 -c "
import os
os.environ['MT5_LOGIN'] = '5039692049'
os.environ['MT5_PASSWORD'] = 'B_S8BmRn'
os.environ['MT5_SERVER'] = 'MetaQuotes-Demo'

from components.actions.mt5_demo_mock import MT5DemoMock
action = MT5DemoMock()

# Test account info
action.set_data({'action': 'info'})
action.run()

# Test buy order
action.set_data({'action': 'buy', 'symbol': 'EURUSD', 'volume': '0.01'})
action.run()
"
```

## Migration Path to Production

### Step 1: Validate Mock Implementation
- Test all webhook scenarios with MT5DemoMock
- Verify TradingView integration works
- Test error handling and logging

### Step 2: Set Up Windows Environment
- Provision Windows VPS
- Install MetaTrader 5 terminal
- Configure demo account
- Test manual trading

### Step 3: Deploy Real Implementation
```python
# Change settings.py
REGISTERED_ACTIONS = ['BitsoSpot', 'MT5Demo']  # Switch to real implementation

# Update requirements.txt to include MetaTrader5 (Windows only)
MetaTrader5==5.0.45
```

### Step 4: Production Testing
- Start with demo account
- Test small position sizes
- Monitor logs carefully
- Implement proper error handling

## Troubleshooting

### Mock Implementation Issues
```bash
# Check environment variables
echo $MT5_LOGIN
echo $MT5_PASSWORD

# Check Python imports
python3 -c "from components.actions.mt5_demo_mock import MT5DemoMock; print('OK')"
```

### Real Implementation Issues (Windows)
```powershell
# Check MT5 terminal is running
tasklist | findstr terminal64.exe

# Check Python MT5 package
python -c "import MetaTrader5 as mt5; print('OK')"

# Test MT5 connection
python -c "
import MetaTrader5 as mt5
print('Initialize:', mt5.initialize())
print('Account info:', mt5.account_info())
mt5.shutdown()
"
```

## Security Considerations

### Demo Account Safety
- Always test with demo accounts first
- Demo accounts use virtual money only
- No financial risk during development

### Production Security
- Use environment variables for credentials
- Never commit credentials to version control
- Implement proper logging (without sensitive data)
- Set up monitoring and alerts
- Use proper firewall rules
- Regular security updates

## Performance Considerations

### Mock Implementation
- Very fast (no external dependencies)
- Suitable for high-frequency testing
- No network latency

### Real Implementation
- Network latency to MT5 servers
- MT5 terminal must stay running
- Windows system resource requirements
- Consider connection timeouts

## Support and Maintenance

### Mock Implementation
- Maintained as part of webhook bot
- Cross-platform compatibility
- Easy to extend with new features

### Real Implementation
- Requires Windows system administration
- MT5 terminal updates and maintenance
- Broker-specific considerations
- Network connectivity monitoring

## Conclusion

The current setup with **MT5DemoMock** allows you to:
- ✅ Develop and test on macOS/Linux
- ✅ Validate TradingView webhook integration
- ✅ Test all trading logic without risk
- ✅ Use Docker for deployment (mock mode)

When ready for production:
- Deploy on Windows VPS with real **MT5Demo**
- Or use hybrid architecture with Linux webhook bot + Windows MT5 service
- Start with demo account for safety
- Monitor carefully before going live
