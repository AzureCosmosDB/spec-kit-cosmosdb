---
description: "Generate an API endpoint backed by Cosmos DB with proper error mapping."
---

# /cosmos.endpoint

> Generate an API endpoint backed by Cosmos DB with proper error mapping.

## Intent

Create an HTTP endpoint (REST or GraphQL) that uses a Cosmos DB repository, with proper status code mapping, validation, and error responses.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{method}}` | HTTP method | "GET", "POST", "PATCH", "DELETE" |
| `{{path}}` | Route path | "/api/orders/:orderId" |
| `{{operation}}` | What it does | "Get order by ID for the authenticated customer" |
| `{{framework}}` | Web framework | "Express", "Fastify", "ASP.NET Core Minimal API" |
| `{{language}}` | Target language | "TypeScript" or "C#" |

## Prescriptive Prompt

Generate an API endpoint. Follow these constraints:

### Error Mapping

| Cosmos Exception | HTTP Status | Response Body |
|-----------------|-------------|---------------|
| 404 NotFound | 404 | `{ "error": "Resource not found" }` |
| 409 Conflict | 409 | `{ "error": "Resource already exists" }` |
| 412 PreconditionFailed | 409 | `{ "error": "Resource was modified, retry" }` |
| 429 TooManyRequests | 503 | `{ "error": "Service busy", "retryAfter": N }` |
| 400 BadRequest | 400 | `{ "error": "Invalid request" }` |

### Requirements

1. Input validation before calling repository
2. Extract partition key from auth context or path params
3. Use repository (never call Cosmos SDK directly in handler)
4. Return consistent error shape: `{ error: string, details?: any }`
5. Include request correlation ID in response headers
6. Log operation with RU charge from response headers

### Output

1. Route/endpoint handler code
2. Request/response type definitions
3. Validation logic
4. Integration test example

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.
