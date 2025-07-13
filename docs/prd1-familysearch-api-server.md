#### PRD 1: FamilySearch API Server

**Overview**  
This server acts as a dedicated connector for FamilySearch's API, exposing tools for authenticated searches and data retrieval. It isolates provider-specific logic (auth, rate limits) while outputting standardized data for upstream consumption.

**Goals/Objectives**

- Enable secure, rate-limited access to FamilySearch historical records (census, vitals).
- Support AI-agent workflows by returning parseable, GEDCOM X-aligned JSON.
- Minimize external calls through caching to comply with ToS.

**Scope**  
In: Authentication, core search tools, basic parsing.  
Out: Full tree management (use FamilySearch directly); image downloads (link only).

**Functional Requirements**

- Tools:
  - `authenticate_user(client_id: str, redirect_uri: str = None) -> dict`: Handles OAuth Code Flow; returns token with expiry.
  - `search_census_records(given_name: str, surname: str, year: int, place: str = None, max_results: int = 20) -> List[Dict]`: Queries /records/search; returns [{ "name": str, "birthDate": str, "residencePlace": str, "recordUrl": str, "fsId": str }].
  - `search_vital_records(event_type: str, name: str, date_range: tuple, place: str = None) -> List[Dict]`: Similar for birth/death/marriage.
  - `get_record_by_id(fs_id: str) -> Dict`: Fetches full record/household details.
- Utilities: `@retry_on_429`, `@cache(ttl=86400)`, `normalize_place(place: str) -> str`.
- Error Handling: Raise custom exceptions for 401/429/400; return friendly messages.

**Non-Functional Requirements**

- Performance: <2s response time; handle 10 concurrent calls.
- Security: Env-based creds; no credential logging.
- Reliability: 99% uptime; auto token refresh.
- Scalability: Async I/O; Docker-ready.

**Dependencies**

- Python libs: httpx, async-lru, pydantic.
- External: FamilySearch developer account.

**Milestones**

- v0.1: Scaffold + auth tool (1 week).
- v0.2: Search tools + tests (1 week).
- v1.0: Full integration testing with sample data (1 week).
