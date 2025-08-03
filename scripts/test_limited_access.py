#!/usr/bin/env python3
"""
Test limited FamilySearch API access without authentication.

This script tests endpoints that support unauthenticated sessions
to see if we can access basic FamilySearch data without OAuth.
"""

import os
import sys
import httpx
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_places_endpoint():
    """Test the Places endpoint which supports unauthenticated access."""
    print("🔍 Testing Places Endpoint (Unauthenticated)...")
    
    # Test places search endpoint
    places_url = "https://api.familysearch.org/platform/places/search"
    
    try:
        async with httpx.AsyncClient() as client:
            # Test with a simple search
            params = {
                'q': 'New York',
                'count': 5
            }
            response = await client.get(places_url, params=params, timeout=30)
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Body: {response.text[:500]}...")
            
            if response.status_code == 200:
                print("✅ Places endpoint accessible without authentication!")
                return True
            else:
                print(f"❌ Places endpoint failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error testing places endpoint: {e}")
        return False

async def test_date_authority():
    """Test the Date Authority endpoint."""
    print("\n🔍 Testing Date Authority Endpoint...")
    
    date_url = "https://api.familysearch.org/platform/dates"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(date_url, timeout=30)
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text[:500]}...")
            
            if response.status_code == 200:
                print("✅ Date authority accessible without authentication!")
                return True
            else:
                print(f"❌ Date authority failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error testing date authority: {e}")
        return False

async def test_person_search():
    """Test the Person Search endpoint."""
    print("\n🔍 Testing Person Search Endpoint...")
    
    search_url = "https://api.familysearch.org/platform/tree/persons"
    
    try:
        async with httpx.AsyncClient() as client:
            # Test with a simple search
            params = {
                'q': 'John Smith',
                'count': 5
            }
            response = await client.get(search_url, params=params, timeout=30)
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text[:500]}...")
            
            if response.status_code == 200:
                print("✅ Person search accessible without authentication!")
                return True
            else:
                print(f"❌ Person search failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error testing person search: {e}")
        return False

async def test_api_root():
    """Test the API root endpoint."""
    print("\n🔍 Testing API Root Endpoint...")
    
    root_url = "https://api.familysearch.org/platform"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(root_url, timeout=30)
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text[:500]}...")
            
            if response.status_code == 200:
                print("✅ API root accessible!")
                return True
            else:
                print(f"❌ API root failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error testing API root: {e}")
        return False

async def test_unauthenticated_session_token():
    """Test getting an unauthenticated session token."""
    print("\n🔍 Testing Unauthenticated Session Token...")
    
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    if not client_id:
        print("❌ FAMILYSEARCH_CLIENT_ID not set in environment")
        return None
    token_url = "https://identbeta.familysearch.org/cis-web/oauth2/v3/token"
    
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
                print("✅ Unauthenticated session token obtained!")
                # Parse the token response
                try:
                    token_data = response.json()
                    if 'access_token' in token_data:
                        print(f"✅ Access token: {token_data['access_token'][:20]}...")
                        return token_data['access_token']
                except:
                    print("⚠️  Could not parse token response")
                return True
            else:
                print(f"❌ Unauthenticated session failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error testing unauthenticated session: {e}")
        return False

async def test_api_with_token(token):
    """Test API access with a token."""
    print(f"\n🔍 Testing API Access with Token...")
    
    api_url = "https://api.familysearch.org/platform"
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/x-gedcomx-v1+json'
            }
            response = await client.get(api_url, headers=headers, timeout=30)
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text[:500]}...")
            
            if response.status_code == 200:
                print("✅ API accessible with token!")
                return True
            else:
                print(f"❌ API access failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error testing API with token: {e}")
        return False

async def main():
    """Run all limited access tests."""
    print("🚀 FamilySearch Limited Access Test")
    print("=" * 60)
    
    tests = [
        test_api_root,
        test_places_endpoint,
        test_date_authority,
        test_person_search,
        test_unauthenticated_session_token
    ]
    
    passed = 0
    total = len(tests)
    token = None
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
                if isinstance(result, str):  # Token returned
                    token = result
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    # If we got a token, test API access with it
    if token:
        await test_api_with_token(token)
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    print("\n💡 Key Findings:")
    print("- Some FamilySearch endpoints may be accessible without authentication")
    print("- Unauthenticated sessions may provide limited API access")
    print("- This could be useful for basic functionality without OAuth setup")
    
    print("\n📝 Next Steps:")
    print("1. Check which endpoints work without authentication")
    print("2. Test if unauthenticated sessions provide sufficient access")
    print("3. Consider if limited access meets your needs")
    print("4. If not, proceed with OAuth setup for full access")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 