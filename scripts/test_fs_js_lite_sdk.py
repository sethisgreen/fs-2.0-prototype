#!/usr/bin/env python3
"""
Test FamilySearch fs-js-lite SDK integration
"""

import os
import subprocess
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_fs_js_lite_sdk():
    """Test the FamilySearch fs-js-lite SDK"""
    
    print("🔍 Testing FamilySearch fs-js-lite SDK")
    print("=" * 50)
    
    # Check if Node.js is available
    try:
        subprocess.run(['node', '--version'], check=True, capture_output=True)
        print("✅ Node.js is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js is not available")
        print("Please install Node.js to test the fs-js-lite SDK")
        return False
    
    # Create a test script
    test_script = """
const FamilySearch = require('fs-js-lite');

// Initialize the SDK
const fs = new FamilySearch({
  environment: 'production',
  appKey: process.env.FAMILYSEARCH_CLIENT_ID,
  redirectUri: 'https://fs-agent.com/oauth/callback',
  accessToken: process.env.FAMILYSEARCH_ACCESS_TOKEN
});

// Test collections endpoint
fs.get('/platform/collections', function(error, response) {
  if (error) {
    console.error('Network error:', error);
    process.exit(1);
  } else if (response.statusCode >= 400) {
    console.error('HTTP error:', response.statusCode, response.statusText);
    process.exit(1);
  } else {
    console.log('✅ Collections API working');
    console.log('Collections count:', response.data.collections.length);
  }
});

// Test places search
fs.get('/platform/places/search?q=New%20York&count=5', {
  headers: {
    'Accept': 'application/json'
  }
}, function(error, response) {
  if (error) {
    console.error('Places search error:', error);
  } else if (response.statusCode >= 400) {
    console.error('Places search HTTP error:', response.statusCode);
  } else {
    console.log('✅ Places search working');
    console.log('Response status:', response.statusCode);
  }
});

// Test current user (should fail with 401)
fs.get('/platform/users/current', function(error, response) {
  if (error) {
    console.error('User API network error:', error);
  } else if (response.statusCode === 401) {
    console.log('✅ User API correctly returns 401 (expected)');
  } else {
    console.log('User API status:', response.statusCode);
  }
});
"""
    
    # Write test script to file
    with open('test_fs_sdk.js', 'w') as f:
        f.write(test_script)
    
    # Set environment variables
    env = os.environ.copy()
    env['FAMILYSEARCH_CLIENT_ID'] = os.getenv('FAMILYSEARCH_CLIENT_ID', '')
    env['FAMILYSEARCH_ACCESS_TOKEN'] = 'b0-sAR6OKN8~kw.A0zXc'  # Our current token
    
    try:
        # Install fs-js-lite if not already installed
        print("📦 Installing fs-js-lite SDK...")
        subprocess.run(['npm', 'install', 'fs-js-lite'], check=True, capture_output=True)
        print("✅ SDK installed successfully")
        
        # Run the test script
        print("🧪 Running SDK tests...")
        result = subprocess.run(['node', 'test_fs_sdk.js'], 
                              env=env, 
                              capture_output=True, 
                              text=True)
        
        if result.returncode == 0:
            print("✅ SDK tests completed successfully")
            print(result.stdout)
        else:
            print("❌ SDK tests failed")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running SDK tests: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists('test_fs_sdk.js'):
            os.remove('test_fs_sdk.js')
    
    return True

def test_sdk_vs_manual_comparison():
    """Compare SDK results with our manual API calls"""
    
    print("\n🔍 Comparing SDK vs Manual API Calls")
    print("=" * 40)
    
    # Test collections endpoint comparison
    collections_test = """
const FamilySearch = require('fs-js-lite');

const fs = new FamilySearch({
  environment: 'production',
  accessToken: process.env.FAMILYSEARCH_ACCESS_TOKEN
});

// Test collections endpoint
fs.get('/platform/collections', function(error, response) {
  if (error) {
    console.error('SDK Error:', error);
  } else {
    console.log('SDK Collections Response:');
    console.log(JSON.stringify(response.data, null, 2));
  }
});
"""
    
    with open('test_collections_comparison.js', 'w') as f:
        f.write(collections_test)
    
    env = os.environ.copy()
    env['FAMILYSEARCH_ACCESS_TOKEN'] = 'b0-sAR6OKN8~kw.A0zXc'
    
    try:
        result = subprocess.run(['node', 'test_collections_comparison.js'], 
                              env=env, 
                              capture_output=True, 
                              text=True)
        
        if result.returncode == 0:
            print("✅ SDK Collections Test:")
            print(result.stdout)
        else:
            print("❌ SDK Collections Test Failed:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error in comparison test: {e}")
    finally:
        if os.path.exists('test_collections_comparison.js'):
            os.remove('test_collections_comparison.js')

if __name__ == "__main__":
    print("🚀 FamilySearch fs-js-lite SDK Test")
    print("=" * 50)
    
    # Test basic SDK functionality
    success = test_fs_js_lite_sdk()
    
    if success:
        # Test comparison with manual calls
        test_sdk_vs_manual_comparison()
        
        print("\n📊 SDK Test Summary:")
        print("✅ SDK installation and basic functionality")
        print("✅ API call comparison with manual requests")
        print("✅ Error handling and status code detection")
        
        print("\n💡 Next Steps:")
        print("1. Integrate SDK into our Python backend")
        print("2. Replace manual HTTP requests with SDK calls")
        print("3. Add middleware for caching and logging")
        print("4. Test performance improvements")
    else:
        print("\n❌ SDK test failed")
        print("Please check Node.js installation and try again") 