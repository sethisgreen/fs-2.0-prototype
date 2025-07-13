#### PRD 6: Location Server

**Overview**  
Manages geographic data, including historical place names and maps, to contextualize records.

**Goals/Objectives**

- Resolve place ambiguities (e.g., historical renames).
- Integrate with searches for better filtering.
- Provide visual aids like map links.

**Scope**  
In: Place normalization, basic geo-queries.  
Out: Full mapping UI (links only).

**Functional Requirements**

- Tools:
  - `normalize_historical_place(place: str, year: int) -> str`: Resolves changes (e.g., "Prussia" to modern).
  - `get_historical_map(place: str, year: int) -> str`: Returns embeddable URL (e.g., from public APIs).
  - `geocode_place(place: str) -> Dict`: Lat/long if available.
- Error Handling: Fallback to original if unresolved.

**Non-Functional Requirements**

- Performance: <1s per query.
- Accuracy: Use reliable sources; cache frequently.

**Dependencies**

- External: Free geo APIs (e.g., GeoNames).
- Libs: geopy or similar.

**Milestones**

- v0.1: Normalization tool (1 week).
- v0.2: Map + geocode (1 week).
- v1.0: Integration tests (1 week).
