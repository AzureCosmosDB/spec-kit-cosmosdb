---
description: "Generate a custom indexing policy optimized for specific query patterns."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Spec Context (optional)

If the current project has an active Spec Kit specification (e.g. `.specify/specs/<feature>/spec.md`, or a path provided in the user input), **read it first** and use it as the source of intent: entity names, fields, access patterns, scale, and consistency requirements. Prefer values from the spec over generic defaults. If no spec is present, fall back to the inputs below. **Do not modify the spec.**


# /speckit.cosmosdb.index-policy

> Generate a custom indexing policy optimized for specific query patterns.

## Intent

Create an indexing policy that includes only paths needed by queries, reducing write RU cost while maintaining query performance.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{queries}}` | All queries this container serves | "WHERE customerId=@id AND status=@s ORDER BY createdAt DESC" |
| `{{document_schema}}` | Document shape | "{ id, customerId, status, createdAt, items[], total, metadata{} }" |

## Prescriptive Prompt

Generate an indexing policy. Follow these constraints:

### Methodology

1. Start with EXCLUDE ALL: `"excludedPaths": [{"path": "/*"}]`
2. Include `/` for `id` (always indexed)
3. For each query in {{queries}}, add paths used in WHERE, ORDER BY, GROUP BY
4. For ORDER BY with multiple fields, add composite index
5. For array fields used in queries, include the array path with `[]`

### Output JSON

```json
{
  "indexingMode": "consistent",
  "automatic": true,
  "includedPaths": [
    // Only paths used in queries
  ],
  "excludedPaths": [
    { "path": "/*" }
  ],
  "compositeIndexes": [
    // For multi-field ORDER BY
  ],
  "spatialIndexes": [],
  "vectorIndexes": []
}
```

### Include with justification

For each included path, comment:
```
"/customerId/?": "Used in WHERE equality filter - query 1, 2"
"/createdAt/?": "Used in ORDER BY and range filter - query 1"
```

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="speckit-cosmosdb/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "speckit-cosmosdb/0.1.0"`. For Java, use `.userAgentSuffix("speckit-cosmosdb/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Default policy (`includedPaths: [{"path": "/*"}]`) - indexes everything, costs RU on every write
- ❌ Including paths not used in any query
- ❌ Missing composite index for multi-field ORDER BY
- ❌ Indexing large text fields never queried
- ❌ Excluding paths used in WHERE clauses
