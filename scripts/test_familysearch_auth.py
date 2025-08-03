#!/usr/bin/env python3
"""
Test script for FamilySearch API authentication setup.

This script helps verify that your redirect URI and authentication configuration
are properly set up before implementing the full OAuth flow.
"""

import os
import sys
import urllib.parse
import httpx
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment_variables():
    """Test that all required environment variables are set."""
    print("🔍 Testing Environment Variables...")
    
    required_vars = [
        'FAMILYSEARCH_CLIENT_ID',
        'FAMILYSEARCH_CLIENT_SECRET', 
        'FAMILYSEARCH_REDIRECT_URI',
        'FAMILYSEARCH_AUTH_BASE_URL',
        'FAMILYSEARCH_TOKEN_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {value[:20]}..." if len(value) > 20 else f"✅ {var}: {value}")
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("Please set these in your .env file")
        return False
    
    print("✅ All environment variables are set")
    return True

def test_authorization_url():
    """Test the authorization URL construction."""
    print("\n🔍 Testing Authorization URL...")
    
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    redirect_uri = os.getenv('FAMILYSEARCH_REDIRECT_URI')
    auth_base_url = os.getenv('FAMILYSEARCH_AUTH_BASE_URL')
    
    # Construct authorization URL
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': 'openid profile email',
        'state': 'test_state_123'
    }
    
    auth_url = f"{auth_base_url}/authorization?{urllib.parse.urlencode(params)}"
    
    print(f"Authorization URL: {auth_url}")
    print(f"✅ Authorization URL constructed successfully")
    
    return auth_url

def test_token_url():
    """Test the token URL configuration."""
    print("\n🔍 Testing Token URL...")
    
    token_url = os.getenv('FAMILYSEARCH_TOKEN_URL')
    print(f"Token URL: {token_url}")
    print(f"✅ Token URL configured")
    
    return token_url

def test_redirect_uri_format():
    """Test that the redirect URI is properly formatted."""
    print("\n🔍 Testing Redirect URI Format...")
    
    redirect_uri = os.getenv('FAMILYSEARCH_REDIRECT_URI')
    
    # Check if it's a valid URL
    try:
        parsed = urllib.parse.urlparse(redirect_uri)
        if parsed.scheme and parsed.netloc:
            print(f"✅ Redirect URI format is valid: {redirect_uri}")
            
            # Check if it's localhost for development
            if 'localhost' in parsed.netloc or '127.0.0.1' in parsed.netloc:
                print("ℹ️  Using localhost for development (this is correct for testing)")
            else:
                print("ℹ️  Using production domain (ensure this is registered with FamilySearch)")
                
            return True
        else:
            print(f"❌ Invalid redirect URI format: {redirect_uri}")
            return False
    except Exception as e:
        print(f"❌ Error parsing redirect URI: {e}")
        return False

def test_curl_commands():
    """Generate test curl commands."""
    print("\n🔍 Generating Test Commands...")
    
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    redirect_uri = os.getenv('FAMILYSEARCH_REDIRECT_URI')
    auth_base_url = os.getenv('FAMILYSEARCH_AUTH_BASE_URL')
    token_url = os.getenv('FAMILYSEARCH_TOKEN_URL')
    
    # Test authorization URL
    auth_params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': 'openid profile email',
        'state': 'test_state_123'
    }
    
    auth_curl = f"""curl "{auth_base_url}/authorization?{urllib.parse.urlencode(auth_params)}"
"""
    
    # Test token exchange (placeholder)
    token_curl = f"""curl -X POST "{token_url}" \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "grant_type=authorization_code&code=YOUR_AUTH_CODE&redirect_uri={redirect_uri}&client_id={client_id}"
"""
    
    print("📋 Test Authorization URL:")
    print(auth_curl)
    print("\n📋 Test Token Exchange (replace YOUR_AUTH_CODE with actual code):")
    print(token_curl)
    
    return True

def test_familysearch_endpoints():
    """Test basic connectivity to FamilySearch endpoints."""
    print("\n🔍 Testing FamilySearch Endpoint Connectivity...")
    
    endpoints = [
        "https://api.familysearch.org/platform",
        "https://identbeta.familysearch.org/cis-web/oauth2/v3/authorization"
    ]
    
    for endpoint in endpoints:
        try:
            response = httpx.get(endpoint, timeout=10)
            if response.status_code in [200, 401, 403]:  # These are expected responses
                print(f"✅ {endpoint}: {response.status_code}")
            else:
                print(f"⚠️  {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Connection failed - {e}")
    
    return True

def main():
    """Run all tests."""
    print("🚀 FamilySearch API Authentication Setup Test")
    print("=" * 50)
    
    tests = [
        test_environment_variables,
        test_redirect_uri_format,
        test_authorization_url,
        test_token_url,
        test_familysearch_endpoints,
        test_curl_commands
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Your configuration looks good.")
        print("\n📝 Next Steps:")
        print("1. Contact FamilySearch to register your redirect URI")
        print("2. Test the OAuth flow with the provided curl commands")
        print("3. Implement the token exchange in your server code")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 