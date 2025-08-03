#!/usr/bin/env python3
"""
Test real FamilySearch authentication with actual API calls.

This script tests different authentication approaches to see what works
without requiring a pre-registered redirect URI.
"""

import os
import sys
import urllib.parse
import httpx
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_unauthenticated_session():
    """Test unauthenticated session grant type."""
    print("🔍 Testing Unauthenticated Session Grant...")
    
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    if not client_id or client_id == 'your_beta_client_id_here':
        print("❌ FAMILYSEARCH_CLIENT_ID not set or using placeholder")
        return False
    
    token_url = os.getenv('FAMILYSEARCH_TOKEN_URL', 'https://identbeta.familysearch.org/cis-web/oauth2/v3/token')
    
    data = {
        'grant_type': 'unauthenticated_session',
        'client_id': client_id
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data, timeout=30)
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Body: {response.text}")
            
            if response.status_code == 200:
                print("✅ Unauthenticated session successful!")
                return True
            else:
                print(f"❌ Unauthenticated session failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error testing unauthenticated session: {e}")
        return False

async def test_authorization_urls():
    """Test authorization URLs in browser."""
    print("\n🔍 Testing Authorization URLs...")
    
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    if not client_id or client_id == 'your_beta_client_id_here':
        print("❌ FAMILYSEARCH_CLIENT_ID not set or using placeholder")
        return False
    
    auth_base_url = os.getenv('FAMILYSEARCH_AUTH_BASE_URL', 'https://identbeta.familysearch.org/cis-web/oauth2/v3')
    
    # Test 1: Without redirect_uri
    params_no_redirect = {
        'response_type': 'code',
        'client_id': client_id,
        'scope': 'openid profile email',
        'state': 'test_state_123'
    }
    auth_url_no_redirect = f"{auth_base_url}/authorization?{urllib.parse.urlencode(params_no_redirect)}"
    
    # Test 2: With localhost redirect_uri
    params_with_redirect = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': 'http://localhost:8001/oauth/callback',
        'scope': 'openid profile email',
        'state': 'test_state_123'
    }
    auth_url_with_redirect = f"{auth_base_url}/authorization?{urllib.parse.urlencode(params_with_redirect)}"
    
    print("📋 Test 1: Authorization WITHOUT redirect_uri")
    print(f"URL: {auth_url_no_redirect}")
    print("   Open this URL in your browser to test")
    
    print("\n📋 Test 2: Authorization WITH localhost redirect_uri")
    print(f"URL: {auth_url_with_redirect}")
    print("   Open this URL in your browser to test")
    
    return True

async def test_api_access_with_token():
    """Test API access with a token (if we get one)."""
    print("\n🔍 Testing API Access...")
    
    # This would be called after we get a token
    api_url = "https://api.familysearch.org/platform"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, timeout=30)
            print(f"API Status Code: {response.status_code}")
            print(f"API Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                print("✅ API access successful!")
                return True
            else:
                print(f"⚠️  API access returned: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error testing API access: {e}")
        return False

async def test_curl_commands():
    """Generate curl commands for manual testing."""
    print("\n🔍 Generating Curl Commands...")
    
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    if not client_id or client_id == 'your_beta_client_id_here':
        print("❌ FAMILYSEARCH_CLIENT_ID not set or using placeholder")
        return False
    
    auth_base_url = os.getenv('FAMILYSEARCH_AUTH_BASE_URL', 'https://identbeta.familysearch.org/cis-web/oauth2/v3')
    token_url = os.getenv('FAMILYSEARCH_TOKEN_URL', 'https://identbeta.familysearch.org/cis-web/oauth2/v3/token')
    
    print("📋 Manual Test Commands:")
    print("\n1. Test Authorization WITHOUT redirect_uri:")
    auth_params_no_redirect = {
        'response_type': 'code',
        'client_id': client_id,
        'scope': 'openid profile email',
        'state': 'test_state_123'
    }
    print(f"curl \"{auth_base_url}/authorization?{urllib.parse.urlencode(auth_params_no_redirect)}\"")
    
    print("\n2. Test Authorization WITH localhost redirect_uri:")
    auth_params_with_redirect = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': 'http://localhost:8001/oauth/callback',
        'scope': 'openid profile email',
        'state': 'test_state_123'
    }
    print(f"curl \"{auth_base_url}/authorization?{urllib.parse.urlencode(auth_params_with_redirect)}\"")
    
    print("\n3. Test Unauthenticated Session Token:")
    print(f"curl -X POST \"{token_url}\" \\")
    print(f"  -H \"Content-Type: application/x-www-form-urlencoded\" \\")
    print(f"  -d \"grant_type=unauthenticated_session&client_id={client_id}\"")
    
    print("\n4. Test API Access (after getting token):")
    print("curl -H \"Authorization: Bearer YOUR_TOKEN\" \\")
    print("  \"https://api.familysearch.org/platform\"")
    
    return True

async def main():
    """Run all authentication tests."""
    print("🚀 Real FamilySearch Authentication Test")
    print("=" * 60)
    
    # Check if we have real credentials
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    if not client_id or client_id == 'your_beta_client_id_here':
        print("⚠️  Using placeholder credentials. Set your real FAMILYSEARCH_CLIENT_ID in .env")
        print("   Tests will show what the requests would look like but won't work with placeholders")
    
    tests = [
        test_unauthenticated_session,
        test_authorization_urls,
        test_api_access_with_token,
        test_curl_commands
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    print("\n📝 Next Steps:")
    print("1. Set your real FAMILYSEARCH_CLIENT_ID in .env")
    print("2. Try the authorization URLs in your browser")
    print("3. Test the unauthenticated session curl command")
    print("4. Check what error messages you get")
    print("5. See if FamilySearch accepts requests without pre-registered redirect URIs")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 