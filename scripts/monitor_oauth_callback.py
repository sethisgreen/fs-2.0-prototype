#!/usr/bin/env python3
"""
Monitor OAuth callback and capture authorization code
"""

import time
import requests
from urllib.parse import urlparse, parse_qs

def monitor_callback():
    """Monitor the callback URL for authorization codes"""
    
    print("🔍 Monitoring OAuth Callback")
    print("=" * 40)
    print("After completing FamilySearch authorization in your browser,")
    print("you should be redirected to our callback page.")
    print()
    print("The callback URL will contain the authorization code.")
    print("Please check your browser and copy the code from the callback page.")
    print()
    
    # Test the callback page
    try:
        response = requests.get("https://www.fs-agent.com/oauth/callback")
        if response.status_code == 200:
            print("✅ Callback page is accessible")
        else:
            print(f"❌ Callback page returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing callback page: {e}")
    
    print()
    print("📝 Instructions:")
    print("1. Complete the FamilySearch login in your browser")
    print("2. You'll be redirected to: https://fs-agent.com/oauth/callback")
    print("3. Look for the authorization code on the callback page")
    print("4. Copy the code and run: python scripts/test_familysearch_oauth.py <code>")
    print()
    
    return True

if __name__ == "__main__":
    monitor_callback() 