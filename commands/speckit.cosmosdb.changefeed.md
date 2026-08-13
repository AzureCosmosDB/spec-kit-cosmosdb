---
description: "Generate a change feed processor for event-driven processing."
---

# /cosmos.changefeed

> Generate a change feed processor for event-driven processing.

## Intent

Create a change feed processor that reacts to document changes in a Cosmos DB container, with proper lease management, error handling, and scaling.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{source_container}}` | Container to watch | "orders" |
| `{{processor_name}}` | Unique processor name | "order-notifications" |
| `{{trigger_action}}` | What to do on change | "Send notification when status changes to 'shipped'" |
| `{{language}}` | Target language | "TypeScript" or "C#" |
| `{{hosting}}` | Where it runs | "Azure Functions" or "Background service" or "Container app" |

## Prescriptive Prompt

Generate a change feed processor. Follow these constraints:

### Architecture

1. **Lease container**: Use a dedicated `leases` container (partition key `/id`)
2. **Processor name**: Must be unique per consumer group — use `{{processor_name}}`
3. **Start time**: Default to `StartTime.Now()` for new deployments; support `StartTime.Beginning()` for replay
4. **Batch size**: Default `MaxItemCount = 100`, tune based on processing time
5. **Instance name**: Use hostname/pod name for horizontal scaling

### Processing Logic

For {{trigger_action}}:
1. Filter relevant changes (not all documents in the feed are relevant)
2. Process idempotently (change feed has at-least-once delivery)
3. Use a deduplication check (store processed change `_lsn` or derive idempotency key)
4. On transient failure: throw to retry the batch
5. On poison message: log, send to dead-letter, skip

### Hosting Patterns

**Azure Functions (recommended for serverless)**:
- Use `CosmosDBTrigger` binding
- Configure `LeaseContainerName`, `CreateLeaseContainerIfNotExists`
- Set `MaxItemsPerInvocation` for batch control

**Background Service**:
- Implement `IHostedService` / long-running process
- Graceful shutdown: stop processor on cancellation token
- Health check: expose last processed timestamp

### Output

1. Change feed processor setup code
2. Processing handler with idempotency
3. Lease container configuration
4. Error handling with dead-letter pattern
5. Scaling guidance (instances = physical partitions in source)

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Processing without idempotency check
- ❌ Shared lease container across unrelated processors
- ❌ No dead-letter strategy for poison messages
- ❌ Blocking I/O in the handler without async
- ❌ Ignoring lease container throughput (needs RU too)
