# FamilySearch API Quick Reference

## Authentication Endpoints

| Endpoint                                                         | Method | Purpose                 |
| ---------------------------------------------------------------- | ------ | ----------------------- |
| `https://ident.familysearch.org/cis-web/oauth2/v3/authorization` | GET    | Get authorization URL   |
| `https://ident.familysearch.org/cis-web/oauth2/v3/token`         | POST   | Exchange code for token |

## Records Search Endpoints

| Endpoint                                                         | Method | Headers                                                                        | Purpose                     |
| ---------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------ | --------------------------- |
| `https://api.familysearch.org/platform/records/search`           | POST   | `Authorization: Bearer {token}`, `Content-Type: application/x-gedcomx-v1+json` | Search historical records   |
| `https://api.familysearch.org/platform/records/{record_id}`      | GET    | `Authorization: Bearer {token}`                                                | Get specific record details |
| `https://api.familysearch.org/platform/tree/persons/{person_id}` | GET    | `Authorization: Bearer {token}`                                                | Get person details          |

## Common Parameters

### Search Parameters

- `givenName`: First name
- `surname`: Last name
- `eventDate`: Year or date range
- `place`: Location
- `count`: Number of results (max 100)
- `eventType`: "birth", "death", "marriage"

### Response Headers

- `X-Rate-Limit-Remaining`: Remaining requests
- `X-Rate-Limit-Reset`: Reset time
- `Content-Type`: `application/x-gedcomx-v1+json`

## Rate Limits

| Plan     | Requests/Hour | Notes                         |
| -------- | ------------- | ----------------------------- |
| Standard | 1,000         | Basic API access              |
| Beta     | 5,000         | Enhanced access with beta key |

## Common HTTP Status Codes

| Code | Meaning      | Action               |
| ---- | ------------ | -------------------- |
| 200  | Success      | Process response     |
| 401  | Unauthorized | Refresh token        |
| 429  | Rate Limited | Wait and retry       |
| 400  | Bad Request  | Check parameters     |
| 404  | Not Found    | Record doesn't exist |

## GEDCOM X Response Structure

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
          "relationships": [...]
        }
      ]
    }
  ]
}
```

## Environment Variables

```bash
FAMILYSEARCH_CLIENT_ID=your_beta_client_id
FAMILYSEARCH_CLIENT_SECRET=your_beta_client_secret
FAMILYSEARCH_REDIRECT_URI=http://localhost:8001/oauth/callback
FAMILYSEARCH_API_BASE_URL=https://api.familysearch.org/platform
FAMILYSEARCH_AUTH_BASE_URL=https://ident.familysearch.org/cis-web/oauth2/v3
```

## Quick Test Commands

### Test OAuth Flow

```bash
curl "https://ident.familysearch.org/cis-web/oauth2/v3/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:8001/oauth/callback&scope=openid%20profile%20email"
```

### Test Records Search

```bash
curl -X POST "https://api.familysearch.org/platform/records/search" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/x-gedcomx-v1+json" \
  -d '{"query":{"persons":[{"names":[{"nameForms":[{"parts":[{"type":"http://gedcomx.org/v1/Given","value":"John"},{"type":"http://gedcomx.org/v1/Surname","value":"Smith"}]}]}]}]},"count":10}'
```

## Error Handling Patterns

```python
# Rate limiting
if response.status_code == 429:
    retry_after = int(response.headers.get('Retry-After', 60))
    await asyncio.sleep(retry_after)
    return await api_call()  # Retry

# Token refresh
if response.status_code == 401:
    new_token = await refresh_access_token()
    return await api_call(token=new_token)  # Retry with new token
```

## Caching Strategy

```python
@alru_cache(ttl=86400)  # 24 hours
async def cached_search(given_name: str, surname: str, year: int):
    # Implementation
    pass
```

## Security Best Practices

1. **Never log access tokens**
2. **Use environment variables for credentials**
3. **Implement proper token refresh**
4. **Respect rate limits**
5. **Validate all inputs**
6. **Use HTTPS for all requests**
