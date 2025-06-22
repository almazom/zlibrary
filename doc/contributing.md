# Contributing Guide

Thank you for your interest in contributing to the Z-Library Python API! This guide will help you get started with contributing to the project.

## Getting Started

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/zlibrary.git
   cd zlibrary
   ```

2. **Development Environment**
   
   **Using devenv (Recommended):**
   ```bash
   # Install devenv if not already installed
   # See: https://devenv.sh/getting-started/
   
   devenv shell
   ```
   
   **Manual Setup:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
   
   pip install -e .
   pip install build twine pytest
   ```

3. **Set Up Test Credentials**
   ```bash
   export ZLOGIN="your-test-email@example.com"
   export ZPASSW="your-test-password"
   ```

### Running Tests

```bash
# With devenv
devenv shell -c test

# Manual
python src/test.py
```

### Building

```bash
# With devenv
devenv shell -c build

# Manual
rm -rf dist/
python -m build
```

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Keep functions focused and single-purpose
- Add docstrings to all public functions and classes

**Example:**
```python
async def search_books(
    query: str,
    filters: Optional[Dict[str, Any]] = None
) -> List[BookItem]:
    """Search for books with optional filters.
    
    Args:
        query: Search query string
        filters: Optional search filters
        
    Returns:
        List of BookItem objects
        
    Raises:
        EmptyQueryError: If query is empty
        ParseError: If response cannot be parsed
    """
    if not query.strip():
        raise EmptyQueryError("Query cannot be empty")
    
    # Implementation here
```

### Error Handling

- Use specific exception types from `exception.py`
- Include helpful error messages
- Log errors appropriately using the logger module

**Example:**
```python
from .exception import ParseError
from .logger import logger

try:
    result = parse_html(response)
except Exception as e:
    logger.error(f"Failed to parse HTML: {e}")
    raise ParseError(f"Could not parse response: {e}")
```

### Async/Await Patterns

- All I/O operations should be async
- Use proper exception handling in async functions
- Implement rate limiting where appropriate

**Example:**
```python
async def fetch_with_retry(url: str, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            return await GET_request(url)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"Request failed, retrying: {e}")
            await asyncio.sleep(2 ** attempt)
```

## Contributing Areas

### High Priority

1. **Error Handling Improvements**
   - More specific exception types
   - Better error messages
   - Graceful degradation strategies

2. **HTML Parsing Robustness**
   - Handle HTML structure changes
   - Improve selector reliability
   - Add fallback parsing methods

3. **Performance Optimization**
   - Request caching
   - Connection pooling improvements
   - Memory usage optimization

4. **Testing Infrastructure**
   - Unit tests with mocked responses
   - Integration test improvements
   - Continuous integration setup

### Medium Priority

1. **Feature Enhancements**
   - Additional search filters
   - Bulk operations
   - Export functionality

2. **Documentation**
   - API reference improvements
   - More usage examples
   - Video tutorials

3. **Platform Support**
   - Windows compatibility testing
   - macOS specific features
   - Mobile platform considerations

### Low Priority

1. **Convenience Features**
   - CLI interface
   - GUI wrapper
   - Browser extensions integration

## Code Organization

### Project Structure

```
src/zlibrary/
├── __init__.py          # Public API exports
├── libasync.py          # Main AsyncZlib class
├── abs.py               # Abstract classes and paginators
├── profile.py           # User profile management
├── booklists.py         # Booklist functionality
├── util.py              # HTTP utility functions
├── const.py             # Constants and enums
├── exception.py         # Custom exceptions
└── logger.py            # Logging configuration
```

### Adding New Features

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature-name
   ```

2. **Implement Feature**
   - Add to appropriate module
   - Follow existing patterns
   - Include error handling

3. **Add Tests**
   - Unit tests for new functions
   - Integration tests if needed
   - Update existing tests if modified

4. **Update Documentation**
   - Docstrings for new functions
   - README updates if needed
   - Example usage in `/examples`

### HTML Parsing Guidelines

When working with HTML parsing:

1. **Use BeautifulSoup Consistently**
   ```python
   from bs4 import BeautifulSoup as bsoup
   from bs4 import Tag
   
   soup = bsoup(html, features="lxml")
   ```

2. **Robust Element Selection**
   ```python
   # Good: Check for element existence and type
   element = soup.find("div", {"class": "book-info"})
   if element and isinstance(element, Tag):
       title = element.get_text().strip()
   else:
       raise ParseError("Could not find book info")
   
   # Bad: Assume element exists
   title = soup.find("div", {"class": "book-info"}).get_text()
   ```

3. **Handle Missing Data Gracefully**
   ```python
   def extract_book_year(soup) -> Optional[str]:
       year_element = soup.find("span", {"class": "year"})
       if year_element:
           year_text = year_element.get_text().strip()
           if year_text.isdigit():
               return year_text
       return None
   ```

## Pull Request Process

### Before Submitting

1. **Test Your Changes**
   ```bash
   # Run existing tests
   python src/test.py
   
   # Test with different scenarios
   python examples/python/basic_usage.py
   ```

2. **Update Documentation**
   - Add/update docstrings
   - Update README if needed
   - Add examples for new features

3. **Check Code Style**
   ```bash
   # Use black for formatting (if available)
   black src/zlibrary/
   
   # Check with flake8 (if available)
   flake8 src/zlibrary/
   ```

### Submitting PR

1. **Create Descriptive Title**
   - "Add support for advanced search filters"
   - "Fix parsing error for book authors"
   - "Improve error handling in login process"

2. **Write Clear Description**
   ```markdown
   ## Changes
   - Added support for date range filtering in search
   - Updated SearchPaginator to handle new parameters
   - Added tests for date filtering functionality
   
   ## Testing
   - Tested with various date ranges
   - Verified backward compatibility
   - Updated existing tests
   
   ## Breaking Changes
   None
   
   ## Related Issues
   Fixes #123
   ```

3. **Include Test Results**
   - Show test output
   - Include example usage
   - Demonstrate the fix/feature

### Review Process

1. **Automated Checks**
   - Code builds successfully
   - Tests pass
   - No obvious security issues

2. **Manual Review**
   - Code quality and style
   - Architecture alignment
   - Documentation completeness

3. **Testing**
   - Reviewer tests the changes
   - Edge cases considered
   - Performance impact assessed

## Bug Reports

### Good Bug Report Template

```markdown
## Bug Description
Brief description of the issue

## Environment
- Python version: 3.x.x
- zlibrary version: x.x.x
- Operating system: Linux/macOS/Windows
- Network setup: Direct/Proxy/Tor

## Steps to Reproduce
1. Initialize client with...
2. Call search with...
3. Error occurs when...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Error Messages
```
Full error traceback here
```

## Additional Context
- Logs with DEBUG level enabled
- Network conditions
- Account type (free/premium)
```

### Security Issues

For security-related issues:

1. **Do NOT open public issues**
2. **Contact maintainers directly**
3. **Provide minimal reproduction case**
4. **Do not include credentials or personal data**

## Documentation Contributions

### Types of Documentation

1. **API Reference** (`/doc/api-reference.md`)
   - Function signatures
   - Parameter descriptions
   - Return value specifications
   - Exception details

2. **Guides** (`/doc/*.md`)
   - Step-by-step tutorials
   - Best practices
   - Common use cases

3. **Examples** (`/examples/`)
   - Working code samples
   - Real-world scenarios
   - Different complexity levels

### Documentation Style

1. **Clear and Concise**
   - Use simple language
   - Provide complete examples
   - Include expected outputs

2. **Structured Format**
   - Use consistent headers
   - Include code blocks with syntax highlighting
   - Add cross-references

3. **Keep Updated**
   - Update with code changes
   - Verify examples still work
   - Remove outdated information

## Community Guidelines

### Communication

- Be respectful and constructive
- Help newcomers learn the codebase
- Share knowledge and best practices
- Ask questions when unsure

### Code of Conduct

- Focus on technical merits
- Accept feedback gracefully
- Provide helpful reviews
- Maintain professional behavior

## Release Process

### Version Numbering

Following Semantic Versioning (SemVer):
- `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

### Release Checklist

1. **Update Version Numbers**
   - `setup.cfg`
   - `pyproject.toml`
   - `__init__.py` (if applicable)

2. **Update Changelog**
   - Document all changes
   - Credit contributors
   - Note breaking changes

3. **Test Release**
   - Full test suite passes
   - Examples work correctly
   - Documentation builds

4. **Create Release**
   - Tag version in git
   - Build distribution packages
   - Upload to PyPI

## Getting Help

### For Contributors

- Join development discussions in issues
- Ask questions about architecture decisions
- Request guidance on implementation approaches
- Seek feedback on proposed changes

### For Users

- Check existing documentation first
- Search closed issues for solutions
- Provide complete information when asking questions
- Share solutions that work for you

## Recognition

Contributors are recognized through:
- Git commit history
- Release notes acknowledgments
- README contributor section
- Project maintainer considerations

Thank you for contributing to the Z-Library Python API! Your efforts help make this tool better for everyone.