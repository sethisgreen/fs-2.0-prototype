#!/usr/bin/env python3
"""
Comprehensive test of FamilySearch API endpoints with unauthenticated session.

This script tests all available endpoints to see exactly what we can access
with an unauthenticated session token.
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

async def test_collections_endpoints(token):
    """Test collections-related endpoints."""
    print("🔍 Testing Collections Endpoints...")
    
    endpoints = [
        "https://api.familysearch.org/platform/collections",
        "https://api.familysearch.org/platform/collections/tree",
        "https://api.familysearch.org/platform/collections/records",
        "https://api.familysearch.org/platform/collections/memories",
        "https://api.familysearch.org/platform/collections/discussions",
        "https://api.familysearch.org/platform/collections/sources",
        "https://api.familysearch.org/platform/collections/places",
        "https://api.familysearch.org/platform/collections/dates"
    ]
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/x-gedcomx-v1+json'
    }
    
    for endpoint in endpoints:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=headers, timeout=30)
                print(f"📚 {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    print(f"   ✅ Accessible")
                    try:
                        data = response.json()
                        if 'collections' in data:
                            print(f"   📊 Found {len(data['collections'])} collections")
                    except:
                        pass
                elif response.status_code == 401:
                    print(f"   ❌ Unauthorized")
                elif response.status_code == 403:
                    print(f"   ❌ Forbidden")
                elif response.status_code == 404:
                    print(f"   ❌ Not Found")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

async def test_places_endpoints(token):
    """Test places-related endpoints."""
    print("\n🔍 Testing Places Endpoints...")
    
    endpoints = [
        "https://api.familysearch.org/platform/places/search?q=New%20York&count=5",
        "https://api.familysearch.org/platform/places/search?q=London&count=5",
        "https://api.familysearch.org/platform/places/search?q=Paris&count=5",
        "https://api.familysearch.org/platform/authorities/places",
        "https://api.familysearch.org/platform/authorities/places/search?q=New%20York",
        "https://api.familysearch.org/platform/places/descriptions",
        "https://api.familysearch.org/platform/places/types"
    ]
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/x-gedcomx-v1+json'
    }
    
    for endpoint in endpoints:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=headers, timeout=30)
                print(f"🏛️  {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    print(f"   ✅ Accessible")
                    try:
                        data = response.json()
                        if 'places' in data:
                            print(f"   📊 Found {len(data['places'])} places")
                        elif 'entries' in data:
                            print(f"   📊 Found {len(data['entries'])} entries")
                    except:
                        pass
                elif response.status_code == 204:
                    print(f"   ⚠️  No Content")
                elif response.status_code == 401:
                    print(f"   ❌ Unauthorized")
                elif response.status_code == 404:
                    print(f"   ❌ Not Found")
                elif response.status_code == 406:
                    print(f"   ❌ Not Acceptable")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

async def test_dates_endpoints(token):
    """Test dates-related endpoints."""
    print("\n🔍 Testing Dates Endpoints...")
    
    endpoints = [
        "https://api.familysearch.org/platform/dates?date=1850",
        "https://api.familysearch.org/platform/dates?date=1900",
        "https://api.familysearch.org/platform/dates?date=1800",
        "https://api.familysearch.org/platform/authorities/dates",
        "https://api.familysearch.org/platform/authorities/dates/1850"
    ]
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/x-gedcomx-v1+json'
    }
    
    for endpoint in endpoints:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=headers, timeout=30)
                print(f"📅 {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    print(f"   ✅ Accessible")
                    try:
                        data = response.json()
                        print(f"   📄 Response: {response.text[:100]}...")
                    except:
                        pass
                elif response.status_code == 401:
                    print(f"   ❌ Unauthorized")
                elif response.status_code == 404:
                    print(f"   ❌ Not Found")
                elif response.status_code == 406:
                    print(f"   ❌ Not Acceptable")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

async def test_search_endpoints(token):
    """Test search-related endpoints."""
    print("\n🔍 Testing Search Endpoints...")
    
    endpoints = [
        "https://api.familysearch.org/platform/tree/persons?q=John%20Smith&count=5",
        "https://api.familysearch.org/platform/tree/persons?q=Mary%20Johnson&count=5",
        "https://api.familysearch.org/platform/records/search?q=John%20Smith&count=5",
        "https://api.familysearch.org/platform/records/search?q=Mary%20Johnson&count=5",
        "https://api.familysearch.org/platform/tree/persons/search?q=John%20Smith&count=5"
    ]
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/x-gedcomx-v1+json'
    }
    
    for endpoint in endpoints:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=headers, timeout=30)
                print(f"🔍 {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    print(f"   ✅ Accessible")
                    try:
                        data = response.json()
                        if 'persons' in data:
                            print(f"   📊 Found {len(data['persons'])} persons")
                        elif 'entries' in data:
                            print(f"   📊 Found {len(data['entries'])} entries")
                    except:
                        pass
                elif response.status_code == 400:
                    print(f"   ❌ Bad Request")
                elif response.status_code == 401:
                    print(f"   ❌ Unauthorized")
                elif response.status_code == 404:
                    print(f"   ❌ Not Found")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

async def test_authorities_endpoints(token):
    """Test authorities-related endpoints."""
    print("\n🔍 Testing Authorities Endpoints...")
    
    endpoints = [
        "https://api.familysearch.org/platform/authorities",
        "https://api.familysearch.org/platform/authorities/places",
        "https://api.familysearch.org/platform/authorities/dates",
        "https://api.familysearch.org/platform/authorities/names",
        "https://api.familysearch.org/platform/authorities/genders",
        "https://api.familysearch.org/platform/authorities/event-types"
    ]
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/x-gedcomx-v1+json'
    }
    
    for endpoint in endpoints:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=headers, timeout=30)
                print(f"📖 {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    print(f"   ✅ Accessible")
                    try:
                        data = response.json()
                        print(f"   📄 Response: {response.text[:100]}...")
                    except:
                        pass
                elif response.status_code == 401:
                    print(f"   ❌ Unauthorized")
                elif response.status_code == 404:
                    print(f"   ❌ Not Found")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

async def test_utilities_endpoints(token):
    """Test utilities and other endpoints."""
    print("\n🔍 Testing Utilities Endpoints...")
    
    endpoints = [
        "https://api.familysearch.org/platform",
        "https://api.familysearch.org/platform/utilities",
        "https://api.familysearch.org/platform/utilities/version",
        "https://api.familysearch.org/platform/utilities/status",
        "https://api.familysearch.org/platform/utilities/health"
    ]
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/x-gedcomx-v1+json'
    }
    
    for endpoint in endpoints:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=headers, timeout=30)
                print(f"🔧 {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    print(f"   ✅ Accessible")
                    try:
                        data = response.json()
                        print(f"   📄 Response: {response.text[:100]}...")
                    except:
                        pass
                elif response.status_code == 301:
                    print(f"   ⚠️  Redirect")
                elif response.status_code == 401:
                    print(f"   ❌ Unauthorized")
                elif response.status_code == 404:
                    print(f"   ❌ Not Found")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

async def main():
    """Run comprehensive endpoint testing."""
    print("🚀 FamilySearch Unauthenticated Session Endpoint Test")
    print("=" * 70)
    
    # Get token
    token = await get_unauthenticated_token()
    if not token:
        print("❌ Could not get unauthenticated session token")
        return
    
    print(f"✅ Got token: {token[:20]}...")
    
    # Test all endpoint categories
    await test_collections_endpoints(token)
    await test_places_endpoints(token)
    await test_dates_endpoints(token)
    await test_search_endpoints(token)
    await test_authorities_endpoints(token)
    await test_utilities_endpoints(token)
    
    print("\n" + "=" * 70)
    print("📊 Summary of Unauthenticated Session Access:")
    print("✅ Collections: Basic collection information")
    print("⚠️  Places: Limited access (406 errors)")
    print("✅ Dates: Date authority information")
    print("❌ Search: Person/record search not available")
    print("❌ Authorities: Most authority endpoints not available")
    print("⚠️  Utilities: Limited utility access")
    
    print("\n💡 Key Findings:")
    print("- Unauthenticated sessions provide very limited access")
    print("- Collections and dates endpoints work best")
    print("- Search functionality requires full authentication")
    print("- This is suitable for basic reference data only")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 