#!/usr/bin/env python3
"""
FamilySearch API Server using fs-js-lite SDK
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Import our SDK wrapper
from fs_sdk_wrapper import FamilySearchSDKWrapper, get_fs_sdk

# Load environment variables
load_dotenv()

class FamilySearchAPIServer:
    """FamilySearch API Server using fs-js-lite SDK"""
    
    def __init__(self):
        self.sdk = None
        self.access_token = os.getenv('FAMILYSEARCH_ACCESS_TOKEN')
        self.client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
        self.client_secret = os.getenv('FAMILYSEARCH_CLIENT_SECRET')
        
        # Initialize SDK if we have an access token
        if self.access_token:
            self.sdk = get_fs_sdk(self.access_token)
    
    def initialize_sdk(self, access_token: str):
        """Initialize SDK with access token"""
        self.access_token = access_token
        self.sdk = get_fs_sdk(access_token)
        return self.sdk is not None
    
    def get_familysearch_collections(self) -> Dict[str, Any]:
        """Get FamilySearch collections using SDK"""
        if not self.sdk:
            return {
                'error': 'SDK not initialized. Please authenticate first.',
                'status': 'error'
            }
        
        try:
            result = self.sdk.get_collections()
            
            if result.get('type') == 'success':
                return {
                    'status': 'success',
                    'collections': result.get('data', {}).get('collections', []),
                    'count': len(result.get('data', {}).get('collections', [])),
                    'message': f"Successfully retrieved {len(result.get('data', {}).get('collections', []))} collections"
                }
            else:
                return {
                    'status': 'error',
                    'error': result.get('error', 'Unknown error'),
                    'message': 'Failed to retrieve collections'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Exception occurred while retrieving collections'
            }
    
    def get_familysearch_tree_info(self) -> Dict[str, Any]:
        """Get FamilySearch tree collection info using SDK"""
        if not self.sdk:
            return {
                'error': 'SDK not initialized. Please authenticate first.',
                'status': 'error'
            }
        
        try:
            result = self.sdk.get_collection_details('tree')
            
            if result.get('type') == 'success':
                return {
                    'status': 'success',
                    'tree_info': result.get('data', {}),
                    'message': 'Successfully retrieved tree collection info'
                }
            else:
                return {
                    'status': 'error',
                    'error': result.get('error', 'Unknown error'),
                    'message': 'Failed to retrieve tree collection info'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Exception occurred while retrieving tree info'
            }
    
    def get_familysearch_records_info(self) -> Dict[str, Any]:
        """Get FamilySearch records collection info using SDK"""
        if not self.sdk:
            return {
                'error': 'SDK not initialized. Please authenticate first.',
                'status': 'error'
            }
        
        try:
            result = self.sdk.get_collection_details('records')
            
            if result.get('type') == 'success':
                return {
                    'status': 'success',
                    'records_info': result.get('data', {}),
                    'message': 'Successfully retrieved records collection info'
                }
            else:
                return {
                    'status': 'error',
                    'error': result.get('error', 'Unknown error'),
                    'message': 'Failed to retrieve records collection info'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Exception occurred while retrieving records info'
            }
    
    def search_places(self, query: str, count: int = 5) -> Dict[str, Any]:
        """Search for places using SDK"""
        if not self.sdk:
            return {
                'error': 'SDK not initialized. Please authenticate first.',
                'status': 'error'
            }
        
        try:
            result = self.sdk.search_places(query, count)
            
            if result.get('type') == 'success':
                return {
                    'status': 'success',
                    'places': result.get('data', {}).get('places', []),
                    'count': len(result.get('data', {}).get('places', [])),
                    'query': query,
                    'message': f"Found {len(result.get('data', {}).get('places', []))} places for '{query}'"
                }
            else:
                return {
                    'status': 'error',
                    'error': result.get('error', 'Unknown error'),
                    'message': f'Failed to search places for "{query}"'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'message': f'Exception occurred while searching places for "{query}"'
            }
    
    def get_place_details(self, place_id: str) -> Dict[str, Any]:
        """Get place details by ID using SDK"""
        if not self.sdk:
            return {
                'error': 'SDK not initialized. Please authenticate first.',
                'status': 'error'
            }
        
        try:
            result = self.sdk.get_place_by_id(place_id)
            
            if result.get('type') == 'success':
                return {
                    'status': 'success',
                    'place': result.get('data', {}).get('places', [{}])[0] if result.get('data', {}).get('places') else {},
                    'place_id': place_id,
                    'message': f'Successfully retrieved place details for {place_id}'
                }
            else:
                return {
                    'status': 'error',
                    'error': result.get('error', 'Unknown error'),
                    'message': f'Failed to retrieve place details for {place_id}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'message': f'Exception occurred while retrieving place details for {place_id}'
            }
    
    def search_census_records(self, given_name: str, surname: str, year: int = None, place: str = None) -> Dict[str, Any]:
        """Search for census records using SDK (stubbed - records API not available)"""
        return {
            'status': 'stubbed',
            'message': 'Records search not available with current authentication',
            'note': 'This endpoint requires full OAuth access to records API',
            'search_params': {
                'given_name': given_name,
                'surname': surname,
                'year': year,
                'place': place
            },
            'mock_results': [
                {
                    'id': 'mock-census-1',
                    'title': f'Census Record for {given_name} {surname}',
                    'year': year or 1850,
                    'place': place or 'Unknown',
                    'source': 'Mock Census Data'
                }
            ]
        }
    
    def search_vital_records(self, given_name: str, surname: str, event_type: str = 'birth', year: int = None) -> Dict[str, Any]:
        """Search for vital records using SDK (stubbed - records API not available)"""
        return {
            'status': 'stubbed',
            'message': 'Records search not available with current authentication',
            'note': 'This endpoint requires full OAuth access to records API',
            'search_params': {
                'given_name': given_name,
                'surname': surname,
                'event_type': event_type,
                'year': year
            },
            'mock_results': [
                {
                    'id': f'mock-{event_type}-1',
                    'title': f'{event_type.title()} Record for {given_name} {surname}',
                    'event_type': event_type,
                    'year': year or 1850,
                    'source': f'Mock {event_type.title()} Data'
                }
            ]
        }
    
    def get_record_by_id(self, record_id: str) -> Dict[str, Any]:
        """Get record details by ID using SDK (stubbed - records API not available)"""
        return {
            'status': 'stubbed',
            'message': 'Record retrieval not available with current authentication',
            'note': 'This endpoint requires full OAuth access to records API',
            'record_id': record_id,
            'mock_record': {
                'id': record_id,
                'title': f'Mock Record {record_id}',
                'type': 'mock',
                'source': 'Mock Record Data'
            }
        }
    
    def authenticate_user(self, authorization_code: str = None) -> Dict[str, Any]:
        """Authenticate user (stubbed - requires OAuth flow)"""
        if authorization_code:
            return {
                'status': 'success',
                'message': 'Authorization code received',
                'note': 'Token exchange would happen here in full implementation',
                'authorization_code': authorization_code
            }
        else:
            return {
                'status': 'stubbed',
                'message': 'OAuth authentication flow not implemented',
                'note': 'This would initiate OAuth flow in full implementation'
            }
    
    def test_connectivity(self) -> Dict[str, Any]:
        """Test SDK connectivity"""
        if not self.sdk:
            return {
                'status': 'error',
                'error': 'SDK not initialized',
                'message': 'Please authenticate first'
            }
        
        try:
            result = self.sdk.test_connectivity()
            
            if result.get('type') == 'success':
                return {
                    'status': 'success',
                    'message': 'SDK connectivity test passed',
                    'collections_count': len(result.get('data', {}).get('collections', [])),
                    'sdk_status': 'connected'
                }
            else:
                return {
                    'status': 'error',
                    'error': result.get('error', 'Unknown error'),
                    'message': 'SDK connectivity test failed'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Exception occurred during connectivity test'
            }

# Global server instance
fs_server = FamilySearchAPIServer()

# Initialize with current token if available
if os.getenv('FAMILYSEARCH_ACCESS_TOKEN'):
    fs_server.initialize_sdk(os.getenv('FAMILYSEARCH_ACCESS_TOKEN'))

if __name__ == "__main__":
    # Test the server
    print("🧪 Testing FamilySearch API Server with SDK")
    print("=" * 50)
    
    # Test connectivity
    connectivity = fs_server.test_connectivity()
    print(f"Connectivity: {connectivity}")
    
    # Test collections
    collections = fs_server.get_familysearch_collections()
    print(f"Collections: {collections}")
    
    # Test places search
    places = fs_server.search_places("New York", 3)
    print(f"Places Search: {places}")
    
    print("\n✅ Server tests completed") 