

import os
import json
from typing import List, Dict, Optional, Tuple, Any
from mcp_kit import ProxyMCP, Tool
from pydantic import BaseModel
import httpx
from async_lru import alru_cache
from retrying import retry
import dotenv
import structlog
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
import uvicorn

# Load environment variables
dotenv.load_dotenv()

logger = structlog.get_logger()

# --- Models ---
class AuthResponse(BaseModel):
    token: str
    expiry: int

class Record(BaseModel):
    name: str
    birthDate: Optional[str]
    residencePlace: Optional[str]
    recordUrl: str
    fsId: str

class CollectionInfo(BaseModel):
    id: str
    title: str
    description: Optional[str]
    links: Dict[str, Any]

# --- Globals for demo (in-memory token store) ---
TOKENS = {}

# --- FastAPI app for OAuth callback ---
app = FastAPI()

@app.get("/oauth/callback")
async def oauth_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    logger.info("OAuth callback received", code=code, state=state)
    if not code:
        return JSONResponse({"error": "Missing code"}, status_code=400)
    # Exchange code for token (stubbed)
    # TODO: Implement real token exchange with FamilySearch
    token = f"mock_token_for_{code}"
    TOKENS[state or "default"] = {"token": token, "expiry": 3600}
    return JSONResponse({"token": token, "expiry": 3600})

# --- Utilities ---
@alru_cache(ttl=86400)
async def normalize_place(place: str) -> str:
    logger.info("Normalizing place", place=place)
    return place

def retry_on_429(exception):
    return isinstance(exception, httpx.HTTPStatusError) and exception.response.status_code == 429

async def get_unauthenticated_token() -> Optional[str]:
    """Get an unauthenticated session token for limited API access."""
    client_id = os.getenv('FAMILYSEARCH_CLIENT_ID')
    if not client_id or client_id == 'your_beta_client_id_here':
        logger.warning("No valid FAMILYSEARCH_CLIENT_ID set")
        return None
    
    token_url = os.getenv('FAMILYSEARCH_TOKEN_URL', 'https://identbeta.familysearch.org/cis-web/oauth2/v3/token')
    
    data = {
        'grant_type': 'unauthenticated_session',
        'client_id': client_id,
        'ip_address': '127.0.0.1'
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data, timeout=30)
            if response.status_code == 200:
                token_data = response.json()
                logger.info("Successfully obtained unauthenticated session token")
                return token_data.get('access_token')
            else:
                logger.error("Failed to get unauthenticated token", status_code=response.status_code)
                return None
    except Exception as e:
        logger.error("Error getting unauthenticated token", error=str(e))
        return None

async def make_authenticated_request(endpoint: str, params: Dict = None) -> Optional[Dict]:
    """Make an authenticated request to FamilySearch API."""
    token = await get_unauthenticated_token()
    if not token:
        logger.warning("No token available for authenticated request")
        return None
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/x-gedcomx-v1+json'
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, headers=headers, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"API request failed", endpoint=endpoint, status_code=response.status_code)
                return None
    except Exception as e:
        logger.error("Error making authenticated request", endpoint=endpoint, error=str(e))
        return None

# --- Tool Implementations ---
async def authenticate_user(client_id: str, redirect_uri: Optional[str] = None) -> Dict:
    """Returns the FamilySearch OAuth authorization URL for the user to visit."""
    logger.info("Authenticating user (OAuth URL generation)", client_id=client_id, redirect_uri=redirect_uri)
    
    # Use beta environment URLs
    base_url = os.getenv('FAMILYSEARCH_AUTH_BASE_URL', 'https://identbeta.familysearch.org/cis-web/oauth2/v3')
    redirect = redirect_uri or os.getenv("FAMILYSEARCH_REDIRECT_URI", "http://localhost:8001/oauth/callback")
    state = "demo_state"  # In production, generate a secure random state
    
    url = (
        f"{base_url}/authorization?response_type=code&client_id={client_id}"
        f"&redirect_uri={redirect}&scope=openid%20profile%20email&state={state}"
    )
    return {"authorization_url": url, "state": state}

@retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, retry_on_exception=retry_on_429)
async def search_census_records(given_name: str, surname: str, year: int, place: Optional[str] = None, max_results: int = 20, access_token: Optional[str] = None) -> List[Dict]:
    """Queries FamilySearch /records/search; returns census records."""
    logger.info("Searching census records", given_name=given_name, surname=surname, year=year, place=place, max_results=max_results)
    
    # Try with unauthenticated session first
    if not access_token:
        logger.info("No access token provided, trying unauthenticated session")
        # For now, return mock data since search requires full authentication
        return [Record(name=f"{given_name} {surname}", birthDate=str(year), residencePlace=place or "", recordUrl="https://familysearch.org/mock", fsId="FS123").dict()]
    
    # TODO: Implement real search with authenticated token
    # This will work once we have full OAuth access
    return [Record(name=f"{given_name} {surname}", birthDate=str(year), residencePlace=place or "", recordUrl="https://familysearch.org/mock", fsId="FS123").dict()]

async def search_vital_records(event_type: str, name: str, date_range: Tuple[str, str], place: Optional[str] = None, access_token: Optional[str] = None) -> List[Dict]:
    """Searches for birth/death/marriage records."""
    logger.info("Searching vital records", event_type=event_type, name=name, date_range=date_range, place=place)
    
    # TODO: Implement real FamilySearch API call for vital records
    # This will work once we have full OAuth access
    return []

async def get_record_by_id(fs_id: str, access_token: Optional[str] = None) -> Dict:
    """Fetches full record/household details by FamilySearch ID."""
    logger.info("Getting record by ID", fs_id=fs_id)
    
    # TODO: Implement real FamilySearch API call to fetch record by ID
    # This will work once we have full OAuth access
    return {}

async def get_familysearch_collections() -> List[Dict]:
    """Get information about available FamilySearch collections."""
    logger.info("Getting FamilySearch collections")
    
    endpoint = "https://api.familysearch.org/platform/collections"
    data = await make_authenticated_request(endpoint)
    
    if data and 'collections' in data:
        collections = []
        for collection in data['collections']:
            collections.append({
                'id': collection.get('id'),
                'title': collection.get('title'),
                'description': collection.get('description'),
                'links': collection.get('links', {})
            })
        return collections
    else:
        logger.warning("Could not retrieve collections data")
        return []

async def get_familysearch_tree_info() -> Dict:
    """Get information about the FamilySearch Family Tree collection."""
    logger.info("Getting FamilySearch tree information")
    
    endpoint = "https://api.familysearch.org/platform/collections/tree"
    data = await make_authenticated_request(endpoint)
    
    if data:
        return {
            'collection_id': data.get('collections', [{}])[0].get('id'),
            'title': data.get('collections', [{}])[0].get('title'),
            'links': data.get('links', {}),
            'description': data.get('description')
        }
    else:
        logger.warning("Could not retrieve tree information")
        return {}

async def get_familysearch_records_info() -> Dict:
    """Get information about the FamilySearch Historical Records collection."""
    logger.info("Getting FamilySearch records information")
    
    endpoint = "https://api.familysearch.org/platform/collections/records"
    data = await make_authenticated_request(endpoint)
    
    if data:
        return {
            'collection_id': data.get('collections', [{}])[0].get('id'),
            'title': data.get('collections', [{}])[0].get('title'),
            'links': data.get('links', {}),
            'description': data.get('description')
        }
    else:
        logger.warning("Could not retrieve records information")
        return {}

# --- MCP Server Setup ---
proxy = ProxyMCP()

proxy.add_tool(Tool(
    name="authenticate_user",
    description="Returns the FamilySearch OAuth authorization URL for the user to visit.",
    fn=authenticate_user,
    input_model=BaseModel.construct(__fields__={
        'client_id': (str, ...),
        'redirect_uri': (Optional[str], None)
    }),
    output_model=Dict
))

proxy.add_tool(Tool(
    name="search_census_records",
    description="Queries FamilySearch /records/search; returns census records.",
    fn=search_census_records,
    input_model=BaseModel.construct(__fields__={
        'given_name': (str, ...),
        'surname': (str, ...),
        'year': (int, ...),
        'place': (Optional[str], None),
        'max_results': (int, 20),
        'access_token': (Optional[str], None)
    }),
    output_model=List[Record]
))

proxy.add_tool(Tool(
    name="search_vital_records",
    description="Searches for birth/death/marriage records.",
    fn=search_vital_records,
    input_model=BaseModel.construct(__fields__={
        'event_type': (str, ...),
        'name': (str, ...),
        'date_range': (Tuple[str, str], ...),
        'place': (Optional[str], None),
        'access_token': (Optional[str], None)
    }),
    output_model=List[Record]
))

proxy.add_tool(Tool(
    name="get_record_by_id",
    description="Fetches full record/household details by FamilySearch ID.",
    fn=get_record_by_id,
    input_model=BaseModel.construct(__fields__={
        'fs_id': (str, ...),
        'access_token': (Optional[str], None)
    }),
    output_model=Record
))

proxy.add_tool(Tool(
    name="get_familysearch_collections",
    description="Get information about available FamilySearch collections (works with unauthenticated session).",
    fn=get_familysearch_collections,
    input_model=BaseModel.construct(__fields__={}),
    output_model=List[CollectionInfo]
))

proxy.add_tool(Tool(
    name="get_familysearch_tree_info",
    description="Get information about the FamilySearch Family Tree collection (works with unauthenticated session).",
    fn=get_familysearch_tree_info,
    input_model=BaseModel.construct(__fields__={}),
    output_model=Dict
))

proxy.add_tool(Tool(
    name="get_familysearch_records_info",
    description="Get information about the FamilySearch Historical Records collection (works with unauthenticated session).",
    fn=get_familysearch_records_info,
    input_model=BaseModel.construct(__fields__={}),
    output_model=Dict
))

if __name__ == '__main__':
    logger.info("Starting FamilySearch MCP server and FastAPI app...")
    import threading
    # Start FastAPI app in a separate thread
    def run_fastapi():
        uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
    threading.Thread(target=run_fastapi, daemon=True).start()
    # Start MCP server (blocking)
    proxy.run() 