---
description: "Apply Cosmos DB best-practice rules for the current session"
---

# /speckit.cosmosdb.agent-kit

> Load Cosmos DB best-practice rules into the current AI coding session.

## Intent

Inject a comprehensive set of Cosmos DB best-practice rules so the AI agent follows them for all code generation in this session. This command is automatically triggered by the `after_plan` hook.

## Usage

This command takes no arguments. Simply run it to activate the rules.

## Rules

The following rules must be applied to **all** Cosmos DB code generated in this session:

---

# Cosmos DB Agent Kit — Best Practice Rules

These rules are enforced automatically by the Cosmos Intent SDK Agent Kit. They apply to all code in this repository that interacts with Azure Cosmos DB.

## Client Management

- **Always** use a singleton `CosmosClient` instance per application lifetime. Never create a new client per request.
- **Never** hardcode connection strings or keys in source code. Use environment variables, Azure Key Vault, or Managed Identity.
- **Prefer** Managed Identity (DefaultAzureCredential) over connection strings in production.
- Use **Direct** connection mode for latency-sensitive workloads; use **Gateway** mode only when behind corporate proxies or restrictive firewalls.
- **Always** set `user_agent_suffix` (or `ApplicationName` in .NET) to identify your app in telemetry and diagnostics.
- Configure `CosmosClientOptions` with appropriate connection limits for your expected concurrency.

## Data Modeling

- **Design containers around access patterns**, not entity types. One container can hold multiple entity types.
- **Choose partition keys based on your most frequent query**. The most-read query determines the partition key.
- **Never** use `/id` as partition key unless items are always read individually with no list/query patterns.
- **Denormalize** related data that is read together. Avoid JOINs across containers.
- **Avoid large documents** (>100KB). Split large arrays into separate items with a shared partition key.
- Use **hierarchical partition keys** for multi-tenant scenarios (e.g., `/tenantId`, `/category`, `/id`).
- Set **TTL** on ephemeral, time-series, or session data. Don't accumulate data that has no long-term value.
- Keep **item size under 2MB** (hard limit). Target <50KB for optimal performance.

## Query Patterns

- **Never** use `SELECT *` in production queries. Select only the fields you need.
- **Always** include the partition key in WHERE clauses. Cross-partition queries require explicit justification.
- **Use parameterized queries** to prevent injection and enable query plan caching.
- **Prefer point reads** (`ReadItem` with id + partition key) over queries when fetching a single item. Point reads cost 1 RU and bypass the query engine.
- Use `OFFSET/LIMIT` or continuation tokens for pagination. Never fetch unbounded result sets.
- Use **composite indexes** for queries with multiple ORDER BY or filter+sort combinations.
- Avoid **fan-out queries** that hit all partitions. Design data to support single-partition access.

## Error Handling & Retry

- **Always** implement retry with exponential backoff for transient errors (HTTP 429, 449, 503).
- Respect the `x-ms-retry-after-ms` / `Retry-After` header on 429 responses. Never ignore throttling.
- Set **request timeouts** appropriate to your SLA (default 60s for point operations, longer for queries).
- Handle `PreconditionFailed` (412) gracefully — it means your ETag-based optimistic concurrency detected a conflict.
- Distinguish between **transient** (retry) and **permanent** (fail fast) errors. 400/404 are permanent; don't retry them.
- Log `x-ms-request-charge` (RU cost) for monitoring and capacity planning.

## Concurrency

- **Always** use ETags for optimistic concurrency on updates. Read the item, modify it, write it back with `If-Match`.
- Handle conflicts with a **read-modify-write** retry loop (limited retries, typically 3-5).
- For high-contention scenarios, consider the **change feed** pattern or stored procedures for atomic operations.
- **Never** assume read-your-writes consistency in multi-region setups unless using Session or stronger consistency.

## Performance

- Define **custom indexing policies**. Exclude paths you never query on to reduce RU cost on writes.
- Use **composite indexes** for queries that sort by or filter on multiple properties.
- Use **bulk operations** (Bulk Executor / AllowBulkExecution) for batch inserts/updates of 100+ items.
- Enable **integrated cache** for read-heavy, tolerance-to-staleness workloads to reduce RU consumption.
- Use **point reads** instead of queries wherever you have the id and partition key.
- Monitor **normalized RU consumption** per partition to detect hot partitions.

## Security

- **Never** commit connection strings, keys, or tokens to source control.
- **Prefer** Azure Managed Identity / Entra ID RBAC over master keys.
- Use **resource tokens** or Entra ID for client-side / mobile access with scoped permissions.
- Enable **Azure Private Link** for network isolation in production.
- Apply **least-privilege RBAC roles** — use Cosmos DB Data Reader/Writer, not Contributor.

## Cost Optimization

- **Estimate RU cost** before deploying new queries. Use `x-ms-request-charge` to validate.
- Use **point reads** (1 RU for 1KB) instead of queries (minimum 2.3 RU) when possible.
- Avoid **fan-out queries** — they multiply RU cost by partition count.
- Use **autoscale throughput** for variable workloads; manual throughput for predictable ones.
- Consider **serverless** for dev/test and bursty low-traffic workloads.
- Enable **TTL** to auto-delete expired data instead of paying storage for stale items.
- Use **hierarchical partition keys** to avoid synthetic partition key overhead and storage skew.
