---
description: "Generate vector search configuration and query code for Azure Cosmos DB."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.vector

> Generate vector search configuration and query code for Azure Cosmos DB.

## Intent

Set up vector search in Azure Cosmos DB with proper embedding storage, vector indexing policy, and similarity search queries.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{use_case}}` | What vector search is for | "Product similarity search" |
| `{{embedding_model}}` | Model generating embeddings | "text-embedding-ada-002" (1536 dims) |
| `{{dimensions}}` | Vector dimensions | 1536 |
| `{{distance_metric}}` | Similarity metric | "cosine", "euclidean", "dotProduct" |
| `{{language}}` | Target language | "Python" or "C#" |

## Prescriptive Prompt

Generate vector search setup for {{use_case}}. Follow these constraints:

### Container Configuration

1. Vector embedding policy in container properties:
```json
{
  "vectorEmbeddings": [
    {
      "path": "/embedding",
      "dataType": "float32",
      "distanceFunction": "{{distance_metric}}",
      "dimensions": {{dimensions}}
    }
  ]
}
```

2. Vector index in indexing policy:
```json
{
  "vectorIndexes": [
    {
      "path": "/embedding",
      "type": "quantizedFlat"  // choose per rules below
    }
  ]
}
```

### Index Type Selection

**Choose based on the number of vectors scanned _per important query_ AFTER partition-key and filter predicates - NOT total container size.**

- `flat`: Exact brute-force, 100% recall. Use for small, focused candidate sets. **Hard limit: 505 dimensions.**
- `quantizedFlat`: Brute-force over compressed vectors, supports up to 4,096 dims. Good starting point when filters/partition scope leave **≤ 50,000 vectors per search**. Slight accuracy loss from quantization.
- `diskANN`: Approximate nearest-neighbor, up to 4,096 dims. Best latency/throughput/RU when important queries span **> 50,000 vectors**. Does not guarantee exact/deterministic top-K.

**Activation threshold:** `quantizedFlat` and `diskANN` require **at least 1,000 indexed vectors** before the index is used. Below that, queries fall back to a full scan regardless of index type.

### Embedding Normalization (cosine)

When using `cosine` distance, normalize embeddings to unit length (L2 norm = 1):
```
normalized = vector / sqrt(sum(x**2 for x in vector))
```
- Cosine measures angle, not magnitude - unnormalized vectors give inconsistent scores.
- Most models (Azure OpenAI etc.) already return normalized vectors, but normalize mock/test embeddings explicitly.

### Document Schema

```json
{
  "id": "product-123",
  "partitionKey": "category-electronics",
  "title": "...",
  "description": "...",
  "embedding": [0.012, -0.034, ...],  // {{dimensions}} floats
  "metadata": { ... }
}
```

### Query Pattern

Always use `ORDER BY VectorDistance(...)` (not `WHERE`) and parameterize the query vector (hard-coded arrays cause query-plan cache misses):

```sql
SELECT TOP @k c.id, c.title, VectorDistance(c.embedding, @queryVector) AS score
FROM c
WHERE c.partitionKey = @partitionKey
ORDER BY VectorDistance(c.embedding, @queryVector)
```

### Output

1. Container creation with vector policy
2. Document model with embedding field
3. Embedding generation helper (call {{embedding_model}})
4. Vector search query function
5. Hybrid search (vector + metadata filter) example
6. Indexing policy JSON

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="speckit-cosmosdb/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "speckit-cosmosdb/0.1.0"`. For Java, use `.userAgentSuffix("speckit-cosmosdb/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Storing embeddings without vector index (falls back to brute force)
- ❌ Choosing index type from total container size instead of per-query vector count after filters
- ❌ Using `flat` for > 505 dimensions (exceeds service limit)
- ❌ Cross-partition vector search without justification
- ❌ Not specifying dimensions in policy (causes runtime errors)
- ❌ Storing embedding as string instead of float array
- ❌ Unnormalized embeddings with cosine distance (inconsistent scores)
- ❌ Hard-coding the query vector instead of parameterizing (query-plan cache misses)
- ❌ Filtering with `WHERE VectorDistance(...) < x` instead of `ORDER BY VectorDistance(...)`
