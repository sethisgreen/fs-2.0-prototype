# FamilySearch Web Search MCP Server - Implementation Summary

## What Was Built

A complete MCP (Model Context Protocol) server that enables AI agents to search FamilySearch's public website using web scraping techniques. This server is designed to work with custom user agents to bypass Imperva firewall protection.

## Key Components

### 1. Core Server (`server.py`)
- **FastMCP Server**: Uses the modern MCP library for server implementation
- **Three Search Tools**:
  - `search_familysearch_records`: General search for any genealogical record
  - `search_census_records`: Census-specific searches
  - `search_vital_records`: Vital records (birth, death, marriage) searches
- **Async Functions**: All search functions are async for better performance

### 2. Web Scraping Engine (`FamilySearchWebSearcher`)
- **Custom User Agent**: Configurable to bypass Imperva firewall
- **HTML Parsing**: Uses BeautifulSoup to extract structured data from search results
- **Data Extraction**: Extracts titles, URLs, record types, dates, locations, and descriptions
- **Error Handling**: Graceful handling of network errors and parsing issues

### 3. Rate Limiting (`rate_limiter.py`)
- **Intelligent Rate Limiting**: Respects FamilySearch's rate limits
- **Minute/Hour Limits**: Configurable requests per minute and hour
- **Minimum Delays**: Ensures minimum delay between requests
- **Retry Logic**: Exponential backoff for failed requests

### 4. Configuration System (`config.py`)
- **Environment Variables**: All settings configurable via environment variables
- **Pydantic Settings**: Type-safe configuration management
- **Flexible Configuration**: Easy to adjust for different environments

### 5. Testing Suite
- **Simple Test** (`simple_test.py`): Quick functionality verification
- **Comprehensive Test** (`test_server.py`): Full test suite with multiple scenarios
- **Rate Limiting Test**: Verifies rate limiting behavior

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │───▶│  FastMCP Server  │───▶│  Search Tools   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Rate Limiter     │    │ HTML Parser     │
                       └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ HTTP Client      │───▶│ FamilySearch    │
                       │ (Custom UA)      │    │ Website         │
                       └──────────────────┘    └─────────────────┘
```

## Data Flow

1. **MCP Tool Call**: Client calls one of the three search tools
2. **Rate Limiting**: Rate limiter checks if request is allowed
3. **HTTP Request**: Custom user agent makes request to FamilySearch
4. **HTML Parsing**: BeautifulSoup parses the response
5. **Data Extraction**: Structured data extracted from HTML
6. **Caching**: Results cached for future requests
7. **Response**: Structured results returned to MCP client

## Configuration

### Environment Variables
```bash
# Custom user agent to bypass Imperva firewall
FAMILYSEARCH_WEB_CUSTOM_USER_AGENT="your-custom-user-agent-here"

# Rate limiting settings
FAMILYSEARCH_WEB_REQUESTS_PER_MINUTE=30
FAMILYSEARCH_WEB_REQUESTS_PER_HOUR=1000

# Server settings
FAMILYSEARCH_WEB_SERVER_PORT=8002
```

### Key Settings
- **Rate Limiting**: 30 requests/minute, 1000 requests/hour (default)
- **Caching**: 1 hour TTL for search results
- **Timeouts**: 30 seconds for requests, 10 seconds for connections
- **Retry Logic**: 3 attempts with exponential backoff

## Usage Examples

### Basic Search
```python
results = await search_familysearch_records(
    given_name="John",
    surname="Smith",
    year=1850,
    max_results=10
)
```

### Census Search
```python
results = await search_census_records(
    given_name="Mary",
    surname="Johnson",
    year=1860,
    location="New York",
    max_results=5
)
```

### Vital Records Search
```python
results = await search_vital_records(
    given_name="William",
    surname="Brown",
    record_type="birth",
    year=1880,
    max_results=5
)
```

## Security Features

1. **Custom User Agent**: Bypasses Imperva firewall restrictions
2. **Rate Limiting**: Prevents overwhelming FamilySearch servers
3. **Error Handling**: Graceful handling of network issues
4. **Logging**: Comprehensive logging for monitoring
5. **Caching**: Reduces redundant requests

## Testing

### Quick Test
```bash
python3 simple_test.py
```

### Full Test Suite
```bash
python3 test_server.py
```

### Manual Testing
```bash
# Start server
python3 server.py

# In another terminal, test with curl
curl -X POST http://localhost:8000/tools/search_familysearch_records/call \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"given_name": "John", "surname": "Smith", "year": 1850}}'
```

## Deployment

### Local Development
```bash
cd servers/familysearch-web-search
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
python3 server.py
```

### Production Considerations
1. **Environment Variables**: Set all configuration via environment variables
2. **Logging**: Configure structured logging for production
3. **Monitoring**: Add health checks and metrics
4. **Security**: Use HTTPS and proper authentication
5. **Scaling**: Consider load balancing for multiple instances

## Troubleshooting

### Common Issues
1. **Connection Timeouts**: Increase `request_timeout` in configuration
2. **Rate Limiting**: Reduce `requests_per_minute` if getting blocked
3. **Parsing Errors**: Check if FamilySearch has changed their HTML structure
4. **User Agent Issues**: Update the custom user agent if requests are being blocked

### Debug Mode
```python
import structlog
structlog.configure(log_level="DEBUG")
```

## Future Enhancements

1. **More Record Types**: Add support for immigration, military, and other record types
2. **Advanced Search**: Add fuzzy matching and name variations
3. **Batch Processing**: Support for bulk searches
4. **Data Export**: Export results in various formats (GEDCOM, CSV, etc.)
5. **Integration**: Connect with other genealogy services
6. **AI Enhancement**: Add AI-powered record analysis and suggestions

## Dependencies

- **mcp**: Modern MCP library for server implementation
- **httpx**: Async HTTP client for web requests
- **beautifulsoup4**: HTML parsing and data extraction
- **pydantic**: Data validation and settings management
- **structlog**: Structured logging
- **async-lru**: Async caching utilities

## License

This project is part of the FS 2.0 Prototype and follows the same licensing terms.