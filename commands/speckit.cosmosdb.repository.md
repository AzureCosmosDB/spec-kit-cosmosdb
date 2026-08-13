---
description: "Generate a data access layer (repository) for a Cosmos DB container."
---

# /cosmos.repository

> Generate a data access layer (repository) for a Cosmos DB container.

## Intent

Create a repository class/module that encapsulates all Cosmos DB operations for a specific entity, with proper error handling, retry logic, and query patterns.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{entity_name}}` | Entity this repository manages | "Order" |
| `{{container_name}}` | Container name | "orders" |
| `{{partition_key}}` | Partition key path | "/customerId" |
| `{{operations}}` | CRUD + query operations needed | "create, getById, getByCustomer, updateStatus, delete" |
| `{{language}}` | Target language | "TypeScript" or "C#" |

## Prescriptive Prompt

Generate a repository for {{entity_name}} in {{language}}. Follow these constraints:

### Structure

1. Constructor receives `Container` instance (injected, never creates its own client)
2. Each operation in {{operations}} becomes a typed method
3. All methods return typed results (not raw Response objects to callers)
4. Error handling: catch `CosmosException`/cosmos errors, throw domain exceptions

### Method Patterns

**Create**: 
- Use `container.createItem(item, { partitionKey })` / `CreateItemAsync`
- Return created document with generated id
- Handle 409 Conflict explicitly

**Read (point read)**:
- Use `container.readItem(id, partitionKey)` / `ReadItemAsync`  
- NEVER use a query when you have id + partition key
- Handle 404 explicitly, return null/Option

**Query**:
- Use parameterized queries
- Always include partition key in query filter
- Return typed array with continuation token support

**Update**:
- Read current → modify → replace with ETag (optimistic concurrency)
- OR use patch operations for single-field updates
- Handle 412 PreconditionFailed (ETag mismatch)

**Delete**:
- Soft delete preferred (set `deleted: true`, rely on TTL)
- Handle 404 gracefully

### Output

Complete file with:
- Type imports
- Interface/type for the entity
- Repository class with all methods
- Proper TypeScript/C# typing throughout
- JSDoc/XML doc comments on each method
- Unit test file with mocked container

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Querying by id when partition key is known (use point read)
- ❌ Returning raw SDK response types to callers
- ❌ No ETag handling on updates
- ❌ Creating CosmosClient inside repository
- ❌ Catching and swallowing errors silently
- ❌ Unbounded query results without pagination
