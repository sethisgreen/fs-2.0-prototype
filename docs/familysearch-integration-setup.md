# FamilySearch API Integration Setup Guide

## Overview

This guide walks you through setting up the FamilySearch API integration for the FS 2.0 Prototype using your beta API credentials.

## Prerequisites

- FamilySearch Developer Account with beta API access
- Beta API Client ID and Secret
- Python 3.10+ environment

## Step 1: Environment Setup

### 1.1 Create Environment File

Copy the template and add your credentials:

```bash
cp env.template .env
```

### 1.2 Add Your Beta API Credentials

Edit `.env` and replace the placeholder values:

```bash
# FamilySearch OAuth Credentials (Beta API)
FAMILYSEARCH_CLIENT_ID=your_actual_beta_client_id
FAMILYSEARCH_CLIENT_SECRET=your_actual_beta_client_secret
FAMILYSEARCH_REDIRECT_URI=http://localhost:8001/oauth/callback

# FamilySearch API Configuration
FAMILYSEARCH_API_BASE_URL=https://api.familysearch.org/platform
FAMILYSEARCH_AUTH_BASE_URL=https://ident.familysearch.org/cis-web/oauth2/v3

# Development Settings
DEBUG=true
LOG_LEVEL=INFO
```

## Step 2: Install Dependencies

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Update FamilySearch Server Implementation

The current `servers/familysearch-api/server.py` contains mock implementations. You'll need to replace the TODO sections with real API calls.

### 3.1 Key Areas to Update

1. **OAuth Token Exchange** (line 47):

```python
# Replace mock token exchange with real implementation
async def exchange_code_for_token(code: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{os.getenv('FAMILYSEARCH_AUTH_BASE_URL')}/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": os.getenv("FAMILYSEARCH_CLIENT_ID"),
                "client_secret": os.getenv("FAMILYSEARCH_CLIENT_SECRET"),
                "redirect_uri": os.getenv("FAMILYSEARCH_REDIRECT_URI")
            }
        )
        response.raise_for_status()
        return response.json()
```

2. **Records Search** (line 86):

```python
# Replace mock search with real API call
async def search_census_records_real(given_name: str, surname: str, year: int,
                                   place: Optional[str] = None, max_results: int = 20,
                                   access_token: str) -> List[Dict]:
    async with httpx.AsyncClient() as client:
        # Create GEDCOM X compliant search request
        search_request = create_gedcomx_search_request(
            given_name=given_name,
            surname=surname,
            year=year,
            place=place,
            max_results=max_results
        )

        response = await client.post(
            f"{os.getenv('FAMILYSEARCH_API_BASE_URL')}/records/search",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/x-gedcomx-v1+json"
            },
            json=search_request
        )
        response.raise_for_status()

        # Convert to GEDCOM X format
        fs_response = response.json()
        gedcomx_records = convert_familysearch_to_gedcomx(fs_response)

        # Convert to standard format
        return [convert_gedcomx_to_standard_record(record) for record in gedcomx_records]
```

## Step 4: Test the Integration

### 4.1 Start the FamilySearch Server

```bash
cd servers/familysearch-api
python server.py
```

### 4.2 Test OAuth Flow

1. Visit: `http://localhost:8001/oauth/callback`
2. You should see the OAuth callback endpoint working

### 4.3 Test API Calls

Use the MCP tools to test:

```python
# Test authentication
result = await authenticate_user(client_id="your_client_id")

# Test search (with valid access token)
result = await search_census_records(
    given_name="John",
    surname="Smith",
    year=1850,
    place="New York",
    access_token="your_access_token"
)
```

## Step 5: Rate Limiting and Caching

### 5.1 Implement Rate Limiting

The beta API allows 5000 requests per hour. Add rate limiting:

```python
from asyncio import Semaphore
import time

# Rate limiting
MAX_REQUESTS_PER_HOUR = 5000
rate_limit_semaphore = Semaphore(MAX_REQUESTS_PER_HOUR)

async def rate_limited_api_call(func, *args, **kwargs):
    async with rate_limit_semaphore:
        return await func(*args, **kwargs)
```

### 5.2 Enhanced Caching

Update caching strategy for better performance:

```python
@alru_cache(ttl=86400, maxsize=1000)
async def cached_search(given_name: str, surname: str, year: int, place: str = None):
    # Implementation with caching
    pass
```

## Step 6: Error Handling

### 6.1 Add Comprehensive Error Handling

```python
class FamilySearchAPIError(Exception):
    """Custom exception for FamilySearch API errors."""
    pass

async def handle_api_response(response: httpx.Response) -> Dict[str, Any]:
    """Handle API responses with proper error handling."""
    if response.status_code == 401:
        raise FamilySearchAPIError("Invalid or expired access token")
    elif response.status_code == 429:
        raise FamilySearchAPIError("Rate limit exceeded")
    elif response.status_code >= 400:
        raise FamilySearchAPIError(f"API error: {response.status_code}")

    return response.json()
```

## Step 7: Monitoring and Logging

### 7.1 Add Request Monitoring

```python
import structlog

logger = structlog.get_logger()

async def log_api_request(endpoint: str, params: Dict[str, Any]):
    logger.info("FamilySearch API request",
                endpoint=endpoint,
                params=params,
                timestamp=time.time())
```

## Step 8: Security Considerations

### 8.1 Secure Token Storage

```python
import os
from cryptography.fernet import Fernet

def encrypt_token(token: str) -> str:
    """Encrypt access tokens for storage."""
    key = os.getenv("TOKEN_ENCRYPTION_KEY").encode()
    f = Fernet(key)
    return f.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    """Decrypt access tokens for use."""
    key = os.getenv("TOKEN_ENCRYPTION_KEY").encode()
    f = Fernet(key)
    return f.decrypt(encrypted_token.encode()).decode()
```

## Step 9: Testing

### 9.1 Create Integration Tests

```python
# tests/test_familysearch_integration.py
import pytest
from servers.familysearch_api.server import search_census_records

@pytest.mark.asyncio
async def test_search_census_records():
    """Test real FamilySearch API integration."""
    result = await search_census_records(
        given_name="John",
        surname="Smith",
        year=1850,
        access_token="valid_token"
    )

    assert len(result) > 0
    assert "name" in result[0]
    assert "fsId" in result[0]
```

## Step 10: Production Deployment

### 10.1 Environment Variables

Ensure all sensitive data is in environment variables:

```bash
# Production .env
FAMILYSEARCH_CLIENT_ID=prod_client_id
FAMILYSEARCH_CLIENT_SECRET=prod_client_secret
FAMILYSEARCH_REDIRECT_URI=https://yourdomain.com/oauth/callback
DEBUG=false
LOG_LEVEL=WARNING
```

### 10.2 Docker Configuration

Update `servers/familysearch-api/Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8001
CMD ["python", "server.py"]
```

## Troubleshooting

### Common Issues

1. **401 Unauthorized**: Check your client ID and secret
2. **429 Rate Limited**: Implement proper rate limiting
3. **Invalid GEDCOM X**: Use the provided utilities for format conversion
4. **Token Expired**: Implement token refresh logic

### Debug Mode

Set `DEBUG=true` in your `.env` file to see detailed logs.

## Next Steps

1. **Replace all TODO sections** in `server.py` with real implementations
2. **Add comprehensive tests** for all API endpoints
3. **Implement token refresh** logic for long-running sessions
4. **Add monitoring** for API usage and errors
5. **Set up CI/CD** for automated testing

## Support

- FamilySearch Developer Documentation: https://www.familysearch.org/developers/
- GEDCOM X Specification: https://github.com/FamilySearch/gedcomx
- API Status: Check FamilySearch developer portal for status updates
