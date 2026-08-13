---
description: "Generate a point read operation (the cheapest possible Cosmos DB read at 1 RU)."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.point-read

> Generate a point read operation (the cheapest possible Cosmos DB read at 1 RU).

## Intent

Implement a point read using id + partition key, which costs exactly 1 RU for documents < 1KB.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{entity}}` | Entity type | "Order" |
| `{{id_source}}` | Where the id comes from | "URL path parameter" |
| `{{partition_key_source}}` | Where PK comes from | "authenticated user's customerId" |
| `{{language}}` | Target language | "TypeScript" or "C#" |

## Prescriptive Prompt

Generate a point read. Follow these constraints:

### Naming & Structure Constraints (MANDATORY)

- Function MUST be named `get_{entity_snake_case}_by_id()` (Python) / `get{Entity}ById()` (TS) / `Get{Entity}ByIdAsync()` (C#)
  - Example: entity "UserProfile" → `get_user_profile_by_id()`
- Return type MUST be `Optional[dict]` (Python) / `T | null` (TS) / `T?` (C#)
- MUST handle 404 by returning `None`/`null` — NEVER raise/throw for not-found
- `partition_key` MUST be an explicit function parameter (not inferred or hardcoded)
- Entity model MUST use pydantic `BaseModel` (Python) / interface (TS) / record (C#)
- MUST use `Optional[T]` annotation style (not `T | None` union syntax)
- MUST log RU charge using standard `logging` module

### What is a Point Read?

- `ReadItemAsync(id, partitionKey)` — NOT a query
- Cost: 1 RU for < 1KB document (scales linearly with size)
- Requires BOTH `id` AND `partition key` value
- Returns single document or 404

### When to Use

✅ You have both `id` and partition key value → ALWAYS use point read
❌ You only have `id` → you need a query (or reconsider your data model)
❌ You need multiple documents → use a query

### Implementation

```
try {
  ItemResponse<T> response = await container.ReadItemAsync<T>(
    id: "{{id_source}}",
    partitionKey: new PartitionKey("{{partition_key_source}}")
  );
  T document = response.Resource;
  double ruCharge = response.RequestCharge; // Should be ~1 RU
} catch (CosmosException ex) when (ex.StatusCode == HttpStatusCode.NotFound) {
  // Document doesn't exist
  return null;
}
```

### Output

1. Point read function named `get_{entity_snake_case}_by_id()` with `partition_key` as explicit parameter
2. 404 handling (return `None` — never throw for not-found)
3. RU charge logging via standard `logging`
4. Comparison comment showing equivalent query (and why it's worse)

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ `SELECT * FROM c WHERE c.id = @id` when partition key is known (query costs 3+ RU vs 1 RU point read)
- ❌ Not passing partition key to ReadItem (causes cross-partition attempt)
- ❌ Throwing exception for 404 in normal flow
- ❌ Using `T | None` union syntax instead of `Optional[T]`
- ❌ Using dataclass instead of pydantic BaseModel
- ❌ Omitting `partition_key` as an explicit parameter
