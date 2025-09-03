#!/usr/bin/env python3
"""
Test FamilySearch OAuth flow with whitelisted redirect URI
"""

import os
import sys
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_familysearch_oauth():
    """Test the complete FamilySearch OAuth flow"""
    
    # Get credentials from environment
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    client_secret = os.getenv('FAMILYSEARCH_CLIENT_SECRET')
    redirect_uri = "https://fs-agent.com/oauth/callback"
    
    if not client_id:
        print("❌ FAMILYSEARCH_CLIENT_ID not found in environment")
        print("Please set your FamilySearch client ID in .env file")
        return False
    
    if not client_secret:
        print("❌ FAMILYSEARCH_CLIENT_SECRET not found in environment")
        print("Please set your FamilySearch client secret in .env file")
        return False
    
    print("🔐 Testing FamilySearch OAuth Flow")
    print(f"Client ID: {client_id[:8]}...")
    print(f"Redirect URI: {redirect_uri}")
    print()
    
    # Step 1: Generate authorization URL
    auth_url = "https://identbeta.familysearch.org/cis-web/oauth2/v3/authorization"
    state = "test_state_123"
    
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'state': state,
        'scope': 'openid profile email'
    }
    
    authorization_url = f"{auth_url}?{urlencode(params)}"
    
    print("📋 Authorization URL:")
    print(authorization_url)
    print()
    
    # Step 2: Open browser for user authorization
    print("🌐 Opening browser for FamilySearch authorization...")
    print("Please complete the authorization in your browser.")
    print("After authorization, you'll be redirected to our callback page.")
    print()
    
    try:
        webbrowser.open(authorization_url)
        print("✅ Browser opened successfully")
        print()
        print("📝 Next steps:")
        print("1. Complete the FamilySearch login in your browser")
        print("2. You'll be redirected to: https://fs-agent.com/oauth/callback")
        print("3. Check the callback page for the authorization code")
        print("4. We can then exchange the code for an access token")
        
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        print("Please manually visit the authorization URL above")
    
    return True

def test_token_exchange(code):
    """Test exchanging authorization code for access token"""
    
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    client_secret = os.getenv('FAMILYSEARCH_CLIENT_SECRET')
    redirect_uri = "https://fs-agent.com/oauth/callback"
    
    if not code:
        print("❌ No authorization code provided")
        return False
    
    print(f"🔄 Exchanging authorization code for access token...")
    print(f"Code: {code[:10]}...")
    
    token_url = "https://identbeta.familysearch.org/cis-web/oauth2/v3/token"
    
    # For public clients, don't send client_secret
    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'code': code,
        'redirect_uri': redirect_uri
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': os.getenv('CUSTOM_USER_AGENT', 'FS-Agent-Test/1.0')
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(token_url, data=data, headers=headers)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                token_data = response.json()
                print("✅ Token exchange successful!")
                print(f"Access Token: {token_data.get('access_token', 'N/A')[:20]}...")
                print(f"Token Type: {token_data.get('token_type', 'N/A')}")
                print(f"Expires In: {token_data.get('expires_in', 'N/A')} seconds")
                print(f"Scope: {token_data.get('scope', 'N/A')}")
                
                # Test API call with the token
                test_api_call(token_data.get('access_token'))
                
                return True
            else:
                print(f"❌ Token exchange failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error during token exchange: {e}")
        return False

def test_api_call(access_token):
    """Test making an API call with the access token"""
    
    if not access_token:
        print("❌ No access token provided")
        return False
    
    print("\n🔍 Testing API call with access token...")
    
    # Test the current user endpoint
    api_url = "https://api.familysearch.org/platform/users/current"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/x-gedcomx-v1+json',
        'User-Agent': os.getenv('CUSTOM_USER_AGENT', 'FS-Agent-Test/1.0')
    }
    
    try:
        with httpx.Client() as client:
            response = client.get(api_url, headers=headers)
            
            print(f"API Status Code: {response.status_code}")
            
            if response.status_code == 200:
                user_data = response.json()
                print("✅ API call successful!")
                print(f"User ID: {user_data.get('users', [{}])[0].get('id', 'N/A')}")
                print(f"Contact Name: {user_data.get('users', [{}])[0].get('contactName', 'N/A')}")
                return True
            else:
                print(f"❌ API call failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error during API call: {e}")
        return False

if __name__ == "__main__":
    print("🚀 FamilySearch OAuth Test")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # If authorization code is provided as argument
        code = sys.argv[1]
        test_token_exchange(code)
    else:
        # Start the OAuth flow
        test_familysearch_oauth() 