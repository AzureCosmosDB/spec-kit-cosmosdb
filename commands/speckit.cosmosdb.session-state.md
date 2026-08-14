---
description: "Generate a session/cache storage pattern with Azure Cosmos DB and TTL-based expiration."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Spec Context (optional)

If the current project has an active Spec Kit specification (e.g. `.specify/specs/<feature>/spec.md`, or a path provided in the user input), **read it first** and use it as the source of intent: entity names, fields, access patterns, scale, and consistency requirements. Prefer values from the spec over generic defaults. If no spec is present, fall back to the inputs below. **Do not modify the spec.**


# /speckit.cosmosdb.session-state

> Generate a session/cache storage pattern with Azure Cosmos DB and TTL-based expiration.

## Intent

Implement web application session state management backed by Azure Cosmos DB, with automatic expiration via TTL, fast point reads for session retrieval, and proper security for session tokens.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{framework}}` | Web framework | "FastAPI" or "Express" or "ASP.NET Core" |
| `{{language}}` | Target language | "Python" or "TypeScript" or "C#" |
| `{{session_fields}}` | Session data shape | "{ userId, role, preferences, cart }" |
| `{{ttl_seconds}}` | Session timeout | "3600" (1 hour) |

## Prescriptive Prompt

Generate session state storage for {{framework}}. Follow these constraints:

### Container Design

1. **Container name**: `sessions`
2. **Partition key**: `/sessionId` - each session is its own partition (uniform distribution)
3. **TTL**: Container default = `{{ttl_seconds}}` seconds
4. **Throughput**: Autoscale 400–4000 RU/s (session reads are 1 RU point reads)
5. **Indexing**: Exclude all paths (`/*` excluded); only `/sessionId` and `/userId` indexed

### Document Schema

```json
{
  "id": "<session-id>",
  "sessionId": "<session-id>",
  "userId": "<user-id>",
  "data": { {{session_fields}} },
  "createdAt": "<ISO-8601>",
  "lastAccessed": "<ISO-8601>",
  "ttl": {{ttl_seconds}}
}
```

### Session Operations

1. **Create session**: Generate cryptographically random session ID (32+ bytes, hex/base64)
2. **Read session**: Point read by `id` + `sessionId` partition key (1 RU)
3. **Update session**: Patch `data` and reset `ttl` on each access (sliding expiration)
4. **Delete session**: Delete item on explicit logout
5. **Extend session**: "Remember me" → set `ttl` to 30 days (2592000)

### Sliding Expiration

1. On EVERY session read, update `lastAccessed` and reset `ttl` to {{ttl_seconds}}
2. Use Azure Cosmos DB **patch operation** for efficient partial update (cheaper than replace)
3. Batch the TTL reset - don't block the response on it (fire-and-forget or background task)

### Security

1. **Session ID**: Cryptographically random - `secrets.token_hex(32)` (Python) / `crypto.randomBytes(32)` (Node)
2. **Cookie**: `HttpOnly`, `Secure`, `SameSite=Strict`
3. **No sensitive data**: Never store passwords or full tokens in session
4. **Session fixation**: Regenerate session ID on privilege escalation (login)
5. **Concurrent sessions**: Optionally limit per user; query by `/userId` index

### Framework Integration

For {{framework}}:
1. Implement session middleware/backend interface
2. Hook into framework's native session mechanism
3. Cookie management (set/read/clear)
4. Lazy loading: don't read session until accessed

### Output

1. Session container creation with TTL and indexing policy
2. Session document model
3. Session store class (create/read/update/delete/extend)
4. Framework middleware integration for {{framework}}
5. Sliding expiration with patch operation
6. Security configuration (cookie settings, ID generation)

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="speckit-cosmosdb/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "speckit-cosmosdb/0.1.0"`. For Java, use `.userAgentSuffix("speckit-cosmosdb/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Sequential/predictable session IDs (security vulnerability)
- ❌ Storing session in a shared partition key (hot partition)
- ❌ Full document replace for TTL refresh (wasteful; use patch)
- ❌ No TTL - sessions never expire (resource leak)
- ❌ Query-based session lookup when ID is known (use point read)
- ❌ Storing sensitive credentials in session document
- ❌ Blocking response on TTL refresh write
