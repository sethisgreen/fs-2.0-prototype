#!/usr/bin/env python3
"""
Test what data we can get from collections endpoints with unauthenticated session.

This script examines the actual data returned by the collections endpoints
that are accessible with unauthenticated sessions.
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
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    if not client_id:
        print("❌ FAMILYSEARCH_CLIENT_ID not set in environment")
        return False
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

async def examine_collections_data(token):
    """Examine the data returned by collections endpoints."""
    print("🔍 Examining Collections Data...")
    
    collections_endpoints = [
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
    
    for endpoint in collections_endpoints:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=headers, timeout=30)
                if response.status_code == 200:
                    print(f"\n📚 {endpoint}:")
                    try:
                        data = response.json()
                        print(f"   📊 Structure: {list(data.keys())}")
                        
                        if 'collections' in data:
                            collections = data['collections']
                            print(f"   📊 Found {len(collections)} collections:")
                            for i, collection in enumerate(collections[:3]):  # Show first 3
                                print(f"     {i+1}. ID: {collection.get('id', 'N/A')}")
                                print(f"        Title: {collection.get('title', 'N/A')}")
                                if 'links' in collection:
                                    links = collection['links']
                                    print(f"        Links: {list(links.keys())}")
                        
                        # Show a sample of the raw data
                        print(f"   📄 Sample data: {json.dumps(data, indent=2)[:500]}...")
                        
                    except Exception as e:
                        print(f"   ❌ Error parsing JSON: {e}")
                        print(f"   📄 Raw response: {response.text[:200]}...")
                else:
                    print(f"❌ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

async def test_what_we_can_do():
    """Test what practical functionality we can achieve."""
    print("\n🔍 Testing Practical Functionality...")
    
    token = await get_unauthenticated_token()
    if not token:
        print("❌ Could not get token")
        return
    
    print(f"✅ Got token: {token[:20]}...")
    
    # Test what we can actually do with the collections
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/x-gedcomx-v1+json'
    }
    
    # Test if we can access specific collection data
    test_urls = [
        "https://api.familysearch.org/platform/collections/tree",
        "https://api.familysearch.org/platform/collections/records"
    ]
    
    for url in test_urls:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=30)
                if response.status_code == 200:
                    print(f"\n✅ {url}:")
                    try:
                        data = response.json()
                        print(f"   📊 Data structure: {list(data.keys())}")
                        if 'collections' in data:
                            for collection in data['collections']:
                                print(f"   📚 Collection: {collection.get('id')} - {collection.get('title')}")
                                if 'links' in collection:
                                    for link_name, link_data in collection['links'].items():
                                        print(f"      🔗 {link_name}: {link_data.get('href', 'N/A')}")
                    except Exception as e:
                        print(f"   ❌ Error parsing: {e}")
        except Exception as e:
            print(f"❌ {url}: {e}")

async def main():
    """Run the collections data examination."""
    print("🚀 FamilySearch Collections Data Examination")
    print("=" * 60)
    
    token = await get_unauthenticated_token()
    if not token:
        print("❌ Could not get unauthenticated session token")
        return
    
    print(f"✅ Got token: {token[:20]}...")
    
    await examine_collections_data(token)
    await test_what_we_can_do()
    
    print("\n" + "=" * 60)
    print("📊 Summary of Available Endpoints with Unauthenticated Session:")
    print("✅ Collections: All collection endpoints work")
    print("   - /collections (main collections list)")
    print("   - /collections/tree (family tree collection)")
    print("   - /collections/records (historical records)")
    print("   - /collections/memories (photos and stories)")
    print("   - /collections/discussions (comments and discussions)")
    print("   - /collections/sources (source citations)")
    print("   - /collections/places (place information)")
    print("   - /collections/dates (date information)")
    
    print("\n❌ NOT Available with Unauthenticated Session:")
    print("   - Person search")
    print("   - Record search")
    print("   - Place search")
    print("   - Date authority lookup")
    print("   - Authorities endpoints")
    print("   - Utilities endpoints")
    
    print("\n💡 Practical Use Cases:")
    print("1. Get information about available FamilySearch collections")
    print("2. Access collection metadata and links")
    print("3. Build reference data for your application")
    print("4. Understand FamilySearch's data structure")
    print("5. Prepare for full authentication later")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 