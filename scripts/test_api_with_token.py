#!/usr/bin/env python3
"""
Test different FamilySearch API endpoints with access token
"""

import os
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_endpoints(access_token):
    """Test different API endpoints with the access token"""
    
    if not access_token:
        print("❌ No access token provided")
        return False
    
    print("🔍 Testing FamilySearch API Endpoints")
    print("=" * 50)
    print(f"Token: {access_token[:20]}...")
    print()
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/x-gedcomx-v1+json',
        'User-Agent': os.getenv('CUSTOM_USER_AGENT', 'FS-Agent-Test/1.0')
    }
    
    # Test different endpoints
    endpoints = [
        {
            'name': 'Current User (Profile)',
            'url': 'https://api.familysearch.org/platform/users/current',
            'description': 'Get current user profile'
        },
        {
            'name': 'Current User (Tree)',
            'url': 'https://api.familysearch.org/platform/tree/current-person',
            'description': 'Get current person in tree'
        },
        {
            'name': 'Collections',
            'url': 'https://api.familysearch.org/platform/collections',
            'description': 'Get available collections'
        },
        {
            'name': 'Places Search',
            'url': 'https://api.familysearch.org/platform/places/search?q=New%20York&count=5',
            'description': 'Search for places'
        },
        {
            'name': 'Person Search',
            'url': 'https://api.familysearch.org/platform/tree/persons?q=John%20Smith&count=5',
            'description': 'Search for persons'
        },
        {
            'name': 'Records Search',
            'url': 'https://api.familysearch.org/platform/records/search?q=John%20Smith&count=5',
            'description': 'Search for records'
        }
    ]
    
    results = []
    
    with httpx.Client() as client:
        for endpoint in endpoints:
            print(f"🔍 Testing: {endpoint['name']}")
            print(f"URL: {endpoint['url']}")
            
            try:
                response = client.get(endpoint['url'], headers=headers)
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ Success!")
                    data = response.json()
                    print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not JSON'}")
                elif response.status_code == 401:
                    print("❌ Unauthorized - Token might be invalid or expired")
                elif response.status_code == 403:
                    print("❌ Forbidden - Token valid but no permission")
                elif response.status_code == 404:
                    print("❌ Not Found - Endpoint doesn't exist")
                else:
                    print(f"❌ Error: {response.status_code}")
                    print(f"Response: {response.text[:200]}...")
                
                results.append({
                    'name': endpoint['name'],
                    'url': endpoint['url'],
                    'status': response.status_code,
                    'success': response.status_code == 200
                })
                
            except Exception as e:
                print(f"❌ Error: {e}")
                results.append({
                    'name': endpoint['name'],
                    'url': endpoint['url'],
                    'status': 'Error',
                    'success': False
                })
            
            print("-" * 40)
    
    # Summary
    print("\n📊 API Test Summary:")
    print("=" * 30)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Successful: {len(successful)}")
    for result in successful:
        print(f"  - {result['name']}")
    
    print(f"❌ Failed: {len(failed)}")
    for result in failed:
        print(f"  - {result['name']} ({result['status']})")
    
    return len(successful) > 0

def test_token_info(access_token):
    """Test getting token information"""
    
    print("\n🔍 Testing Token Information")
    print("=" * 30)
    
    # Try to decode or validate the token
    print(f"Token Type: family_search")
    print(f"Token Length: {len(access_token)} characters")
    print(f"Token Format: {access_token[:10]}...{access_token[-10:]}")
    
    # Test if token is still valid by trying a simple endpoint
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/x-gedcomx-v1+json',
        'User-Agent': os.getenv('CUSTOM_USER_AGENT', 'FS-Agent-Test/1.0')
    }
    
    try:
        with httpx.Client() as client:
            # Try the collections endpoint which should work
            response = client.get('https://api.familysearch.org/platform/collections', headers=headers)
            
            if response.status_code == 200:
                print("✅ Token appears to be valid")
                data = response.json()
                print(f"Collections available: {len(data.get('collections', []))}")
            else:
                print(f"❌ Token validation failed: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
    except Exception as e:
        print(f"❌ Error validating token: {e}")

if __name__ == "__main__":
    # Get token from command line or environment
    import sys
    
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        token = input("Enter access token: ").strip()
    
    if not token:
        print("❌ No token provided")
        sys.exit(1)
    
    print("🚀 FamilySearch API Token Test")
    print("=" * 50)
    
    # Test token info
    test_token_info(token)
    
    # Test API endpoints
    test_api_endpoints(token) 