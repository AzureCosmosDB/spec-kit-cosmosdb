---
description: "Generate bulk operation code for high-throughput writes to Cosmos DB."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.bulk

> Generate bulk operation code for high-throughput writes to Cosmos DB.

## Intent

Create bulk insert/update/delete operations that maximize throughput using the SDK's bulk execution feature.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{operation_type}}` | Bulk operation | "insert", "upsert", "replace", "delete" |
| `{{entity_name}}` | Entity being processed | "Product" |
| `{{source}}` | Where data comes from | "CSV file", "API response", "Queue messages" |
| `{{estimated_count}}` | Number of items | "100K" |
| `{{language}}` | Target language | "TypeScript" or "C#" |

## Prescriptive Prompt

Generate bulk operations for {{operation_type}} of {{entity_name}}. Follow these constraints:

### SDK Configuration

```
CosmosClientOptions:
  AllowBulkExecution = true    # CRITICAL: enables batching
  MaxRetryAttemptsOnRateLimitedRequests = 25
  MaxRetryWaitTimeOnRateLimitedRequests = 60s
```

### Implementation Pattern

1. **Create all tasks concurrently** - don't await individually
2. **Group by partition key** - SDK batches same-partition operations automatically
3. **Use `Task.WhenAll` / `Promise.all`** - let SDK handle internal batching
4. **Stream from source** - don't load all {{estimated_count}} items into memory
5. **Limit concurrency** - process in windows of 500-1000 concurrent operations

### Progress & Error Handling

1. Track: total, succeeded, failed, retried counts
2. Log every 1000 operations processed
3. Collect failed items with error details
4. After bulk: report success rate and total RU consumed
5. For failed items: write to error file/container for retry

### Output

1. Bulk executor class/function
2. Progress reporting
3. Error collection and retry logic
4. Example usage with sample data
5. Performance tuning notes (throughput vs RU/s provisioned)

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Sequential awaits in a loop (kills throughput)
- ❌ `AllowBulkExecution = false` (default, must explicitly enable)
- ❌ Loading entire dataset into memory
- ❌ No progress reporting for long operations
- ❌ Ignoring 429s without retry
- ❌ No error collection (silent failures)
