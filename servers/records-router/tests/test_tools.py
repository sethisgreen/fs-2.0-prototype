
import pytest
from mcp_kit import ProxyMCP
from servers.records_router import server

@pytest.fixture(scope="module")
def mcp():
    return server.proxy

def test_search_records_mock(mcp):
    tool = mcp.get_tool("search_records")
    # Should return merged mock data from FamilySearch
    result = tool.fn(query="John", providers=["familysearch"], filters={})
    assert isinstance(result, list)
    assert any("name" in r for r in result)

def test_merge_results(mcp):
    tool = mcp.get_tool("merge_results")
    mock_results = [[{"name": "John Doe"}], [{"name": "John Doe"}], [{"name": "Jane Smith"}]]
    merged = tool.fn(results=mock_results)
    assert len(merged) == 2
    names = [r["name"] for r in merged]
    assert "John Doe" in names and "Jane Smith" in names 