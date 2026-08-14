# Rules System

## Overview

The speckit-cosmosdb references **111 best-practice rules** organized across **12 categories**, sourced from the [cosmosdb-agent-kit](https://github.com/AzureCosmosDB/cosmosdb-agent-kit). These rules encode domain expertise that constrains AI-generated output to produce architecturally sound Azure Cosmos DB solutions.

## Rule Categories & Prefixes

| Prefix | Category | Count | Description |
|--------|----------|-------|-------------|
| `model-*` | Data Modeling | ~12 | Document structure, embedding vs referencing, denormalization |
| `partition-*` | Partition Keys | ~10 | Key selection, cardinality, cross-partition avoidance |
| `query-*` | Queries | ~12 | Filter optimization, projections, pagination patterns |
| `sdk-*` | SDK Patterns | ~10 | Connection policies, retry, bulk, transactional batch |
| `index-*` | Indexing | ~9 | Composite indexes, spatial, range vs hash |
| `throughput-*` | Throughput | ~10 | RU budgeting, autoscale, serverless vs provisioned |
| `global-*` | Global Distribution | ~8 | Multi-region writes, consistency levels, conflict resolution |
| `monitor-*` | Monitoring | ~8 | Diagnostics, metrics, alerting patterns |
| `design-*` | Design Patterns | ~12 | Change feed, materialized views, event sourcing |
| `tooling-*` | Tooling | ~6 | Emulator, Data Explorer, CI/CD |
| `vector-*` | Vector Search | ~7 | Embedding storage, similarity search, hybrid queries |
| `fts-*` | Full-Text Search | ~7 | Text indexing, scoring, linguistic analysis |

## How Prompt Templates Reference Rules

Each prompt template includes a `rules` field specifying which rule prefixes apply:

```yaml
# prompts/design-container/prompt.yaml
name: design-container
rules:
  - model-*
  - partition-*
  - index-*
variables:
  - name: entity_description
    type: string
  - name: access_patterns
    type: string[]
```

When a prompt is rendered, the referenced rules are injected into the system context as constraints. The AI must conform its output to these rules.

## Rule Format

Each rule is a short, actionable statement:

```
partition-001: Choose a partition key with high cardinality that appears in most query WHERE clauses.
partition-002: Avoid partition keys that create hot partitions (e.g., timestamps, sequential IDs).
partition-003: For multi-tenant apps, use tenantId as partition key unless tenant sizes vary >100x.
```

## Adding Custom Rules

Place additional `.rules` files in the `rules/custom/` directory. They follow the same format and can be referenced by prompt templates using their prefix.

## Rule Resolution

1. Template declares `rules: [partition-*, model-*]`
2. SDK loads all rules matching those glob patterns
3. Rules are deduplicated and sorted by ID
4. Rules are injected as a numbered constraint list in the system prompt
5. AI output is expected to conform; the testing harness validates structural adherence
