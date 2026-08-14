---
description: "Generate continuation-token-based pagination for Cosmos DB queries."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.pagination

> Generate continuation-token-based pagination for Cosmos DB queries.

## Intent

Implement efficient pagination using continuation tokens (not OFFSET/LIMIT) for large result sets.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{entity}}` | Entity type | "Order" |
| `{{page_size}}` | Items per page | 25 |
| `{{language}}` | Target language | "Python" or "C#" or "TypeScript" |

## Prescriptive Prompt

Generate paginated query. Follow these constraints:

### Naming & Structure Constraints (MANDATORY)

- Function MUST be named `list_{entity_snake_case}s()` (Python) / `list{Entity}s()` (TS) / `List{Entity}sAsync()` (C#)
- File MUST be named `list_{entity_snake_case}s.py`
- MUST accept `page_size: int` and `continuation_token: Optional[str] = None` as explicit parameters
- MUST return a dataclass/model named `PagedResult` with fields: `items: List[dict]`, `continuation_token: Optional[str]`, `has_more: bool`
- `partition_key` MUST be an explicit parameter (avoid cross-partition unless stated)
- MUST set `max_item_count=page_size` in query options
- MUST log RU charge per page using standard `logging`

### Rules

1. Use `container.query_items()` with `max_item_count` set to page_size
2. Return continuation token from response headers for next page
3. Accept continuation token to resume from previous position
4. Always scope to a single partition key when possible
5. Never use `OFFSET n LIMIT m` - it re-reads skipped rows and costs O(n) RU

### Output

1. Paginated query function returning `PagedResult`
2. `PagedResult` dataclass with items, continuation_token, has_more
3. RU charge logging per page
4. API endpoint example showing token passed via header or query param

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="speckit-cosmosdb/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "speckit-cosmosdb/0.1.0"`. For Java, use `.userAgentSuffix("speckit-cosmosdb/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ `OFFSET n LIMIT m` (costs RU for skipped documents)
- ❌ Fetching all results then slicing in memory
- ❌ Exposing raw continuation token without base64 encoding to clients
- ❌ Cross-partition query without explicit acknowledgment of fan-out cost
