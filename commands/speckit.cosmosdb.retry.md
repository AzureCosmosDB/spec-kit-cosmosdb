---
description: "Generate 429 (TooManyRequests) handling with exponential backoff."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Spec Context (optional)

If the current project has an active Spec Kit specification (e.g. `.specify/specs/<feature>/spec.md`, or a path provided in the user input), **read it first** and use it as the source of intent: entity names, fields, access patterns, scale, and consistency requirements. Prefer values from the spec over generic defaults. If no spec is present, fall back to the inputs below. **Do not modify the spec.**


# /speckit.cosmosdb.retry

> Generate 429 (TooManyRequests) handling with exponential backoff.

## Intent

Implement proper retry logic for Azure Cosmos DB rate-limited requests, either via SDK configuration or custom retry policy.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{language}}` | Target language | "TypeScript" or "C#" or "Python" |
| `{{context}}` | Where retry is needed | "SDK client options" or "custom HTTP retry" |

## Prescriptive Prompt

Generate 429 retry handling. Follow these constraints:

### Naming & Structure Constraints (MANDATORY)

- Custom retry MUST be implemented as a **decorator** named `@cosmos_retry` (Python) / wrapper function `cosmosRetry` (TS) / attribute `[CosmosRetry]` (C#)
- Decorator file MUST be named `retry.py` (Python) / `retry.ts` (TS) / `CosmosRetry.cs` (C#)
- MUST use exponential backoff **with jitter** using `random.uniform(0, 1.0)` seconds
- MUST log every retry attempt using standard `logging` module (Python) / `ILogger` (C#) / `console.warn` (TS)
- Max retries MUST default to `3` (configurable via parameter)
- MUST specifically handle `CosmosHttpResponseError` with status code `429`
- MUST include circuit breaker with 50% threshold over 10s window
- Metrics MUST track: `retry_count` (int), `total_delay_ms` (float), `success_after_retry` (bool)

### SDK-Level (Preferred)

The Azure Cosmos DB SDK handles 429s automatically when configured:

```
MaxRetryAttemptsOnRateLimitedRequests = 9
MaxRetryWaitTimeOnRateLimitedRequests = 30 seconds
```

This is sufficient for most workloads. The SDK reads `x-ms-retry-after-ms` header and backs off automatically.

### Custom Retry (When SDK isn't enough)

For scenarios beyond SDK retry (e.g., bulk operations, custom HTTP calls):

1. **Respect `Retry-After` header** - never retry before the indicated time
2. **Exponential backoff**: base delay × 2^attempt + `random.uniform(0, 1.0)` jitter
3. **Max attempts**: 3 (default, configurable)
4. **Circuit breaker**: if > 50% of requests are 429 in a 10s window, pause all operations for `Retry-After` period
5. **Log every retry** with: attempt number, delay, operation type, partition key

### Backoff Formula

```
delay = min(RetryAfterMs, baseDelay * 2^attempt + random.uniform(0, 1.0) * 1000)
maxDelay = 30000ms
```

### Output

1. SDK configuration (always include this)
2. Custom retry decorator named `@cosmos_retry` with configurable `max_retries=3`
3. Logging integration via standard `logging` module
4. Metrics: `retry_count` (int), `total_delay_ms` (float), `success_after_retry` (bool)

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="speckit-cosmosdb/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "speckit-cosmosdb/0.1.0"`. For Java, use `.userAgentSuffix("speckit-cosmosdb/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Fixed delay retry (no backoff)
- ❌ Ignoring `Retry-After` header
- ❌ Retrying non-transient errors (400, 404)
- ❌ No maximum retry limit (infinite retry loop)
- ❌ Retrying without jitter (thundering herd)
- ❌ Implementing retry as a class instead of a decorator
- ❌ Using `structlog` or third-party logging instead of stdlib `logging`
