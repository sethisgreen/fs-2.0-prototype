#!/usr/bin/env python3
"""
Python wrapper for FamilySearch fs-js-lite SDK
"""

import os
import json
import subprocess
import asyncio
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FamilySearchSDKWrapper:
    """Python wrapper for FamilySearch fs-js-lite SDK"""
    
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token or os.getenv('FAMILYSEARCH_ACCESS_TOKEN')
        self.client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
        self.redirect_uri = 'https://fs-agent.com/oauth/callback'
        
        # Ensure Node.js is available
        self._check_node_availability()
        
        # Create the SDK initialization script
        self._create_sdk_script()
    
    def _check_node_availability(self):
        """Check if Node.js is available"""
        try:
            subprocess.run(['node', '--version'], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("Node.js is required for FamilySearch SDK integration")
    
    def _create_sdk_script(self):
        """Create the SDK initialization script"""
        self.sdk_script = """
const FamilySearch = require('fs-js-lite');

// Initialize the SDK
const fs = new FamilySearch({
  environment: 'production',
  appKey: process.env.FAMILYSEARCH_CLIENT_ID,
  redirectUri: 'https://fs-agent.com/oauth/callback',
  accessToken: process.env.FAMILYSEARCH_ACCESS_TOKEN
});

// Export the SDK instance
module.exports = fs;
"""
        
        # Write SDK script to file
        with open('fs_sdk_init.js', 'w') as f:
            f.write(self.sdk_script)
    
    def _run_sdk_call(self, method: str, endpoint: str, options: Dict = None) -> Dict[str, Any]:
        """Execute an SDK call and return the result"""
        
        # Create the call script
        call_script = f"""
const fs = require('./fs_sdk_init.js');

// Make the API call
fs.{method}('{endpoint}', {json.dumps(options) if options else '{}'}, function(error, response) {{
  if (error) {{
    console.error(JSON.stringify({{error: error.message, type: 'network_error'}}));
    process.exit(1);
  }} else {{
    console.log(JSON.stringify({{
      statusCode: response.statusCode,
      statusText: response.statusText,
      data: response.data,
      headers: response.headers,
      type: 'success'
    }}));
  }}
}});
"""
        
        # Write call script to file
        with open('fs_sdk_call.js', 'w') as f:
            f.write(call_script)
        
        # Set environment variables
        env = os.environ.copy()
        env['FAMILYSEARCH_CLIENT_ID'] = self.client_id or ''
        env['FAMILYSEARCH_ACCESS_TOKEN'] = self.access_token or ''
        
        try:
            # Execute the call
            result = subprocess.run(
                ['node', 'fs_sdk_call.js'],
                env=env,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            # Clean up
            if os.path.exists('fs_sdk_call.js'):
                os.remove('fs_sdk_call.js')
            
            if result.returncode == 0:
                # Parse successful response
                response_data = json.loads(result.stdout)
                return response_data
            else:
                # Parse error response
                try:
                    error_data = json.loads(result.stderr)
                    return error_data
                except json.JSONDecodeError:
                    return {
                        'error': result.stderr,
                        'type': 'execution_error'
                    }
                    
        except subprocess.TimeoutExpired:
            return {
                'error': 'Request timeout',
                'type': 'timeout_error'
            }
        except Exception as e:
            return {
                'error': str(e),
                'type': 'execution_error'
            }
    
    def get_collections(self) -> Dict[str, Any]:
        """Get FamilySearch collections"""
        return self._run_sdk_call('get', '/platform/collections')
    
    def get_collection_details(self, collection_id: str) -> Dict[str, Any]:
        """Get details for a specific collection"""
        return self._run_sdk_call('get', f'/platform/collections/{collection_id}')
    
    def search_places(self, query: str, count: int = 5) -> Dict[str, Any]:
        """Search for places"""
        options = {
            'headers': {
                'Accept': 'application/json'
            }
        }
        return self._run_sdk_call('get', f'/platform/places/search?q={query}&count={count}', options)
    
    def get_place_by_id(self, place_id: str) -> Dict[str, Any]:
        """Get place details by ID"""
        return self._run_sdk_call('get', f'/platform/places/{place_id}')
    
    def get_current_user(self) -> Dict[str, Any]:
        """Get current user profile (may return 401)"""
        return self._run_sdk_call('get', '/platform/users/current')
    
    def get_current_person(self) -> Dict[str, Any]:
        """Get current person in tree (may return 401)"""
        return self._run_sdk_call('get', '/platform/tree/current-person')
    
    def get_person(self, person_id: str) -> Dict[str, Any]:
        """Get person details by ID (may return 401)"""
        return self._run_sdk_call('get', f'/platform/tree/persons/{person_id}')
    
    def search_records(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Search for records (may return 404)"""
        options = {
            'body': query_data,
            'headers': {
                'Content-Type': 'application/x-gedcomx-v1+json'
            }
        }
        return self._run_sdk_call('post', '/platform/records/search', options)
    
    def test_connectivity(self) -> Dict[str, Any]:
        """Test SDK connectivity"""
        return self._run_sdk_call('get', '/platform/collections')
    
    def __del__(self):
        """Cleanup temporary files"""
        for filename in ['fs_sdk_init.js', 'fs_sdk_call.js']:
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except:
                    pass

# Convenience functions for easy integration
def get_fs_sdk(access_token: Optional[str] = None) -> FamilySearchSDKWrapper:
    """Get a FamilySearch SDK wrapper instance"""
    return FamilySearchSDKWrapper(access_token)

def test_sdk_connectivity(access_token: Optional[str] = None) -> Dict[str, Any]:
    """Test SDK connectivity"""
    sdk = get_fs_sdk(access_token)
    return sdk.test_connectivity()

if __name__ == "__main__":
    # Test the SDK wrapper
    print("🧪 Testing FamilySearch SDK Wrapper")
    print("=" * 40)
    
    # Test connectivity
    result = test_sdk_connectivity()
    print(f"Connectivity Test: {result}")
    
    if result.get('type') == 'success':
        print("✅ SDK wrapper is working correctly")
    else:
        print(f"❌ SDK wrapper error: {result}") 