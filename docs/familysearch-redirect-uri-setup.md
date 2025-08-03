# FamilySearch Redirect URI Setup Guide

## Overview

This guide explains how to set up the correct redirect URI for FamilySearch API authentication and what you need to provide to FamilySearch for whitelisting.

## Redirect URI Requirements

### What FamilySearch Needs

When you contact FamilySearch developer support to register your redirect URI, you need to provide:

1. **Your Developer Key/Client ID**
2. **The exact redirect URI you want to use**
3. **Environment (Beta/Production)**

### Recommended Redirect URI Options

#### Option 1: Local Development (Recommended for Testing)

```
http://localhost:8001/oauth/callback
```

#### Option 2: Production HTTPS (For Live App)

```
https://yourdomain.com/oauth/callback
```

#### Option 3: Custom Path (More Secure)

```
https://yourdomain.com/api/familysearch/callback
```

## Environment Configuration

### Beta Environment (Recommended for Development)

Since you have beta API access, use these URLs:

```bash
# Authorization URL (Beta)
FAMILYSEARCH_AUTH_BASE_URL=https://identbeta.familysearch.org/cis-web/oauth2/v3

# Token URL (Beta)
FAMILYSEARCH_TOKEN_URL=https://identbeta.familysearch.org/cis-web/oauth2/v3/token

# Redirect URI
FAMILYSEARCH_REDIRECT_URI=http://localhost:8001/oauth/callback
```

### Production Environment (For Live App)

```bash
# Authorization URL (Production)
FAMILYSEARCH_AUTH_BASE_URL=https://ident.familysearch.org/cis-web/oauth2/v3

# Token URL (Production)
FAMILYSEARCH_TOKEN_URL=https://ident.familysearch.org/cis-web/oauth2/v3/token

# Redirect URI
FAMILYSEARCH_REDIRECT_URI=https://yourdomain.com/oauth/callback
```

## Contacting FamilySearch Developer Support

### Email Template

```
Subject: Redirect URI Registration for Beta API Access

Hello FamilySearch Developer Support,

I am developing a genealogy research tool (FS 2.0 Prototype) and need to register a redirect URI for OAuth 2.0 authentication.

Developer Key/Client ID: [YOUR_BETA_CLIENT_ID]
Environment: Beta
Redirect URI: http://localhost:8001/oauth/callback

This is for a local development environment. I may need to register additional URIs for production deployment later.

Please whitelist this redirect URI for my beta API access.

Thank you,
[Your Name]
```

### What to Expect

- FamilySearch will review your request
- They may ask for additional information about your application
- Once approved, your redirect URI will be whitelisted
- You'll receive confirmation via email

## Testing Your Redirect URI

### 1. Test OAuth Flow

Once your redirect URI is whitelisted, test the flow:

```bash
# Test authorization URL
curl "https://identbeta.familysearch.org/cis-web/oauth2/v3/authorization?response_type=code&client_id=YOUR_BETA_CLIENT_ID&redirect_uri=http%3A%2F%2Flocalhost%3A8001%2Foauth%2Fcallback&scope=openid%20profile%20email"
```

### 2. Test Token Exchange

```bash
# Test token exchange
curl -X POST "https://identbeta.familysearch.org/cis-web/oauth2/v3/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code&code=YOUR_AUTH_CODE&redirect_uri=http://localhost:8001/oauth/callback&client_id=YOUR_BETA_CLIENT_ID"
```

## Security Considerations

### 1. HTTPS for Production

- Always use HTTPS for production redirect URIs
- Never use HTTP for production environments

### 2. URI Validation

- The redirect URI must match exactly (including protocol, domain, port, and path)
- Query parameters are allowed but must be consistent

### 3. State Parameter

- Always include a `state` parameter for security
- Validate the state parameter in your callback

## Implementation in Your Code

### Updated Environment Variables

```bash
# .env file
FAMILYSEARCH_CLIENT_ID=your_beta_client_id
FAMILYSEARCH_CLIENT_SECRET=your_beta_client_secret
FAMILYSEARCH_REDIRECT_URI=http://localhost:8001/oauth/callback
FAMILYSEARCH_AUTH_BASE_URL=https://identbeta.familysearch.org/cis-web/oauth2/v3
FAMILYSEARCH_TOKEN_URL=https://identbeta.familysearch.org/cis-web/oauth2/v3/token
```

### Updated Server Configuration

```python
# In your server.py
AUTH_BASE_URL = os.getenv("FAMILYSEARCH_AUTH_BASE_URL", "https://identbeta.familysearch.org/cis-web/oauth2/v3")
TOKEN_URL = os.getenv("FAMILYSEARCH_TOKEN_URL", "https://identbeta.familysearch.org/cis-web/oauth2/v3/token")
REDIRECT_URI = os.getenv("FAMILYSEARCH_REDIRECT_URI", "http://localhost:8001/oauth/callback")
```

## Troubleshooting

### Common Issues

1. **"Invalid redirect_uri" Error**

   - Ensure the URI is exactly registered with FamilySearch
   - Check for trailing slashes or missing protocols

2. **"Client not found" Error**

   - Verify your client ID is correct
   - Ensure you're using the right environment (beta vs production)

3. **"Unauthorized" Error**
   - Check that your client secret is correct
   - Verify you're using the right token URL

### Debug Steps

1. **Verify Registration**: Contact FamilySearch to confirm your redirect URI is registered
2. **Test Authorization URL**: Use curl to test the authorization endpoint
3. **Check Logs**: Monitor your server logs for detailed error messages
4. **Validate Parameters**: Ensure all required parameters are present and correct

## Next Steps

1. **Contact FamilySearch** with your redirect URI for whitelisting
2. **Update your .env file** with the correct beta URLs
3. **Test the OAuth flow** once whitelisted
4. **Implement the token exchange** in your server code
5. **Add proper error handling** for authentication failures

## Support Resources

- FamilySearch Developer Support: [developer@familysearch.org](mailto:developer@familysearch.org)
- FamilySearch Developer Documentation: https://www.familysearch.org/en/developers/docs/
- OAuth 2.0 Specification: https://tools.ietf.org/html/rfc6749
