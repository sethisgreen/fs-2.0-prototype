# FamilySearch OAuth Realm Configuration Issue

## 🔍 **Issue Summary**

**Error:** `invalid_request` - "Client needs a realm configured for openid-connect"

**Status:** OAuth flow fails during authorization due to missing realm configuration

## 📋 **Technical Details**

### Error Details

- **Error Code:** `invalid_request`
- **Error Description:** "Validation exception. Client needs a realm configured for openid-connect"
- **OAuth Flow:** Authorization Code Flow
- **Client Type:** Public Client (Web Application)
- **Redirect URI:** `https://fs-agent.com/oauth/callback`

### What We've Tested

✅ **Working:**

- Redirect URI whitelisting
- OAuth callback handling
- Basic OAuth URL generation
- Unauthenticated session access

❌ **Failing:**

- Authorization Code Flow (realm configuration required)
- Client Credentials Flow (not supported for public clients)

## 🛠️ **Solutions to Try**

### 1. Contact FamilySearch Support

**Subject:** OAuth Client Realm Configuration Issue

**Message Template:**

```
Hello FamilySearch Developer Support,

I'm developing an application that integrates with the FamilySearch API using OAuth 2.0 Authorization Code Flow.

**Issue:** When attempting OAuth authorization, I receive the error:
"Validation exception. Client needs a realm configured for openid-connect"

**Client Details:**
- Client ID: [YOUR_CLIENT_ID]
- Application Type: Web Application (Public Client)
- Redirect URI: https://fs-agent.com/oauth/callback
- OAuth Flow: Authorization Code Flow

**Steps to Reproduce:**
1. Navigate to: https://identbeta.familysearch.org/cis-web/oauth2/v3/authorization?response_type=code&client_id=[CLIENT_ID]&redirect_uri=https%3A%2F%2Ffs-agent.com%2Foauth%2Fcallback&state=test
2. Complete FamilySearch login
3. Receive error: "Client needs a realm configured for openid-connect"

**Questions:**
1. What realm configuration is required for OpenID Connect?
2. How should I configure the client for OAuth 2.0 Authorization Code Flow?
3. Are there specific settings needed in the FamilySearch Developer Portal?

Thank you for your assistance.

Best regards,
[Your Name]
```

### 2. Alternative Approaches

#### Option A: Use Unauthenticated Sessions

- Continue with current unauthenticated session access
- Limited but functional for basic API calls
- Good for testing and development

#### Option B: Request Realm Configuration

- Contact FamilySearch support
- Provide client details and use case
- Request proper realm configuration

#### Option C: Use Different OAuth Flow

- Test if other grant types work
- Explore alternative authentication methods

## 📊 **Current Working Capabilities**

With unauthenticated sessions, we can access:

- ✅ Collection metadata
- ✅ Date authority information
- ✅ Basic API structure

## 🎯 **Next Steps**

1. **Immediate:** Continue development with unauthenticated sessions
2. **Short-term:** Contact FamilySearch support about realm configuration
3. **Long-term:** Implement full OAuth once realm is configured

## 📞 **Contact Information**

- **FamilySearch Developer Support:** [Find contact info in developer portal]
- **Documentation:** https://www.familysearch.org/en/developers/docs/api
- **Developer Portal:** [Your FamilySearch developer portal URL]
