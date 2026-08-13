---
description: "Generate a CosmosClient singleton pattern for dependency injection."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.singleton

> Generate a CosmosClient singleton pattern for dependency injection.

## Intent

Create a properly configured CosmosClient singleton that is registered once and shared across the application lifetime.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{language}}` | Target language/framework | "C# + ASP.NET Core" or "TypeScript + Express" |
| `{{auth_model}}` | Authentication | "connection-string" or "DefaultAzureCredential" |

## Prescriptive Prompt

Generate a CosmosClient singleton. Follow these constraints exactly:

### Naming & Structure Constraints (MANDATORY)

- Module/file MUST be named `cosmos_client.py` (Python) or `cosmosClient.ts` (TypeScript) or `CosmosClientFactory.cs` (C#)
- Singleton function MUST be named `get_cosmos_client()` (Python) / `getCosmosClient()` (TS) / `GetCosmosClient()` (C#)
- MUST use **module-level singleton pattern** (not class-based `__new__` or metaclass)
- Settings class MUST be named `CosmosSettings`
- Health check function MUST be named `check_cosmos_health`
- MUST include type hints on ALL functions and return types
- Disposal MUST use FastAPI lifespan context manager (Python) / `IHostApplicationLifetime` (C#) — NOT `atexit`

### Rules

1. **ONE instance per application** — registered as singleton in DI
2. **Configuration via environment variables**:
   - `COSMOS_ENDPOINT` — account endpoint URL
   - `COSMOS_KEY` — primary key (if connection string auth)
   - `COSMOS_DATABASE` — default database name
   - `COSMOS_CONNECTION_STRING` — full connection string (alternative)
3. **Client options**:
   ```
   ConnectionMode = Direct (production) / Gateway (emulator)
   ApplicationName = "{{app_name}}"
   MaxRetryAttemptsOnRateLimitedRequests = 9
   MaxRetryWaitTimeOnRateLimitedRequests = 30s
   CosmosClientTelemetryOptions.DisableDistributedTracing = false
   ```
4. **Dispose on shutdown** — register disposal with application lifetime via lifespan
5. **Health check** — expose `ReadAccountAsync()` as health probe

### Output

1. Configuration class named `CosmosSettings` using pydantic `BaseSettings` (Python) or `IOptions<T>` (C#)
2. DI registration code
3. Health check implementation named `check_cosmos_health`
4. Environment variable documentation

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ `new CosmosClient()` in a constructor or method
- ❌ Transient/scoped registration
- ❌ Hardcoded connection strings
- ❌ Missing disposal on app shutdown
- ❌ No retry configuration
- ❌ Class-based singleton using `__new__` or metaclass
- ❌ Using `atexit` for disposal instead of lifespan
