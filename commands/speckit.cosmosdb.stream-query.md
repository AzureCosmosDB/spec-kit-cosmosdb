---
description: "Generate an efficient streaming query for large result sets."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Spec Context (optional)

If the current project has an active Spec Kit specification (e.g. `.specify/specs/<feature>/spec.md`, or a path provided in the user input), **read it first** and use it as the source of intent: entity names, fields, access patterns, scale, and consistency requirements. Prefer values from the spec over generic defaults. If no spec is present, fall back to the inputs below. **Do not modify the spec.**


# /speckit.cosmosdb.stream-query

> Generate an efficient streaming query for large result sets.

## Intent

Implement memory-efficient iteration over large Azure Cosmos DB query results using async generators/iterators without loading all results into memory.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{entity}}` | Entity type | "AuditLog" |
| `{{query}}` | SQL query | "SELECT * FROM c WHERE c.createdAt > @since" |
| `{{language}}` | Target language | "Python" or "C#" or "TypeScript" |

## Prescriptive Prompt

Generate a streaming query. Follow these constraints:

### Naming & Structure Constraints (MANDATORY)

- Function MUST be named `stream_{entity_snake_case}s()` (Python) / `stream{Entity}s()` (TS) / `Stream{Entity}sAsync()` (C#)
- File MUST be named `stream_{entity_snake_case}s.py`
- MUST be an `async generator` (Python `AsyncGenerator[dict, None]`) / `IAsyncEnumerable<T>` (C#) / `AsyncGenerator<T>` (TS)
- `partition_key` MUST be an explicit parameter when single-partition; if cross-partition, MUST set `partition_key=None` (async) or `enable_cross_partition_query=True` (sync) explicitly
- MUST set `max_item_count` to control page size (default 100)
- MUST yield individual items (not pages)
- MUST log cumulative RU charge using standard `logging` at end of iteration
- MUST accept optional `max_items: Optional[int] = None` to cap total results

### Rules

1. Use `container.query_items()` which returns an async pager
2. Iterate page-by-page internally, yield items one at a time
3. Track cumulative RU charge across all pages
4. Respect `max_items` limit if provided - stop iteration after N items
5. Log total RU and item count when generator is exhausted or stopped

### Output

1. Async generator function yielding individual documents
2. Cumulative RU tracking across pages
3. Optional max_items early termination
4. Usage example with `async for` loop
5. Memory usage note (O(page_size) not O(total_results))

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="speckit-cosmosdb/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "speckit-cosmosdb/0.1.0"`. For Java, use `.userAgentSuffix("speckit-cosmosdb/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ `list(query_items(...))` - loads everything into memory
- ❌ No RU tracking across pages
- ❌ Cross-partition query without explicit flag and cost warning
- ❌ Returning a list instead of streaming/yielding
- ❌ No way to limit total items consumed
