---
description: "Create stored procedures for atomic transactional operations within a partition."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.stored-proc

> Create stored procedures for atomic transactional operations within a partition.

## Intent

Write server-side stored procedures for Cosmos DB that execute atomic multi-document operations within a single logical partition, with proper error handling and bounded execution.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{operation_description}}` | What the proc does | "Transfer balance between two accounts" |
| `{{language}}` | Client language for invocation | "TypeScript" or "C#" or "Python" |
| `{{entities}}` | Documents involved | "accounts, transactions" |

## Prescriptive Prompt

Generate a stored procedure for: {{operation_description}}. Follow these constraints:

### When to Use Stored Procedures

- ✅ Atomic multi-document writes within ONE partition key
- ✅ Server-side validation before write (optimistic concurrency)
- ✅ Batch operations that must all succeed or all fail
- ❌ NOT for cross-partition operations (use Transactional Batch instead for single-partition, or saga pattern for cross-partition)
- ❌ NOT for read-heavy logic (query from client instead)
- ❌ NOT as a general application layer (hard to debug, version, test)

### Stored Procedure Structure (JavaScript only)

```javascript
function procedureName(param1, param2) {
    var context = getContext();
    var collection = context.getCollection();
    var response = context.getResponse();
    
    // 1. Validate inputs
    // 2. Query/read existing documents
    // 3. Perform logic
    // 4. Create/replace documents
    // 5. Set response body
}
```

### Bounded Execution Rules

1. **Check return value of every async call** - `collection.createDocument()`, `collection.replaceDocument()`, `collection.queryDocuments()` return `false` if request is not accepted (timeout approaching)
2. **Implement continuation**: If `false` is returned, set response with continuation token and re-invoke from client
3. **Max execution time**: 5 seconds - design for early exit
4. **Max request body**: 2MB - limit batch sizes

### Error Handling

1. **Throw on business rule violation**: `throw new Error("Insufficient balance")` - this aborts the transaction
2. **All writes are atomic**: If the proc throws, ALL writes in that execution are rolled back
3. **Return meaningful errors**: Set response body with error code before throwing
4. **Handle "not accepted"**: When `collection.createDocument()` returns `false`, respond with partial progress

### Implementation for {{operation_description}}

1. Stored procedure JavaScript source (the server-side code)
2. Client-side invocation code in {{language}}:
   - Specify partition key value (MUST match the partition the proc operates on)
   - Pass parameters as array
   - Handle response and errors
3. Registration/deployment script
4. Unit test pattern (mock `getContext()`)

### Output

1. Stored procedure JavaScript code
2. Client invocation in {{language}}
3. Error handling on client side
4. Continuation pattern if batch may exceed limits

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Cross-partition logic in a single stored procedure (impossible)
- ❌ Not checking return value of collection operations
- ❌ Unbounded loops without continuation logic
- ❌ Large response bodies (keep under 1MB)
- ❌ Using stored procedures for simple single-document CRUD
- ❌ Hardcoding partition key values in the procedure
