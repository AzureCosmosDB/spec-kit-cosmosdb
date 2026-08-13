---
description: "Generate API pagination with Cosmos DB continuation tokens exposed as opaque cursors."
---

# /cosmos.api-pagination

> Generate API pagination with Cosmos DB continuation tokens exposed as opaque cursors.

## Intent

Implement cursor-based API pagination that wraps Cosmos DB's continuation tokens in opaque, URL-safe cursors, providing a clean pagination API without exposing internal database state to consumers.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{entity}}` | Entity being paginated | "Product" |
| `{{language}}` | Target language | "Python" or "C#" or "TypeScript" |
| `{{framework}}` | API framework | "FastAPI" or "Express" or "ASP.NET Core" |
| `{{default_page_size}}` | Default items per page | "25" |

## Prescriptive Prompt

Generate API pagination for `{{entity}}` in {{framework}}. Follow these constraints:

### Cursor Design

1. **Opaque cursor**: Base64-encode the Cosmos continuation token — consumers MUST NOT parse it
2. **Encoding**: `base64url(json({ "ct": "<continuation_token>", "v": 1 }))` — versioned for future changes
3. **First page**: No cursor parameter → first page
4. **Last page**: Response includes `null` cursor → no more pages
5. **Cursor validation**: Decode and validate structure; return 400 on invalid cursor

### API Contract

**Request**:
```
GET /{{entity_plural}}?limit={{default_page_size}}&cursor=<opaque-cursor>
```

**Response**:
```json
{
  "items": [...],
  "cursor": "<next-cursor-or-null>",
  "hasMore": true/false
}
```

### Query Execution

1. **Page size**: Use `limit` query param, default `{{default_page_size}}`, max `100`
2. **Continuation token**: Pass decoded token to Cosmos query as `continuation_token`
3. **Consistent results**: Same partition key scope per paginated query
4. **Cross-partition**: Supported but warn about RU cost; prefer scoped queries

### Implementation Rules

1. **Never expose raw continuation token** — it contains internal partition state
2. **Cursor is single-use**: Each cursor produces the NEXT page only
3. **No total count**: Cosmos DB doesn't efficiently support `COUNT(*)` — omit `totalItems`
4. **Stateless**: All pagination state is IN the cursor — no server-side session
5. **Stable ordering**: Always include `ORDER BY` to ensure deterministic pagination
6. **Max page size**: Enforce server-side max (100) regardless of client request

### Framework Integration

For {{framework}}:
1. Pagination query parameters (limit, cursor) with validation
2. Response model with items + cursor + hasMore
3. Endpoint implementation with Cosmos query + continuation
4. OpenAPI/Swagger documentation for pagination parameters

### Error Handling

1. **Expired cursor**: Cosmos tokens may expire after hours — return 400 "Cursor expired, restart from first page"
2. **Invalid cursor**: Malformed base64 or wrong version → 400
3. **Empty page**: If Cosmos returns 0 items but has continuation → fetch next automatically (don't return empty page to client)

### Output

1. Cursor encode/decode utilities (base64url with version)
2. Pagination request/response models
3. Paginated query executor (wraps Cosmos SDK query with continuation)
4. API endpoint for {{entity}} with pagination
5. Input validation (max page size, cursor format)
6. Empty-page handling (auto-fetch next until items or end)

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Exposing raw Cosmos continuation tokens in API response
- ❌ Offset-based pagination (`skip/take`) — doesn't work efficiently in Cosmos
- ❌ Returning `totalCount` (requires expensive full scan)
- ❌ Returning empty pages to client (confusing UX)
- ❌ No `ORDER BY` in paginated query (non-deterministic results)
- ❌ Unbounded page size (client requests 10,000 items)
- ❌ Server-side cursor storage (stateful pagination)
