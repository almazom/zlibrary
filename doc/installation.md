# Installation and Setup Guide

## Requirements

- Python 3.7 or higher
- Z-Library account (singlelogin account required)
- Internet connection
- Optional: Tor for onion domain access

## Installation

### Method 1: PyPI Installation

```bash
pip install zlibrary
```

### Method 2: Development Installation

```bash
# Clone the repository
git clone https://github.com/sertraline/zlibrary.git
cd zlibrary

# Using devenv (recommended for development)
devenv shell

# Or using pip
pip install -e .
```

### Method 3: Build from Source

```bash
# Clone and build
git clone https://github.com/sertraline/zlibrary.git
cd zlibrary

# Build package
python -m build
pip install dist/zlibrary*.whl
```

## Dependencies

The library requires these packages (automatically installed):

### Core Dependencies
- `aiohttp` (≥3.10.5) - Async HTTP client
- `aiohttp-socks` (≥0.9.0) - SOCKS proxy support
- `beautifulsoup4` (≥4.12.3) - HTML parsing
- `lxml` (≥5.3.0) - XML/HTML parser backend

### Performance Dependencies
- `aiodns` (≥3.2.0) - Fast DNS resolution
- `Brotli` (≥1.1.0) - Compression support
- `ujson` (≥5.10.0) - Fast JSON parsing
- `yarl` (≥1.11.1) - URL parsing

### Additional Dependencies
- `attrs` (≥24.2.0) - Class creation utilities
- `cffi` (≥1.17.1) - C Foreign Function Interface

## Basic Setup

### 1. Account Requirements

You need a Z-Library singlelogin account:

1. Visit [z-library.sk](https://z-library.sk)
2. Create or use existing account
3. Ensure you have singlelogin access

### 2. Environment Variables (Recommended)

```bash
# Set credentials as environment variables
export ZLOGIN="your-email@example.com"
export ZPASSW="your-password"
```

### 3. Basic Usage Test

```python
import asyncio
import zlibrary

async def test_connection():
    lib = zlibrary.AsyncZlib()
    await lib.login("your-email", "your-password")
    
    # Test search
    results = await lib.search("python programming", count=5)
    books = await results.next()
    
    print(f"Found {len(books)} books")
    print(f"First book: {books[0].name}")

# Run test
asyncio.run(test_connection())
```

## Advanced Setup

### Tor/Onion Configuration

For enhanced privacy using Tor onion domains:

#### 1. Install Tor

**Ubuntu/Debian:**
```bash
sudo apt install tor obfs4proxy
sudo systemctl enable --now tor
```

**Arch Linux:**
```bash
sudo pacman -S tor obfs4proxy
sudo systemctl enable --now tor
```

**macOS:**
```bash
brew install tor
brew services start tor
```

#### 2. Configure Tor (if blocked)

Edit `/etc/tor/torrc` to add bridges:

```
UseBridges 1
ClientTransportPlugin obfs4 exec /usr/bin/obfs4proxy

# Add bridges (get from bridges@torproject.org)
Bridge obfs4 [bridge-address]
```

Restart Tor:
```bash
sudo systemctl restart tor
```

#### 3. Use with Z-Library

```python
import zlibrary

lib = zlibrary.AsyncZlib(
    onion=True,
    proxy_list=['socks5://127.0.0.1:9050']
)
```

### Proxy Configuration

#### Single Proxy
```python
lib = zlibrary.AsyncZlib(
    proxy_list=['http://proxy.example.com:8080']
)
```

#### Proxy Chain
```python
lib = zlibrary.AsyncZlib(
    proxy_list=[
        'http://first-proxy.com:8080',
        'socks5://second-proxy.com:1080',
        'socks4://third-proxy.com:9050'
    ]
)
```

#### Authenticated Proxy
```python
lib = zlibrary.AsyncZlib(
    proxy_list=['http://user:pass@proxy.example.com:8080']
)
```

## Development Setup

### Using devenv (Recommended)

```bash
# Install devenv if not already installed
# See: https://devenv.sh/getting-started/

# Clone repository
git clone https://github.com/sertraline/zlibrary.git
cd zlibrary

# Enter development environment
devenv shell

# This automatically:
# - Sets up Python 3.12
# - Installs dependencies with uv
# - Provides build and test scripts
```

### Manual Development Setup

```bash
# Clone repository
git clone https://github.com/sertraline/zlibrary.git
cd zlibrary

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install in development mode
pip install -e .

# Install development dependencies
pip install build twine pytest
```

### Running Tests

```bash
# With devenv
devenv shell -c test

# Manual
python src/test.py

# Set credentials for testing
export ZLOGIN="your-test-email"
export ZPASSW="your-test-password"
```

### Building Package

```bash
# With devenv
devenv shell -c build

# Manual
rm -rf dist/
python -m build
```

## Troubleshooting

### Common Issues

#### 1. Login Failed
- Verify credentials are correct
- Check if account has singlelogin access
- Try different domain (clearnet vs onion)

#### 2. Connection Timeout
- Check internet connection
- Verify proxy configuration
- Try without proxy first

#### 3. Parse Errors
- Z-Library may have changed their HTML structure
- Check for library updates
- Enable debug logging to see raw responses

#### 4. Proxy Issues
- Verify proxy is running and accessible
- Test proxy with other tools
- Check proxy authentication if required

### Debug Logging

Enable comprehensive logging:

```python
import logging

# Enable zlibrary debug logging
logger = logging.getLogger("zlibrary")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# Enable aiohttp debug logging
logging.getLogger("aiohttp").setLevel(logging.DEBUG)
```

### Performance Tuning

#### Adjust Concurrency
```python
# Reduce concurrent requests for slow connections
lib = zlibrary.AsyncZlib(semaphore=True)
# The semaphore is set to 64 by default, modify in source if needed
```

#### Custom Timeouts
```python
# Modify request timeouts in util.py
# Default timeout is typically 30 seconds
```

## Configuration Files

### Environment File (.env)

```bash
# Create .env file in your project
ZLOGIN=your-email@example.com
ZPASSW=your-secure-password
PROXY_URL=socks5://127.0.0.1:9050
```

Load in Python:
```python
import os
from dotenv import load_dotenv

load_dotenv()

lib = zlibrary.AsyncZlib()
await lib.login(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
```

### Configuration Class Example

```python
import os
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ZLibConfig:
    email: str = os.getenv('ZLOGIN', '')
    password: str = os.getenv('ZPASSW', '')
    use_onion: bool = False
    proxies: Optional[List[str]] = None
    debug: bool = False
    
    def create_client(self):
        return zlibrary.AsyncZlib(
            onion=self.use_onion,
            proxy_list=self.proxies
        )
```

## Security Best Practices

1. **Never hardcode credentials** in source code
2. **Use environment variables** or secure credential storage
3. **Consider using Tor** for enhanced privacy
4. **Rotate credentials regularly**
5. **Monitor account usage** to avoid limits
6. **Use HTTPS proxies** when possible
7. **Keep the library updated** for security patches