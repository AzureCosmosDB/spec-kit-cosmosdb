---
description: "Analyze the active spec/tasks and recommend the relevant Azure Cosmos DB commands to run during implementation (auto-fires before /implement)."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.advise

> Lightweight router that inspects the active Spec Kit feature and recommends **only the relevant** Azure Cosmos DB commands for the work about to be implemented. This is the `before_implement` advisor: it does **not** generate code and does **not** load every command — it points you at the few that matter.

## What to do

1. **Read the active feature context** (do not modify it):
   - Resolve the feature directory (`.specify/specs/<feature>/`); read `spec.md`, `plan.md`, and `tasks.md` if present.
   - If none resolve, use `$ARGUMENTS` as the description of what's being built.

2. **Identify the Azure Cosmos DB access patterns and concerns** the feature actually requires. Consider:
   - Data model & partition strategy (entities, access patterns, scale)
   - Read patterns (point reads vs. queries vs. pagination)
   - Write patterns (create/upsert/patch/transaction/bulk)
   - Advanced needs (change feed, vector/RAG, multi-tenant, TTL, global distribution, autoscale)
   - Cross-cutting concerns (client singleton, retry, diagnostics, index policy)

3. **Recommend ONLY the commands the feature actually requires** — a focused shortlist **sized to the feature**: 3–5 for a simple single-entity feature, up to ~10 for a genuinely multi-pattern one, but **never more than the access patterns require**. For each, give a one-line reason naming the specific spec element it serves. Present as an ordered checklist the developer (or agent) can run during `/speckit.implement`.

### Selection discipline (MANDATORY — apply before you finalize the list)

- **Necessity test:** include a command ONLY if you can name the exact access pattern, entity, or requirement in the spec that needs it. If you cannot, DROP it — never recommend a command "just in case."
- **Resolve overlaps — pick ONE, not both:** `changefeed-processor` **or** `changefeed`; `pagination` **or** `api-pagination`; `transaction` **or** `stored-proc` for single-partition atomicity; and a `scaffold-*` command **or** its constituent granular commands — never a scaffold *plus* the pieces it already includes.
- **Do not pad with generic cross-cutting commands** (`singleton`, `connection`, `retry`, `diagnostics`, `serialization`) unless the spec's stated scale, resilience, or serialization needs specifically call for them.
- **Right-size, don't pad:** remove any command you cannot tie to a specific requirement. Most features need ~4–8 commands; only genuinely multi-pattern features (multiple entities, change feed, multi-tenant, etc.) need more. The goal is the SMALLEST list that fully covers the feature's access patterns.
- **But keep the genuinely-required ones:** trimming removes padding and duplicates — it must NOT drop commands the spec's core access patterns depend on (e.g. `model`/`partition-key` for the data design, and the primary read/write/query/transaction patterns the feature actually uses).

4. **Do not inline or execute** those commands here. Just recommend them. The developer runs the relevant `/speckit.cosmosdb.*` commands explicitly; each loads its own prescriptive guidance only when invoked. This keeps context lean.

## Output format

```
## Recommended Azure Cosmos DB commands for this feature

Based on <spec/plan/tasks or your description>, run these during implementation:

1. /speckit.cosmosdb.<name>  — <why, tied to the spec>
2. /speckit.cosmosdb.<name>  — <why>
...

(Skipped the rest of the catalog — not relevant to this feature.)
```

## Command Catalog (index only — load full command on invocation)

- `/speckit.cosmosdb.api-pagination` — API pagination with Cosmos continuation tokens exposed as opaque cursors.
- `/speckit.cosmosdb.autoscale` — Configure autoscale throughput for variable workloads.
- `/speckit.cosmosdb.availability` — Configure availability strategy and circuit breaker for resilient Cosmos access.
- `/speckit.cosmosdb.bulk` — bulk operation code for high-throughput writes to Azure Cosmos DB.
- `/speckit.cosmosdb.changefeed-processor` — a complete change feed processor with lease management, error handling, and checkpointing.
- `/speckit.cosmosdb.changefeed` — a change feed processor for event-driven processing.
- `/speckit.cosmosdb.conditional-create` — a conditional create that rejects duplicates using ifNoneMatch ETag.
- `/speckit.cosmosdb.connection` — connection configuration for emulator and production environments.
- `/speckit.cosmosdb.container` — Cosmos container configuration with throughput, indexing, and partition strategy.
- `/speckit.cosmosdb.cqrs` — a CQRS pattern with Azure Cosmos DB: write model + read views materialized via change feed.
- `/speckit.cosmosdb.cross-partition` — a cross-partition query with explicit cost awareness and guards.
- `/speckit.cosmosdb.diagnostics` — Add SDK diagnostics logging for troubleshooting latency and errors.
- `/speckit.cosmosdb.endpoint` — an API endpoint backed by Cosmos with proper error mapping.
- `/speckit.cosmosdb.etag` — optimistic concurrency control using ETags.
- `/speckit.cosmosdb.event-sourcing` — an event sourcing implementation with Azure Cosmos DB: append-only events, snapshots, and projections.
- `/speckit.cosmosdb.global-distribution` — Configure multi-region writes, conflict resolution, and preferred regions.
- `/speckit.cosmosdb.hierarchical-pk` — Design hierarchical (sub-partitioned) partition keys for multi-tenant and high-cardinality scenarios.
- `/speckit.cosmosdb.index-policy` — a custom indexing policy optimized for specific query patterns.
- `/speckit.cosmosdb.migrate` — a migration plan and code to move from another database to Azure Cosmos DB.
- `/speckit.cosmosdb.model` — a Cosmos document model with intentional partition key strategy.
- `/speckit.cosmosdb.multi-tenant` — multi-tenant data isolation patterns for Azure Cosmos DB.
- `/speckit.cosmosdb.pagination` — continuation-token-based pagination for Cosmos queries.
- `/speckit.cosmosdb.partition-key` — Recommend an optimal partition key for a container based on access patterns.
- `/speckit.cosmosdb.patch` — atomic patch operations for partial document updates.
- `/speckit.cosmosdb.point-read` — a point read operation (the cheapest possible Cosmos read at 1 RU).
- `/speckit.cosmosdb.query` — an optimized Cosmos SQL query with RU estimation.
- `/speckit.cosmosdb.rag` — Scaffold a complete RAG (Retrieval-Augmented Generation) application with Cosmos vector search.
- `/speckit.cosmosdb.repository` — a data access layer (repository) for a Cosmos container.
- `/speckit.cosmosdb.retry` — 429 (TooManyRequests) handling with exponential backoff.
- `/speckit.cosmosdb.scaffold-analytics` — a complete Cosmos event analytics pipeline with deterministic, production-ready architecture.
- `/speckit.cosmosdb.scaffold-booking` — a complete Cosmos appointment/reservation system with deterministic, production-ready architecture.
- `/speckit.cosmosdb.scaffold-chat` — a complete Cosmos real-time chat application with deterministic, production-ready architecture.
- `/speckit.cosmosdb.scaffold-cms` — a complete Cosmos content management system with deterministic, production-ready architecture.
- `/speckit.cosmosdb.scaffold-ecommerce` — a complete Cosmos e-commerce order API with deterministic, production-ready architecture.
- `/speckit.cosmosdb.scaffold-inventory` — a complete Cosmos warehouse inventory management application with deterministic, production-ready architecture.
- `/speckit.cosmosdb.scaffold-iot` — a complete Cosmos IoT device telemetry application with deterministic, production-ready architecture.
- `/speckit.cosmosdb.scaffold-saas` — a complete Cosmos multi-tenant SaaS platform with deterministic, production-ready architecture.
- `/speckit.cosmosdb.scaffold-social` — a complete Cosmos social feed/timeline application with deterministic, production-ready architecture.
- `/speckit.cosmosdb.scaffold-workflow` — a complete Cosmos workflow/task management application with deterministic, production-ready architecture.
- `/speckit.cosmosdb.scaffold` — a complete Cosmos application with deterministic, production-ready architecture.
- `/speckit.cosmosdb.serialization` — Configure JSON serialization for correct property naming, enum handling, and custom converters.
- `/speckit.cosmosdb.session-state` — a session/cache storage pattern with Cosmos and TTL-based expiration.
- `/speckit.cosmosdb.singleton` — a CosmosClient singleton pattern for dependency injection.
- `/speckit.cosmosdb.stored-proc` — Create stored procedures for atomic transactional operations within a partition.
- `/speckit.cosmosdb.stream-query` — an efficient streaming query for large result sets.
- `/speckit.cosmosdb.transaction` — a transactional batch operation within a single partition.
- `/speckit.cosmosdb.ttl` — Configure Time-to-Live policies for automatic data expiration.
- `/speckit.cosmosdb.upsert` — an upsert operation with conflict handling.
- `/speckit.cosmosdb.vector` — vector search configuration and query code for Azure Cosmos DB.

---

**Meta commands** (not part of implementation generation):
- `/speckit.cosmosdb.recommend` — deeper interactive design recommendation
- `/speckit.cosmosdb.explain` — explain a Cosmos concept or decision
- `/speckit.cosmosdb.review` — audit generated code (auto-fires after implement)
