# Book Discovery Engine v1.0.0

Atomic engine that discovers random book URLs from Russian bookstore category pages using Claude AI integration.

## 🎯 Purpose

The Book Discovery Engine is a self-contained, reusable component designed to:
- Discover fresh book URLs from Russian bookstore category pages
- Provide random book selection for testing and validation
- Support multiple bookstores with configurable categories  
- Return structured JSON output for pipeline integration

## 🚀 Quick Start

```bash
# Basic usage - discover 5 books from eksmo.ru
./engine.sh --store eksmo.ru

# Discover from specific category and page
./engine.sh --store alpinabook.ru --category business --page 3 --count 3

# Verbose mode with custom timeout
./engine.sh --store eksmo.ru --category fiction --verbose --timeout 90
```

## 📋 API Reference

### Required Arguments
- `--store <store>` - Target bookstore (eksmo.ru, alpinabook.ru)

### Optional Arguments
- `--category <category>` - Book category (default: books)
- `--page <number>` - Page number (default: random)
- `--count <number>` - Books to discover (default: 5)
- `--output-format <format>` - Output format: json (default: json)
- `--timeout <seconds>` - Request timeout (default: 60)
- `--config <file>` - Custom config file
- `--verbose` - Enable detailed logging
- `--help` - Show help information

### Output Format

**Success Response:**
```json
{
  "status": "success",
  "engine": {
    "name": "book_discovery",
    "version": "1.0.0"
  },
  "request": {
    "store": "eksmo.ru",
    "category": "fiction",
    "page": 2,
    "requested_count": 5
  },
  "result": {
    "discovered_count": 4,
    "books": [
      {
        "title": "Капля духов в открытую рану",
        "url": "https://eksmo.ru/book/kaplya-dukhov-v-otkrytuyu-ranu-ITD1403451/"
      },
      {
        "title": "Большая книга мифов России", 
        "url": "https://eksmo.ru/book/bolshaya-kniga-mifov-rossii-ITD1419653/"
      }
    ]
  },
  "timestamp": "2025-08-13T16:45:17.123Z"
}
```

**Error Response:**
```json
{
  "status": "error",
  "engine": {
    "name": "book_discovery",
    "version": "1.0.0"
  },
  "error": {
    "code": "network_error",
    "message": "Failed to discover books from eksmo.ru"
  },
  "timestamp": "2025-08-13T16:45:17.123Z"
}
```

### Exit Codes
- `0` - Success, books discovered
- `1` - No books found on specified page/category
- `2` - Invalid arguments provided  
- `3` - Network error or timeout
- `4` - Store not supported or disabled
- `5` - Parsing error in response

## 🏪 Supported Stores

### eksmo.ru
- **Type**: Commercial bookstore
- **Categories**: books, fiction, non-fiction, novelties, bestsellers
- **Max Pages**: 50
- **Status**: ✅ Fully supported

### alpinabook.ru  
- **Type**: Academic/business bookstore
- **Categories**: business, psychology, science, education
- **Max Pages**: 20  
- **Status**: ✅ Fully supported

### labirint.ru
- **Type**: Commercial bookstore
- **Categories**: books, fiction, children, education
- **Status**: ⚠️ Disabled (anti-bot protection)

## ⚙️ Configuration

The engine uses `config/defaults.yaml` for configuration. Key settings:

```yaml
stores:
  eksmo.ru:
    enabled: true
    base_url: "https://eksmo.ru"
    categories:
      fiction: "/catalog/fiction/"
      books: "/catalog/books/"
    pagination:
      max_pages: 50
    rate_limiting:
      delay_ms: 2000
```

### Custom Configuration
```bash
# Use custom config file
./engine.sh --store eksmo.ru --config /path/to/custom.yaml
```

## 🔧 Dependencies

### System Requirements
- **bash** >= 4.0
- **curl** (for HTTP requests)
- **jq** (for JSON processing)
- **claude** (Claude AI CLI)

### Optional Dependencies
- **yq** (enhanced YAML parsing)
- **timeout** (command timeout handling)

### Installation Check
```bash
# Verify dependencies
./engine.sh --store eksmo.ru --verbose
```

## 🧪 Testing

### Unit Tests
```bash
# Run engine unit tests
./tests/unit_tests.sh

# Run with specific store
./tests/unit_tests.sh --store eksmo.ru
```

### Integration Tests
```bash
# Test against live stores
./tests/integration_tests.sh

# Test with network timeout
./tests/integration_tests.sh --timeout-test
```

### Manual Testing
```bash
# Test basic functionality
./engine.sh --store eksmo.ru --count 2 --verbose

# Test error handling
./engine.sh --store invalid_store
```

## 🔍 Troubleshooting

### Common Issues

**1. No books found (Exit Code 1)**
```bash
# Try different page or category
./engine.sh --store eksmo.ru --page 1 --category bestsellers
```

**2. Network timeout (Exit Code 3)**
```bash  
# Increase timeout
./engine.sh --store eksmo.ru --timeout 120
```

**3. Claude AI unavailable**
```bash
# Check Claude installation
which claude
claude --help
```

**4. Store not supported (Exit Code 4)**
```bash
# Check available stores
grep -A 5 "stores:" config/defaults.yaml
```

### Debug Mode
```bash
# Enable verbose logging
./engine.sh --store eksmo.ru --verbose

# Check configuration
./engine.sh --help
```

## 🏗️ Architecture

### Design Principles
- **Atomic**: Single responsibility (book URL discovery)
- **Reusable**: Standard CLI interface for pipeline integration
- **Configurable**: YAML-based store and behavior configuration
- **Testable**: Comprehensive unit and integration tests
- **Observable**: Structured logging and error reporting

### Pipeline Integration
```bash
# Use in pipeline
./book_discovery/engine.sh --store eksmo.ru | \
  ./book_extraction/engine.sh --input stdin | \
  ./book_validation/engine.sh --input stdin
```

### Error Handling Strategy
- **Graceful degradation**: Continue on non-critical errors
- **Clear exit codes**: Specific codes for different failure types
- **Structured errors**: JSON error responses for parsing
- **Detailed logging**: Verbose mode for debugging

## 🔄 Development

### Adding New Stores
1. Update `config/defaults.yaml` with store configuration
2. Add store-specific category mappings
3. Update `manifest.json` supported stores list
4. Add unit tests for new store
5. Update documentation

### Extending Categories
1. Add category to store configuration in YAML
2. Test category URL patterns
3. Update manifest supported categories
4. Add integration tests

### Performance Optimization
- Configure appropriate timeouts per store
- Implement rate limiting to respect store policies
- Cache successful store/category combinations
- Optimize Claude prompt for faster responses

## 📊 Performance

- **Typical Response Time**: 15-30 seconds
- **Success Rate**: ~85% (varies by store)
- **Books Per Request**: 3-5 typical
- **Rate Limiting**: Built-in delays (1.5-3s between requests)

## 🔗 Integration Examples

See `examples/usage_examples.sh` for complete integration examples.

## 📚 API Documentation

See `docs/api.md` for detailed API specification.

## 🐛 Bug Reports

Report issues with:
- Engine version and configuration used
- Complete command line arguments
- Full error output (with --verbose)
- Store and category being tested

## 📈 Changelog

### v1.0.0 (2025-08-13)
- Initial release
- Support for eksmo.ru and alpinabook.ru  
- Claude AI integration
- Comprehensive error handling
- Full documentation and testing suite

---

**Author**: IUC Test Framework  
**License**: Project License  
**Documentation**: Complete API docs in `docs/`