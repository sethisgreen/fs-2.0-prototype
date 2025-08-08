#!/usr/bin/env python3
"""
Comprehensive test of FamilySearch authenticated endpoints
"""

import os
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_authenticated_endpoints(access_token):
    """Test all available authenticated endpoints"""
    
    if not access_token:
        print("❌ No access token provided")
        return False
    
    print("🔍 Comprehensive FamilySearch API Test")
    print("=" * 60)
    print(f"Token: {access_token[:20]}...")
    print()
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/x-gedcomx-v1+json',
        'User-Agent': os.getenv('CUSTOM_USER_AGENT', 'FS-Agent-Test/1.0')
    }
    
    # Comprehensive list of endpoints to test
    endpoints = [
        # Collections (known to work)
        {
            'name': 'Collections',
            'url': 'https://api.familysearch.org/platform/collections',
            'category': 'Collections'
        },
        {
            'name': 'Tree Collections',
            'url': 'https://api.familysearch.org/platform/collections/tree',
            'category': 'Collections'
        },
        {
            'name': 'Records Collections',
            'url': 'https://api.familysearch.org/platform/collections/records',
            'category': 'Collections'
        },
        {
            'name': 'Memories Collections',
            'url': 'https://api.familysearch.org/platform/collections/memories',
            'category': 'Collections'
        },
        {
            'name': 'Discussions Collections',
            'url': 'https://api.familysearch.org/platform/collections/discussions',
            'category': 'Collections'
        },
        {
            'name': 'Sources Collections',
            'url': 'https://api.familysearch.org/platform/collections/sources',
            'category': 'Collections'
        },
        {
            'name': 'Places Collections',
            'url': 'https://api.familysearch.org/platform/collections/places',
            'category': 'Collections'
        },
        {
            'name': 'Dates Collections',
            'url': 'https://api.familysearch.org/platform/collections/dates',
            'category': 'Collections'
        },
        
        # User endpoints
        {
            'name': 'Current User',
            'url': 'https://api.familysearch.org/platform/users/current',
            'category': 'User'
        },
        {
            'name': 'Current Person',
            'url': 'https://api.familysearch.org/platform/tree/current-person',
            'category': 'User'
        },
        
        # Tree endpoints
        {
            'name': 'Person by ID',
            'url': 'https://api.familysearch.org/platform/tree/persons/KWQS-BB1',
            'category': 'Tree'
        },
        {
            'name': 'Person Parents',
            'url': 'https://api.familysearch.org/platform/tree/persons/KWQS-BB1/parents',
            'category': 'Tree'
        },
        {
            'name': 'Person Spouses',
            'url': 'https://api.familysearch.org/platform/tree/persons/KWQS-BB1/spouses',
            'category': 'Tree'
        },
        {
            'name': 'Person Children',
            'url': 'https://api.familysearch.org/platform/tree/persons/KWQS-BB1/children',
            'category': 'Tree'
        },
        
        # Records endpoints
        {
            'name': 'Records Search',
            'url': 'https://api.familysearch.org/platform/records/search?q=John%20Smith&count=5',
            'category': 'Records'
        },
        {
            'name': 'Records by ID',
            'url': 'https://api.familysearch.org/platform/records/2MMM-8Q9',
            'category': 'Records'
        },
        
        # Places endpoints
        {
            'name': 'Places Search',
            'url': 'https://api.familysearch.org/platform/places/search?q=New%20York&count=5',
            'category': 'Places'
        },
        {
            'name': 'Places by ID',
            'url': 'https://api.familysearch.org/platform/places/6002147',
            'category': 'Places'
        },
        
        # Utilities
        {
            'name': 'Platform Root',
            'url': 'https://api.familysearch.org/platform',
            'category': 'Utilities'
        }
    ]
    
    results = {}
    
    with httpx.Client() as client:
        for endpoint in endpoints:
            category = endpoint['category']
            if category not in results:
                results[category] = []
            
            print(f"🔍 Testing: {endpoint['name']} ({category})")
            print(f"URL: {endpoint['url']}")
            
            try:
                response = client.get(endpoint['url'], headers=headers)
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ Success!")
                    data = response.json()
                    if isinstance(data, dict):
                        print(f"Response keys: {list(data.keys())}")
                        if 'collections' in data:
                            print(f"Collections count: {len(data['collections'])}")
                    else:
                        print("Response: JSON object")
                elif response.status_code == 401:
                    print("❌ Unauthorized")
                elif response.status_code == 403:
                    print("❌ Forbidden")
                elif response.status_code == 404:
                    print("❌ Not Found")
                elif response.status_code == 406:
                    print("❌ Not Acceptable")
                else:
                    print(f"❌ Error: {response.status_code}")
                    print(f"Response: {response.text[:100]}...")
                
                results[category].append({
                    'name': endpoint['name'],
                    'url': endpoint['url'],
                    'status': response.status_code,
                    'success': response.status_code == 200
                })
                
            except Exception as e:
                print(f"❌ Error: {e}")
                results[category].append({
                    'name': endpoint['name'],
                    'url': endpoint['url'],
                    'status': 'Error',
                    'success': False
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
            print(f"    - {endpoint['name']}")
        
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
    
    test_authenticated_endpoints(token) 