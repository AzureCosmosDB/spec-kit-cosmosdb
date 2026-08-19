# Azure Cosmos DB best practices (Spec Kit — Azure Cosmos DB extension)

Apply these rules whenever you write Azure Cosmos DB (NoSQL API) code, in any language. They are compact on purpose (this file is always-on context). For deeper, ready-to-use implementations, run the matching `/speckit.cosmosdb.*` command.

## Rules

1. **Auth:** use `DefaultAzureCredential` (azure-identity). Never hardcode account keys or connection strings.
2. **User agent (mandatory):** every `CosmosClient` sets an application name — Python `user_agent_suffix="speckit-cosmosdb/<version>"`, .NET `CosmosClientOptions.ApplicationName`, Java/JS `userAgentSuffix`.
3. **Client singleton:** create one `CosmosClient` and reuse it (dependency-injected); never instantiate per request.
4. **Reference the existing database** — do not create databases. You may create containers, and should choose partition keys and index/vector policy deliberately.
5. **Partition key:** design it intentionally from the access patterns (high cardinality); use a **hierarchical** (sub-partitioned) key for multi-tenant / high-cardinality data. (`/speckit.cosmosdb.partition-key`, `.hierarchical-pk`)
6. **Reads:** when you have `id` + partition key, use a **point read** (`read_item`/`ReadItem`), pass the partition key explicitly, and **return `None`/`null` on 404** — never throw for not-found. (`/speckit.cosmosdb.point-read`)
7. **Queries:** parameterize with `@name` (no string interpolation/f-strings), keep them **partition-scoped** (partition key in `WHERE`), and **project specific fields — never `SELECT *`**. Avoid cross-partition queries unless the access pattern genuinely requires it. (`/speckit.cosmosdb.query`)
8. **Concurrency:** use **ETag** optimistic concurrency (`If-Match`) with a bounded retry for read-modify-write; use a **transactional batch** for single-partition multi-item atomicity. (`/speckit.cosmosdb.etag`, `.transaction`)
9. **429 (TooManyRequests):** handle with exponential backoff + jitter. (`/speckit.cosmosdb.retry`)
10. **Indexing:** match the index policy to the query patterns; don't ship default indexing for production. (`/speckit.cosmosdb.index-policy`)
11. **Bulk:** use bulk execution for high-throughput batch writes. (`/speckit.cosmosdb.bulk`)

## Getting deeper help

- New project: `/speckit.cosmosdb.scaffold` (or a domain scaffold, e.g. `/speckit.cosmosdb.scaffold-saas`).
- Specific pattern: run the matching command above; each loads its full prescriptive guidance only when invoked.
- Not sure which to run: `/speckit.cosmosdb.advise` recommends the relevant commands for your feature.
