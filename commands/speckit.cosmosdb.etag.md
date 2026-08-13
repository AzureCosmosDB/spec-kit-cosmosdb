---
description: "Generate optimistic concurrency control using ETags."
---

# /cosmos.etag

> Generate optimistic concurrency control using ETags.

## Intent

Implement ETag-based optimistic concurrency to prevent lost updates when multiple writers modify the same document.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{entity}}` | Entity needing concurrency control | "Order" |
| `{{language}}` | Target language | "TypeScript" or "C#" |
| `{{conflict_strategy}}` | How to handle conflicts | "retry 3 times" or "return conflict to caller" |

## Prescriptive Prompt

Generate ETag concurrency pattern. Follow these constraints:

### Pattern: Read → Modify → Replace with ETag

```
1. Read document → get _etag from response headers
2. Modify document in memory
3. Replace with IfMatchEtag condition
4. If 412 PreconditionFailed:
   - Re-read document (get fresh ETag)
   - Re-apply modification
   - Retry replace
   - Max retries: 3
```

### Implementation

```
// Read
ItemResponse<T> response = await container.ReadItemAsync<T>(id, pk);
T item = response.Resource;
string etag = response.ETag;

// Modify
item.status = "shipped";

// Replace with ETag
RequestOptions options = { IfMatchEtag = etag };
try {
  await container.ReplaceItemAsync(item, id, pk, options);
} catch (CosmosException ex) when (ex.StatusCode == 412) {
  // Conflict — retry or return to caller
}
```

### Output

1. Read-modify-replace function with ETag
2. Retry loop with configurable max attempts
3. Conflict resolution strategy per {{conflict_strategy}}
4. Unit test demonstrating concurrent modification detection

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Last-write-wins without ETag (silent data loss)
- ❌ Infinite retry on conflict
- ❌ Storing ETag in the document body (it's a response header)
- ❌ Using ETag on create (only applies to replace/delete)
