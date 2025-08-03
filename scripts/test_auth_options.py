#!/usr/bin/env python3
"""
Test different FamilySearch authentication approaches.

This script tests various authentication methods to see what works
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

def test_authorization_without_redirect():
    """Test authorization without providing a redirect_uri parameter."""
    print("🔍 Testing Authorization WITHOUT redirect_uri...")
    
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    if not client_id:
        print("❌ FAMILYSEARCH_CLIENT_ID not set in environment")
        return None
    auth_base_url = os.getenv('FAMILYSEARCH_AUTH_BASE_URL', 'https://identbeta.familysearch.org/cis-web/oauth2/v3')
    
    # Construct authorization URL without redirect_uri
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'scope': 'openid profile email',
        'state': 'test_state_123'
    }
    
    auth_url = f"{auth_base_url}/authorization?{urllib.parse.urlencode(params)}"
    
    print(f"Authorization URL (no redirect_uri): {auth_url}")
    print("✅ Authorization URL constructed without redirect_uri")
    
    return auth_url

def test_authorization_with_localhost():
    """Test authorization with localhost redirect URI."""
    print("\n🔍 Testing Authorization WITH localhost redirect_uri...")
    
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    if not client_id:
        print("❌ FAMILYSEARCH_CLIENT_ID not set in environment")
        return None
    auth_base_url = os.getenv('FAMILYSEARCH_AUTH_BASE_URL', 'https://identbeta.familysearch.org/cis-web/oauth2/v3')
    
    # Construct authorization URL with localhost redirect
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': 'http://localhost:8001/oauth/callback',
        'scope': 'openid profile email',
        'state': 'test_state_123'
    }
    
    auth_url = f"{auth_base_url}/authorization?{urllib.parse.urlencode(params)}"
    
    print(f"Authorization URL (with localhost): {auth_url}")
    print("✅ Authorization URL constructed with localhost redirect")
    
    return auth_url

def test_unauthenticated_session():
    """Test unauthenticated session grant type."""
    print("\n🔍 Testing Unauthenticated Session Grant...")
    
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    if not client_id:
        print("❌ FAMILYSEARCH_CLIENT_ID not set in environment")
        return None, None
    token_url = os.getenv('FAMILYSEARCH_TOKEN_URL', 'https://identbeta.familysearch.org/cis-web/oauth2/v3/token')
    
    # Test unauthenticated session grant
    data = {
        'grant_type': 'unauthenticated_session',
        'client_id': client_id
    }
    
    print(f"Token URL: {token_url}")
    print(f"Request data: {data}")
    print("✅ Unauthenticated session request prepared")
    
    return token_url, data

def test_password_grant():
    """Test password grant type (if credentials are available)."""
    print("\n🔍 Testing Password Grant...")
    
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    if not client_id:
        print("❌ FAMILYSEARCH_CLIENT_ID not set in environment")
        return None, None
    username = os.getenv('FAMILYSEARCH_USERNAME')
    password = os.getenv('FAMILYSEARCH_PASSWORD')
    token_url = os.getenv('FAMILYSEARCH_TOKEN_URL', 'https://identbeta.familysearch.org/cis-web/oauth2/v3/token')
    
    if not username or not password:
        print("⚠️  Username/password not provided in environment variables")
        print("   Set FAMILYSEARCH_USERNAME and FAMILYSEARCH_PASSWORD to test password grant")
        return None, None
    
    data = {
        'grant_type': 'password',
        'client_id': client_id,
        'username': username,
        'password': password
    }
    
    print(f"Token URL: {token_url}")
    print(f"Request data: {dict(data, password='***')}")
    print("✅ Password grant request prepared")
    
    return token_url, data

def test_endpoint_connectivity():
    """Test basic connectivity to FamilySearch endpoints."""
    print("\n🔍 Testing Endpoint Connectivity...")
    
    endpoints = [
        "https://api.familysearch.org/platform",
        "https://identbeta.familysearch.org/cis-web/oauth2/v3/authorization",
        "https://identbeta.familysearch.org/cis-web/oauth2/v3/token"
    ]
    
    for endpoint in endpoints:
        try:
            response = httpx.get(endpoint, timeout=10)
            print(f"✅ {endpoint}: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.text[:100]}...")
        except Exception as e:
            print(f"❌ {endpoint}: Connection failed - {e}")
    
    return True

def test_curl_commands():
    """Generate test curl commands for manual testing."""
    print("\n🔍 Generating Test Commands...")
    
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    if not client_id:
        print("❌ FAMILYSEARCH_CLIENT_ID not set in environment")
        return None
    auth_base_url = os.getenv('FAMILYSEARCH_AUTH_BASE_URL', 'https://identbeta.familysearch.org/cis-web/oauth2/v3')
    token_url = os.getenv('FAMILYSEARCH_TOKEN_URL', 'https://identbeta.familysearch.org/cis-web/oauth2/v3/token')
    
    print("📋 Test 1: Authorization WITHOUT redirect_uri")
    auth_params_no_redirect = {
        'response_type': 'code',
        'client_id': client_id,
        'scope': 'openid profile email',
        'state': 'test_state_123'
    }
    print(f"curl \"{auth_base_url}/authorization?{urllib.parse.urlencode(auth_params_no_redirect)}\"")
    
    print("\n📋 Test 2: Authorization WITH localhost redirect_uri")
    auth_params_with_redirect = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': 'http://localhost:8001/oauth/callback',
        'scope': 'openid profile email',
        'state': 'test_state_123'
    }
    print(f"curl \"{auth_base_url}/authorization?{urllib.parse.urlencode(auth_params_with_redirect)}\"")
    
    print("\n📋 Test 3: Unauthenticated Session Token")
    print(f"curl -X POST \"{token_url}\" \\")
    print(f"  -H \"Content-Type: application/x-www-form-urlencoded\" \\")
    print(f"  -d \"grant_type=unauthenticated_session&client_id={client_id}\"")
    
    print("\n📋 Test 4: Password Grant Token (if credentials available)")
    print(f"curl -X POST \"{token_url}\" \\")
    print(f"  -H \"Content-Type: application/x-www-form-urlencoded\" \\")
    print(f"  -d \"grant_type=password&client_id={client_id}&username=YOUR_USERNAME&password=YOUR_PASSWORD\"")
    
    return True

def main():
    """Run all authentication tests."""
    print("🚀 FamilySearch Authentication Options Test")
    print("=" * 60)
    
    tests = [
        test_authorization_without_redirect,
        test_authorization_with_localhost,
        test_unauthenticated_session,
        test_password_grant,
        test_endpoint_connectivity,
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
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    print("\n📝 Manual Testing Instructions:")
    print("1. Try the authorization URLs in your browser")
    print("2. Use the curl commands to test token endpoints")
    print("3. Check if FamilySearch accepts requests without pre-registered redirect URIs")
    print("4. Test if unauthenticated sessions work for basic API access")
    
    print("\n💡 Key Questions to Answer:")
    print("- Does FamilySearch accept authorization requests without redirect_uri?")
    print("- Does FamilySearch accept localhost redirect URIs without pre-registration?")
    print("- Can we use unauthenticated sessions for basic API access?")
    print("- What error messages do we get for different approaches?")

if __name__ == "__main__":
    main() 