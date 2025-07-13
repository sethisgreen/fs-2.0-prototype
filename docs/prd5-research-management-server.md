#### PRD 5: Research Management Server

**Overview**  
Tracks sessions, sources, and outputs for organized, reproducible research.

**Goals/Objectives**

- Maintain audit trails for citations and logs.
- Flag conflicts and generate reports.
- Support export to formats like CSV/GEDCOM.

**Scope**  
In: Logging, citation, conflict tools.  
Out: Full UI (API-only).

**Functional Requirements**

- Tools:
  - `log_research_session(query: str, results: List[Dict]) -> str`: Persists to DB with timestamp.
  - `track_sources(record: Dict) -> Dict`: Adds citation blob.
  - `generate_citations(sources: List[Dict]) -> str`: Formats in Chicago style.
  - `flag_conflicts(events: List[Dict]) -> List[str]`: Detects inconsistencies (e.g., overlapping dates).
- Utilities: DB wrappers for insert/query.

**Non-Functional Requirements**

- Storage: SQLite MVP; scale to Postgres.
- Security: Encrypt personal data at rest.

**Dependencies**

- Outputs from other servers.
- Libs: asyncpg, redis (caching).

**Milestones**

- v0.1: Logging + citation tools (1 week).
- v0.2: Conflict flagging (1 week).
- v1.0: Export features + tests (1 week).
