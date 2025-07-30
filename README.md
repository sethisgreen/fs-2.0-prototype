# FS 2.0 Prototype

This is a prototype for a genealogy research tool focused on integrating with FamilySearch and other providers. The system is designed with modular servers to handle API interactions, record routing, document processing, analysis, research management, and location services.

## Project Overview

The prototype aims to build an efficient, ethical genealogy research system using AI agents. It follows a split-server architecture for scalability and maintainability. Key features include secure API access, data standardization, privacy compliance, and incremental development.

## MCP Servers

### 1. FamilySearch API Server (`servers/familysearch-api/`)
Traditional API-based integration with FamilySearch's official API.

### 2. FamilySearch Web Search Server (`servers/familysearch-web-search/`) ⭐ **NEW**
**Web scraping-based MCP server** that can search FamilySearch's public website using custom user agents to bypass Imperva firewall protection.

#### Features:
- **Web Scraping**: Searches FamilySearch's public website for genealogical records
- **Custom User Agent**: Configurable user agent to bypass firewall restrictions
- **Rate Limiting**: Intelligent rate limiting to respect FamilySearch's servers
- **Caching**: Built-in caching to reduce redundant requests
- **Retry Logic**: Automatic retry with exponential backoff
- **Multiple Search Types**: Support for census, vital records, and general searches
- **Structured Logging**: Comprehensive logging for debugging and monitoring

#### Quick Start:
```bash
cd servers/familysearch-web-search
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your custom user agent
python3 server.py
```

#### Available Tools:
- `search_familysearch_records`: General search for any type of genealogical record
- `search_census_records`: Search specifically for census records
- `search_vital_records`: Search for vital records (birth, death, marriage)

### 3. Records Router Server (`servers/records-router/`)
Routes and standardizes records from multiple sources.

## Suggestions for Changes and Adjustments

Before proceeding with development, incorporate the following refinements:

1. **Adopt GEDCOM X as a Standard Data Format**: Standardize outputs to GEDCOM X for interoperability.
2. **Enhance Privacy and Compliance Features**: Add consent mechanisms, anonymization, and compliance with data regs.
3. **Refine Authentication Strategy**: Use OAuth Code Flow with a centralized auth module.
4. **Incorporate AI-Specific Best Practices**: Include human-in-the-loop validation, aggressive caching, and fallbacks.
5. **Start with a Minimal Prototype Scope**: Begin with FamilySearch API Server and Records Router, 5-7 core tools.
6. **Add Non-Functional Priorities**: Security (env vars, sanitization), Testing (80%+ coverage with pytest), Deployment (Docker Compose), Monitoring (elg).
7 Cannibalize reusability, add `merge_results` in Records Router.

These adjustments will enhance resilience and alignment with best practices.

## Product Requirements Documents (PRDs)

Detailed PRDs for each server are available in the `docs` directory:

- [Suggestions for Changes](./docs/suggestions.md)
- [PRD 1: FamilySearch API Server](./docs/prd1-familysearch-api-server.md)
- [PRD 2: Records Router Server](./docs/prd2-records-router-server.md)
- [PRD 3: Document Processing Server](./docs/prd3-document-processing-server.md)
- [PRD 4: Analysis Server](./docs/prd4-analysis-server.md)
- [PRD 5: Research Management Server](./docs/prd5-research-management-server.md)
- [PRD 6: Location Server](./docs/prd6-location-server.md)

## Next Steps

Following the minimal prototype scope, we will start by implementing the FamilySearch API Server and Records Router in Python, ensuring alignment with the PRDs and suggestions.

## Development Guidelines

- Use Python for backend servers.
- Follow best practices for async handling, security, and testing as outlined.
- For any frontend/mobile components, adhere to React Native and Expo guidelines (though backend-focused initially).

## Testing

### FamilySearch Web Search Server
```bash
cd servers/familysearch-web-search
source venv/bin/activate
python3 simple_test.py  # Quick functionality test
python3 test_server.py  # Comprehensive test suite
```

## Security Considerations

- **User Agent Configuration**: The web search server uses configurable user agents to bypass firewall restrictions
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
