---
description: "Generate a complete change feed processor with lease management, error handling, and checkpointing."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.changefeed-processor

> Generate a complete change feed processor with lease management, error handling, and checkpointing.

## Intent

Create a production-ready change feed processor that continuously monitors a source container, processes document changes with at-least-once delivery guarantees, and manages leases for horizontal scaling.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{source_container}}` | Container to monitor | "orders" |
| `{{language}}` | Target language | "Python" or "C#" or "TypeScript" |
| `{{processing_logic}}` | What to do with changes | "Update denormalized order summaries in read container" |
| `{{lease_container_name}}` | Lease container name | "order-processor-leases" |

## Prescriptive Prompt

Generate a change feed processor for `{{source_container}}`. Follow these constraints:

### Lease Container Setup

1. **Dedicated lease container**: Named `{{lease_container_name}}`, partition key `/id`
2. **Throughput**: Minimum 400 RU/s; scale with partition count of source
3. **Create if not exists**: Processor startup MUST auto-create lease container
4. **Isolation**: NEVER share lease container across unrelated processors

### Processor Configuration

1. **Processor name**: Derive from source + purpose (e.g., `{{source_container}}-materializer`)
2. **Instance name**: Use hostname/pod name for multi-instance deployments
3. **Start from**: `StartTime.Now()` for first deployment; support `StartTime.Beginning()` via config flag
4. **Batch size**: `MaxItemCount = 100` (default); expose as config
5. **Poll interval**: 5 seconds default; configurable

### Processing Logic

For `{{processing_logic}}`:

1. **Idempotency**: Every change MUST be processed idempotently
   - Use `_lsn` + document `id` as deduplication key
   - Store last processed LSN per partition in checkpoint store
2. **Filtering**: Not every document in the feed is relevant - filter early
3. **Batch processing**: Process entire batch before acknowledging
4. **Error handling**:
   - Transient errors: Throw to retry entire batch (automatic re-delivery)
   - Poison documents: Catch, log, send to dead-letter container, continue batch
   - Dead-letter container: `{{source_container}}-deadletter` with original doc + error + timestamp

### Checkpointing

1. **Automatic**: SDK checkpoints after handler returns successfully
2. **Manual checkpoint**: NOT needed unless doing partial batch processing
3. **Checkpoint frequency**: Per-batch (default SDK behavior)
4. **Recovery**: On restart, resumes from last checkpoint - expect some re-delivery

### Scaling

1. **Max instances** = number of physical partitions in source container
2. **Lease stealing**: Automatic when instances added/removed
3. **Monitoring**: Track `EstimatedLag` metric per lease for alerting
4. **Health check**: Expose last processed timestamp; alert if > 5 min stale

### Output

1. Lease container creation code
2. Change feed processor builder/configuration
3. Change handler with idempotency and dead-letter pattern
4. Graceful shutdown (stop processor on SIGTERM/cancellation)
5. Health check exposing processing lag
6. Dead-letter container schema and write logic

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Processing without idempotency (at-least-once means duplicates happen)
- ❌ Shared lease container for unrelated processors
- ❌ No dead-letter strategy for poison messages
- ❌ Synchronous/blocking I/O in handler
- ❌ Ignoring lease container RU needs
- ❌ No health check or lag monitoring
- ❌ Manual checkpointing when SDK auto-checkpoint suffices
