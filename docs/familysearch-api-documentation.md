# FamilySearch API Documentation

## Overview

This document provides the essential information needed to integrate with the FamilySearch API for the FS 2.0 Prototype.

## Authentication

### OAuth 2.0 Flow

FamilySearch uses OAuth 2.0 with Authorization Code flow:

1. **Authorization URL**: `https://ident.familysearch.org/cis-web/oauth2/v3/authorization`
2. **Token Exchange URL**: `https://ident.familysearch.org/cis-web/oauth2/v3/token`
3. **Required Scopes**: `openid profile email`

### Environment Variables Needed

```bash
FAMILYSEARCH_CLIENT_ID=your_client_id
FAMILYSEARCH_CLIENT_SECRET=your_client_secret
FAMILYSEARCH_REDIRECT_URI=http://localhost:8001/oauth/callback
```

## Core API Endpoints

### 1. Records Search

**Endpoint**: `https://api.familysearch.org/platform/records/search`
**Method**: GET
**Headers**: `Authorization: Bearer {access_token}`

**Parameters**:

- `givenName`: First name
- `surname`: Last name
- `eventDate`: Year or date range
- `place`: Location
- `count`: Number of results (max 100)

**Response Format** (GEDCOM X):

```json
{
  "entries": [
    {
      "id": "FS123",
      "title": "Record Title",
      "content": [
        {
          "type": "http://gedcomx.org/v1/Record",
          "attribution": {...},
          "sourceDescriptions": [...],
          "persons": [...],
          "relationships": [...],
          "sourceReferences": [...]
        }
      ]
    }
  ]
}
```

### 2. Person Details

**Endpoint**: `https://api.familysearch.org/platform/tree/persons/{person_id}`
**Method**: GET

### 3. Record Details

**Endpoint**: `https://api.familysearch.org/platform/records/{record_id}`
**Method**: GET

### 4. Vital Records Search

**Endpoint**: `https://api.familysearch.org/platform/records/search`
**Parameters**:

- `eventType`: "birth", "death", "marriage"
- `givenName`, `surname`
- `eventDate`, `eventPlace`

## Rate Limits

- **Standard**: 1000 requests per hour
- **Beta**: 5000 requests per hour (with beta API key)
- **Headers**: Check `X-Rate-Limit-Remaining` and `X-Rate-Limit-Reset`

## Data Models

### Record Model (GEDCOM X aligned)

```python
class Record(BaseModel):
    id: str
    name: str
    birthDate: Optional[str]
    deathDate: Optional[str]
    residencePlace: Optional[str]
    recordUrl: str
    fsId: str
    sourceDescriptions: List[Dict] = []
    persons: List[Dict] = []
    relationships: List[Dict] = []
```

### Person Model

```python
class Person(BaseModel):
    id: str
    names: List[Dict]
    facts: List[Dict]
    sources: List[Dict]
    relationships: List[Dict]
```

## Error Handling

### Common HTTP Status Codes

- `200`: Success
- `401`: Unauthorized (invalid/expired token)
- `429`: Rate limit exceeded
- `400`: Bad request
- `404`: Record not found

### Retry Strategy

```python
@retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000)
async def api_call_with_retry():
    # Implementation with exponential backoff
```

## Caching Strategy

- **Cache TTL**: 24 hours for search results
- **Cache Key**: `{endpoint}_{parameters_hash}`
- **Invalidation**: On record updates (if available)

## Development Setup

### 1. Get FamilySearch Developer Account

1. Visit: https://www.familysearch.org/developers/
2. Create developer account
3. Register your application
4. Get Client ID and Secret

### 2. Environment Setup

Create `.env` file:

```bash
FAMILYSEARCH_CLIENT_ID=your_beta_client_id
FAMILYSEARCH_CLIENT_SECRET=your_beta_client_secret
FAMILYSEARCH_REDIRECT_URI=http://localhost:8001/oauth/callback
FAMILYSEARCH_API_BASE_URL=https://api.familysearch.org/platform
```

### 3. Testing

- Use FamilySearch's sandbox environment for development
- Test with known historical records
- Validate GEDCOM X format compliance

## Integration Notes

### GEDCOM X Compliance

- All responses should be converted to GEDCOM X format
- Use standard GEDCOM X namespaces
- Include proper attribution and source descriptions

### Privacy Considerations

- Never log personal data
- Implement data anonymization for testing
- Respect FamilySearch ToS regarding AI agent usage
- Limit query frequency to avoid rate limiting

### Beta API Features

With beta API key, you get access to:

- Higher rate limits (5000 req/hour)
- Additional endpoints
- Enhanced search capabilities
- Real-time data updates

## Next Steps for Implementation

1. **Replace mock implementations** in `servers/familysearch-api/server.py`
2. **Add proper OAuth flow** with token management
3. **Implement GEDCOM X conversion** utilities
4. **Add comprehensive error handling** and retry logic
5. **Set up caching** with async-lru
6. **Create integration tests** with real API calls
7. **Add monitoring** for rate limits and errors
