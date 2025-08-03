#!/usr/bin/env python3
"""
Comprehensive test of all stubbed servers working together.

This script tests the integration between all servers to ensure they can
work with limited FamilySearch access and provide a complete testing environment.
"""

import os
import sys
import asyncio
import httpx
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_familysearch_server():
    """Test FamilySearch server functionality."""
    print("🔍 Testing FamilySearch Server...")
    
    # Test unauthenticated session functionality
    try:
        async with httpx.AsyncClient() as client:
            # Test collections endpoint
            response = await client.get("http://localhost:8001/mcp")
            if response.status_code == 200:
                print("   ✅ FamilySearch server is running")
            else:
                print("   ❌ FamilySearch server not responding")
                return False
    except Exception as e:
        print(f"   ❌ Error connecting to FamilySearch server: {e}")
        return False
    
    return True

async def test_records_router():
    """Test Records Router functionality."""
    print("🔍 Testing Records Router...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test basic connectivity
            response = await client.get("http://localhost:8002/mcp")
            if response.status_code == 200:
                print("   ✅ Records Router is running")
            else:
                print("   ❌ Records Router not responding")
                return False
    except Exception as e:
        print(f"   ❌ Error connecting to Records Router: {e}")
        return False
    
    return True

async def test_document_processing():
    """Test Document Processing server."""
    print("🔍 Testing Document Processing Server...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test basic connectivity
            response = await client.get("http://localhost:8003/mcp")
            if response.status_code == 200:
                print("   ✅ Document Processing server is running")
            else:
                print("   ❌ Document Processing server not responding")
                return False
    except Exception as e:
        print(f"   ❌ Error connecting to Document Processing server: {e}")
        return False
    
    return True

async def test_analysis_server():
    """Test Analysis server."""
    print("🔍 Testing Analysis Server...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test basic connectivity
            response = await client.get("http://localhost:8004/mcp")
            if response.status_code == 200:
                print("   ✅ Analysis server is running")
            else:
                print("   ❌ Analysis server not responding")
                return False
    except Exception as e:
        print(f"   ❌ Error connecting to Analysis server: {e}")
        return False
    
    return True

async def test_research_management():
    """Test Research Management server."""
    print("🔍 Testing Research Management Server...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test basic connectivity
            response = await client.get("http://localhost:8005/mcp")
            if response.status_code == 200:
                print("   ✅ Research Management server is running")
            else:
                print("   ❌ Research Management server not responding")
                return False
    except Exception as e:
        print(f"   ❌ Error connecting to Research Management server: {e}")
        return False
    
    return True

async def test_location_server():
    """Test Location server."""
    print("🔍 Testing Location Server...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test basic connectivity
            response = await client.get("http://localhost:8006/mcp")
            if response.status_code == 200:
                print("   ✅ Location server is running")
            else:
                print("   ❌ Location server not responding")
                return False
    except Exception as e:
        print(f"   ❌ Error connecting to Location server: {e}")
        return False
    
    return True

async def test_integration_workflow():
    """Test a complete integration workflow."""
    print("\n🔍 Testing Integration Workflow...")
    
    try:
        async with httpx.AsyncClient() as client:
            # 1. Create a research project
            project_response = await client.post(
                "http://localhost:8005/call_tool",
                json={
                    "name": "create_research_project",
                    "arguments": {
                        "title": "John Smith Family Research",
                        "description": "Researching the Smith family in 1850s New York",
                        "tags": ["census", "vital_records", "new_york"]
                    }
                }
            )
            
            if project_response.status_code == 200:
                project_data = project_response.json()
                project_id = project_data.get("content", {}).get("id")
                print(f"   ✅ Created research project: {project_id}")
                
                # 2. Search for places
                place_response = await client.post(
                    "http://localhost:8006/call_tool",
                    json={
                        "name": "search_places",
                        "arguments": {
                            "query": "Albany",
                            "place_type": "city"
                        }
                    }
                )
                
                if place_response.status_code == 200:
                    place_data = place_response.json()
                    print(f"   ✅ Found places: {len(place_data.get('content', {}).get('results', []))}")
                
                # 3. Analyze genealogical data
                analysis_response = await client.post(
                    "http://localhost:8004/call_tool",
                    json={
                        "name": "analyze_genealogical_data",
                        "arguments": {
                            "query": "census records 1850",
                            "data_sources": ["familysearch"]
                        }
                    }
                )
                
                if analysis_response.status_code == 200:
                    analysis_data = analysis_response.json()
                    print(f"   ✅ Generated analysis with {len(analysis_data.get('content', {}).get('findings', []))} findings")
                
                # 4. Search for records
                search_response = await client.post(
                    "http://localhost:8002/call_tool",
                    json={
                        "name": "search_records",
                        "arguments": {
                            "query": "John Smith",
                            "providers": ["familysearch"],
                            "filters": {"year": 1850, "place": "New York"}
                        }
                    }
                )
                
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    print(f"   ✅ Found {len(search_data.get('content', []))} records")
                
                # 5. Process a document
                doc_response = await client.post(
                    "http://localhost:8003/call_tool",
                    json={
                        "name": "process_document",
                        "arguments": {
                            "document_url": "https://familysearch.org/mock/census/1850",
                            "document_type": "census"
                        }
                    }
                )
                
                if doc_response.status_code == 200:
                    doc_data = doc_response.json()
                    print(f"   ✅ Processed document with {len(doc_data.get('content', {}).get('extracted_persons', []))} persons")
                
                print("   ✅ Integration workflow completed successfully!")
                return True
                
            else:
                print(f"   ❌ Failed to create research project: {project_response.status_code}")
                return False
                
    except Exception as e:
        print(f"   ❌ Error in integration workflow: {e}")
        return False

async def main():
    """Run comprehensive server testing."""
    print("🚀 Testing All Stubbed Servers")
    print("=" * 60)
    
    # Test individual servers
    servers = [
        ("FamilySearch", test_familysearch_server),
        ("Records Router", test_records_router),
        ("Document Processing", test_document_processing),
        ("Analysis", test_analysis_server),
        ("Research Management", test_research_management),
        ("Location", test_location_server)
    ]
    
    server_results = {}
    
    for server_name, test_func in servers:
        try:
            result = await test_func()
            server_results[server_name] = result
        except Exception as e:
            print(f"   ❌ Error testing {server_name}: {e}")
            server_results[server_name] = False
    
    # Test integration workflow
    integration_result = await test_integration_workflow()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    all_passed = True
    for server_name, result in server_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {server_name}: {status}")
        if not result:
            all_passed = False
    
    integration_status = "✅ PASS" if integration_result else "❌ FAIL"
    print(f"   Integration Workflow: {integration_status}")
    
    if not integration_result:
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed! Your stubbed servers are ready for testing.")
        print("\n💡 Next Steps:")
        print("1. Add your real FamilySearch credentials to .env")
        print("2. Test with real OAuth authentication")
        print("3. Replace stubbed implementations with real API calls")
        print("4. Deploy and test in production environment")
    else:
        print("⚠️  Some tests failed. Check server configurations and try again.")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure all servers are running on correct ports")
        print("2. Check that MCP servers are properly configured")
        print("3. Verify network connectivity between servers")
        print("4. Check server logs for detailed error messages")

if __name__ == "__main__":
    asyncio.run(main()) 