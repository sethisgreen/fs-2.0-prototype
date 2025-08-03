

import os
import json
from typing import List, Dict, Optional
from mcp_kit import ProxyMCP, Tool
from pydantic import BaseModel
import httpx
import structlog
from rapidfuzz import fuzz

logger = structlog.get_logger()

# --- Models ---
class SearchResult(BaseModel):
    provider: str
    name: str
    birthDate: Optional[str]
    deathDate: Optional[str]
    residencePlace: Optional[str]
    recordUrl: str
    fsId: str
    confidence: float

class SearchRequest(BaseModel):
    query: str
    providers: List[str] = ["familysearch"]
    filters: Dict = {}

# --- Configuration ---
FAMILYSEARCH_MCP_URL = os.getenv("FAMILYSEARCH_MCP_URL", "http://localhost:8001/mcp")

# --- Utilities ---
def calculate_confidence(query: str, result: Dict) -> float:
    """Calculate confidence score for search result."""
    name = result.get('name', '')
    if not name:
        return 0.0
    
    # Use fuzzy string matching
    ratio = fuzz.ratio(query.lower(), name.lower())
    return ratio / 100.0

def merge_search_results(results: List[Dict]) -> List[Dict]:
    """Merge and deduplicate search results."""
    seen = set()
    merged = []
    
    for result in results:
        # Create a unique key for deduplication
        key = f"{result.get('name', '')}_{result.get('fsId', '')}"
        if key not in seen:
            seen.add(key)
            merged.append(result)
    
    # Sort by confidence score
    merged.sort(key=lambda x: x.get('confidence', 0.0), reverse=True)
    return merged

async def call_familysearch_api(tool_name: str, params: Dict = None) -> List[Dict]:
    """Call FamilySearch API via MCP server."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FAMILYSEARCH_MCP_URL}/call_tool",
                json={
                    "name": tool_name,
                    "arguments": params or {}
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result.get('content', [])
    except Exception as e:
        logger.error("Error calling FamilySearch MCP server", error=str(e))
        return []

# --- Tool Implementations ---
async def search_records(query: str, providers: List[str] = ["familysearch"], filters: Dict = {}) -> List[Dict]:
    """Routes to sub-servers (e.g., FamilySearch), merges into standardized list."""
    logger.info("Searching records", query=query, providers=providers, filters=filters)
    
    all_results = []
    
    for provider in providers:
        if provider == "familysearch":
            # Try different search approaches
            results = []
            
            # 1. Try collections info (works with unauthenticated session)
            try:
                collections = await call_familysearch_api("get_familysearch_collections")
                if collections:
                    logger.info(f"Retrieved {len(collections)} FamilySearch collections")
                    # Add collection info as metadata
                    for collection in collections:
                        results.append({
                            'provider': 'familysearch',
                            'name': f"Collection: {collection.get('title', 'Unknown')}",
                            'birthDate': None,
                            'deathDate': None,
                            'residencePlace': None,
                            'recordUrl': f"https://familysearch.org/collections/{collection.get('id', '')}",
                            'fsId': collection.get('id', ''),
                            'confidence': 0.8,
                            'type': 'collection_info'
                        })
            except Exception as e:
                logger.warning("Could not retrieve collections", error=str(e))
            
            # 2. Try tree info (works with unauthenticated session)
            try:
                tree_info = await call_familysearch_api("get_familysearch_tree_info")
                if tree_info:
                    logger.info("Retrieved FamilySearch tree information")
                    results.append({
                        'provider': 'familysearch',
                        'name': f"Family Tree: {tree_info.get('title', 'FamilySearch Family Tree')}",
                        'birthDate': None,
                        'deathDate': None,
                        'residencePlace': None,
                        'recordUrl': "https://familysearch.org/tree",
                        'fsId': tree_info.get('collection_id', 'FSFT'),
                        'confidence': 0.9,
                        'type': 'tree_info'
                    })
            except Exception as e:
                logger.warning("Could not retrieve tree info", error=str(e))
            
            # 3. Try records info (works with unauthenticated session)
            try:
                records_info = await call_familysearch_api("get_familysearch_records_info")
                if records_info:
                    logger.info("Retrieved FamilySearch records information")
                    results.append({
                        'provider': 'familysearch',
                        'name': f"Records: {records_info.get('title', 'FamilySearch Historical Records')}",
                        'birthDate': None,
                        'deathDate': None,
                        'residencePlace': None,
                        'recordUrl': "https://familysearch.org/search",
                        'fsId': records_info.get('collection_id', 'FSHRA'),
                        'confidence': 0.9,
                        'type': 'records_info'
                    })
            except Exception as e:
                logger.warning("Could not retrieve records info", error=str(e))
            
            # 4. Try actual search (requires full authentication)
            try:
                # Extract name parts from query for search
                name_parts = query.split()
                if len(name_parts) >= 2:
                    given_name = name_parts[0]
                    surname = name_parts[-1]
                    year = filters.get('year', 1850)  # Default year
                    place = filters.get('place')
                    
                    search_results = await call_familysearch_api("search_census_records", {
                        'given_name': given_name,
                        'surname': surname,
                        'year': year,
                        'place': place,
                        'max_results': 10
                    })
                    
                    if search_results:
                        logger.info(f"Retrieved {len(search_results)} search results")
                        for result in search_results:
                            result['provider'] = 'familysearch'
                            result['confidence'] = calculate_confidence(query, result)
                            result['type'] = 'search_result'
                            results.append(result)
            except Exception as e:
                logger.warning("Could not perform search (may require full authentication)", error=str(e))
            
            all_results.extend(results)
    
    # Merge and deduplicate results
    merged_results = merge_search_results(all_results)
    
    logger.info(f"Returning {len(merged_results)} merged results")
    return merged_results

async def get_provider_info(provider: str = "familysearch") -> Dict:
    """Get information about a specific provider."""
    logger.info("Getting provider info", provider=provider)
    
    if provider == "familysearch":
        try:
            # Get collections info
            collections = await call_familysearch_api("get_familysearch_collections")
            tree_info = await call_familysearch_api("get_familysearch_tree_info")
            records_info = await call_familysearch_api("get_familysearch_records_info")
            
            return {
                'provider': 'familysearch',
                'name': 'FamilySearch',
                'description': 'FamilySearch Family Tree and Historical Records',
                'collections_count': len(collections) if collections else 0,
                'tree_available': bool(tree_info),
                'records_available': bool(records_info),
                'authentication_required': True,
                'limited_access_available': True
            }
        except Exception as e:
            logger.error("Error getting FamilySearch provider info", error=str(e))
            return {
                'provider': 'familysearch',
                'name': 'FamilySearch',
                'description': 'FamilySearch Family Tree and Historical Records',
                'error': str(e)
            }
    
    return {
        'provider': provider,
        'name': 'Unknown Provider',
        'description': 'Provider information not available'
    }

async def test_provider_connectivity(provider: str = "familysearch") -> Dict:
    """Test connectivity to a specific provider."""
    logger.info("Testing provider connectivity", provider=provider)
    
    if provider == "familysearch":
        try:
            # Test with collections endpoint (works with unauthenticated session)
            collections = await call_familysearch_api("get_familysearch_collections")
            
            return {
                'provider': 'familysearch',
                'status': 'connected',
                'collections_accessible': bool(collections),
                'collections_count': len(collections) if collections else 0,
                'authentication_type': 'unauthenticated_session',
                'full_search_available': False,  # Requires full OAuth
                'limited_access_available': True
            }
        except Exception as e:
            return {
                'provider': 'familysearch',
                'status': 'error',
                'error': str(e),
                'authentication_type': 'unknown',
                'full_search_available': False,
                'limited_access_available': False
            }
    
    return {
        'provider': provider,
        'status': 'unknown',
        'error': 'Provider not implemented'
    }

# --- MCP Server Setup ---
proxy = ProxyMCP()

proxy.add_tool(Tool(
    name="search_records",
    description="Routes to sub-servers (e.g., FamilySearch), merges into standardized list.",
    fn=search_records,
    input_model=BaseModel.construct(__fields__={
        'query': (str, ...),
        'providers': (List[str], ["familysearch"]),
        'filters': (Dict, {})
    }),
    output_model=List[SearchResult]
))

proxy.add_tool(Tool(
    name="get_provider_info",
    description="Get information about a specific provider.",
    fn=get_provider_info,
    input_model=BaseModel.construct(__fields__={
        'provider': (str, "familysearch")
    }),
    output_model=Dict
))

proxy.add_tool(Tool(
    name="test_provider_connectivity",
    description="Test connectivity to a specific provider.",
    fn=test_provider_connectivity,
    input_model=BaseModel.construct(__fields__={
        'provider': (str, "familysearch")
    }),
    output_model=Dict
))

if __name__ == '__main__':
    logger.info("Starting Records Router MCP server...")
    proxy.run() 