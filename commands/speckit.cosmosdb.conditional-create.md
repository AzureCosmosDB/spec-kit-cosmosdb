---
description: "Generate a conditional create that rejects duplicates using ifNoneMatch ETag."
---

<!-- User arguments: $ARGUMENTS -->

# /speckit.cosmosdb.conditional-create

> Generate a conditional create that rejects duplicates using ifNoneMatch ETag.

## Intent

Implement an insert-only operation that fails gracefully if a document with the same id already exists, using ETag preconditions.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{entity}}` | Entity type | "Registration" |
| `{{partition_key_path}}` | Partition key property | "/eventId" |
| `{{language}}` | Target language | "Python" or "C#" or "TypeScript" |

## Prescriptive Prompt

Generate a conditional create. Follow these constraints:

### Naming & Structure Constraints (MANDATORY)

- Function MUST be named `create_{entity_snake_case}_if_not_exists()` (Python) / `create{Entity}IfNotExists()` (TS) / `Create{Entity}IfNotExistsAsync()` (C#)
- File MUST be named `create_{entity_snake_case}.py`
- `partition_key` MUST be an explicit function parameter
- Return type MUST be `Tuple[dict, bool]` — (document, created) where `created=False` means already existed
- MUST use `if_none_match_etag="*"` to reject if any version exists
- MUST handle `CosmosHttpResponseError` with status 409 (Conflict) → return existing doc
- MUST log RU charge using standard `logging`

### Rules

1. Use `container.create_item()` with `if_none_match_etag="*"`
2. This causes server-side rejection if document id already exists in that partition
3. On 409 Conflict: fetch existing document via point read and return `(existing, False)`
4. On success: return `(created_doc, True)`
5. This is idempotent — safe to retry without creating duplicates

### Output

1. Conditional create function with `if_none_match_etag="*"`
2. 409 handling that returns existing document
3. Return tuple indicating whether creation occurred
4. RU charge logging
5. Usage example showing idempotent API endpoint

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Read-then-write to check existence (race condition)
- ❌ Swallowing 409 without returning existing state
- ❌ Using upsert when insert-only semantics are required
- ❌ Missing partition key in the create call
