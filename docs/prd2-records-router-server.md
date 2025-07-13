#### PRD 2: Records Router Server

**Overview**  
A high-level orchestrator that proxies calls to dedicated API servers (e.g., FamilySearch, future Ancestry) and merges results. It provides a unified interface for record searches, abstracting provider details.

**Goals/Objectives**

- Centralize record queries to enable "try-all providers" strategies.
- Deduplicate and rank results for agent efficiency.
- Facilitate chaining to Analysis or Management servers.

**Scope**  
In: Routing, merging, basic filtering.  
Out: Provider-specific auth (handled downstream).

**Functional Requirements**

- Tools:
  - `search_records(query: str, providers: List[str] = ["familysearch"], filters: Dict = {}) -> List[Dict]`: Routes to sub-servers; merges into standardized list.
  - `merge_results(results: List[List[Dict]]) -> List[Dict]`: Deduplicates using rapidfuzz; ranks by relevance.
  - `filter_records(records: List[Dict], criteria: Dict) -> List[Dict]`: Applies post-filters (e.g., date range).
- Error Handling: Aggregate sub-errors; fallback to available providers.

**Non-Functional Requirements**

- Performance: <5s for multi-provider queries.
- Security: Validate inputs; log queries anonymized.
- Reliability: Graceful degradation if a sub-server fails.

**Dependencies**

- MCP tool_proxy for sub-server calls.
- Sub-servers: FamilySearch API Server (initially).

**Milestones**

- v0.1: Routing to one provider (1 week).
- v0.2: Merging + multi-provider support (1 week).
- v1.0: End-to-end workflow tests (1 week).
