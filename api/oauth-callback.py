#!/usr/bin/env python3
"""
Vercel serverless function for FamilySearch OAuth callback.
"""

import os
import json
import httpx
from urllib.parse import parse_qs, urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def handler(request, context):
    """Vercel serverless function handler for OAuth callback."""
    
    # Parse request
    method = request.get('method', 'GET')
    path = request.get('path', '/')
    headers = request.get('headers', {})
    body = request.get('body', '')
    
    # Handle CORS preflight
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'message': 'CORS preflight'})
        }
    
    # Parse query parameters
    parsed_url = urlparse(path)
    query_params = parse_qs(parsed_url.query)
    
    try:
        if method == 'GET' and '/oauth/callback' in path:
            return handle_oauth_callback(query_params)
        elif method == 'GET' and '/api/collections' in path:
            return handle_collections()
        elif method == 'GET' and '/api/health' in path:
            return handle_health()
        else:
            return handle_not_found()
            
    except Exception as e:
        return handle_error(str(e))

def handle_oauth_callback(query_params):
    """Handle OAuth callback from FamilySearch."""
    try:
        # Extract authorization code
        code = query_params.get('code', [None])[0]
        state = query_params.get('state', [None])[0]
        
        if not code:
            return send_error_response("No authorization code received", 400)
        
        # Exchange code for token
        token_data = exchange_code_for_token(code)
        
        if token_data:
            return send_json_response({
                "success": True,
                "message": "OAuth callback successful",
                "code": code,
                "state": state,
                "token_received": bool(token_data.get('access_token'))
            })
        else:
            return send_error_response("Failed to exchange code for token", 400)
            
    except Exception as e:
        return send_error_response(f"OAuth callback error: {str(e)}", 500)

def handle_collections():
    """Handle collections API endpoint."""
    try:
        # Get unauthenticated token
        token = get_unauthenticated_token()
        
        if not token:
            return send_error_response("Could not get unauthenticated token", 500)
        
        # Fetch collections
        collections = fetch_collections(token)
        
        if collections:
            return send_json_response({
                "success": True,
                "collections": collections
            })
        else:
            return send_error_response("Failed to fetch collections", 500)
            
    except Exception as e:
        return send_error_response(f"Collections error: {str(e)}", 500)

def handle_health():
    """Handle health check endpoint."""
    return send_json_response({
        "status": "healthy",
        "service": "FamilySearch OAuth Callback",
        "version": "1.0.0"
    })

def handle_not_found():
    """Handle 404 errors."""
    return send_error_response("Endpoint not found", 404)

def handle_error(error_message):
    """Handle general errors."""
    return send_error_response(f"Internal server error: {error_message}", 500)

def get_unauthenticated_token():
    """Get an unauthenticated session token."""
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    if not client_id:
        return None
    
    token_url = os.getenv('FAMILYSEARCH_TOKEN_URL', 'https://identbeta.familysearch.org/cis-web/oauth2/v3/token')
    
    data = {
        'grant_type': 'unauthenticated_session',
        'client_id': client_id,
        'ip_address': '127.0.0.1'
    }
    
    try:
        response = httpx.post(token_url, data=data, timeout=30)
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get('access_token')
        else:
            return None
    except Exception:
        return None

def fetch_collections(token):
    """Fetch FamilySearch collections."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/x-gedcomx-v1+json'
    }
    
    try:
        response = httpx.get(
            "https://api.familysearch.org/platform/collections",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception:
        return None

def exchange_code_for_token(code):
    """Exchange authorization code for access token."""
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    client_secret = os.getenv('FAMILYSEARCH_CLIENT_SECRET')
    
    # Get the Vercel URL from environment
    vercel_url = os.getenv('VERCEL_URL', 'http://localhost:3000')
    if not vercel_url.startswith('http'):
        vercel_url = f"https://{vercel_url}"
    
    redirect_uri = f"{vercel_url}/oauth/callback"
    token_url = os.getenv('FAMILYSEARCH_TOKEN_URL', 'https://identbeta.familysearch.org/cis-web/oauth2/v3/token')
    
    if not client_id or not client_secret:
        return None
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    try:
        response = httpx.post(token_url, data=data, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception:
        return None

def send_json_response(data, status_code=200):
    """Send JSON response."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(data)
    }

def send_error_response(message, status_code=500):
    """Send error response."""
    return send_json_response({
        "success": False,
        "error": message
    }, status_code) 