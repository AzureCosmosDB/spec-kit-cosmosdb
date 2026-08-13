---
description: "Generate connection configuration for emulator and production environments."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.connection

> Generate connection configuration for emulator and production environments.

## Intent

Create a configuration module that supports both the Cosmos DB emulator (local dev) and production Azure endpoint.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{language}}` | Target language | "TypeScript" or "C#" |
| `{{environments}}` | Environments needed | "local, dev, staging, production" |

## Prescriptive Prompt

Generate connection config. Follow these constraints:

### Environment Detection

```
if (environment === "local"):
  endpoint = "https://localhost:8081"
  key = well-known emulator key
  connectionMode = Gateway
  disableSSLVerification = true

if (environment === "production"):
  endpoint = from environment variable
  auth = DefaultAzureCredential (preferred) or key
  connectionMode = Direct
  disableSSLVerification = false
```

### Well-Known Emulator Values

```
Endpoint: https://localhost:8081
Key: C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==
Connection String: AccountEndpoint=https://localhost:8081/;AccountKey=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==
```

### Output

1. Configuration interface/class
2. Environment-based factory function
3. Example `.env` file for each environment
4. Docker compose snippet for emulator

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Hardcoded production credentials
- ❌ Same connection mode for emulator and production
- ❌ No emulator support (blocks local development)
- ❌ Connection string in source code
