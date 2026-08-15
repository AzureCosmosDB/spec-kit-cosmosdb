# Azure Cosmos DB - Spec Kit Extension

> ⚠️ **Preview release (v0.1.0).** This extension is in active development. Commands, prompts, and behavior may change between versions. Feedback and issues are very welcome.

Prescriptive prompt templates for Azure Cosmos DB that produce deterministic, best-practice code with any AI coding agent.

This is a [Spec Kit](https://github.com/github/spec-kit) extension. It provides 53 commands covering micro patterns, component patterns, full scaffolds, and meta tools for Azure Cosmos DB development.

## Installation

```bash
specify extension add cosmosdb --from https://github.com/AzureCosmosDB/spec-kit-cosmosdb/archive/refs/tags/v0.1.0.zip
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

## Typical Workflow: Building a Cosmos DB App with Spec Kit

This extension's commands sit **alongside** the standard Spec Kit loop (`/speckit.specify` → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`). They inject prescriptive, best-practice Azure Cosmos DB code at the points where the data layer matters — with two **automatic hooks**: `before_implement` (recommends the relevant commands) and `after_implement` (reviews the result).

> **How automation works:** when you run `/speckit.implement`, the **`before_implement` hook auto-fires `speckit.cosmosdb.advise`**, which reads your spec/tasks and recommends *only the relevant* Cosmos commands (a shortlist, not all 49). You then invoke those recommended `speckit.cosmosdb.*` commands to get prescriptive best-practice code — the base `/implement` still generates generic code on its own, so invoking the recommended commands is what upgrades the data layer to best-practice. After implementation, the **`after_implement` hook** auto-fires `review`.

> **Context-efficient:** the advisor injects a compact command *index* (~1.5K tokens) plus a short recommendation — never the full library. Each recommended command loads its full guidance only when you invoke it.

Here is a typical end-to-end flow for building an app whose data layer runs on Azure Cosmos DB:

```bash
# 1. SPECIFY — describe the feature (standard Spec Kit)
/speckit.specify "An e-commerce service that stores orders and lets customers
                  look up their order history quickly"

# 2. (optional) RECOMMEND — let the extension suggest a Cosmos design from the spec
/speckit.cosmosdb.recommend
#   → reads the active spec, proposes partition-key strategy, access patterns,
#     and which cosmosdb commands to use. Advisory only.

# 3. PLAN — produce the implementation plan (standard Spec Kit)
/speckit.plan

# 4. Design the data layer with prescriptive Cosmos commands.
#    With spec-context awareness, these read the active spec for intent
#    (entities, access patterns, scale) — no need to re-type everything.
/speckit.cosmosdb.model            # document model + partition key strategy
/speckit.cosmosdb.partition-key    # validate/derive the partition key choice
/speckit.cosmosdb.container        # container with indexing + PK
/speckit.cosmosdb.repository       # repository pattern over the model

# 5. TASKS — break the plan into tasks (standard Spec Kit)
/speckit.tasks

# 6. IMPLEMENT — generate code (standard Spec Kit).
#    The before_implement hook auto-fires `advise`, which recommends ONLY
#    the relevant Cosmos commands for this feature. Invoke those to get
#    best-practice implementations for each access pattern:
/speckit.implement
#   → before_implement hook: `advise` recommends e.g. point-read, query, pagination
/speckit.cosmosdb.point-read       # 1-RU reads by id + partition key
/speckit.cosmosdb.query            # optimized, parameterized queries
/speckit.cosmosdb.pagination       # continuation-token pagination
/speckit.cosmosdb.upsert           # conflict-aware writes
/speckit.cosmosdb.retry            # exponential-backoff retry logic

# 7. REVIEW — fires AUTOMATICALLY after /speckit.implement via the
#    after_implement hook (or run it explicitly any time):
/speckit.cosmosdb.review           # audits generated code vs. Cosmos best practices
```

**Shortcut for whole-app skeletons:** if you're starting a well-known app shape, the `scaffold-*` commands generate a complete best-practice starting point in one step (e.g. `/speckit.cosmosdb.scaffold-ecommerce`, `scaffold-chat`, `scaffold-saas`), which you then refine through the normal loop.

### Where each command type fits the flow

| Spec Kit phase | Cosmos commands you'd typically use | Invocation |
|----------------|-------------------------------------|------------|
| `specify` | *(none — describe intent in plain language)* | — |
| after `specify` | `recommend` | explicit (advisory) |
| `plan` | `model`, `partition-key`, `container`, `repository`, `index-policy` | explicit |
| `tasks` | *(none)* | — |
| before `implement` | `advise` (recommends the relevant subset) | **automatic (hook)** |
| `implement` | `point-read`, `query`, `pagination`, `upsert`, `patch`, `transaction`, `changefeed`, `vector`, etc. | explicit (per advisor shortlist) |
| after `implement` | `review` | **automatic (hook)** |

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
| `speckit.cosmosdb.advise` | Analyze the active spec/tasks and recommend only the relevant commands (auto-fires before implement) |
| `speckit.cosmosdb.recommend` | Conversational entry point - describe what you want, get the right command |
| `speckit.cosmosdb.review` | Review generated code against Azure Cosmos DB best practices |
| `speckit.cosmosdb.explain` | Explain Azure Cosmos DB concepts in context |

> **Best-practice rules:** For always-on Azure Cosmos DB coding guardrails, install the [`cosmosdb-agent-kit`](https://github.com/AzureCosmosDB/cosmosdb-agent-kit) skill separately. It loads 100+ best-practice rules into your AI session. This extension focuses on prescriptive *workflows*; the agent kit provides the passive ruleset.

## Hooks

This extension provides two automatic hooks:

- **`before_implement`** → `speckit.cosmosdb.advise`: Inspects the active spec/plan/tasks and recommends **only the relevant** Azure Cosmos DB commands for the feature being implemented. It injects a lightweight command *index* (~1.5K tokens) and a shortlist — **not** the full command library — so `/implement` becomes Cosmos-aware without bloating the context window. You then invoke the recommended `speckit.cosmosdb.*` commands, each of which loads its full prescriptive guidance only when called.
- **`after_implement`** → `speckit.cosmosdb.review`: Optionally reviews generated code against Azure Cosmos DB best practices.

> **Context-efficient by design:** the `before_implement` advisor never loads all 49 generative commands. It surfaces a small relevant subset (typically 3–8), and each full command is loaded only on explicit invocation. Commands remain fully separate and independently runnable.

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
