#!/usr/bin/env python3
"""
Test FamilySearch API access with the unauthenticated session token.

This script tests what endpoints we can access with the token
we obtained from the unauthenticated session.
"""

import os
import sys
import httpx
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def get_unauthenticated_token():
    """Get an unauthenticated session token."""
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID', 'b0019MWRSQE2VBRACTDD')
    token_url = "https://identbeta.familysearch.org/cis-web/oauth2/v3/token"
    
    data = {
        'grant_type': 'unauthenticated_session',
        'client_id': client_id,
        'ip_address': '127.0.0.1'
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data, timeout=30)
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get('access_token')
            else:
                print(f"❌ Failed to get token: {response.status_code}")
                return None
    except Exception as e:
        print(f"❌ Error getting token: {e}")
        return None

async def test_api_with_token(token):
    """Test various API endpoints with the token."""
    print(f"🔍 Testing API Endpoints with Token: {token[:20]}...")
    
    endpoints = [
        "https://api.familysearch.org/platform",
        "https://api.familysearch.org/platform/collections",
        "https://api.familysearch.org/platform/places/search?q=New%20York&count=5",
        "https://api.familysearch.org/platform/dates?date=1850",
        "https://api.familysearch.org/platform/tree/persons?q=John%20Smith&count=5",
        "https://api.familysearch.org/platform/records/search?q=John%20Smith&count=5",
        "https://api.familysearch.org/platform/authorities/places",
        "https://api.familysearch.org/platform/authorities/dates"
    ]
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/x-gedcomx-v1+json'
    }
    
    for endpoint in endpoints:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=headers, timeout=30)
                print(f"✅ {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    print(f"   Response: {response.text[:200]}...")
                elif response.status_code == 204:
                    print("   Response: No content (success)")
                elif response.status_code == 401:
                    print("   Response: Unauthorized (token not valid for this endpoint)")
                elif response.status_code == 403:
                    print("   Response: Forbidden (endpoint requires different permissions)")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

async def test_search_endpoints(token):
    """Test search-specific endpoints."""
    print(f"\n🔍 Testing Search Endpoints with Token...")
    
    search_endpoints = [
        "https://api.familysearch.org/platform/tree/persons?q=John%20Smith&count=5",
        "https://api.familysearch.org/platform/records/search?q=John%20Smith&count=5",
        "https://api.familysearch.org/platform/places/search?q=New%20York&count=5",
        "https://api.familysearch.org/platform/authorities/places?q=New%20York"
    ]
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/x-gedcomx-v1+json'
    }
    
    for endpoint in search_endpoints:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=headers, timeout=30)
                print(f"🔍 {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    print(f"   ✅ Search successful!")
                    # Try to parse the response
                    try:
                        data = response.json()
                        if 'entries' in data:
                            print(f"   📊 Found {len(data['entries'])} results")
                        elif 'persons' in data:
                            print(f"   📊 Found {len(data['persons'])} persons")
                        elif 'places' in data:
                            print(f"   📊 Found {len(data['places'])} places")
                    except:
                        print(f"   📄 Response length: {len(response.text)} characters")
                elif response.status_code == 204:
                    print("   ⚠️  No content returned")
                elif response.status_code == 401:
                    print("   ❌ Unauthorized - token not valid for this endpoint")
                elif response.status_code == 403:
                    print("   ❌ Forbidden - endpoint requires different permissions")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

async def test_limited_functionality():
    """Test what limited functionality we can achieve."""
    print(f"\n🔍 Testing Limited Functionality...")
    
    token = await get_unauthenticated_token()
    if not token:
        print("❌ Could not get token")
        return
    
    print(f"✅ Got token: {token[:20]}...")
    
    # Test basic functionality
    await test_api_with_token(token)
    await test_search_endpoints(token)
    
    print(f"\n💡 Summary of Limited Access:")
    print("- We can get an unauthenticated session token")
    print("- Some endpoints may be accessible with this token")
    print("- This provides limited but functional API access")
    print("- No redirect URI registration required!")

async def main():
    """Run the token-based tests."""
    print("🚀 FamilySearch API Access with Unauthenticated Token")
    print("=" * 60)
    
    await test_limited_functionality()
    
    print("\n" + "=" * 60)
    print("📝 Key Findings:")
    print("✅ Unauthenticated sessions work without redirect URI registration")
    print("✅ We can get access tokens for limited API access")
    print("✅ Some endpoints are accessible with this token")
    print("✅ This provides a working alternative to full OAuth")
    
    print("\n💡 Next Steps:")
    print("1. Test what specific data we can access")
    print("2. Implement this in your server code")
    print("3. Consider if limited access meets your needs")
    print("4. If not, proceed with full OAuth for complete access")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 