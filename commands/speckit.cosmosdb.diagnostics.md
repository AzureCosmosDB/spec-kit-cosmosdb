---
description: "Add SDK diagnostics logging for troubleshooting latency and errors."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.diagnostics

> Add SDK diagnostics logging for troubleshooting latency and errors.

## Intent

Configure Cosmos DB SDK diagnostics to capture request-level telemetry for debugging slow queries, 429s, timeouts, and connectivity issues.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{language}}` | Target language | "TypeScript" or "C#" or "Python" or "Java" |
| `{{framework}}` | Application framework | "ASP.NET Core" or "Express" or "FastAPI" or "Spring Boot" |

## Prescriptive Prompt

Generate diagnostics configuration for {{language}} with {{framework}}. Follow these constraints:

### What to Capture

1. **Request charge** (RU consumed per operation)
2. **Latency** (end-to-end and server-side)
3. **Status code** and sub-status code
4. **Contacted regions** and retries
5. **Activity ID** (for Azure support correlation)

### Diagnostics Strategy

1. **Always log diagnostics for failures** (4xx/5xx responses)
2. **Log diagnostics for slow operations** (> threshold, e.g., > 100ms)
3. **Sample diagnostics for successful operations** (1-5% sample rate in production)
4. **Never log full diagnostics for every request in production** (too verbose, performance impact)

### SDK-Specific Implementation

**C#**: Access `response.Diagnostics.ToString()` - contains full trace
**Java**: `response.getDiagnostics().toString()`
**Python**: `response.get_response_headers()` for charge/activity-id
**TypeScript/JavaScript**: `response.diagnostics` object

### Structured Logging Fields

```
cosmos.operation: "ReadItem"
cosmos.container: "orders"
cosmos.partition_key: "tenant-123"
cosmos.request_charge: 3.5
cosmos.latency_ms: 45
cosmos.status_code: 200
cosmos.activity_id: "guid-here"
cosmos.region: "East US"
cosmos.retry_count: 0
```

### Output

1. Diagnostics handler/middleware for {{framework}}
2. Conditional logging (errors + slow + sampled success)
3. Structured log output format
4. Dashboard query examples (KQL/Application Insights)

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="speckit-cosmosdb/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "speckit-cosmosdb/0.1.0"`. For Java, use `.userAgentSuffix("speckit-cosmosdb/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Logging full diagnostics string for every successful request (performance + cost)
- ❌ Not logging diagnostics at all (blind in production)
- ❌ Ignoring `RequestCharge` (can't optimize what you don't measure)
- ❌ Only logging on exceptions (misses 429s handled by SDK retry)
