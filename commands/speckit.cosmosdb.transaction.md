---
description: "Generate a transactional batch operation within a single partition."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.transaction

> Generate a transactional batch operation within a single partition.

## Intent

Implement atomic multi-operation transactions using Cosmos DB transactional batch, guaranteed within one logical partition.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{operations}}` | What the batch does | "Create order + update inventory + write event" |
| `{{partition_key_path}}` | Partition key | "/customerId" |
| `{{language}}` | Target language | "Python" or "C#" or "TypeScript" |

## Prescriptive Prompt

Generate a transactional batch. Follow these constraints:

### Naming & Structure Constraints (MANDATORY)

- Function MUST be named `execute_{operation_name}_batch()` (Python) / `execute{Operation}Batch()` (TS) / `Execute{Operation}BatchAsync()` (C#)
- File MUST be named `batch_{operation_name}.py`
- `partition_key` MUST be an explicit parameter (all items MUST share same PK)
- MUST validate all items share the same partition key BEFORE executing batch
- MUST return `BatchResult` dataclass with fields: `success: bool`, `results: List[dict]`, `ru_charge: float`
- MUST handle partial failure by checking each operation's status code
- MUST log total RU charge using standard `logging`

### Rules

1. All operations in a batch MUST target the same logical partition
2. Maximum 100 operations per batch (validate and raise if exceeded)
3. Maximum 2MB total request size
4. Operations execute atomically - all succeed or all fail
5. Use `container.execute_item_batch()` (Python) / `Container.CreateTransactionalBatch()` (C#)

### Output

1. Batch execution function with partition key validation
2. `BatchResult` dataclass
3. Pre-flight validation (same PK, ≤100 ops, size check)
4. Error handling with per-operation status inspection
5. RU charge logging

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Batch across different partition keys (will fail with 400)
- ❌ More than 100 operations without splitting
- ❌ No pre-validation of partition key consistency
- ❌ Ignoring individual operation status codes in response
- ❌ Using separate requests when atomicity is required
