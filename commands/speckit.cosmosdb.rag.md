---
description: "Scaffold a complete RAG (Retrieval-Augmented Generation) application with Cosmos DB vector search."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.rag

> Scaffold a complete RAG (Retrieval-Augmented Generation) application with Cosmos DB vector search.

## Intent

Generate a full RAG application structure using Cosmos DB as the vector store, including embedding generation, vector indexing, hybrid search (vector + filter), and chat history storage.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{language}}` | Target language | "TypeScript" or "C#" or "Python" |
| `{{embedding_model}}` | Embedding model | "text-embedding-ada-002" or "text-embedding-3-small" |
| `{{llm_provider}}` | LLM for generation | "Azure OpenAI" or "OpenAI" or "local" |
| `{{use_case}}` | Application domain | "customer support KB" or "internal docs search" or "product catalog" |

## Prescriptive Prompt

Scaffold a RAG application for {{use_case}} using {{language}}, {{embedding_model}} embeddings, and {{llm_provider}} for generation, with Cosmos DB as the vector store. Follow these constraints:

### Architecture Overview

```
Documents → Chunking → Embedding → Cosmos DB (vector index)
                                         ↓
User Query → Embed Query → Vector Search → Top-K docs → LLM → Response
                                         ↓
                              Chat History (same Cosmos DB account)
```

### Container Design

1. **Documents container** (`/category` or `/source` partition key):
   - `id`, `content`, `embedding` (float array), `metadata`, `source`, `chunkIndex`
   - Vector index on `embedding` property
2. **Chat history container** (`/sessionId` partition key):
   - `id`, `sessionId`, `role`, `content`, `timestamp`, `tokens`
   - TTL enabled for session expiry

### Vector Index Configuration

1. **Index type**: `quantizedFlat` for < 10K items, `diskANN` for larger datasets
2. **Dimensions**: Match {{embedding_model}} output (ada-002 = 1536, 3-small = 1536, 3-large = 3072)
3. **Similarity**: `cosine` (default, works for normalized embeddings)
4. **Indexing policy**: Include vector path in index; exclude from range index

```json
{
  "vectorIndexes": [
    { "path": "/embedding", "type": "diskANN" }
  ],
  "vectorEmbeddingPolicy": {
    "vectorEmbeddings": [
      {
        "path": "/embedding",
        "dataType": "float32",
        "dimensions": 1536,
        "distanceFunction": "cosine"
      }
    ]
  }
}
```

### Document Ingestion Pipeline

1. **Chunking**: Split documents into 500-1000 token chunks with 100-token overlap
2. **Embedding**: Call {{embedding_model}} to generate vector for each chunk
3. **Upsert**: Store chunk with embedding in Cosmos DB
4. **Metadata**: Preserve source, page number, section title for citation

### Search Implementation

1. **Vector search query**:
```sql
SELECT TOP @topK c.id, c.content, c.metadata,
       VectorDistance(c.embedding, @queryVector) AS score
FROM c
ORDER BY VectorDistance(c.embedding, @queryVector)
```

2. **Hybrid search** (vector + filter):
```sql
SELECT TOP @topK c.id, c.content,
       VectorDistance(c.embedding, @queryVector) AS score
FROM c
WHERE c.category = @category
ORDER BY VectorDistance(c.embedding, @queryVector)
```

3. **Top-K**: Default 5-10 results; tune based on context window size

### Generation (LLM Call)

1. **System prompt**: Define role and constraints for {{use_case}}
2. **Context injection**: Insert top-K search results into prompt
3. **Citation**: Include source metadata so LLM can cite
4. **Chat history**: Include last N turns from chat history container
5. **Token budget**: Reserve tokens for context (max 60% of context window)

### Chat History Management

1. Store each user/assistant message with `sessionId` partition key
2. TTL: 24 hours for anonymous, 30 days for authenticated
3. Retrieve last 10 messages for context (or summarize if > 10)

### Output (Scaffold Structure)

```
src/
├── config/           # Cosmos DB + LLM connection config
├── ingestion/        # Document chunking + embedding pipeline
│   ├── chunker       # Text splitting logic
│   ├── embedder      # Embedding API client
│   └── loader        # Cosmos DB upsert
├── search/           # Vector search + hybrid search
├── generation/       # LLM prompt assembly + call
├── chat/             # Chat history CRUD
├── api/              # HTTP endpoints (query, ingest, history)
└── models/           # Document, ChatMessage, SearchResult types
```

1. Full project scaffold with the above structure
2. Container creation scripts (documents + chat history + vector index)
3. Ingestion script (chunking + embedding + upsert)
4. Search function (vector + hybrid)
5. Generation function (context assembly + LLM call)
6. Chat history management
7. API endpoint for end-to-end RAG query

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Storing embeddings without a vector index (full scan = expensive)
- ❌ Chunks too large (> 2000 tokens) - embeddings lose specificity
- ❌ Chunks too small (< 100 tokens) - lack context
- ❌ No overlap between chunks (misses context at boundaries)
- ❌ Ignoring token limits (stuffing too many results into prompt)
- ❌ Not persisting chat history (loses conversational context)
- ❌ Using cross-partition queries for chat history (partition by sessionId)
- ❌ Flat vector index for > 10K documents (use diskANN for scale)
