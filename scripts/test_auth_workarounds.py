#!/usr/bin/env python3
"""
Test various workarounds for FamilySearch API access.

This script tests different approaches to see if we can access
FamilySearch data without requiring a pre-registered redirect URI.
"""

import os
import sys
import urllib.parse
import httpx
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_unauthenticated_session_with_ip():
    """Test unauthenticated session with IP address parameter."""
    print("🔍 Testing Unauthenticated Session with IP Address...")
    
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    if not client_id:
        print("❌ FAMILYSEARCH_CLIENT_ID not set in environment")
        return None
    token_url = "https://identbeta.familysearch.org/cis-web/oauth2/v3/token"
    
    data = {
        'grant_type': 'unauthenticated_session',
        'client_id': client_id,
        'ip_address': '127.0.0.1'  # Add IP address parameter
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data, timeout=30)
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")
            
            if response.status_code == 200:
                print("✅ Unauthenticated session with IP successful!")
                try:
                    token_data = response.json()
                    if 'access_token' in token_data:
                        print(f"✅ Access token: {token_data['access_token'][:20]}...")
                        return token_data['access_token']
                except:
                    print("⚠️  Could not parse token response")
                return True
            else:
                print(f"❌ Unauthenticated session with IP failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error testing unauthenticated session with IP: {e}")
        return False

async def test_authorization_without_redirect_browser():
    """Test authorization URL without redirect_uri in browser."""
    print("\n🔍 Testing Authorization URL Without Redirect (Browser Test)...")
    
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    if not client_id:
        print("❌ FAMILYSEARCH_CLIENT_ID not set in environment")
        return None
    auth_base_url = "https://identbeta.familysearch.org/cis-web/oauth2/v3"
    
    # Test authorization without redirect_uri
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'scope': 'openid profile email',
        'state': 'test_state_123'
    }
    
    auth_url = f"{auth_base_url}/authorization?{urllib.parse.urlencode(params)}"
    
    print(f"Authorization URL (no redirect_uri): {auth_url}")
    print("📋 Open this URL in your browser to test")
    print("   This will show if FamilySearch accepts requests without redirect_uri")
    
    return auth_url

async def test_authorization_with_localhost_browser():
    """Test authorization URL with localhost redirect in browser."""
    print("\n🔍 Testing Authorization URL With Localhost (Browser Test)...")
    
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    if not client_id:
        print("❌ FAMILYSEARCH_CLIENT_ID not set in environment")
        return None
    auth_base_url = "https://identbeta.familysearch.org/cis-web/oauth2/v3"
    
    # Test authorization with localhost redirect
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': 'http://localhost:8001/oauth/callback',
        'scope': 'openid profile email',
        'state': 'test_state_123'
    }
    
    auth_url = f"{auth_base_url}/authorization?{urllib.parse.urlencode(params)}"
    
    print(f"Authorization URL (with localhost): {auth_url}")
    print("📋 Open this URL in your browser to test")
    print("   This will show if FamilySearch accepts localhost without pre-registration")
    
    return auth_url

async def test_public_endpoints():
    """Test endpoints that might be publicly accessible."""
    print("\n🔍 Testing Potentially Public Endpoints...")
    
    endpoints = [
        "https://api.familysearch.org/platform/places/search?q=New%20York&count=5",
        "https://api.familysearch.org/platform/dates?date=1850",
        "https://api.familysearch.org/platform/tree/persons?pids=KWQS-MBQ",
        "https://api.familysearch.org/platform/collections",
        "https://api.familysearch.org/platform/authorities/places"
    ]
    
    for endpoint in endpoints:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, timeout=30)
                print(f"✅ {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    print(f"   Response: {response.text[:100]}...")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

async def test_curl_commands():
    """Generate curl commands for manual testing."""
    print("\n🔍 Generating Manual Test Commands...")
    
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    if not client_id:
        print("❌ FAMILYSEARCH_CLIENT_ID not set in environment")
        return None
    auth_base_url = "https://identbeta.familysearch.org/cis-web/oauth2/v3"
    token_url = "https://identbeta.familysearch.org/cis-web/oauth2/v3/token"
    
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
    
    print("\n3. Test Unauthenticated Session with IP:")
    print(f"curl -X POST \"{token_url}\" \\")
    print(f"  -H \"Content-Type: application/x-www-form-urlencoded\" \\")
    print(f"  -d \"grant_type=unauthenticated_session&client_id={client_id}&ip_address=127.0.0.1\"")
    
    print("\n4. Test Public Endpoints:")
    print("curl \"https://api.familysearch.org/platform/places/search?q=New%20York&count=5\"")
    print("curl \"https://api.familysearch.org/platform/collections\"")
    
    return True

async def main():
    """Run all workaround tests."""
    print("🚀 FamilySearch Authentication Workarounds Test")
    print("=" * 60)
    
    tests = [
        test_unauthenticated_session_with_ip,
        test_authorization_without_redirect_browser,
        test_authorization_with_localhost_browser,
        test_public_endpoints,
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
    
    print("\n💡 Key Questions to Answer:")
    print("1. Does FamilySearch accept authorization requests without redirect_uri?")
    print("2. Does FamilySearch accept localhost redirect URIs without pre-registration?")
    print("3. Does unauthenticated session with IP address work?")
    print("4. Are there any publicly accessible endpoints?")
    
    print("\n📝 Manual Testing Instructions:")
    print("1. Try the authorization URLs in your browser")
    print("2. Test the curl commands")
    print("3. Check what error messages you get")
    print("4. See if any endpoints work without authentication")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 