# Azure Cosmos DB - Spec Kit Extension

Prescriptive prompt templates for Azure Cosmos DB that produce deterministic, best-practice code with any AI coding agent.

This is a [Spec Kit](https://github.com/spec-kit/spec-kit) extension. It provides 53 commands covering micro patterns, component patterns, full scaffolds, and meta tools for Azure Cosmos DB development.

## Installation

```bash
specify extension add cosmosdb --from https://github.com/TheovanKraay/spec-kit-cosmosdb/archive/refs/tags/v1.0.0.zip
```

## Two Paths: Guided vs. Explicit Commands

### 🎨 Guided Path
Describe what you want in plain language - the SDK figures out the right commands:

```
/speckit.cosmosdb.recommend "I want to build a real-time chat app with message history"
```

### 🔧 Explicit Path
Call specific commands directly when you know exactly what you need:

```
/speckit.cosmosdb.scaffold-chat
/speckit.cosmosdb.singleton
/speckit.cosmosdb.changefeed
```

## Available Commands

### Micro Patterns (single-concern, composable)

| Command | Description |
|---------|-------------|
| `speckit.cosmosdb.singleton` | Generate a CosmosClient singleton pattern for dependency injection |
| `speckit.cosmosdb.retry` | Generate retry logic with exponential backoff for Azure Cosmos DB |
| `speckit.cosmosdb.connection` | Generate Azure Cosmos DB connection configuration |
| `speckit.cosmosdb.point-read` | Generate an efficient point read operation |
| `speckit.cosmosdb.upsert` | Generate an upsert operation with conflict handling |
| `speckit.cosmosdb.patch` | Generate a partial document update (patch) operation |
| `speckit.cosmosdb.etag` | Generate optimistic concurrency with ETags |
| `speckit.cosmosdb.transaction` | Generate a transactional batch operation |
| `speckit.cosmosdb.pagination` | Generate pagination with continuation tokens |
| `speckit.cosmosdb.partition-key` | Generate partition key strategy |
| `speckit.cosmosdb.index-policy` | Generate a custom indexing policy |
| `speckit.cosmosdb.diagnostics` | Generate diagnostics and request charge logging |
| `speckit.cosmosdb.cross-partition` | Generate a cross-partition query with justification |
| `speckit.cosmosdb.conditional-create` | Generate a conditional create operation |
| `speckit.cosmosdb.serialization` | Generate serialization configuration |
| `speckit.cosmosdb.stream-query` | Generate streaming query results |
| `speckit.cosmosdb.availability` | Generate high-availability patterns |

### Component Patterns (multi-concern building blocks)

| Command | Description |
|---------|-------------|
| `speckit.cosmosdb.model` | Generate a Azure Cosmos DB document model with partition key strategy |
| `speckit.cosmosdb.repository` | Generate a repository pattern for Azure Cosmos DB |
| `speckit.cosmosdb.query` | Generate optimized Azure Cosmos DB queries |
| `speckit.cosmosdb.container` | Generate container creation with indexing and partition strategy |
| `speckit.cosmosdb.changefeed` | Generate a change feed consumer |
| `speckit.cosmosdb.changefeed-processor` | Generate a change feed processor with leases |
| `speckit.cosmosdb.bulk` | Generate bulk import/export operations |
| `speckit.cosmosdb.ttl` | Generate TTL-based data expiration |
| `speckit.cosmosdb.autoscale` | Generate autoscale throughput configuration |
| `speckit.cosmosdb.hierarchical-pk` | Generate hierarchical partition key patterns |
| `speckit.cosmosdb.multi-tenant` | Generate multi-tenant isolation patterns |
| `speckit.cosmosdb.global-distribution` | Generate multi-region configuration |
| `speckit.cosmosdb.endpoint` | Generate API endpoints backed by Azure Cosmos DB |
| `speckit.cosmosdb.api-pagination` | Generate API-level pagination over Azure Cosmos DB |
| `speckit.cosmosdb.stored-proc` | Generate stored procedures |
| `speckit.cosmosdb.vector` | Generate vector search with Azure Cosmos DB |
| `speckit.cosmosdb.cqrs` | Generate CQRS pattern with Azure Cosmos DB |
| `speckit.cosmosdb.event-sourcing` | Generate event sourcing with Azure Cosmos DB |
| `speckit.cosmosdb.session-state` | Generate session state management |

### Scaffold Commands (full application generation)

| Command | Description |
|---------|-------------|
| `speckit.cosmosdb.scaffold` | Generate a complete Azure Cosmos DB application |
| `speckit.cosmosdb.scaffold-chat` | Scaffold a real-time chat application |
| `speckit.cosmosdb.scaffold-ecommerce` | Scaffold an e-commerce application |
| `speckit.cosmosdb.scaffold-iot` | Scaffold an IoT data platform |
| `speckit.cosmosdb.scaffold-saas` | Scaffold a multi-tenant SaaS application |
| `speckit.cosmosdb.scaffold-social` | Scaffold a social media application |
| `speckit.cosmosdb.scaffold-cms` | Scaffold a content management system |
| `speckit.cosmosdb.scaffold-analytics` | Scaffold an analytics dashboard |
| `speckit.cosmosdb.scaffold-booking` | Scaffold a booking/reservation system |
| `speckit.cosmosdb.scaffold-inventory` | Scaffold an inventory management system |
| `speckit.cosmosdb.scaffold-workflow` | Scaffold a workflow automation system |
| `speckit.cosmosdb.migrate` | Generate a data migration plan |
| `speckit.cosmosdb.rag` | Scaffold a RAG (Retrieval Augmented Generation) app |

### Meta Commands

| Command | Description |
|---------|-------------|
| `speckit.cosmosdb.recommend` | Conversational entry point - describe what you want, get the right command |
| `speckit.cosmosdb.review` | Review generated code against Azure Cosmos DB best practices |
| `speckit.cosmosdb.explain` | Explain Azure Cosmos DB concepts in context |

> **Best-practice rules:** For always-on Azure Cosmos DB coding guardrails, install the [`cosmosdb-agent-kit`](https://github.com/AzureCosmosDB/cosmosdb-agent-kit) skill separately. It loads 100+ best-practice rules into your AI session. This extension focuses on prescriptive *workflows*; the agent kit provides the passive ruleset.

## Hooks

This extension provides one automatic hook:

- **`after_implement`** → `speckit.cosmosdb.review`: Optionally reviews generated code against Azure Cosmos DB best practices.

## Testing Results

Determinism testing across multiple AI models shows:

- **Micro patterns**: ~80-95% structural consistency across independent generations
- **Component patterns**: ~75-90% structural consistency
- **Scaffolds**: ~85-95% structural consistency with prescriptive constraints

Full test results are in `testing/results/`.

## Compatibility

See [COMPATIBILITY.md](COMPATIBILITY.md) for supported languages, frameworks, and AI coding agents.

## License

MIT - see [LICENSE](LICENSE).
