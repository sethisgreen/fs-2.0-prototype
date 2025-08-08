#!/usr/bin/env python3
"""
Test alternative FamilySearch API endpoints and different API versions
"""

import os
import httpx
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_alternative_endpoints(access_token):
    """Test alternative endpoints and API versions"""
    
    if not access_token:
        print("❌ No access token provided")
        return False
    
    print("🔍 Testing Alternative FamilySearch API Endpoints")
    print("=" * 60)
    print(f"Token: {access_token[:20]}...")
    print()
    
    # Standard headers
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/x-gedcomx-v1+json',
        'User-Agent': os.getenv('CUSTOM_USER_AGENT', 'FS-Agent-Test/1.0')
    }
    
    # Alternative endpoints to test
    test_cases = [
        # Alternative user endpoints
        {
            'name': 'User Profile (v2)',
            'url': 'https://api.familysearch.org/platform/v2/users/current',
            'headers': headers,
            'category': 'User'
        },
        {
            'name': 'User Profile (beta)',
            'url': 'https://api.familysearch.org/platform/beta/users/current',
            'headers': headers,
            'category': 'User'
        },
        
        # Alternative tree endpoints
        {
            'name': 'Tree Root',
            'url': 'https://api.familysearch.org/platform/tree',
            'headers': headers,
            'category': 'Tree'
        },
        {
            'name': 'Tree Persons',
            'url': 'https://api.familysearch.org/platform/tree/persons',
            'headers': headers,
            'category': 'Tree'
        },
        
        # Alternative records endpoints
        {
            'name': 'Records Root',
            'url': 'https://api.familysearch.org/platform/records',
            'headers': headers,
            'category': 'Records'
        },
        {
            'name': 'Records Search (v2)',
            'url': 'https://api.familysearch.org/platform/v2/records/search',
            'headers': headers,
            'category': 'Records'
        },
        
        # Alternative places endpoints
        {
            'name': 'Places Root',
            'url': 'https://api.familysearch.org/platform/places',
            'headers': headers,
            'category': 'Places'
        },
        {
            'name': 'Places Search (v2)',
            'url': 'https://api.familysearch.org/platform/v2/places/search?q=New%20York',
            'headers': headers,
            'category': 'Places'
        },
        
        # Different Accept headers
        {
            'name': 'Places Search (JSON)',
            'url': 'https://api.familysearch.org/platform/places/search?q=New%20York',
            'headers': {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'User-Agent': os.getenv('CUSTOM_USER_AGENT', 'FS-Agent-Test/1.0')
            },
            'category': 'Places'
        },
        {
            'name': 'Places Search (XML)',
            'url': 'https://api.familysearch.org/platform/places/search?q=New%20York',
            'headers': {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/xml',
                'User-Agent': os.getenv('CUSTOM_USER_AGENT', 'FS-Agent-Test/1.0')
            },
            'category': 'Places'
        },
        
        # Discovery endpoints
        {
            'name': 'Platform Discovery',
            'url': 'https://api.familysearch.org/platform',
            'headers': headers,
            'category': 'Discovery'
        },
        {
            'name': 'API Discovery',
            'url': 'https://api.familysearch.org',
            'headers': headers,
            'category': 'Discovery'
        },
        
        # Collections with different Accept headers
        {
            'name': 'Collections (JSON)',
            'url': 'https://api.familysearch.org/platform/collections',
            'headers': {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'User-Agent': os.getenv('CUSTOM_USER_AGENT', 'FS-Agent-Test/1.0')
            },
            'category': 'Collections'
        },
        
        # Test specific collection endpoints
        {
            'name': 'Tree Collection Details',
            'url': 'https://api.familysearch.org/platform/collections/tree',
            'headers': headers,
            'category': 'Collections'
        },
        {
            'name': 'Records Collection Details',
            'url': 'https://api.familysearch.org/platform/collections/records',
            'headers': headers,
            'category': 'Collections'
        },
        {
            'name': 'Places Collection Details',
            'url': 'https://api.familysearch.org/platform/collections/places',
            'headers': headers,
            'category': 'Collections'
        }
    ]
    
    results = {}
    
    with httpx.Client() as client:
        for test_case in test_cases:
            category = test_case['category']
            if category not in results:
                results[category] = []
            
            print(f"🔍 Testing: {test_case['name']} ({category})")
            print(f"URL: {test_case['url']}")
            print(f"Accept: {test_case['headers'].get('Accept', 'N/A')}")
            
            try:
                response = client.get(test_case['url'], headers=test_case['headers'])
                
                print(f"Status: {response.status_code}")
                print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
                
                if response.status_code == 200:
                    print("✅ Success!")
                    try:
                        data = response.json()
                        if isinstance(data, dict):
                            print(f"Response keys: {list(data.keys())}")
                            if 'collections' in data:
                                print(f"Collections count: {len(data['collections'])}")
                            elif 'links' in data:
                                print(f"Available links: {list(data['links'].keys())}")
                        else:
                            print("Response: JSON object")
                    except json.JSONDecodeError:
                        print("Response: Not JSON")
                        print(f"Response preview: {response.text[:200]}...")
                        
                elif response.status_code == 301:
                    print("🔄 Redirect")
                    print(f"Location: {response.headers.get('location', 'N/A')}")
                elif response.status_code == 401:
                    print("❌ Unauthorized")
                elif response.status_code == 403:
                    print("❌ Forbidden")
                elif response.status_code == 404:
                    print("❌ Not Found")
                elif response.status_code == 406:
                    print("❌ Not Acceptable")
                elif response.status_code == 204:
                    print("✅ No Content (successful but empty)")
                else:
                    print(f"❌ Error: {response.status_code}")
                    print(f"Response: {response.text[:200]}...")
                
                results[category].append({
                    'name': test_case['name'],
                    'url': test_case['url'],
                    'status': response.status_code,
                    'success': response.status_code in [200, 204],
                    'content_type': response.headers.get('content-type', 'N/A')
                })
                
            except Exception as e:
                print(f"❌ Error: {e}")
                results[category].append({
                    'name': test_case['name'],
                    'url': test_case['url'],
                    'status': 'Error',
                    'success': False,
                    'content_type': 'N/A'
                })
            
            print("-" * 50)
    
    # Summary by category
    print("\n📊 API Test Summary by Category:")
    print("=" * 50)
    
    for category, endpoints in results.items():
        successful = [e for e in endpoints if e['success']]
        failed = [e for e in endpoints if not e['success']]
        
        print(f"\n📂 {category}:")
        print(f"  ✅ Successful: {len(successful)}/{len(endpoints)}")
        for endpoint in successful:
            print(f"    - {endpoint['name']} ({endpoint['status']})")
        
        if failed:
            print(f"  ❌ Failed: {len(failed)}/{len(endpoints)}")
            for endpoint in failed:
                print(f"    - {endpoint['name']} ({endpoint['status']})")
    
    # Overall summary
    total_successful = sum(len([e for e in endpoints if e['success']]) for endpoints in results.values())
    total_endpoints = sum(len(endpoints) for endpoints in results.values())
    
    print(f"\n🎯 Overall Summary:")
    print(f"  ✅ Successful: {total_successful}/{total_endpoints}")
    print(f"  ❌ Failed: {total_endpoints - total_successful}/{total_endpoints}")
    
    return total_successful > 0

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        token = input("Enter access token: ").strip()
    
    if not token:
        print("❌ No token provided")
        sys.exit(1)
    
    test_alternative_endpoints(token) 