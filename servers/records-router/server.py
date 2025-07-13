

import os
from typing import List, Dict
from mcp_kit import ProxyMCP, McpTarget, Tool, Content, TextContent
from pydantic import BaseModel
from rapidfuzz import fuzz
import dotenv

dotenv.load_dotenv()

class SearchQuery(BaseModel):
    query: str
    providers: List[str] = ['familysearch']
    filters: Dict = {}

async def search_records(query: str, providers: List[str] = ['familysearch'], filters: Dict = {}) -> List[Dict]:
    # Proxy calls to sub-servers
    results = []
    for provider in providers:
        proxy = ProxyMCP(target=McpTarget(name=provider, url=os.getenv(f'{provider.upper()}_MCP_URL')))
        sub_results = await proxy.call_tool('search_census_records', {'query': query})  # Example call
        results.extend(sub_results)
    return merge_results(results)

def merge_results(results: List[List[Dict]]) -> List[Dict]:
    # Deduplicate using rapidfuzz
    merged = []
    for res in results:
        for item in res:
            if not any(fuzz.ratio(item['name'], m['name']) > 90 for m in merged):
                merged.append(item)
    return sorted(merged, key=lambda x: x.get('relevance', 0), reverse=True)

# Implement filter_records similarly

# MCP Server setup
proxy = ProxyMCP(target=McpTarget(name='records-router', url='http://localhost:8002/mcp'))

if __name__ == '__main__':
    proxy.run() 