
import pytest
from mcp_kit import ProxyMCP
from servers.familysearch_api import server

@pytest.fixture(scope="module")
def mcp():
    return server.proxy

def test_authenticate_user(mcp):
    tool = mcp.get_tool("authenticate_user")
    result = tool.fn(client_id="demo-client-id", redirect_uri="http://localhost:8001/oauth/callback")
    assert "authorization_url" in result
    assert result["state"] == "demo_state"

def test_search_census_records_mock(mcp):
    tool = mcp.get_tool("search_census_records")
    result = tool.fn(given_name="John", surname="Doe", year=1900, place="Utah", max_results=1, access_token=None)
    assert isinstance(result, list)
    assert result[0]["name"] == "John Doe"
    assert result[0]["birthDate"] == "1900" 