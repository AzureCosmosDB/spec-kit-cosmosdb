---
description: "Generate an event sourcing implementation with Azure Cosmos DB: append-only events, snapshots, and projections."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.event-sourcing

> Generate an event sourcing implementation with Azure Cosmos DB: append-only events, snapshots, and projections.

## Intent

Implement event sourcing where state changes are stored as an immutable sequence of events in Azure Cosmos DB, with snapshot optimization and read projections materialized via change feed.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{aggregate}}` | Aggregate root entity | "ShoppingCart" |
| `{{events}}` | Domain events | "ItemAdded, ItemRemoved, CartCheckedOut, CartAbandoned" |
| `{{language}}` | Target language | "Python" or "C#" or "TypeScript" |

## Prescriptive Prompt

Generate event sourcing for `{{aggregate}}`. Follow these constraints:

### Event Store Container

1. **Container name**: `events`
2. **Partition key**: `/aggregateId` - all events for one aggregate in same partition
3. **Document schema**:
   ```json
   {
     "id": "<aggregateId>_<version>",
     "aggregateId": "<aggregate-id>",
     "aggregateType": "{{aggregate}}",
     "version": <sequential-integer>,
     "eventType": "<one of {{events}}>",
     "data": { <event-specific payload> },
     "metadata": { "userId": "...", "correlationId": "...", "timestamp": "..." },
     "ttl": -1
   }
   ```
4. **Ordering**: Events ordered by `version` within aggregate (enforced by application)
5. **Immutability**: NEVER update or delete events - append only
6. **Indexing**: Include `/aggregateId`, `/aggregateType`, `/version`; exclude `/data/*`

### Concurrency Control

1. **Optimistic concurrency**: Use expected version on append
2. **Implementation**: Read current max version, write `version + 1` with conditional check
3. **Conflict**: If version conflict → reload events, re-apply command, retry (max 3 times)
4. **Unique ID**: `id` = `{aggregateId}_{version}` ensures no duplicate versions

### Aggregate Rehydration

1. **Load**: Query all events for aggregate, ordered by version
2. **Apply**: Fold events over initial state → current state
3. **Performance**: Use snapshot optimization for aggregates with > 50 events

### Snapshots

1. **Container**: Same `events` container, `eventType` = `"Snapshot"`
2. **Frequency**: Create snapshot every 50 events
3. **Loading**: Load latest snapshot + events after snapshot version
4. **Schema**: Snapshot `data` contains full aggregate state at that version

### Projections (via Change Feed)

For each {{events}} event:
1. Change feed processor reads new events
2. Projects into read-optimized view containers
3. Idempotent: use `aggregateId` + `version` as deduplication key
4. Separate processor per projection

### Event Definitions

For each event in {{events}}:
1. Define typed event class with required payload fields
2. Include version migration support (event upcasting for schema changes)
3. Serialize to/from JSON with discriminator on `eventType`

### Output

1. Event store container setup
2. Event base class/interface and typed events for {{events}}
3. Aggregate root with `apply_event()` and `load_from_events()` methods
4. Event append with optimistic concurrency
5. Snapshot creation and loading logic
6. Change feed projector skeleton
7. Example: full lifecycle of {{aggregate}} (create → modify → snapshot → reload)

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="speckit-cosmosdb/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "speckit-cosmosdb/0.1.0"`. For Java, use `.userAgentSuffix("speckit-cosmosdb/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Mutable events (update/delete on event store)
- ❌ No concurrency control (lost events)
- ❌ Loading all events every time without snapshots (unbounded growth)
- ❌ Business logic in projections (projections are read-only transformations)
- ❌ Non-sequential versions (gaps indicate bugs)
- ❌ Using `_ts` for ordering instead of explicit `version`
- ❌ Storing aggregate state directly (that's CRUD, not event sourcing)
