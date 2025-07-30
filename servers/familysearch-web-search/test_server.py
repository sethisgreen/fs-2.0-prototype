#!/usr/bin/env python3
"""
Test script for FamilySearch Web Search MCP Server
"""
import asyncio
import json
from server import search_familysearch_records, search_census_records, search_vital_records
from config import settings
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

async def test_basic_search():
    """Test basic search functionality"""
    logger.info("Testing basic search functionality")
    
    try:
        results = await search_familysearch_records(
            given_name="John",
            surname="Smith",
            year=1850,
            max_results=5
        )
        
        logger.info("Basic search completed", result_count=len(results))
        for i, result in enumerate(results):
            logger.info(f"Result {i+1}", 
                       title=result.get('title'),
                       url=result.get('url'),
                       record_type=result.get('record_type'))
        
        return len(results) > 0
        
    except Exception as e:
        logger.error("Basic search failed", error=str(e))
        return False

async def test_census_search():
    """Test census-specific search"""
    logger.info("Testing census search functionality")
    
    try:
        results = await search_census_records(
            given_name="Mary",
            surname="Johnson",
            year=1860,
            location="New York",
            max_results=3
        )
        
        logger.info("Census search completed", result_count=len(results))
        for i, result in enumerate(results):
            logger.info(f"Census Result {i+1}", 
                       title=result.get('title'),
                       record_type=result.get('record_type'),
                       date_range=result.get('date_range'))
        
        return len(results) > 0
        
    except Exception as e:
        logger.error("Census search failed", error=str(e))
        return False

async def test_vital_records_search():
    """Test vital records search"""
    logger.info("Testing vital records search functionality")
    
    try:
        results = await search_vital_records(
            given_name="William",
            surname="Brown",
            record_type="birth",
            year=1880,
            max_results=3
        )
        
        logger.info("Vital records search completed", result_count=len(results))
        for i, result in enumerate(results):
            logger.info(f"Vital Record {i+1}", 
                       title=result.get('title'),
                       record_type=result.get('record_type'),
                       location=result.get('location'))
        
        return len(results) > 0
        
    except Exception as e:
        logger.error("Vital records search failed", error=str(e))
        return False

async def test_rate_limiting():
    """Test rate limiting functionality"""
    logger.info("Testing rate limiting")
    
    try:
        # Make multiple requests quickly to test rate limiting
        tasks = []
        for i in range(3):
            task = search_familysearch_records(
                given_name=f"Test{i}",
                surname="User",
                year=1900,
                max_results=1
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_results = [r for r in results if not isinstance(r, Exception)]
        logger.info("Rate limiting test completed", 
                   total_requests=len(tasks),
                   successful_requests=len(successful_results))
        
        return len(successful_results) > 0
        
    except Exception as e:
        logger.error("Rate limiting test failed", error=str(e))
        return False

async def main():
    """Run all tests"""
    logger.info("Starting FamilySearch Web Search MCP Server tests")
    
    tests = [
        ("Basic Search", test_basic_search),
        ("Census Search", test_census_search),
        ("Vital Records Search", test_vital_records_search),
        ("Rate Limiting", test_rate_limiting),
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"Running test: {test_name}")
        try:
            result = await test_func()
            results[test_name] = result
            status = "PASSED" if result else "FAILED"
            logger.info(f"Test {test_name}: {status}")
        except Exception as e:
            results[test_name] = False
            logger.error(f"Test {test_name} failed with exception", error=str(e))
    
    # Summary
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    logger.info("Test Summary", 
               total_tests=total,
               passed_tests=passed,
               failed_tests=total - passed)
    
    print(f"\nTest Results:")
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {test_name}: {status}")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)