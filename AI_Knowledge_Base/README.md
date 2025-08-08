# Z-Library API Module - AI Knowledge Base
---
version: 1.0.0
type: project_knowledge_repository
project: zlibrary_api_module
ai_instructions: |
  This knowledge base contains project-specific Deep Research archives, Memory Cards, and Technical Guides for the Z-Library API Module.
  Use semantic search for concept exploration.
  Each file has a unique ID for precise lookups.
  Start with Memory Cards for quick reference, then dive into Deep Research for comprehensive understanding.
---

## Structure

- `/deep_research/` - Deep research archives and comprehensive analysis
- `/memory_cards/` - Memory cards with knowledge units
- `/manifests/` - Metadata and configurations
- `/docs/` - Documentation and instructions

## Key Knowledge Areas

### 📚 Z-Library API Module Overview
**Memory Card**: `mc_project_zlibrary_overview_20250806.md`
**Deep Research**: `dr_zlibrary_api_architecture_20250806.md`

**Project Status:**
- ✅ Async Python library for Z-Library access
- ✅ Support for clearnet and Tor domains
- ✅ Cookie-based authentication
- ✅ Comprehensive search and download capabilities
- ⚠️ Authentication credentials required for testing

**Core Technologies:**
- Python 3.12 with async/await
- aiohttp for HTTP requests
- BeautifulSoup4 for HTML parsing
- Proxy chain support (HTTP, SOCKS4, SOCKS5)
- Semaphore-based concurrency control (64 concurrent requests)

### 🔧 Technical Components
- **AsyncZlib**: Main client class for authentication and API interactions
- **SearchPaginator**: Handles paginated search results with caching
- **BookItem**: Individual book representation with fetch capabilities
- **ZlibProfile**: User profile and download limit management
- **Booklists**: Public and private booklist search functionality

## AI Navigation

1. **Quick Start**: Check `mc_project_setup_instructions_20250806.md` for setup guide
2. **API Reference**: See `mc_technical_api_reference_20250806.md` for detailed API docs
3. **Testing Guide**: Reference `mc_project_testing_procedures_20250806.md` for test procedures
4. **Deep Research**: Look in `/deep_research/` for architectural analysis
5. **Memory Cards**: Check `/memory_cards/` for quick reference guides

## Project Capabilities

### Search Features
- Standard book search with filters
- Full-text search within book contents
- Language filtering (200+ languages)
- Format filtering (PDF, EPUB, MOBI, etc.)
- Year range filtering
- Pagination with caching

### Download Management
- Individual book downloads
- Download history tracking
- Daily limit monitoring
- Metadata extraction
- Cover image URLs

### Advanced Features
- Dual domain support (clearnet/Tor)
- Proxy chain configuration
- Session management
- Error handling with custom exceptions
- Structured logging

## Known Issues & Limitations

- **Authentication Required**: All operations require valid Z-Library credentials
- **Rate Limiting**: Daily download limits apply
- **Network Dependencies**: Requires stable internet connection
- **Domain Availability**: Domains may change due to Z-Library's nature

## Last Updated
2025-08-06