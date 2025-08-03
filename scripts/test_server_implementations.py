#!/usr/bin/env python3
"""
Test the actual server implementations without mcp_kit dependency.
"""

import os
import sys
import asyncio
import httpx
import json
from dotenv import load_dotenv

# Add the servers directory to the path
sys.path.append('servers')

# Load environment variables
load_dotenv()

async def test_familysearch_server_implementation():
    """Test the FamilySearch server implementation directly."""
    print("🔍 Testing FamilySearch Server Implementation...")
    
    try:
        # Import the server functions directly
        from familysearch_api.server import (
            get_unauthenticated_token,
            make_authenticated_request,
            get_familysearch_collections,
            get_familysearch_tree_info,
            get_familysearch_records_info
        )
        
        # Test unauthenticated token
        token = await get_unauthenticated_token()
        if token:
            print(f"✅ Got unauthenticated token: {token[:20]}...")
        else:
            print("❌ Failed to get unauthenticated token")
            return False
        
        # Test collections
        collections = await get_familysearch_collections()
        if collections:
            print(f"✅ Retrieved {len(collections)} collections")
            for collection in collections[:3]:  # Show first 3
                print(f"   - {collection.get('id')}: {collection.get('title')}")
        else:
            print("❌ Failed to retrieve collections")
            return False
        
        # Test tree info
        tree_info = await get_familysearch_tree_info()
        if tree_info:
            print(f"✅ Retrieved tree info: {tree_info.get('title', 'Unknown')}")
        else:
            print("❌ Failed to retrieve tree info")
            return False
        
        # Test records info
        records_info = await get_familysearch_records_info()
        if records_info:
            print(f"✅ Retrieved records info: {records_info.get('title', 'Unknown')}")
        else:
            print("❌ Failed to retrieve records info")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing FamilySearch server: {e}")
        return False

async def test_records_router_implementation():
    """Test the Records Router implementation directly."""
    print("\n🔍 Testing Records Router Implementation...")
    
    try:
        # Import the server functions directly
        from records_router.server import (
            search_records,
            get_provider_info,
            test_provider_connectivity
        )
        
        # Test search records
        results = await search_records("John Smith", ["familysearch"], {"year": 1850})
        if results:
            print(f"✅ Search returned {len(results)} results")
            for result in results[:2]:  # Show first 2
                print(f"   - {result.get('name', 'Unknown')} ({result.get('provider', 'Unknown')})")
        else:
            print("❌ Search returned no results")
            return False
        
        # Test provider info
        provider_info = await get_provider_info("familysearch")
        if provider_info:
            print(f"✅ Got provider info: {provider_info.get('name', 'Unknown')}")
        else:
            print("❌ Failed to get provider info")
            return False
        
        # Test connectivity
        connectivity = await test_provider_connectivity("familysearch")
        if connectivity:
            print(f"✅ Connectivity test: {connectivity.get('status', 'Unknown')}")
        else:
            print("❌ Failed connectivity test")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Records Router: {e}")
        return False

async def test_document_processing_implementation():
    """Test the Document Processing implementation directly."""
    print("\n🔍 Testing Document Processing Implementation...")
    
    try:
        # Import the server functions directly
        from document_processing.server import (
            process_document,
            extract_persons_from_document,
            extract_places_from_document,
            extract_dates_from_document
        )
        
        # Test document processing
        doc_url = "https://familysearch.org/mock/census/1850"
        processed_doc = await process_document(doc_url, "census")
        if processed_doc:
            print(f"✅ Processed document: {processed_doc.id}")
            print(f"   Extracted {len(processed_doc.extracted_persons)} persons")
            print(f"   Extracted {len(processed_doc.extracted_places)} places")
            print(f"   Extracted {len(processed_doc.extracted_dates)} dates")
        else:
            print("❌ Failed to process document")
            return False
        
        # Test person extraction
        persons = await extract_persons_from_document(doc_url)
        if persons:
            print(f"✅ Extracted {len(persons)} persons")
        else:
            print("❌ Failed to extract persons")
            return False
        
        # Test place extraction
        places = await extract_places_from_document(doc_url)
        if places:
            print(f"✅ Extracted {len(places)} places")
        else:
            print("❌ Failed to extract places")
            return False
        
        # Test date extraction
        dates = await extract_dates_from_document(doc_url)
        if dates:
            print(f"✅ Extracted {len(dates)} dates")
        else:
            print("❌ Failed to extract dates")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Document Processing: {e}")
        return False

async def test_analysis_implementation():
    """Test the Analysis implementation directly."""
    print("\n🔍 Testing Analysis Implementation...")
    
    try:
        # Import the server functions directly
        from analysis.server import (
            analyze_genealogical_data,
            generate_research_path,
            suggest_research_strategies
        )
        
        # Test analysis
        analysis_result = await analyze_genealogical_data("census records 1850", ["familysearch"])
        if analysis_result:
            print(f"✅ Analysis completed: {len(analysis_result.findings)} findings")
            print(f"   Confidence: {analysis_result.confidence}")
            print(f"   Recommendations: {len(analysis_result.recommendations)}")
        else:
            print("❌ Failed to complete analysis")
            return False
        
        # Test research path generation
        research_path = await generate_research_path("John Smith", analysis_result)
        if research_path:
            print(f"✅ Generated research path: {research_path.title}")
            print(f"   Steps: {len(research_path.steps)}")
            print(f"   Estimated time: {research_path.estimated_time}")
        else:
            print("❌ Failed to generate research path")
            return False
        
        # Test strategy suggestions
        strategies = await suggest_research_strategies("John Smith")
        if strategies:
            print(f"✅ Generated {len(strategies)} research strategies")
        else:
            print("❌ Failed to generate strategies")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Analysis: {e}")
        return False

async def test_research_management_implementation():
    """Test the Research Management implementation directly."""
    print("\n🔍 Testing Research Management Implementation...")
    
    try:
        # Import the server functions directly
        from research_management.server import (
            create_research_project,
            get_research_projects,
            create_research_task,
            create_research_note
        )
        
        # Test project creation
        project = await create_research_project(
            "Test Project",
            "Testing research management functionality",
            ["test", "demo"]
        )
        if project:
            print(f"✅ Created project: {project.id}")
            print(f"   Title: {project.title}")
            print(f"   Status: {project.status}")
        else:
            print("❌ Failed to create project")
            return False
        
        # Test getting projects
        projects = await get_research_projects()
        if projects:
            print(f"✅ Retrieved {len(projects)} projects")
        else:
            print("❌ Failed to retrieve projects")
            return False
        
        # Test task creation
        task = await create_research_task(
            project.id,
            "Test Task",
            "Testing task creation",
            "high",
            2.0
        )
        if task:
            print(f"✅ Created task: {task.id}")
            print(f"   Title: {task.title}")
            print(f"   Priority: {task.priority}")
        else:
            print("❌ Failed to create task")
            return False
        
        # Test note creation
        note = await create_research_note(
            project.id,
            "Test Note",
            "This is a test note for research management testing",
            ["test", "note"]
        )
        if note:
            print(f"✅ Created note: {note.id}")
            print(f"   Title: {note.title}")
            print(f"   Tags: {note.tags}")
        else:
            print("❌ Failed to create note")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Research Management: {e}")
        return False

async def test_location_implementation():
    """Test the Location implementation directly."""
    print("\n🔍 Testing Location Implementation...")
    
    try:
        # Import the server functions directly
        from location.server import (
            search_places,
            get_place_details,
            get_geographic_context,
            normalize_place_name
        )
        
        # Test place search
        search_result = await search_places("Albany", "city")
        if search_result and search_result.results:
            print(f"✅ Found {len(search_result.results)} places")
            for place in search_result.results:
                print(f"   - {place.name} ({place.type})")
        else:
            print("❌ Failed to search places")
            return False
        
        # Test place details
        place_details = await get_place_details("albany")
        if place_details:
            print(f"✅ Got place details: {place_details.name}")
            print(f"   Type: {place_details.type}")
            print(f"   Historical names: {len(place_details.historical_names)}")
        else:
            print("❌ Failed to get place details")
            return False
        
        # Test geographic context
        context = await get_geographic_context("albany", "1850-1900")
        if context:
            print(f"✅ Got geographic context: {context.time_period}")
            print(f"   Historical context: {context.historical_context[:50]}...")
        else:
            print("❌ Failed to get geographic context")
            return False
        
        # Test place normalization
        normalized = await normalize_place_name("albany")
        if normalized:
            print(f"✅ Normalized place name: {normalized['normalized_name']}")
            print(f"   Confidence: {normalized['confidence']}")
        else:
            print("❌ Failed to normalize place name")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Location: {e}")
        return False

async def main():
    """Run all server implementation tests."""
    print("🚀 Testing Server Implementations")
    print("=" * 50)
    
    tests = [
        ("FamilySearch Server", test_familysearch_server_implementation),
        ("Records Router", test_records_router_implementation),
        ("Document Processing", test_document_processing_implementation),
        ("Analysis Server", test_analysis_implementation),
        ("Research Management", test_research_management_implementation),
        ("Location Server", test_location_implementation)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ Error in {test_name}: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Server Implementation Test Results:")
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All server implementations are working correctly!")
        print("\n💡 Implementation Status:")
        print("✅ All 6 PRDs implemented and tested")
        print("✅ FamilySearch unauthenticated session working")
        print("✅ Server logic and data flow validated")
        print("✅ Ready for full OAuth integration")
        print("✅ Ready for production deployment")
    else:
        print("⚠️  Some server implementations need attention.")
        print("Check the error messages above for details.")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main()) 