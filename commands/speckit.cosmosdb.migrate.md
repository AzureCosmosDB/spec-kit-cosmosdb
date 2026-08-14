---
description: "Generate a migration plan and code to move from another database to Azure Cosmos DB."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.migrate

> Generate a migration plan and code to move from another database to Azure Cosmos DB.

## Intent

Produce a complete migration strategy, data transformation code, and validation plan for migrating from a source database to Cosmos DB.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{source_db}}` | Source database technology | "PostgreSQL", "MongoDB", "DynamoDB" |
| `{{source_schema}}` | Current schema/tables description | "users(id, email, name), orders(id, user_id, items[])" |
| `{{query_patterns}}` | Most common access patterns | "Get user by email, Get orders by user" |
| `{{data_volume}}` | Approximate data size | "50GB, 10M documents" |
| `{{language}}` | Implementation language | "Python" or "C#" |

## Prescriptive Prompt

You are generating a database migration from {{source_db}} to Azure Cosmos DB. Follow these constraints exactly:

### Step 1: Data Model Transformation

For each table/collection in {{source_schema}}:
1. Identify the entity and its relationships
2. Determine embedding vs referencing:
   - Embed when: data is read together, child entity doesn't exceed 2MB, bounded cardinality
   - Reference when: unbounded growth, independent access patterns, shared entities
3. Choose partition key based on {{query_patterns}} - the most frequent query filter becomes the partition key candidate
4. Design the document schema with:
   - `id` field (unique within partition)
   - Partition key field at root level
   - `type` discriminator for polymorphic containers
   - Denormalized fields for read optimization

### Step 2: Container Design

Output a container design table:

| Container | Partition Key | Entities | Throughput | Justification |
|-----------|--------------|----------|------------|---------------|

Rules:
- Combine entities into same container ONLY if they share access patterns and partition key
- Use hierarchical partition keys if single key has hot partitions
- Estimate RU/s: point read = 1 RU, query = 3-50 RU depending on complexity

### Step 3: Migration Code

Generate migration script that:
1. Reads from {{source_db}} in batches (1000 records)
2. Transforms to target document model
3. Writes to Cosmos DB using bulk execution (`AllowBulkExecution = true`)
4. Implements checkpoint/resume (store last processed ID)
5. Logs progress and errors to a separate tracking container
6. Validates row counts post-migration

### Step 4: Validation Queries

For each pattern in {{query_patterns}}:
- Original query in source database
- Equivalent Cosmos DB query
- Expected RU cost estimate
- Confirmation that the query uses the partition key (no fan-out)

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="speckit-cosmosdb/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "speckit-cosmosdb/0.1.0"`. For Java, use `.userAgentSuffix("speckit-cosmosdb/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ 1:1 table-to-container mapping without analysis
- ❌ Using JOINs thinking (Cosmos JOIN is intra-document only)
- ❌ Normalizing data as in relational DB
- ❌ Migrating without understanding access patterns first
- ❌ Single-threaded migration for large datasets
- ❌ No validation step

### Output Format

```
migration/
├── analysis.md           # Data model transformation decisions
├── container-design.md   # Container + partition key choices
├── src/
│   ├── extract.{{ext}}   # Read from source
│   ├── transform.{{ext}} # Schema transformation
│   ├── load.{{ext}}      # Bulk write to Cosmos
│   └── validate.{{ext}}  # Post-migration validation
└── runbook.md            # Step-by-step execution guide
```
