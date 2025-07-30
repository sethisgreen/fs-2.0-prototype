# FamilySearch Web Search MCP Server

An MCP (Model Context Protocol) server that enables AI agents to search FamilySearch's public website using web scraping techniques. This server is designed to work with custom user agents to bypass Imperva firewall protection.

## Features

- **Web Scraping**: Searves FamilySearch's public website for genealogical records
- **Custom User Agent**: Configurable user agent to bypass firewall restrictions
- **Rate Limiting**: Intelligent rate limiting to respect FamilySearch's servers
- **Caching**: Built-in caching to reduce redundant requests
- **Retry Logic**: Automatic retry with exponential backoff
- **Multiple Search Types**: Support for census, vital records, and general searches
- **Structured Logging**: Comprehensive logging for debugging and monitoring

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (create a `.env` file):
```bash
# Custom user agent to bypass Imperva firewall
FAMILYSEARCH_WEB_CUSTOM_USER_AGENT="your-custom-user-agent-here"

# Rate limiting settings
FAMILYSEARCH_WEB_REQUESTS_PER_MINUTE=30
FAMILYSEARCH_WEB_REQUESTS_PER_HOUR=1000

# Server settings
FAMILYSEARCH_WEB_SERVER_PORT=8002
```

## Usage

### Starting the Server

```bash
python server.py
```

The server will start on `http://localhost:8002/mcp`

### Available Tools

#### 1. `search_familysearch_records`
General search for any type of genealogical record.

**Parameters:**
- `given_name` (optional): First/given name
- `surname` (optional): Last name/surname
- `year` (optional): Year to search around
- `location` (optional): Location to search in
- `record_type` (optional): Type of record (census, birth, death, marriage, etc.)
- `max_results` (optional): Maximum number of results (1-100, default: 20)

#### 2. `search_census_records`
Search specifically for census records.

**Parameters:**
- `given_name`: First/given name
- `surname`: Last name/surname
- `year`: Census year
- `location` (optional): Location to search in
- `max_results` (optional): Maximum number of results

#### 3. `search_vital_records`
Search for vital records (birth, death, marriage).

**Parameters:**
- `given_name`: First/given name
- `sme`: Last name/surname
- `record_type`: Type of vital record (birth, death, marriage)
- `year` (optional): Year to search around
- `location` (optional): Location to search in
- `max_results` (optional): Maximum number of results

### Example Usage

```python
# Search for John Smith in 1850 census
results = await search_census_records(
    given_name="John",
    surname="Smith",
    year=1850,
    location="New York",
    max_results=10
)

# Search for birth records
results = await search_vital_records(
    given_name="Mary",
    surname="Johnson",
    record_type="birth",
    year=1880,
    max_results=5
)
```

## Configuration

The server uses a configuration system with the following settings:

### Rate Limiting
- `requests_per_minute`: Maximum requests per minute (default: 30)
- `requests_per_hour`: Maximum requests per hour (default: 1000)
- `delay_between_requests`: Minimum delay between requests in seconds (default: 2.0)

### Caching
- `cache_hawk`: Cache time-to-live in seconds (default: 3600)
- `max_cache_size`: Maximum number of cached items (default: 1000)

### Timeouts
- `request_timeout`: HTTP request timeout in seconds (default: 30.0)
- `connection_timeout`: Connection timeout in seconds (default: 10.0)

### Retry Logic
- `max_retries`: Maximum number of retry attempts (default: 3)
- `retry_delay`: Base delay between retries in seconds (default: 1.0)
- `retry_backoff`: Exponential backoff multiplier (default: 2.0)

## Testing

Run the test suite to verify functionality:

```bash
python test_server.py
```

This will test:
- Basic search functionality
- Census-specific searches
- Vital records searches
- Rate limiting behavior

## Architecture

### Components

1. **FamilySearchWebSearcher**: Main scraping class that handles HTTP requests and HTML parsing
2. **RateLimiter**: Manages request rate limiting to respect server limits
3. **RetryHandler**: Handles automatic retries with exponential backoff
4. **Configuration**: Centralized settings management

### Data Flow

1. MCP tool receives search request
2. Rate limiter checks if request is allowed
3. HTTP request made to FamilySearch with custom user agent
4. HTML response parsed using BeautifulSoup
5. Results extracted and structured
6. Results cached for future requests
7. Structured results returned to MCP client

## Security Considerations

- **User Agent**: Uses configurable user agent to bypass firewall restrictions
- **Rate Limiting**: Respects FamilySearch's rate limits to avoid being blocked
- **Error Handling**: Graceful handling of network errors and timeouts
- **Logging**: Comprehensive logging for monitoring and debugging

## Troubleshooting

### Common Issues

1. **Connection Timeouts**: Increase `request_timeout` in configuration
2. **Rate Limiting**: Reduce `requests_per_minute` if getting blocked
3. **Parsing Errors**: Check if FamilySearch has changed their HTML structure
4. **User Agent Issues**: Update the custom user agent if requests are being blocked

### Debugging

Enable debug logging by setting the log level:

```python
import structlog
structlog.configure(log_level="DEBUG")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.