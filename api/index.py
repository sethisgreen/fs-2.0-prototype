#!/usr/bin/env python3
"""
Vercel serverless function for FamilySearch OAuth callback and API endpoints.
"""

import os
import json
import asyncio
import httpx
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VercelHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Vercel serverless functions."""
    
    def do_GET(self):
        """Handle GET requests."""
        try:
            # Parse the URL
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            if path == "/oauth/callback":
                self.handle_oauth_callback(query_params)
            elif path == "/api/collections":
                self.handle_collections()
            elif path == "/api/health":
                self.handle_health()
            else:
                self.handle_not_found()
                
        except Exception as e:
            self.handle_error(str(e))
    
    def do_POST(self):
        """Handle POST requests."""
        try:
            # Parse the URL
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            if path == "/oauth/callback":
                self.handle_oauth_callback(query_params)
            else:
                self.handle_not_found()
                
        except Exception as e:
            self.handle_error(str(e))
    
    def handle_oauth_callback(self, query_params):
        """Handle OAuth callback from FamilySearch."""
        try:
            # Extract authorization code
            code = query_params.get('code', [None])[0]
            state = query_params.get('state', [None])[0]
            
            if not code:
                self.send_error_response("No authorization code received", 400)
                return
            
            # Exchange code for token
            token_data = self.exchange_code_for_token(code)
            
            if token_data:
                self.send_json_response({
                    "success": True,
                    "message": "OAuth callback successful",
                    "code": code,
                    "state": state,
                    "token_received": bool(token_data.get('access_token'))
                })
            else:
                self.send_error_response("Failed to exchange code for token", 400)
                
        except Exception as e:
            self.send_error_response(f"OAuth callback error: {str(e)}", 500)
    
    def handle_collections(self):
        """Handle collections API endpoint."""
        try:
            # Get unauthenticated token
            token = self.get_unauthenticated_token()
            
            if not token:
                self.send_error_response("Could not get unauthenticated token", 500)
                return
            
            # Fetch collections
            collections = self.fetch_collections(token)
            
            if collections:
                self.send_json_response({
                    "success": True,
                    "collections": collections
                })
            else:
                self.send_error_response("Failed to fetch collections", 500)
                
        except Exception as e:
            self.send_error_response(f"Collections error: {str(e)}", 500)
    
    def handle_health(self):
        """Handle health check endpoint."""
        self.send_json_response({
            "status": "healthy",
            "service": "FamilySearch OAuth Callback",
            "version": "1.0.0"
        })
    
    def handle_not_found(self):
        """Handle 404 errors."""
        self.send_error_response("Endpoint not found", 404)
    
    def handle_error(self, error_message):
        """Handle general errors."""
        self.send_error_response(f"Internal server error: {error_message}", 500)
    
    def get_unauthenticated_token(self):
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
            # Use synchronous httpx for Vercel
            response = httpx.post(token_url, data=data, timeout=30)
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get('access_token')
            else:
                return None
        except Exception:
            return None
    
    def fetch_collections(self, token):
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
    
    def exchange_code_for_token(self, code):
        """Exchange authorization code for access token."""
        client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
        client_secret = os.getenv('FAMILYSEARCH_CLIENT_SECRET')
        redirect_uri = os.getenv('VERCEL_URL', 'http://localhost:3000') + '/oauth/callback'
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
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_error_response(self, message, status_code=500):
        """Send error response."""
        self.send_json_response({
            "success": False,
            "error": message
        }, status_code)

def handler(request, context):
    """Vercel serverless function handler."""
    # Create a mock request object for our handler
    class MockRequest:
        def __init__(self, method, path, headers, body):
            self.method = method
            self.path = path
            self.headers = headers
            self.body = body
    
    # Create a mock response object
    class MockResponse:
        def __init__(self):
            self.status_code = 200
            self.headers = {}
            self.body = b""
        
        def write(self, data):
            self.body = data
        
        def get_response(self):
            return {
                "statusCode": self.status_code,
                "headers": self.headers,
                "body": self.body.decode('utf-8') if isinstance(self.body, bytes) else str(self.body)
            }
    
    # Parse the request
    method = request.get('method', 'GET')
    path = request.get('path', '/')
    headers = request.get('headers', {})
    body = request.get('body', '')
    
    # Create mock objects
    mock_request = MockRequest(method, path, headers, body)
    mock_response = MockResponse()
    
    # Create handler and process request
    handler = VercelHandler(mock_request, mock_response, None)
    
    if method == 'GET':
        handler.do_GET()
    elif method == 'POST':
        handler.do_POST()
    else:
        handler.handle_not_found()
    
    return mock_response.get_response()

# For local testing
if __name__ == "__main__":
    import sys
    from http.server import HTTPServer
    
    class LocalHandler(VercelHandler):
        def log_message(self, format, *args):
            print(f"[{self.log_date_time_string()}] {format % args}")
    
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    server = HTTPServer(('localhost', port), LocalHandler)
    print(f"Starting server on port {port}")
    server.serve_forever() 