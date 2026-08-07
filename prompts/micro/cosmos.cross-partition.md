# /cosmos.cross-partition

> Generate a cross-partition query with explicit cost awareness and guards.

## Intent

When a cross-partition query is unavoidable, implement it with proper pagination, cost tracking, and architectural justification.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{query_intent}}` | What data is needed | "Search all orders by status across all customers" |
| `{{justification}}` | Why cross-partition is necessary | "Admin dashboard, infrequent, no alternative" |
| `{{language}}` | Target language | "TypeScript" or "C#" |
| `{{max_ru_budget}}` | Maximum RU to spend | "100 RU" |

## Prescriptive Prompt

Generate a cross-partition query WITH guards. Follow these constraints:

### Before Writing This Query — Consider Alternatives

1. **Can you add a change feed consumer** that materializes this view into a container with the right partition key?
2. **Can you duplicate the data** into a "read model" container partitioned for this query?
3. **Can you use a composite key** that supports both access patterns?

If the answer is no to all, proceed with the guarded cross-partition query.

### Implementation with Guards

```
QueryRequestOptions options = {
  MaxItemCount = 100,           // Limit page size
  MaxBufferedItemCount = 500,   // Limit memory
  // No PartitionKey = cross-partition
};

// RU budget guard
double totalRU = 0;
double maxBudget = {{max_ru_budget}};

FeedIterator<T> iterator = container.GetItemQueryIterator<T>(query, options);

while (iterator.HasMoreResults) {
  FeedResponse<T> response = await iterator.ReadNextAsync();
  totalRU += response.RequestCharge;
  
  if (totalRU > maxBudget) {
    log.Warning("Cross-partition query exceeded RU budget: {totalRU}/{maxBudget}");
    break; // Stop before consuming too much
  }
  
  results.AddRange(response);
}
```

### Required Documentation

Every cross-partition query MUST include a comment:
```
// CROSS-PARTITION QUERY
// Justification: {{justification}}
// Frequency: [how often this runs]
// RU Budget: {{max_ru_budget}}
// TODO: Consider materializing as read model if frequency increases
```

### Output

1. Guarded query implementation with RU budget
2. Pagination with continuation tokens
3. Justification comment block
4. Suggestion for eventual optimization (change feed → read model)

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Cross-partition query without RU budget guard
- ❌ No justification comment
- ❌ Using in a hot path (> 10 req/sec)
- ❌ No pagination (unbounded result set + fan-out = disaster)
- ❌ Ignoring the "consider alternatives" step
