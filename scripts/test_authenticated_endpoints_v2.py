#!/usr/bin/env python3
"""
Comprehensive test of FamilySearch authenticated endpoints with proper headers
"""

import os
import httpx
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_authenticated_endpoints_v2(access_token):
    """Test authenticated endpoints with proper headers and parameters"""
    
    if not access_token:
        print("❌ No access token provided")
        return False
    
    print("🔍 Comprehensive FamilySearch API Test v2")
    print("=" * 60)
    print(f"Token: {access_token[:20]}...")
    print()
    
    # Standard headers for FamilySearch API
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/x-gedcomx-v1+json',
        'Content-Type': 'application/x-gedcomx-v1+json',
        'User-Agent': os.getenv('CUSTOM_USER_AGENT', 'FS-Agent-Test/1.0')
    }
    
    # Test cases with proper parameters
    test_cases = [
        # Records Search (POST method)
        {
            'name': 'Records Search - John Smith',
            'method': 'POST',
            'url': 'https://api.familysearch.org/platform/records/search',
            'data': {
                "query": {
                    "persons": [{
                        "names": [{
                            "nameForms": [{
                                "parts": [
                                    {"type": "http://gedcomx.org/v1/Given", "value": "John"},
                                    {"type": "http://gedcomx.org/v1/Surname", "value": "Smith"}
                                ]
                            }]
                        }]
                    }]
                },
                "count": 5
            },
            'category': 'Records'
        },
        
        # Records Search with date
        {
            'name': 'Records Search - Mary Johnson 1850',
            'method': 'POST',
            'url': 'https://api.familysearch.org/platform/records/search',
            'data': {
                "query": {
                    "persons": [{
                        "names": [{
                            "nameForms": [{
                                "parts": [
                                    {"type": "http://gedcomx.org/v1/Given", "value": "Mary"},
                                    {"type": "http://gedcomx.org/v1/Surname", "value": "Johnson"}
                                ]
                            }]
                        }],
                        "facts": [{
                            "type": "http://gedcomx.org/v1/Birth",
                            "date": {"original": "1850"}
                        }]
                    }]
                },
                "count": 5
            },
            'category': 'Records'
        },
        
        # Current User (GET)
        {
            'name': 'Current User Profile',
            'method': 'GET',
            'url': 'https://api.familysearch.org/platform/users/current',
            'data': None,
            'category': 'User'
        },
        
        # Current Person (GET)
        {
            'name': 'Current Person in Tree',
            'method': 'GET',
            'url': 'https://api.familysearch.org/platform/tree/current-person',
            'data': None,
            'category': 'User'
        },
        
        # Person by ID (GET)
        {
            'name': 'Person by ID - KWQS-BB1',
            'method': 'GET',
            'url': 'https://api.familysearch.org/platform/tree/persons/KWQS-BB1',
            'data': None,
            'category': 'Tree'
        },
        
        # Person Parents (GET)
        {
            'name': 'Person Parents - KWQS-BB1',
            'method': 'GET',
            'url': 'https://api.familysearch.org/platform/tree/persons/KWQS-BB1/parents',
            'data': None,
            'category': 'Tree'
        },
        
        # Person Spouses (GET)
        {
            'name': 'Person Spouses - KWQS-BB1',
            'method': 'GET',
            'url': 'https://api.familysearch.org/platform/tree/persons/KWQS-BB1/spouses',
            'data': None,
            'category': 'Tree'
        },
        
        # Person Children (GET)
        {
            'name': 'Person Children - KWQS-BB1',
            'method': 'GET',
            'url': 'https://api.familysearch.org/platform/tree/persons/KWQS-BB1/children',
            'data': None,
            'category': 'Tree'
        },
        
        # Places Search (GET)
        {
            'name': 'Places Search - New York',
            'method': 'GET',
            'url': 'https://api.familysearch.org/platform/places/search?q=New%20York&count=5',
            'data': None,
            'category': 'Places'
        },
        
        # Places Search with different Accept header
        {
            'name': 'Places Search - JSON Accept',
            'method': 'GET',
            'url': 'https://api.familysearch.org/platform/places/search?q=London&count=5',
            'data': None,
            'headers': {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'User-Agent': os.getenv('CUSTOM_USER_AGENT', 'FS-Agent-Test/1.0')
            },
            'category': 'Places'
        },
        
        # Record by ID (GET)
        {
            'name': 'Record by ID - 2MMM-8Q9',
            'method': 'GET',
            'url': 'https://api.familysearch.org/platform/records/2MMM-8Q9',
            'data': None,
            'category': 'Records'
        },
        
        # Collections (GET) - known working
        {
            'name': 'Collections',
            'method': 'GET',
            'url': 'https://api.familysearch.org/platform/collections',
            'data': None,
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
            print(f"Method: {test_case['method']}")
            print(f"URL: {test_case['url']}")
            
            # Use custom headers if provided, otherwise use standard headers
            request_headers = test_case.get('headers', headers)
            
            try:
                if test_case['method'] == 'GET':
                    response = client.get(test_case['url'], headers=request_headers)
                elif test_case['method'] == 'POST':
                    response = client.post(
                        test_case['url'], 
                        headers=request_headers,
                        json=test_case['data']
                    )
                else:
                    print(f"❌ Unsupported method: {test_case['method']}")
                    continue
                
                print(f"Status: {response.status_code}")
                print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
                
                if response.status_code == 200:
                    print("✅ Success!")
                    try:
                        data = response.json()
                        if isinstance(data, dict):
                            print(f"Response keys: {list(data.keys())}")
                            if 'entries' in data:
                                print(f"Entries count: {len(data['entries'])}")
                            elif 'collections' in data:
                                print(f"Collections count: {len(data['collections'])}")
                            elif 'persons' in data:
                                print(f"Persons count: {len(data['persons'])}")
                        else:
                            print("Response: JSON object")
                    except json.JSONDecodeError:
                        print("Response: Not JSON")
                        print(f"Response preview: {response.text[:200]}...")
                        
                elif response.status_code == 401:
                    print("❌ Unauthorized - Token might be invalid or expired")
                elif response.status_code == 403:
                    print("❌ Forbidden - Token valid but no permission")
                elif response.status_code == 404:
                    print("❌ Not Found - Endpoint doesn't exist")
                elif response.status_code == 406:
                    print("❌ Not Acceptable - Try different Accept header")
                elif response.status_code == 429:
                    print("❌ Rate Limited - Too many requests")
                else:
                    print(f"❌ Error: {response.status_code}")
                    print(f"Response: {response.text[:200]}...")
                
                results[category].append({
                    'name': test_case['name'],
                    'url': test_case['url'],
                    'method': test_case['method'],
                    'status': response.status_code,
                    'success': response.status_code == 200
                })
                
            except Exception as e:
                print(f"❌ Error: {e}")
                results[category].append({
                    'name': test_case['name'],
                    'url': test_case['url'],
                    'method': test_case['method'],
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
            print(f"    - {endpoint['name']} ({endpoint['method']})")
        
        if failed:
            print(f"  ❌ Failed: {len(failed)}/{len(endpoints)}")
            for endpoint in failed:
                print(f"    - {endpoint['name']} ({endpoint['method']}) - {endpoint['status']}")
    
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
    
    test_authenticated_endpoints_v2(token) 