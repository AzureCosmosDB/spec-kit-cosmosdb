---
description: "Generate a Cosmos DB document model with intentional partition key strategy."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.model

> Generate a Cosmos DB document model with intentional partition key strategy.

## Intent

Create a data model (document schema) for a Cosmos DB container with proper partition key selection, indexing hints, and SDK integration.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{entity_name}}` | Name of the entity | "Order" |
| `{{fields}}` | Fields and types | "orderId: string, customerId: string, items: array, total: number, status: enum" |
| `{{access_patterns}}` | How this data is queried | "Get by customerId, filter by status, get by orderId" |
| `{{language}}` | Target language | "TypeScript" or "C#" |
| `{{cardinality}}` | Expected document count | "10M documents" |

## Prescriptive Prompt

Generate a Cosmos DB document model for {{entity_name}}. Follow these constraints:

### Partition Key Selection

Analyze {{access_patterns}} and select partition key:
1. The most frequent equality filter in queries = best partition key candidate
2. Must have high cardinality (not boolean, not status enum with 5 values)
3. Must distribute writes evenly
4. If no single field works, propose hierarchical partition key

Justify your choice with: "Partition key `/{{chosen_key}}` because: [reason based on access patterns]"

### Document Schema Rules

1. `id` must be unique within the partition (use natural key or UUID)
2. Partition key field at document root (never nested)
3. Include system-usable fields:
   - `type`: discriminator string (lowercase entity name)
   - `createdAt`: ISO 8601 timestamp
   - `updatedAt`: ISO 8601 timestamp
4. Embedded sub-documents: only for bounded, co-accessed data
5. Arrays: only for bounded collections (< 100 items typically)
6. No `null` values - omit the field instead

### Output

1. Type/interface definition in {{language}}
2. Example document (valid JSON)
3. Partition key recommendation with justification
4. Suggested indexing policy (include/exclude paths)
5. Estimated document size in KB
6. Container configuration snippet

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Using `/id` as partition key (creates hot partition for sequential IDs)
- ❌ Using low-cardinality field (status, boolean)
- ❌ Unbounded arrays in documents
- ❌ Deeply nested partition key paths
- ❌ Including large blobs in the document (use Azure Blob Storage + reference)
