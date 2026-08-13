---
description: "Generate an upsert operation with conflict handling."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.upsert

> Generate an upsert operation with conflict handling.

## Intent

Implement a safe upsert (insert-or-replace) that handles ETag conflicts and reports RU cost.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{entity}}` | Entity type | "UserProfile" |
| `{{partition_key_path}}` | Partition key property | "/userId" |
| `{{language}}` | Target language | "Python" or "C#" or "TypeScript" |

## Prescriptive Prompt

Generate an upsert operation. Follow these constraints:

### Naming & Structure Constraints (MANDATORY)

- Function MUST be named `upsert_{entity_snake_case}()` (Python) / `upsert{Entity}()` (TS) / `Upsert{Entity}Async()` (C#)
- File MUST be named `upsert_{entity_snake_case}.py` (Python) / `upsert{Entity}.ts` (TS)
- `partition_key` MUST be an explicit function parameter
- Return type MUST be `dict` (the upserted document)
- MUST accept optional `etag: Optional[str] = None` parameter for optimistic concurrency
- When `etag` is provided, MUST use `if_match_etag` access condition
- MUST log RU charge using standard `logging` module
- MUST handle `CosmosHttpResponseError` with status 412 (precondition failed) explicitly

### Rules

1. Use `container.upsert_item()` — NOT separate read-then-write
2. When `etag` is provided, set `if_match_etag=etag` for optimistic concurrency
3. Handle 412 Precondition Failed → raise a domain-specific `ConflictError`
4. Always include `partition_key` in the call
5. Log RU charge after successful upsert

### Output

1. Upsert function with etag-based optimistic concurrency
2. `ConflictError` custom exception class
3. RU charge logging
4. Usage example showing retry-on-conflict pattern

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Read-then-write pattern (race condition)
- ❌ Ignoring ETag for concurrent updates
- ❌ Swallowing 412 errors silently
- ❌ Missing partition key parameter
