# Memory Card: Z-Library API Setup Instructions
---
id: mc_project_setup_instructions_20250806
type: memory_card
category: project
created: 2025-08-06
status: active
---

## Prerequisites
- Python 3.12+
- Z-Library account (for credentials)
- pip or uv package manager
- devenv (optional, for development environment)

## Installation Methods

### Method 1: pip install
```bash
pip install zlibrary
```

### Method 2: Build from source
```bash
# Clone repository
cd zlibrary_api_module

# Using devenv
devenv shell -c build

# Or manually
rm -rf dist
python3 -m build
uv pip install dist/zlibrary*.whl
```

### Method 3: Development mode
```bash
cd zlibrary_api_module
pip install -e src/
```

## Configuration

### Environment Variables
Create `.env` file or export:
```bash
export ZLOGIN="your_email@example.com"
export ZPASSW="your_password"
```

### Enable Logging
```python
import logging

logging.getLogger("zlibrary").addHandler(logging.StreamHandler())
logging.getLogger("zlibrary").setLevel(logging.DEBUG)
```

## Testing Setup

### Run Tests
```bash
# Using devenv
devenv shell -c test

# Or manually
python3 src/test.py

# Run specific tests
python3 test_penguin_books.py
python3 tests/test_auth_only.py
```

### Test with Examples
```bash
# Basic usage example
python3 examples/python/basic_usage.py

# Search and download
python3 examples/python/search_and_download.py

# Advanced features
python3 examples/python/advanced_features.py
```

## Tor/Proxy Setup

### Install Tor
```bash
# Ubuntu/Debian
sudo apt install tor obfs4proxy

# Arch
yay -S tor obfs4proxy

# Enable service
sudo systemctl enable --now tor
```

### Configure Tor Bridges (if blocked)
1. Email bridges@torproject.org with: `get transport obfs4`
2. Edit `/etc/tor/torrc`:
```
UseBridges 1
ClientTransportPlugin obfs4 exec /usr/bin/obfs4proxy
<INSERT YOUR BRIDGES HERE>
```
3. Restart: `sudo systemctl restart tor`

### Use with Tor
```python
client = AsyncZlib(
    onion=True,
    proxy_list=['socks5://127.0.0.1:9050']
)
```

## Quick Verification
```python
import asyncio
from zlibrary import AsyncZlib

async def verify():
    client = AsyncZlib()
    try:
        await client.login(email, password)
        print("✅ Login successful")
        
        profile = await client.profile.get_limits()
        print(f"✅ Daily limit: {profile['daily_remaining']}/{profile['daily_allowed']}")
        
        await client.logout()
        print("✅ Setup verified")
    except Exception as e:
        print(f"❌ Error: {e}")

asyncio.run(verify())
```

## Common Issues

### Authentication Failed
- Verify credentials are correct
- Check if account is active on Z-Library website
- Ensure no special characters need escaping in password

### No Module Found
- Ensure correct Python path: `sys.path.insert(0, 'src')`
- Check installation: `pip list | grep zlibrary`

### Network Issues
- Check internet connection
- Verify proxy settings if using Tor
- Try clearnet if onion fails

### Rate Limiting
- Check daily limits: `await profile.get_limits()`
- Wait for limit reset (shown in hours)
- Consider premium account for higher limits