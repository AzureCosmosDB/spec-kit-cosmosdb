---
description: "Generate a CQRS pattern with Cosmos DB: write model + read views materialized via change feed."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.cqrs

> Generate a CQRS pattern with Cosmos DB: write model + read views materialized via change feed.

## Intent

Implement Command Query Responsibility Segregation where writes go to a normalized command container and read-optimized views are materialized asynchronously via change feed processors.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{write_model}}` | Command-side entity | "Order { id, customerId, items[], status, total }" |
| `{{read_models}}` | Read-side views to materialize | "OrderSummary { orderId, customerName, total, status }, CustomerOrders { customerId, orderCount, lastOrderDate }" |
| `{{language}}` | Target language | "Python" or "C#" or "TypeScript" |

## Prescriptive Prompt

Generate a CQRS implementation. Follow these constraints:

### Write Side (Command Container)

1. **Container name**: `commands` or domain-specific (e.g., `orders`)
2. **Partition key**: Natural entity key (e.g., `/customerId` for orders)
3. **Schema**: Full normalized {{write_model}} — optimized for writes, not reads
4. **Operations**: Upsert/patch only — no reads from command container in query path
5. **Validation**: All business rules enforced BEFORE write (not in materializer)

### Read Side (View Containers)

For each view in {{read_models}}:

1. **Separate container** per read model — optimized for specific query patterns
2. **Partition key**: Chosen for the read access pattern (e.g., `/customerId` for "my orders" view)
3. **Denormalized**: Duplicate data freely — consistency via change feed
4. **Schema**: Exactly what the UI/API needs — no joins, no extra fields

### Materialization (Change Feed Processor)

1. **One processor per read model** (separate lease containers)
2. **Idempotent projection**: Use `_etag` or version to prevent stale overwrites
3. **Projection logic**: Map write model → read model transformation
4. **Eventual consistency**: Read views lag 1–5 seconds behind writes (document this in API)
5. **Error handling**: Dead-letter failed projections; alert on lag > threshold

### Consistency Model

1. **Write-then-read**: After a write, reading from view container MAY return stale data
2. **Read-your-writes**: For immediate consistency, read from command container (costs more RU)
3. **Staleness SLA**: Document expected lag (typically < 2s for change feed)
4. **Conflict resolution**: Last-writer-wins with `_etag` checks on view updates

### Output

1. Write model container setup and document schema
2. Read model container(s) setup — one per view
3. Command handler (write path) with validation
4. Change feed processor(s) — one per read model materializer
5. Query handlers (read path) from view containers
6. Staleness documentation for API consumers

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Reading from command container in query path (defeats CQRS purpose)
- ❌ Single container for both reads and writes
- ❌ Synchronous view updates (must be async via change feed)
- ❌ No idempotency in materializers (duplicate processing will happen)
- ❌ Business logic in materializers (validation belongs on write side)
- ❌ Assuming immediate consistency on read side
