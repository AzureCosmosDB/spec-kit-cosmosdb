---
description: "Generate a Cosmos DB document model with intentional partition key strategy."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.model

> Generate a Cosmos DB document model with intentional partition key strategy.

## Intent

Create a data model (document schema) for a Cosmos DB container with proper partition key selection, indexing hints, and SDK integration.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{entity_name}}` | Name of the entity | "Order" |
| `{{fields}}` | Fields and types | "orderId: string, customerId: string, items: array, total: number, status: enum" |
| `{{access_patterns}}` | How this data is queried | "Get by customerId, filter by status, get by orderId" |
| `{{language}}` | Target language | "TypeScript" or "C#" |
| `{{cardinality}}` | Expected document count | "10M documents" |

## Prescriptive Prompt

Generate a Cosmos DB document model for {{entity_name}}. Follow these constraints:

### Partition Key Selection

Analyze {{access_patterns}} and select partition key:
1. The most frequent equality filter in queries = best partition key candidate
2. Must have high cardinality (not boolean, not status enum with 5 values)
3. Must distribute writes evenly
4. If no single field works, propose hierarchical partition key

Justify your choice with: "Partition key `/{{chosen_key}}` because: [reason based on access patterns]"

### Document Schema Rules

1. `id` must be unique within the partition (use natural key or UUID)
2. Partition key field at document root (never nested)
3. Include system-usable fields:
   - `type`: discriminator string (lowercase entity name)
   - `createdAt`: ISO 8601 timestamp
   - `updatedAt`: ISO 8601 timestamp
4. Embedded sub-documents: only for bounded, co-accessed data
5. Arrays: only for bounded collections (< 100 items typically)
6. No `null` values - omit the field instead

### Output

1. Type/interface definition in {{language}}
2. Example document (valid JSON)
3. Partition key recommendation with justification
4. Suggested indexing policy (include/exclude paths)
5. Estimated document size in KB
6. Container configuration snippet

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="speckit-cosmosdb/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "speckit-cosmosdb/0.1.0"`. For Java, use `.userAgentSuffix("speckit-cosmosdb/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Using `/id` as partition key (creates hot partition for sequential IDs)
- ❌ Using low-cardinality field (status, boolean)
- ❌ Unbounded arrays in documents
- ❌ Deeply nested partition key paths
- ❌ Including large blobs in the document (use Azure Blob Storage + reference)

## Advanced: Multi-Entity Aggregate Design

When modeling **more than one related entity** (e.g. User + Orders + OrderItems), do not model each entity in isolation. Apply aggregate-oriented design driven by access patterns.

### Access Pattern Analysis (do this FIRST)

For every access pattern, capture a row. **Every pattern MUST have an RPS estimate** - if unknown, estimate from business context.

| Pattern # | Description | RPS (peak/avg) | Type | Attributes needed | Latency SLO | Consistency |
|-----------|-------------|----------------|------|-------------------|-------------|-------------|
| 1 | Get user profile by userId on login | 500 / 200 | Read | userId, name, email | <50ms | Session |
| 2 | Create user on signup | 50 / 20 | Write | userId, name, email | <100ms | Strong |

Rule: **every read pattern should have a corresponding write pattern (and vice versa)** unless explicitly declined.

### Aggregate Correlation Analysis

For each candidate entity pair, measure how often they are accessed together:

- **Access correlation**: % of queries that need both entities together
- **Query split**: Entity1 only %, Entity2 only %, both together %
- **Size**: combined max size (must stay well under 2MB), growth pattern (bounded vs unbounded)
- **Update patterns**: independent vs related update frequency

### Identifying-Relationship Check

For each parent-child relationship, ask:
1. **Child independence** - can the child exist without the parent?
2. **Access** - do you always have the parent_id when querying children?
3. **Current design** - would separate containers force cross-partition queries for parent→child?

If **No / Yes / Yes** → use an identifying relationship (partition key = parent_id) instead of a separate container with cross-partition queries.

### Consolidation Decision Framework

| Correlation | Size / Growth | Decision |
|-------------|---------------|----------|
| >70% + identifying relationship | bounded | **Single container, multi-document** (share partition key) |
| >70% joint, small & bounded | <100KB combined | **Single document** (embed) - atomic updates, 1-RU point read |
| 50-70% | analyze coupling (backup, scaling, consistency) | Multi-doc if same ops; separate if divergent |
| <30% OR unbounded growth OR independent scaling | any | **Separate containers** |

- **Single document** = atomic updates + point read (`ReadItem(id, partitionKey)`, 1 RU), but capped at 2MB
- **Multi-document container** = related docs share a partition key, retrieved in one query, transactional within the partition, no per-doc size coupling
- **Separate containers** = clean separation, independent throughput, but cross-partition query cost

### RU Cost Reasoning (validate before finalizing)

Use realistic document sizes, not theoretical 1KB:
- Point read (1KB): 1 RU | Query (1KB): ~2-5 RU | Write (1KB): ~5 RU | Update (1KB): ~7 RU | Delete: ~5 RU
- Large docs (>10KB) scale RU proportionally
- **Cross-partition query overhead**: ~2.5 RU × physical partitions scanned
- **Physical partitions** ≈ total data size ÷ 50GB
- Prefer designs that keep hot/high-RPS patterns single-partition

### Massive-Scale Warning

If write volume exceeds ~10k writes/sec or millions of records land in short bursts, before modeling ask about:
1. **Data binning/chunking** - can individual records be grouped into chunks per document?
2. **Write reduction** - can writes be batched instead of processed individually?
3. **Physical partition implications** - how will total data size inflate cross-partition query cost?

### Multi-Entity Deliverable

When 2+ entities are involved, output:
1. Access pattern table (with RPS)
2. Aggregate/consolidation decisions with justification per entity pair
3. Final container design table: `Container | Partition Key | Entities | Throughput | Justification`
4. Per-container document schemas (as in the single-entity output above)
5. Hot-partition risk assessment for high-RPS patterns
