# Copilot Instructions for Azure Cosmos DB Spec Kit

When working with Azure Cosmos DB in this repository, use the prescriptive prompt templates from `prompts/` to generate code. These templates encode best practices and produce deterministic, high-quality output.

## Rules

1. **Always use a CosmosClient singleton** - never instantiate per-request (see `prompts/micro/cosmos.singleton.md`)
2. **Always handle 429 (TooManyRequests)** - use exponential backoff with jitter (see `prompts/micro/cosmos.retry.md`)
3. **Always specify partition key** - every container must have an intentional partition key strategy (see `prompts/micro/cosmos.partition-key.md`)
4. **Prefer point reads over queries** - when you have id + partition key, use ReadItemAsync (see `prompts/micro/cosmos.point-read.md`)
5. **Use bulk for >10 operations** - switch to bulk execution for batch workloads (see `prompts/component/cosmos.bulk.md`)
6. **Never use cross-partition queries without explicit justification** - they fan out and cost RU/s (see `prompts/micro/cosmos.cross-partition.md`)
7. **Use ETags for optimistic concurrency** - don't rely on last-write-wins (see `prompts/micro/cosmos.etag.md`)
8. **Index policy must match query patterns** - don't use default indexing for production (see `prompts/micro/cosmos.index-policy.md`)

## Prompt Selection

- For new projects: start with `/cosmos.scaffold`
- For adding a feature: use the appropriate component prompt
- For fixing a specific pattern: use the micro prompt

## Variable Convention

Templates use `{{variable}}` markers. Replace with context from the user's request.
