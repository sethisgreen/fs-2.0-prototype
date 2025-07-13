#### PRD 4: Analysis Server

**Overview**  
Performs computations on structured data, such as building timelines or detecting conflicts, to aid agentic decision-making.

**Goals/Objectives**

- Derive insights like relationships from raw facts.
- Suggest research next steps based on gaps.
- Enable AI validation loops.

**Scope**  
In: Core analytics tools.  
Out: Full ML models (start rule-based).

**Functional Requirements**

- Tools:
  - `calculate_relationship(person_a: Dict, person_b: Dict) -> str`: Computes degrees (e.g., "second cousin").
  - `build_timeline(events: List[Dict]) -> List[Dict]`: Sorts and visualizes events.
  - `detect_duplicates(records: List[Dict]) -> List[Dict]`: Flags matches via fuzzy scoring.
  - `suggest_next_steps(gaps: List[str]) -> List[str]`: AI-prompted recommendations (e.g., "Search 1930 census").
- Error Handling: Handle incomplete data gracefully.

**Non-Functional Requirements**

- Performance: <1s per analysis.
- Explainability: Include reasoning in outputs.

**Dependencies**

- Data from Records/Document servers.
- Libs: rapidfuzz, pandas.

**Milestones**

- v0.1: Relationship + duplicate tools (1 week).
- v0.2: Timeline + suggestions (2 weeks).
- v1.0: Validation with test datasets (1 week).
