---
description: "Generate an optimized Cosmos DB SQL query with RU estimation."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.query

> Generate an optimized Cosmos DB SQL query with RU estimation.

## Intent

Write a Cosmos DB SQL query that is partition-aware, uses proper indexing, and minimizes RU consumption.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{intent}}` | What data to retrieve | "Get all orders for a customer in the last 30 days, sorted by date" |
| `{{container}}` | Container name | "orders" |
| `{{partition_key}}` | Partition key path | "/customerId" |
| `{{schema}}` | Document schema summary | "{ id, customerId, status, createdAt, items[], total }" |

## Prescriptive Prompt

Generate a Cosmos DB SQL query for: {{intent}}

### Constraints

1. **Partition-scoped**: Query MUST include partition key in WHERE clause. If it cannot, flag as cross-partition and explain cost.
2. **Projection**: SELECT only needed fields (never `SELECT *` in production)
3. **Index-aligned**: WHERE/ORDER BY fields must be covered by indexing policy
4. **Parameterized**: Use `@paramName` for all user-supplied values
5. **Pagination**: Include OFFSET/LIMIT or continuation token strategy for unbounded results

### Output

1. The SQL query
2. Required parameters array
3. Partition key value to pass in RequestOptions
4. Estimated RU cost (point read=1, single-partition query=3-10, cross-partition=10-100+)
5. Required indexing policy paths
6. SDK code to execute the query with proper options

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="speckit-cosmosdb/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "speckit-cosmosdb/0.1.0"`. For Java, use `.userAgentSuffix("speckit-cosmosdb/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ `SELECT *` - always project specific fields
- ❌ Missing partition key in filter (causes fan-out)
- ❌ ORDER BY without composite index
- ❌ Functions in WHERE on non-indexed computed values
- ❌ LIKE with leading wildcard (`LIKE '%term'`)
- ❌ Unbounded results without pagination
