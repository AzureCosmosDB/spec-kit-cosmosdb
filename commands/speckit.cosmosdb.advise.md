---
description: "Analyze the active spec/tasks, select the relevant Azure Cosmos DB patterns, and inline their compact best-practice rules so implementation applies them directly (auto-fires before /implement)."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.advise

> Inspects the active Spec Kit feature, selects **only the relevant** Azure Cosmos DB patterns, and **inlines their compact best-practice rules** so `/speckit.implement` applies them directly. This is the `before_implement` advisor: it delivers the non-negotiable rules for the few patterns that matter (and names the full `/speckit.cosmosdb.*` command for deeper guidance), rather than only pointing at commands the agent may never invoke.

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

4. **Inline the compact best-practice rules for each selected pattern.** For every pattern you select, copy its bullet block from the **Best-practice rule digest** below directly into your output, so the implementation applies the rules without needing a second command invocation. Still name the full `/speckit.cosmosdb.*` command so the developer can load deeper guidance on demand. Inline ONLY the digests for the patterns this feature needs — the selected shortlist, never the whole digest.

## Output format

```
## Azure Cosmos DB best practices for this feature (apply during /implement)

Based on <spec/plan/tasks or your description>, apply these rules while implementing:

### <pattern> — /speckit.cosmosdb.<name>  (why, tied to the spec)
- <rule 1 from the digest>
- <rule 2 from the digest>

### <pattern> — /speckit.cosmosdb.<name>  (why)
- <rules...>

(Selected only the patterns this feature needs. Run the named command for the full guidance on any pattern.)
```

## Best-practice rule digest (inline the entries for the patterns you select)

Copy the bullet block for each selected pattern into your output. These are the
non-negotiable rules each `/speckit.cosmosdb.*` command enforces; inlining them puts the
guidance in front of the implementer directly instead of behind a command they may never run.

- **model / partition-key** — Choose the partition key from the access patterns, not the data shape: the field most reads filter by, high-cardinality, evenly distributed. Do not default to `/id`. Document the choice and the queries it serves. Give documents `id`, `type`, `createdAt`, `updatedAt`; avoid unbounded arrays and deep nesting.
- **point-read** — For a known `id` + partition key, use a point read (`read_item(id, partition_key)`), never a query. It is the cheapest read (~1 RU). Never `SELECT ... WHERE id = ...` for a single known item.
- **query** — Always parameterize (no string concatenation). Include the partition key in the `WHERE` clause whenever it is known; treat cross-partition queries as intentional and justify them. Avoid `SELECT *`; project only needed fields; set a max item count and paginate.
- **etag (optimistic concurrency)** — For read-modify-write and any concurrent update, capture `_etag` on read and write with `if_match=etag`. On `412` (precondition failed) re-read and retry. This is how you prevent lost updates and overselling under concurrency.
- **transaction / stored-proc** — For multi-item atomicity within a SINGLE partition (e.g. decrement capacity + create a booking), use a transactional batch (or a stored procedure) so the invariant holds atomically. Do not implement cross-item invariants with separate non-atomic writes.
- **conditional-create** — To reject duplicates, create with `if_none_match="*"` and handle `409 Conflict` as "already exists" rather than crashing.
- **retry (429)** — Catch throttling (`429`), honor the `Retry-After` / `x-ms-retry-after-ms` hint, and back off exponentially. Configure the client's retry options rather than failing on the first throttle.
- **404 as null** — Catch not-found (`CosmosResourceNotFoundError` / `404`) and return null/None; never let a missing item surface as an unhandled exception.
- **singleton / connection** — Create ONE `CosmosClient` for the application lifetime (never per request). Authenticate keyless with `DefaultAzureCredential` (endpoint from environment, no keys in code). Set an application name / user-agent suffix. Separate emulator vs production config.
- **pagination** — Page with continuation tokens exposed as opaque cursors; never load an entire container into memory.
- **hierarchical-pk** — For multi-tenant or high-cardinality data, use hierarchical (sub-partitioned) keys (e.g. tenantId then entityId) so a tenant's data co-locates and queries stay single-partition.
- **index-policy** — Do not ship the default index-everything policy for write-heavy or large-document workloads: include only queried paths, exclude the rest.
- **ttl** — For transient/expiring data (sessions, telemetry windows), configure TTL so Cosmos expires it automatically instead of manual cleanup.
- **changefeed / changefeed-processor** — For event-driven projections/materialized views, consume the change feed with a lease container, checkpointing, and error handling; make processing idempotent.
- **bulk** — For high-throughput ingestion, enable bulk mode and batch writes rather than serial point writes.
- **vector** — For RAG/similarity, configure a vector index and use `VectorDistance` in the query; store embeddings on the document.

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
