#!/usr/bin/env python3
import os
import time
import uuid
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field
import structlog

# Optional import: if mcp_kit isn't available (e.g., local Python 3.13),
# fall back to a tiny HTTP shim that exposes /mcp and /call_tool.
try:
    from mcp_kit import ProxyMCP, Tool  # type: ignore
except Exception:  # pragma: no cover
    import asyncio
    import json
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from typing import Callable

    class Tool:  # minimal shim
        def __init__(self, name: str, description: str, fn: Callable, input_model: Any, output_model: Any):
            self.name = name
            self.description = description
            self.fn = fn
            self.input_model = input_model
            self.output_model = output_model

    class ProxyMCP:  # minimal shim
        def __init__(self):
            self._tools: Dict[str, Tool] = {}

        def add_tool(self, tool: Tool):
            self._tools[tool.name] = tool

        def run(self, host: str = "0.0.0.0", port: int = 8000):
            tools = self._tools

            class Handler(BaseHTTPRequestHandler):
                def _set_headers(self, code: int = 200):
                    self.send_response(code)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()

                def do_GET(self):  # noqa: N802
                    if self.path == "/mcp":
                        body = {
                            "status": "ok",
                            "tools": [
                                {"name": t.name, "description": t.description}
                                for t in tools.values()
                            ],
                        }
                        self._set_headers(200)
                        self.wfile.write(json.dumps(body).encode("utf-8"))
                    else:
                        self._set_headers(404)
                        self.wfile.write(b"{}")

                def do_POST(self):  # noqa: N802
                    if self.path == "/call_tool":
                        length = int(self.headers.get("Content-Length", "0"))
                        raw = self.rfile.read(length) if length else b"{}"
                        try:
                            payload = json.loads(raw.decode("utf-8"))
                        except Exception:
                            payload = {}
                        name = payload.get("name")
                        args = payload.get("arguments", {}) or {}
                        tool = tools.get(name)
                        if not tool:
                            self._set_headers(404)
                            self.wfile.write(json.dumps({"error": "tool_not_found"}).encode("utf-8"))
                            return
                        try:
                            result = tool.fn(**args)
                            if asyncio.iscoroutine(result):
                                result = asyncio.run(result)
                            # Pydantic BaseModel support
                            if hasattr(result, "dict"):
                                content = result.dict()
                            else:
                                content = result
                            self._set_headers(200)
                            self.wfile.write(json.dumps({"content": content}).encode("utf-8"))
                        except Exception as e:  # pragma: no cover
                            self._set_headers(500)
                            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                    else:
                        self._set_headers(404)
                        self.wfile.write(b"{}")

            httpd = HTTPServer((host, port), Handler)
            try:
                httpd.serve_forever()
            finally:
                httpd.server_close()

logger = structlog.get_logger()

FS_BASE = "https://beta.familysearch.org"
JSON = "application/json"
GX = "application/x-gedcomx-v1+json"
FS = "application/x-fs-v1+json"

SESSIONS: Dict[str, Dict[str, Any]] = {}

class SetSessionInput(BaseModel):
    access_token: str
    expires_at: Optional[int] = None

class SetSessionOutput(BaseModel):
    session_id: str
    expires_at: int

class AuthStatusInput(BaseModel):
    session_id: str

class AuthStatusOutput(BaseModel):
    is_authenticated: bool
    expires_at: Optional[int] = None

class UserCurrentInput(BaseModel):
    session_id: str

class UserCurrentOutput(BaseModel):
    user: Dict[str, Any]

class AncestryInput(BaseModel):
    session_id: str
    person_id: Optional[str] = None
    generations: int = Field(4, ge=1, le=7)

class AncestryOutput(BaseModel):
    person_id: str
    generations: int
    ancestry: Dict[str, Any]

class DescendancyInput(BaseModel):
    session_id: str
    person_id: Optional[str] = None
    generations: int = Field(3, ge=1, le=6)

class DescendancyOutput(BaseModel):
    person_id: str
    generations: int
    descendancy: Dict[str, Any]

class CollectionsOutput(BaseModel):
    collections: List[Dict[str, Any]]
    total: int

class PlacesSearchInput(BaseModel):
    session_id: str
    text: str
    count: int = 20

class PlacesSearchOutput(BaseModel):
    places: Optional[Dict[str, Any]] = None
    suggestions: Optional[Dict[str, Any]] = None
    attempts: Optional[List[Dict[str, Any]]] = None

class PlaceDetailsInput(BaseModel):
    session_id: str
    place_id: str

class PlaceDetailsOutput(BaseModel):
    place: Dict[str, Any]

class AncestryGapsInput(BaseModel):
    session_id: str
    person_id: Optional[str] = None
    generations: int = Field(4, ge=1, le=7)

class AncestryGapsOutput(BaseModel):
    gaps: Dict[str, Any]

class MatchesInput(BaseModel):
    session_id: str
    person_id: str
    limit: int = 20

class MatchesOutput(BaseModel):
    person_id: str
    matches: Dict[str, Any]

class ScoreMatchInput(BaseModel):
    session_id: str
    person_id: str
    candidate: Dict[str, Any]

class ScoreMatchOutput(BaseModel):
    score: float
    reasons: List[str]

class AttachSourceInput(BaseModel):
    session_id: str
    person_id: str
    source_uri: str
    citation: str
    confirm: bool = False

class AttachSourceOutput(BaseModel):
    status: str
    message: str

def _now_ms() -> int:
    return int(time.time() * 1000)

def _get_token(session_id: str) -> str:
    sess = SESSIONS.get(session_id)
    if not sess or not sess.get("access_token"):
        raise ValueError("Invalid session")
    if sess.get("expires_at") and _now_ms() >= sess["expires_at"]:
        raise ValueError("Session expired")
    return sess["access_token"]

async def _fs_get(token: str, path: str, accept: str = GX, params: Dict[str, Any] = None) -> httpx.Response:
    headers = {"Authorization": f"Bearer {token}", "Accept": accept}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{FS_BASE}{path}", headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp

async def _fs_json(resp: httpx.Response) -> Dict[str, Any]:
    try:
        return resp.json()
    except Exception:
        return {}

async def _resolve_current_person_id(token: str) -> str:
    r = await _fs_get(token, "/platform/users/current", JSON)
    j = await _fs_json(r)
    pid = j.get("users", [{}])[0].get("personId") or j.get("users", [{}])[0].get("links", {}).get("person", {}).get("href", "").split("/")[-1]
    if not pid:
        raise ValueError("Could not resolve current person ID")
    return pid

async def set_session(access_token: str, expires_at: Optional[int] = None) -> SetSessionOutput:
    sid = str(uuid.uuid4())
    SESSIONS[sid] = {"access_token": access_token, "expires_at": expires_at or (_now_ms() + 3600_000)}
    return SetSessionOutput(session_id=sid, expires_at=SESSIONS[sid]["expires_at"])

async def auth_status(session_id: str) -> AuthStatusOutput:
    sess = SESSIONS.get(session_id)
    ok = bool(sess and (not sess.get("expires_at") or _now_ms() < sess["expires_at"]))
    return AuthStatusOutput(is_authenticated=ok, expires_at=(sess or {}).get("expires_at"))

async def user_current(session_id: str) -> UserCurrentOutput:
    token = _get_token(session_id)
    r = await _fs_get(token, "/platform/users/current", JSON)
    return UserCurrentOutput(user=await _fs_json(r))

async def tree_ancestry(session_id: str, person_id: Optional[str] = None, generations: int = 4) -> AncestryOutput:
    token = _get_token(session_id)
    pid = person_id or await _resolve_current_person_id(token)
    r = await _fs_get(token, "/platform/tree/ancestry", GX, params={"person": pid, "generations": generations})
    return AncestryOutput(person_id=pid, generations=generations, ancestry=await _fs_json(r))

async def tree_descendancy(session_id: str, person_id: Optional[str] = None, generations: int = 3) -> DescendancyOutput:
    token = _get_token(session_id)
    pid = person_id or await _resolve_current_person_id(token)
    r = await _fs_get(token, "/platform/tree/descendancy", GX, params={"person": pid, "generations": generations})
    return DescendancyOutput(person_id=pid, generations=generations, descendancy=await _fs_json(r))

async def collections_records(session_id: str) -> CollectionsOutput:
    token = _get_token(session_id)
    r = await _fs_get(token, "/platform/collections/records", GX)
    j = await _fs_json(r)
    cols = j.get("collections", []) if isinstance(j, dict) else []
    return CollectionsOutput(collections=cols, total=len(cols))

async def places_search(session_id: str, text: str, count: int) -> PlacesSearchOutput:
    token = _get_token(session_id)
    attempts: List[Dict[str, Any]] = []

    async def try_req(accept: str, params: Dict[str, Any]):
        try:
            r = await _fs_get(token, "/platform/places/search", accept, params)
            attempts.append({"accept": accept, "params": params, "status": r.status_code})
            return await _fs_json(r)
        except httpx.HTTPStatusError as e:
            attempts.append({"accept": accept, "params": params, "status": e.response.status_code})
            return None

    parsed = await try_req("application/x-gedcomx-atom+json", {"q": f"name:{text}", "count": count})
    if not parsed:
        parsed = await try_req(GX, {"q": text, "count": count})
    if not parsed:
        parsed = await try_req(JSON, {"q": f"name:{text}"})
    if not parsed:
        parsed = await try_req(FS, {"text": text})
    if not parsed:
        parsed = await try_req(GX, {"text": text, "count": count})

    suggestions = None
    if not parsed or (isinstance(parsed, dict) and isinstance(parsed.get("entries"), list) and len(parsed["entries"]) == 0):
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{FS_BASE}/platform/places/autocomplete", headers={"Authorization": f"Bearer {token}", "Accept": JSON}, params={"text": text}, timeout=30)
            r.raise_for_status()
            suggestions = r.json()
        except Exception:
            pass

    return PlacesSearchOutput(places=parsed, suggestions=suggestions, attempts=attempts)

async def place_details(session_id: str, place_id: str) -> PlaceDetailsOutput:
    token = _get_token(session_id)
    r = await _fs_get(token, f"/platform/places/{place_id}", GX)
    return PlaceDetailsOutput(place=await _fs_json(r))

async def ancestry_gaps(session_id: str, person_id: Optional[str] = None, generations: int = 4) -> AncestryGapsOutput:
    out = await tree_ancestry(session_id, person_id, generations)
    persons = out.ancestry.get("persons") or []
    ascs: List[int] = []
    for p in persons:
        asc = p.get("display", {}).get("ascendancyNumber")
        try:
            if asc:
                ascs.append(int(asc))
        except Exception:
            pass
    expected = (2 ** generations) - 1
    have = set(ascs)
    missing_nums = [n for n in range(1, expected + 1) if n not in have]
    gaps = {
        "expectedAncestors": expected,
        "receivedPersons": len(persons),
        "missingCount": len(missing_nums),
        "missingAscendancyNumbers": missing_nums,
    }
    return AncestryGapsOutput(gaps=gaps)

async def tree_person_matches(session_id: str, person_id: str, limit: int = 20) -> MatchesOutput:
    token = _get_token(session_id)
    r = await _fs_get(token, f"/platform/tree/persons/{person_id}/matches", GX)
    data = await _fs_json(r)
    return MatchesOutput(person_id=person_id, matches=data)

def _string_similarity(a: str, b: str) -> float:
    a = (a or "").lower().strip()
    b = (b or "").lower().strip()
    if not a or not b:
        return 0.0
    # very simple token overlap
    sa = set(a.split())
    sb = set(b.split())
    inter = len(sa & sb)
    union = len(sa | sb) or 1
    return inter / union

async def score_match(session_id: str, person_id: str, candidate: Dict[str, Any]) -> ScoreMatchOutput:
    # Heuristic score based on name + lifespan overlap
    reasons: List[str] = []
    score = 0.0
    # name
    cand_name = candidate.get("display", {}).get("name") or candidate.get("title")
    if cand_name:
        reasons.append("name_present")
        score += 0.4
    # lifespan
    life = candidate.get("display", {}).get("lifespan")
    if life:
        reasons.append("lifespan_present")
        score += 0.2
    # ascendancy (if provided)
    if candidate.get("display", {}).get("ascendancyNumber"):
        reasons.append("ascendancy_hint")
        score += 0.1
    # crude text similarity between title/name and person_id (placeholder)
    score = min(1.0, max(0.0, score))
    return ScoreMatchOutput(score=score, reasons=reasons)

async def attach_source(session_id: str, person_id: str, source_uri: str, citation: str, confirm: bool = False) -> AttachSourceOutput:
    if not confirm:
        return AttachSourceOutput(status="needs_confirmation", message="Set confirm=true to attach source")
    token = _get_token(session_id)
    # Minimal POST to sources (stubbed behavior)
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{FS_BASE}/platform/tree/persons/{person_id}/sources",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": GX,
                    "Content-Type": GX,
                },
                json={
                    "sourceDescriptions": [
                        {"about": source_uri, "citations": [{"value": citation}]}
                    ]
                },
                timeout=30,
            )
            if resp.status_code >= 400:
                return AttachSourceOutput(status="error", message=f"{resp.status_code} {resp.text}")
            return AttachSourceOutput(status="attached", message="Source attached")
        except Exception as e:
            return AttachSourceOutput(status="error", message=str(e))

proxy = ProxyMCP()

proxy.add_tool(Tool(
    name="set_session",
    description="Register an access token and receive a session_id for subsequent calls.",
    fn=set_session,
    input_model=SetSessionInput,
    output_model=SetSessionOutput
))

proxy.add_tool(Tool(
    name="auth_status",
    description="Check if session is authenticated and not expired.",
    fn=auth_status,
    input_model=AuthStatusInput,
    output_model=AuthStatusOutput
))

proxy.add_tool(Tool(
    name="user_current",
    description="Get the current authenticated user profile.",
    fn=user_current,
    input_model=UserCurrentInput,
    output_model=UserCurrentOutput
))

proxy.add_tool(Tool(
    name="tree_ancestry",
    description="Get ancestry for a person (default: current user).",
    fn=tree_ancestry,
    input_model=AncestryInput,
    output_model=AncestryOutput
))

proxy.add_tool(Tool(
    name="tree_descendancy",
    description="Get descendancy for a person (default: current user).",
    fn=tree_descendancy,
    input_model=DescendancyInput,
    output_model=DescendancyOutput
))

proxy.add_tool(Tool(
    name="collections_records",
    description="List FamilySearch record collections.",
    fn=collections_records,
    input_model=AuthStatusInput,
    output_model=CollectionsOutput
))

proxy.add_tool(Tool(
    name="places_search",
    description="Search places with multi-accept fallback + autocomplete.",
    fn=places_search,
    input_model=PlacesSearchInput,
    output_model=PlacesSearchOutput
))

proxy.add_tool(Tool(
    name="place_details",
    description="Get detailed info for a place by ID.",
    fn=place_details,
    input_model=PlaceDetailsInput,
    output_model=PlaceDetailsOutput
))

proxy.add_tool(Tool(
    name="ancestry_gaps",
    description="Compute gaps in ancestry coverage over N generations.",
    fn=ancestry_gaps,
    input_model=AncestryGapsInput,
    output_model=AncestryGapsOutput
))

proxy.add_tool(Tool(
    name="tree_person_matches",
    description="Fetch potential matches (hints) for a person.",
    fn=tree_person_matches,
    input_model=MatchesInput,
    output_model=MatchesOutput
))

proxy.add_tool(Tool(
    name="score_match",
    description="Heuristically score a match candidate with reasons.",
    fn=score_match,
    input_model=ScoreMatchInput,
    output_model=ScoreMatchOutput
))

proxy.add_tool(Tool(
    name="attach_source",
    description="Attach a source to a person (confirm=true required).",
    fn=attach_source,
    input_model=AttachSourceInput,
    output_model=AttachSourceOutput
))

if __name__ == "__main__":
    logger.info("Starting FamilySearch Tools MCP server...")
    proxy.run()


