#!/usr/bin/env python3
"""
Simple test script for FamilySearch Web Search functionality
"""
import asyncio
import structlog
from server import search_familysearch_records, search_census_records, search_vital_records

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
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

async def test_search_functionality():
    """Test the search functionality"""
    logger.info("Testing FamilySearch search functionality")
    
    try:
        # Test basic search
        logger.info("Testing basic search...")
        results = await search_familysearch_records(
            given_name="John",
            surname="Smith",
            year=1850,
            max_results=3
        )
        
        logger.info(f"Basic search returned {len(results)} results")
        for i, result in enumerate(results):
            logger.info(f"Result {i+1}: {result.get('title', 'No title')}")
        
        return True
        
    except Exception as e:
        logger.error(f"Search test failed: {e}")
        return False

async def main():
    """Run the test"""
    success = await test_search_functionality()
    
    if success:
        print("✓ Test passed!")
    else:
        print("✗ Test failed!")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())