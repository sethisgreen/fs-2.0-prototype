#!/usr/bin/env python3
"""
Test different OAuth configurations to work around realm requirement
"""

import os
import webbrowser
from urllib.parse import urlencode
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_oauth_configurations():
    """Test different OAuth configurations"""
    
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    redirect_uri = "https://fs-agent.com/oauth/callback"
    
    if not client_id:
        print("❌ FAMILYSEARCH_CLIENT_ID not found")
        return
    
    print("🔧 Testing Different OAuth Configurations")
    print("=" * 50)
    
    # Configuration 1: Basic OAuth (no OpenID Connect)
    print("\n📋 Configuration 1: Basic OAuth (no OpenID Connect)")
    auth_url_1 = "https://identbeta.familysearch.org/cis-web/oauth2/v3/authorization"
    params_1 = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'state': 'test_basic_oauth'
    }
    url_1 = f"{auth_url_1}?{urlencode(params_1)}"
    print(f"URL: {url_1}")
    
    # Configuration 2: Minimal OpenID Connect
    print("\n📋 Configuration 2: Minimal OpenID Connect")
    params_2 = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'state': 'test_minimal_oidc',
        'scope': 'openid'
    }
    url_2 = f"{auth_url_1}?{urlencode(params_2)}"
    print(f"URL: {url_2}")
    
    # Configuration 3: Standard OpenID Connect
    print("\n📋 Configuration 3: Standard OpenID Connect")
    params_3 = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'state': 'test_standard_oidc',
        'scope': 'openid profile email'
    }
    url_3 = f"{auth_url_1}?{urlencode(params_3)}"
    print(f"URL: {url_3}")
    
    # Configuration 4: No scope specified
    print("\n📋 Configuration 4: No scope specified")
    params_4 = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'state': 'test_no_scope'
    }
    url_4 = f"{auth_url_1}?{urlencode(params_4)}"
    print(f"URL: {url_4}")
    
    print("\n🧪 Test Instructions:")
    print("1. Try each configuration URL in your browser")
    print("2. See which one works without the realm error")
    print("3. Report back which configuration succeeds")
    
    # Try the most likely working configuration first
    print("\n🚀 Testing Configuration 1 (Basic OAuth)...")
    try:
        webbrowser.open(url_1)
        print("✅ Browser opened with basic OAuth configuration")
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        print(f"Manual URL: {url_1}")
    
    return {
        'basic_oauth': url_1,
        'minimal_oidc': url_2,
        'standard_oidc': url_3,
        'no_scope': url_4
    }

def test_client_credentials():
    """Test client credentials flow as alternative"""
    
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    client_secret = os.getenv('FAMILYSEARCH_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Missing client credentials")
        return
    
    print("\n🔑 Testing Client Credentials Flow")
    print("=" * 40)
    
    import httpx
    
    token_url = "https://identbeta.familysearch.org/cis-web/oauth2/v3/token"
    
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': os.getenv('CUSTOM_USER_AGENT', 'FS-Agent-Test/1.0')
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(token_url, data=data, headers=headers)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                print("✅ Client credentials flow successful!")
                print(f"Access Token: {token_data.get('access_token', 'N/A')[:20]}...")
                print(f"Token Type: {token_data.get('token_type', 'N/A')}")
                return token_data.get('access_token')
            else:
                print(f"❌ Client credentials failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Error in client credentials flow: {e}")
        return None

if __name__ == "__main__":
    print("🔧 FamilySearch OAuth Configuration Test")
    print("=" * 50)
    
    # Test different OAuth configurations
    configs = test_oauth_configurations()
    
    # Test client credentials as alternative
    print("\n" + "=" * 50)
    test_client_credentials()
    
    print("\n📝 Summary:")
    print("- Try each configuration URL to find one that works")
    print("- Client credentials flow might work as alternative")
    print("- Contact FamilySearch support about realm configuration") 