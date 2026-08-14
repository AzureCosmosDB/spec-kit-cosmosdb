---
description: "Generate Azure Cosmos DB container configuration with throughput, indexing, and partition strategy."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.container

> Generate Azure Cosmos DB container configuration with throughput, indexing, and partition strategy.

## Intent

Produce a complete container configuration including partition key, indexing policy, throughput settings, TTL, and unique keys.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{container_name}}` | Container name | "orders" |
| `{{partition_key}}` | Partition key path | "/customerId" |
| `{{query_patterns}}` | Queries this container serves | "Filter by status, range on createdAt, point read by id+customerId" |
| `{{throughput_model}}` | Throughput approach | "autoscale 4000" or "manual 400" or "serverless" |
| `{{ttl}}` | Time-to-live requirement | "90 days" or "none" |

## Prescriptive Prompt

Generate container configuration for `{{container_name}}`. Follow these constraints:

### Indexing Policy

Based on {{query_patterns}}, generate an indexing policy that:
1. Excludes all paths by default (`"excludedPaths": [{"path": "/*"}]`)
2. Includes ONLY paths used in WHERE, ORDER BY, or JOIN clauses
3. Uses range indexes for numeric/temporal fields used in range queries
4. Uses composite indexes for ORDER BY with multiple fields
5. Adds spatial index only if geo queries are needed

### Throughput

- Serverless: for < 5000 RU/s burst, intermittent workloads
- Autoscale: for variable workloads, set max to 10x average
- Manual: for predictable, steady workloads only

### Output Format

Produce:
1. ARM/Bicep template for the container
2. SDK code to create container programmatically
3. Indexing policy JSON
4. Explanation of each included index path

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="speckit-cosmosdb/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "speckit-cosmosdb/0.1.0"`. For Java, use `.userAgentSuffix("speckit-cosmosdb/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Default indexing policy in production (indexes everything, wastes RU on writes)
- ❌ Manual throughput for variable workloads
- ❌ Composite index that doesn't match any query's ORDER BY
- ❌ TTL without considering downstream change feed consumers
