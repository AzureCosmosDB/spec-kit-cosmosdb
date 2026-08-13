---
description: "Generate atomic patch operations for partial document updates."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.patch

> Generate atomic patch operations for partial document updates.

## Intent

Use Cosmos DB patch API to update specific fields without reading the full document first.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{entity}}` | Entity being patched | "Order" |
| `{{fields_to_update}}` | Fields to modify | "status, updatedAt, shipmentTracking" |
| `{{language}}` | Target language | "TypeScript" or "C#" |
| `{{condition}}` | Optional precondition | "status = 'processing'" |

## Prescriptive Prompt

Generate patch operations. Follow these constraints:

### Patch Operation Types

- `Add` - set field (creates if not exists)
- `Set` - set field (same as Add in most cases)
- `Replace` - replace existing field (fails if not exists)
- `Remove` - delete field
- `Increment` - atomic increment numeric field
- `Move` - move field value to another path

### Implementation

```
PatchOperation[] operations = [
  PatchOperation.Set("/status", "shipped"),
  PatchOperation.Set("/updatedAt", DateTime.UtcNow),
  PatchOperation.Add("/shipmentTracking", trackingObj)
];

// With precondition (conditional patch)
PatchItemRequestOptions options = {
  FilterPredicate = "FROM c WHERE c.status = 'processing'"
};

container.PatchItemAsync<T>(id, partitionKey, operations, options);
```

### When to Use Patch vs Replace

- **Patch**: updating 1-3 fields, don't need full document, want atomicity
- **Replace**: updating many fields, already have the document, need ETag check

### Output

1. Patch operation builder function
2. Conditional patch with filter predicate
3. Error handling (412 if condition fails, 404 if not found)
4. Usage examples for each operation in {{fields_to_update}}

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Read-modify-write when only changing one field (use patch)
- ❌ Patching without partition key
- ❌ Using Replace for single-field updates (wasteful RU)
- ❌ No error handling for failed preconditions
