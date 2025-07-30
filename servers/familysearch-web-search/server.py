import os
import json
import asyncio
from typing import List, Dict, Optional, Any
from urllib.parse import quote_plus, urlencode
from mcp.server import FastMCP
from pydantic import BaseModel, Field
import httpx
from async_lru import alru_cache
import dotenv
from bs4 import BeautifulSoup
import re
from datetime import datetime
import structlog

from config import settings
from rate_limiter import RateLimiter, RetryHandler

dotenv.load_dotenv()

# Configure structured logging
logger = structlog.get_logger()

class SearchResult(BaseModel):
    """Represents a search result from FamilySearch"""
    title: str
    url: str
    record_type: str
    date_range: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    fs_id: Optional[str] = None

class SearchRequest(BaseModel):
    """Request model for search operations"""
    given_name: Optional[str] = None
    surname: Optional[str] = None
    year: Optional[int] = None
    year_range: Optional[str] = None
    location: Optional[str] = None
    record_type: Optional[str] = None
    max_results: int = Field(default=20, ge=1, le=100)

class FamilySearchWebSearcher:
    """Handles web scraping of FamilySearch public website"""
    
    def __init__(self):
        self.base_url = settings.familysearch_base_url
        self.session = None
        self.custom_user_agent = settings.custom_user_agent
        self.rate_limiter = RateLimiter(
            requests_per_minute=settings.requests_per_minute,
            requests_per_hour=settings.requests_per_hour
        )
        self.retry_handler = RetryHandler(
            max_retries=settings.max_retries,
            base_delay=settings.retry_delay,
            max_delay=settings.retry_backoff * settings.max_retries
        )
        self.cache = {}
        self.cache_ttl = settings.cache_ttl
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = httpx.AsyncClient(
            headers={
                "User-Agent": self.custom_user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
            timeout=settings.request_timeout,
            follow_redirects=True
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.aclose()
    
    async def search_records(self, search_request: SearchRequest) -> List[SearchResult]:
        """Search FamilySearch records using web interface"""
        
        # Generate cache key
        cache_key = f"{search_request.given_name}_{search_request.surname}_{search_request.year}_{search_request.location}_{search_request.record_type}_{search_request.max_results}"
        
        # Check cache
        import time
        current_time = time.time()
        if cache_key in self.cache:
            cached_result, cache_time = self.cache[cache_key]
            if current_time - cache_time < self.cache_ttl:
                logger.info("Returning cached result", cache_key=cache_key)
                return cached_result
            else:
                # Remove expired cache entry
                del self.cache[cache_key]
        
        async def _perform_search():
            # Acquire rate limit permission
            await self.rate_limiter.acquire()
            
            # Build search URL
            search_params = {}
            if search_request.given_name:
                search_params["givenName"] = search_request.given_name
            if search_request.surname:
                search_params["surname"] = search_request.surname
            if search_request.year:
                search_params["eventDate"] = str(search_request.year)
            if search_request.location:
                search_params["place"] = search_request.location
            
            # Add record type filter if specified
            if search_request.record_type:
                search_params["recordType"] = search_request.record_type
            
            search_url = f"{self.base_url}/search/records/results"
            if search_params:
                search_url += "?" + urlencode(search_params)
            
            logger.info("Searching FamilySearch", url=search_url, params=search_params)
            
            response = await self.session.get(search_url)
            response.raise_for_status()
            
            # Parse HTML response
            soup = BeautifulSoup(response.text, 'html.parser')
            results = self._parse_search_results(soup, search_request.max_results)
            
            logger.info("Search completed", result_count=len(results))
            return results
        
        # Execute with retry logic
        results = await self.retry_handler.execute_with_retry(_perform_search)
        
        # Cache the results
        self.cache[cache_key] = (results, current_time)
        
        return results
    
    def _parse_search_results(self, soup: BeautifulSoup, max_results: int) -> List[SearchResult]:
        """Parse search results from HTML"""
        results = []
        
        # Look for search result containers
        result_containers = soup.find_all("div", class_=re.compile(r"search-result|record-item"))
        
        for container in result_containers[:max_results]:
            try:
                # Extract title and URL
                title_elem = container.find("a", href=True)
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                url = title_elem["href"]
                if not url.startswith("http"):
                    url = self.base_url + url
                
                # Extract record type
                record_type = self._extract_record_type(container)
                
                # Extract date range
                date_range = self._extract_date_range(container)
                
                # Extract location
                location = self._extract_location(container)
                
                # Extract description
                description = self._extract_description(container)
                
                # Extract FS ID if available
                fs_id = self._extract_fs_id(container)
                
                result = SearchResult(
                    title=title,
                    url=url,
                    record_type=record_type,
                    date_range=date_range,
                    location=location,
                    description=description,
                    fs_id=fs_id
                )
                results.append(result)
                
            except Exception as e:
                logger.warning("Error parsing search result", error=str(e))
                continue
        
        return results
    
    def _extract_record_type(self, container) -> str:
        """Extract record type from container"""
        # Look for record type indicators
        type_indicators = container.find_all(text=re.compile(r"Census|Birth|Death|Marriage|Immigration|Military", re.I))
        if type_indicators:
            return type_indicators[0].strip()
        return "Unknown"
    
    def _extract_date_range(self, container) -> Optional[str]:
        """Extract date range from container"""
        date_pattern = re.compile(r'\d{4}(?:\s*-\s*\d{4})?')
        date_elem = container.find(text=date_pattern)
        if date_elem:
            return date_pattern.search(date_elem).group()
        return None
    
    def _extract_location(self, container) -> Optional[str]:
        """Extract location from container"""
        location_elem = container.find(text=re.compile(r'[A-Z][a-z]+,\s*[A-Z]{2}|[A-Z][a-z]+,\s*[A-Z][a-z]+'))
        if location_elem:
            return location_elem.strip()
        return None
    
    def _extract_description(self, container) -> Optional[str]:
        """Extract description from container"""
        desc_elem = container.find("p", class_=re.compile(r"description|summary"))
        if desc_elem:
            return desc_elem.get_text(strip=True)
        return None
    
    def _extract_fs_id(self, container) -> Optional[str]:
        """Extract FamilySearch ID from container"""
        # Look for FS ID in data attributes or links
        fs_id_elem = container.find(attrs={"data-fs-id": True})
        if fs_id_elem:
            return fs_id_elem["data-fs-id"]
        return None

# MCP Tools
async def search_familysearch_records(
    given_name: Optional[str] = None,
    surname: Optional[str] = None,
    year: Optional[int] = None,
    location: Optional[str] = None,
    record_type: Optional[str] = None,
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """
    Search FamilySearch public website for genealogical records.
    
    Args:
        given_name: First/given name to search for
        surname: Last name/surname to search for
        year: Year to search around
        location: Location to search in
        record_type: Type of record (census, birth, death, marriage, etc.)
        max_results: Maximum number of results to return (1-100)
    
    Returns:
        List of search results with record details
    """
    search_request = SearchRequest(
        given_name=given_name,
        surname=surname,
        year=year,
        location=location,
        record_type=record_type,
        max_results=max_results
    )
    
    async with FamilySearchWebSearcher() as searcher:
        results = await searcher.search_records(search_request)
        return [result.dict() for result in results]

async def search_census_records(
    given_name: str,
    surname: str,
    year: int,
    location: Optional[str] = None,
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """
    Search specifically for census records on FamilySearch.
    
    Args:
        given_name: First/given name
        surname: Last name/surname
        year: Census year
        location: Location to search in
        max_results: Maximum number of results to return
    
    Returns:
        List of census record results
    """
    return await search_familysearch_records(
        given_name=given_name,
        surname=surname,
        year=year,
        location=location,
        record_type="census",
        max_results=max_results
    )

async def search_vital_records(
    given_name: str,
    surname: str,
    record_type: str = "birth",  # birth, death, marriage
    year: Optional[int] = None,
    location: Optional[str] = None,
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """
    Search for vital records (birth, death, marriage) on FamilySearch.
    
    Args:
        given_name: First/given name
        surname: Last name/surname
        record_type: Type of vital record (birth, death, marriage)
        year: Year to search around
        location: Location to search in
        max_results: Maximum number of results to return
    
    Returns:
        List of vital record results
    """
    return await search_familysearch_records(
        given_name=given_name,
        surname=surname,
        year=year,
        location=location,
        record_type=record_type,
        max_results=max_results
    )

# MCP Server setup
server = FastMCP(
    name=settings.server_name,
    instructions="FamilySearch Web Search MCP Server - Search FamilySearch's public website for genealogical records using web scraping techniques."
)

# Register tools
@server.tool(
    name="search_familysearch_records",
    description="Search FamilySearch public website for genealogical records using web interface"
)
async def search_familysearch_records_tool(
    given_name: Optional[str] = None,
    surname: Optional[str] = None,
    year: Optional[int] = None,
    location: Optional[str] = None,
    record_type: Optional[str] = None,
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """Search FamilySearch public website for genealogical records."""
    return await search_familysearch_records(
        given_name=given_name,
        surname=surname,
        year=year,
        location=location,
        record_type=record_type,
        max_results=max_results
    )

@server.tool(
    name="search_census_records",
    description="Search specifically for census records on FamilySearch"
)
async def search_census_records_tool(
    given_name: str,
    surname: str,
    year: int,
    location: Optional[str] = None,
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """Search specifically for census records on FamilySearch."""
    return await search_census_records(
        given_name=given_name,
        surname=surname,
        year=year,
        location=location,
        max_results=max_results
    )

@server.tool(
    name="search_vital_records",
    description="Search for vital records (birth, death, marriage) on FamilySearch"
)
async def search_vital_records_tool(
    given_name: str,
    surname: str,
    record_type: str = "birth",  # birth, death, marriage
    year: Optional[int] = None,
    location: Optional[str] = None,
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """Search for vital records (birth, death, marriage) on FamilySearch."""
    return await search_vital_records(
        given_name=given_name,
        surname=surname,
        record_type=record_type,
        year=year,
        location=location,
        max_results=max_results
    )

if __name__ == '__main__':
    # Run the MCP server
    server.run(transport="streamable-http")