# Vercel Deployment for FamilySearch OAuth Callback

This deployment provides a serverless OAuth callback endpoint for FamilySearch API integration.

## 🚀 Deployment

### 1. **Deploy to Vercel**

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from project root
vercel
```

### 2. **Set Environment Variables**

In your Vercel dashboard, set these environment variables:

```
FAMILYSEARCH_CLIENT_ID=your_beta_client_id
FAMILYSEARCH_CLIENT_SECRET=your_beta_client_secret
FAMILYSEARCH_AUTH_BASE_URL=https://identbeta.familysearch.org/cis-web/oauth2/v3
FAMILYSEARCH_TOKEN_URL=https://identbeta.familysearch.org/cis-web/oauth2/v3/token
```

### 3. **Get Your Redirect URI**

After deployment, your redirect URI will be:
```
https://your-app-name.vercel.app/oauth/callback
```

## 📋 Available Endpoints

### OAuth Callback
- **URL**: `/oauth/callback`
- **Method**: GET
- **Purpose**: Handle FamilySearch OAuth callback

### Collections API
- **URL**: `/api/collections`
- **Method**: GET
- **Purpose**: Test FamilySearch collections access

### Health Check
- **URL**: `/api/health`
- **Method**: GET
- **Purpose**: Service health check

## 🔧 Configuration

### Vercel Configuration (`vercel.json`)
- Routes OAuth callback to Python serverless function
- Sets up CORS headers
- Configures environment variables

### Python Function (`api/oauth-callback.py`)
- Handles OAuth code exchange
- Manages FamilySearch API calls
- Returns JSON responses

## 🧪 Testing

### 1. **Test Health Endpoint**
```bash
curl https://your-app-name.vercel.app/api/health
```

### 2. **Test Collections Endpoint**
```bash
curl https://your-app-name.vercel.app/api/collections
```

### 3. **Test OAuth Callback**
```bash
curl "https://your-app-name.vercel.app/oauth/callback?code=test_code&state=test_state"
```

## 🔐 Security

- Environment variables for all credentials
- CORS headers configured
- Error handling for all endpoints
- No hardcoded secrets

## 📝 Next Steps

1. **Deploy to Vercel**
2. **Set environment variables**
3. **Get your redirect URI**
4. **Register redirect URI with FamilySearch**
5. **Test OAuth flow**

## 🐛 Troubleshooting

### Common Issues:

1. **"react-scripts: command not found"**
   - This is a Python project, not React
   - Use the provided `vercel.json` configuration

2. **Environment variables not set**
   - Set all required environment variables in Vercel dashboard

3. **OAuth callback fails**
   - Check that redirect URI matches exactly
   - Verify client ID and secret are correct

4. **CORS errors**
   - CORS headers are configured in the function
   - Check browser console for specific errors

## 📞 Support

If you encounter issues:
1. Check Vercel function logs
2. Verify environment variables
3. Test endpoints individually
4. Check FamilySearch API documentation 