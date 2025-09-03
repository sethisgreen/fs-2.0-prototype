## FamilySearch API (Beta) — Developer Reference

Purpose: quick, accurate guide for using FamilySearch (FS) API in beta with our Next.js + fs-js-lite integration, focused on collections and record collections discovery.

### Environments and Base URLs

- Production: `https://api.familysearch.org`
- Beta: `https://apibeta.familysearch.org`
- Integration: `https://api-integ.familysearch.org`

We configure fs-js-lite with `environment: "beta"`. The SDK resolves the proper host; you only pass path like `/platform/collections`.

### Authentication

- Flow: OAuth 2.0 Authorization Code (via `identbeta.familysearch.org`) → access token
- Token usage: `Authorization: Bearer <access_token>`
- Cookies: our server sets an HTTP-only cookie `fs_session` and injects the token into the SDK per request

### Content Negotiation (critical)

Many FS endpoints require a specific Accept header:

- Collections: `Accept: application/x-gedcomx-v1+json`
- Places (search): `Accept: application/json` (XML also supported)

In fs-js-lite, pass headers via the `options` argument:

```ts
fs.get(
  "/platform/collections",
  { headers: { Accept: "application/x-gedcomx-v1+json" } },
  cb
);
```

### Response Shapes (with fs-js-lite)

SDK callbacks often return an object shaped like:

- `response.data` when the client parsed JSON
- or `response.body` (string) and you must `JSON.parse(response.body)`

Use this helper to normalize:

```ts
function toJson(res: any) {
  if (res?.data) return res.data;
  if (typeof res?.body === "string") {
    try {
      return JSON.parse(res.body);
    } catch {}
  }
  return res;
}
```

### Collections (Top-Level Discovery)

- Path: `GET /platform/collections`
- Host (beta): `https://apibeta.familysearch.org/platform/collections`
- Accept: `application/x-gedcomx-v1+json`
- Response (JSON):
  - `{ "collections": [ { id, title, links: { self: { href } } }, ... ] }`

Curl example (beta):

```bash
curl -H "Authorization: Bearer $TOKEN" \
     -H "Accept: application/x-gedcomx-v1+json" \
     https://apibeta.familysearch.org/platform/collections
```

SDK example (server route):

```ts
fs.get(
  "/platform/collections",
  { headers: { Accept: "application/x-gedcomx-v1+json" } },
  (err, res) => {
    if (err) return next(err);
    const json = toJson(res); // see helper above
    const collections = json?.collections ?? [];
    // map and return
  }
);
```

### Record Collections (Historical Records)

The historical records “collection” is exposed from the top-level collections list. Use its link:

- Path: `GET /platform/collections/records`
- Accept: `application/x-gedcomx-v1+json`

Notes:

- This endpoint returns metadata for the “Historical Records” collection. Sub-collections and search interfaces are exposed via related links in the payload.
- In our current beta setup, “records search” endpoints (e.g., `/platform/records`, `/platform/records/search`) return `404 Not Found`. This likely indicates required scopes/entitlements not enabled for our app in beta.

Curl example (beta):

```bash
curl -H "Authorization: Bearer $TOKEN" \
     -H "Accept: application/x-gedcomx-v1+json" \
     https://apibeta.familysearch.org/platform/collections/records
```

Typical next steps after fetching `collections/records`:

- Inspect `links` for navigable resources (e.g., records search UI, category listings, or discovery endpoints)
- Follow only documented/self links; some links may be web UI endpoints rather than API surfaces

### Places (Works in beta)

- Path: `GET /platform/places/search?q={query}&count={n}`
- Accept: `application/json` (or XML)

### Known Limitations in Our Beta Access (as observed)

- User/Tree endpoints: 401/404 (insufficient scopes/permissions)
- Records endpoints: 404 Not Found
- Collections works reliably; Places search works with JSON/XML Accept headers

Action: If we need “records search” and person/tree data, request appropriate OAuth scopes and API enablement from FamilySearch for our app in beta.

### Implementation Patterns (Next.js + fs-js-lite)

1. Always set Accept header per endpoint
2. Normalize responses via `response.data` or `JSON.parse(response.body)`
3. Handle non-200 with care (409 conflicts, 404 in beta)
4. Keep the token fresh and validated (we store `expiresAt` in session)

### Minimal Server Snippet (Collections)

```ts
const res = await new Promise((resolve, reject) =>
  fs.get(
    "/platform/collections",
    { headers: { Accept: "application/x-gedcomx-v1+json" } },
    (err: any, r: any) => (err ? reject(err) : resolve(r))
  )
);
const json = toJson(res);
const collections = json?.collections ?? [];
```

### Troubleshooting

- 404 on records endpoints in beta: likely not enabled for the app/scopes
- 409 warning headers mentioning “current user’s tree”: informational; collections still succeed
- If `collections` is empty in UI but API returns items, ensure we parse via `data/body` and pass Accept header

### Next Steps for “Record Collections” UI

- Use `/platform/collections` to discover the `records` collection
- Fetch `/platform/collections/records` and surface its metadata/links in UI
- Once FS grants records search access, add endpoints for searching and category browsing per linked resources
