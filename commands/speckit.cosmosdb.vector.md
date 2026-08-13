---
description: "Generate vector search configuration and query code for Cosmos DB."
---

# /cosmos.vector

> Generate vector search configuration and query code for Cosmos DB.

## Intent

Set up vector search in Cosmos DB with proper embedding storage, vector indexing policy, and similarity search queries.

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
      "type": "quantizedFlat"  // or "flat" for < 5000 docs, "diskANN" for > 100K
    }
  ]
}
```

### Index Type Selection

- `flat`: < 5,000 vectors, perfect recall, highest RU cost per query
- `quantizedFlat`: 5,000-100,000 vectors, good recall, moderate cost
- `diskANN`: > 100,000 vectors, approximate recall, lowest cost at scale

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

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Storing embeddings without vector index (falls back to brute force)
- ❌ Using `flat` index for > 10K vectors (too expensive)
- ❌ Cross-partition vector search without justification
- ❌ Not specifying dimensions in policy (causes runtime errors)
- ❌ Storing embedding as string instead of float array
