---
description: "Generate a complete Azure Cosmos DB application with deterministic, production-ready architecture."
---

<!-- User arguments: $ARGUMENTS -->

# /speckit.cosmosdb.scaffold

> Generate a complete Azure Cosmos DB application with deterministic, production-ready architecture.

## Intent

Scaffold a full application that uses Azure Cosmos DB as its primary data store. The output must be structurally identical across runs given the same inputs — partition keys, file structure, API paths, and SDK usage are all locked down by this prompt.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{app_description}}` | What the application does | "A task management API" |
| `{{language}}` | Target language/framework | "python", "dotnet", "java", "node" |
| `{{entities}}` | Core domain entities | "Users, Tasks, Projects" |
| `{{primary_queries}}` | **The 3-5 most frequent read queries** | "Get all tasks for a user; Get user by ID; List tasks by status for a user" |
| `{{scale}}` | Expected throughput | "100 RPS" or "10K RPS" |
| `{{auth_model}}` | Authentication approach | "Azure AD" or "Connection string" |

## Critical: Partition Key Determination

**You MUST determine partition keys from `{{primary_queries}}` BEFORE generating any code.**

Process:
1. Identify the WHERE clause filter used in >70% of queries for each container
2. That filter field becomes the partition key
3. If no single field dominates, use a hierarchical partition key
4. **NEVER use `/id` as partition key** unless the only access pattern is point-reads by ID

Output a justification comment at the top of every data model file:

```
# PARTITION KEY: /user_id
# JUSTIFICATION: 4 of 5 primary queries filter by user_id (get tasks for user,
# get user tasks by status, get user task by id, update user task).
# Cross-partition required for: admin list-all (opt-in, paginated).
```

## API Convention (MANDATORY — no deviation)

All endpoints MUST follow this exact pattern:

```
GET    /api/{resource}           → 200 + array
POST   /api/{resource}           → 201 + created object + Location header
GET    /api/{resource}/{id}      → 200 + object | 404
PATCH  /api/{resource}/{id}      → 200 + updated object | 404
DELETE /api/{resource}/{id}      → 204 | 404
GET    /api/health               → 200 + {"status": "healthy"}
```

Rules:
- Resource names are **plural** (e.g., `/api/users`, `/api/tasks`)
- Nested resources: `/api/{parent}/{parentId}/{child}` (e.g., `/api/users/{userId}/tasks`)
- All request/response bodies use **camelCase** field names in JSON
- No API versioning in URL (use headers if needed later)
- Standard status codes: 201 create, 200 read/update, 204 delete, 404 not found, 409 conflict (etag mismatch), 429 throttled

## Architecture Requirements

1. **Layering**: Handlers/Routes → Services → Repository → Cosmos SDK (no skipping layers)
2. **CosmosClient**: Single instance, registered as singleton. NEVER create per-request.
3. **Configuration**: Environment variables with typed config. Support both emulator (`COSMOS_ENDPOINT=https://localhost:8081`) and production.
4. **Error handling**: Map Cosmos status codes to HTTP status codes (404→404, 409→409, 429→429 with Retry-After)
5. **Health check**: Verify Cosmos connectivity at `/api/health`

## Data Modeling Constraints

For each entity in `{{entities}}`:
- Include partition key justification comment (see above)
- Include `id` field (string, auto-generated UUID)
- Include `type` discriminator field if container holds multiple entity types
- Include `createdAt` and `updatedAt` timestamps (ISO 8601)
- Partition key field MUST have a default value or be set via factory/classmethod — never require it at construction if it's derived from `id`

## Connection & Resilience

- Retry configuration: max 9 attempts, 30s max wait on 429s
- Connection mode: Direct for production, Gateway for emulator
- ⚠️ Linux emulator (vnext) uses HTTP not HTTPS — set `connection_verify=False` or `disable_ssl_verification=True` for local dev
- Client shutdown/cleanup on app termination
- Application name set in client options

## User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

## Anti-Patterns (REJECT — never generate these)

- ❌ Hardcoded connection strings or keys in source code
- ❌ Cross-partition queries without explicit `# CROSS-PARTITION: reason` comment and `partition_key=None` (async) or `enable_cross_partition_query=True` (sync)
- ❌ Deprecated SDK methods (see language appendix)
- ❌ Creating CosmosClient per-request or in a constructor that runs per-request
- ❌ Using `/id` as partition key without justification
- ❌ f-string interpolation in Cosmos SQL queries (use parameters)
- ❌ Loading unbounded result sets without pagination (max 100 items default)
- ❌ Missing client.close() / dispose on shutdown

## Scale Considerations for `{{scale}}`

- If < 1000 RPS: Single database, autoscale throughput, shared throughput containers
- If 1000-10000 RPS: Dedicated throughput per hot container, consider hierarchical partition keys
- If > 10000 RPS: Multi-region writes, dedicated throughput, partition key analysis required

---

## iteration-config.yaml (ALWAYS generate this file)

```yaml
# iteration-config.yaml — controls iterative refinement of this scaffold
version: 1
scaffold:
  prompt: speckit.cosmosdb.scaffold
  language: "{{language}}"
  generated_at: "{{ISO_8601_TIMESTAMP}}"

validation:
  - name: app-starts
    command: "{{start_command}}"
    expect: "listening on"
    timeout: 15s
  - name: health-check
    command: "curl -sf http://localhost:8000/api/health"
    expect: '{"status":"healthy"}'
  - name: crud-cycle
    script: tests/smoke.sh

iteration:
  max_rounds: 3
  on_failure: fix-and-retry
  on_success: commit
```

---

## Language Appendix: Python

**MUST use when `{{language}}` = python**

### Versions & Dependencies (requirements.txt)
```
azure-cosmos>=4.9.0
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
```

### File Structure (MANDATORY — generate ALL files)
```
{{app_name}}/
├── main.py              # FastAPI app, lifespan, router includes
├── config.py            # Settings class (pydantic-settings BaseSettings)
├── models.py            # Pydantic v2 models with model_config
├── repository.py        # CosmosDB data access (one class per container)
├── service.py           # Business logic
├── requirements.txt     # Pinned dependencies
├── .env.example         # Template with COSMOS_ENDPOINT, COSMOS_KEY, COSMOS_DATABASE
├── iteration-config.yaml
└── README.md
```

### SDK Method Reference (use ONLY these)
```python
# Client creation
from azure.cosmos.aio import CosmosClient
client = CosmosClient(endpoint, credential=key)

# Health check (CORRECT)
await client.get_database_account()

# Database/container access
database = client.get_database_client(db_name)
container = database.get_container_client(container_name)

# CRUD operations
await container.create_item(body=item)
await container.read_item(item=item_id, partition_key=pk_value)
await container.replace_item(item=item_id, body=updated_item)
await container.delete_item(item=item_id, partition_key=pk_value)

# Query (ALWAYS use parameters, never f-strings)
query = "SELECT * FROM c WHERE c.userId = @userId"
parameters = [{"name": "@userId", "value": user_id}]
items = container.query_items(query=query, parameters=parameters, partition_key=pk_value)
results = [item async for item in items]

# Cleanup
await client.close()
```

### Pydantic v2 Patterns
```python
from pydantic import BaseModel, Field
from uuid import uuid4

class CosmosDocument(BaseModel):
    model_config = {"populate_by_name": True}

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str = ""
    created_at: str = Field(default="", alias="createdAt")
    updated_at: str = Field(default="", alias="updatedAt")

class User(CosmosDocument):
    # PARTITION KEY: /id
    # JUSTIFICATION: Users are always accessed by their own ID
    type: str = "user"
    user_name: str = Field(alias="userName")
    email: str
```

### FastAPI Lifespan Pattern
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create cosmos client
    app.state.cosmos_client = CosmosClient(settings.cosmos_endpoint, credential=settings.cosmos_key)
    app.state.database = app.state.cosmos_client.get_database_client(settings.cosmos_database)
    yield
    # Shutdown: close client
    await app.state.cosmos_client.close()

app = FastAPI(lifespan=lifespan)
```

### NEVER use these (deprecated/wrong in Python SDK)
- ❌ `client.read_account()` — does not exist; use `client.get_database_account()`
- ❌ `connection_retry_policy` parameter — not a valid CosmosClient param
- ❌ `ConnectionMode.Direct` — Python async client only supports Gateway mode
- ❌ `client.ReadAccountAsync()` — this is C#, not Python
- ❌ `offer_throughput` on serverless accounts — will throw 400

---

## Language Appendix: .NET (C#)

**MUST use when `{{language}}` = dotnet**

### Versions & Dependencies
```xml
<PackageReference Include="Microsoft.Azure.Cosmos" Version="3.39.*" />
<PackageReference Include="Microsoft.Extensions.Hosting" Version="8.*" />
```

### File Structure (MANDATORY)
```
{{app_name}}/
├── Program.cs              # Minimal API or builder pattern
├── Models/
│   └── {Entity}.cs         # Record types with [JsonPropertyName]
├── Repositories/
│   └── {Entity}Repository.cs
├── Services/
│   └── {Entity}Service.cs
├── Configuration/
│   └── CosmosSettings.cs
├── {{app_name}}.csproj
├── appsettings.json
├── appsettings.Development.json
├── iteration-config.yaml
└── README.md
```

### SDK Patterns
```csharp
// DI registration (singleton)
builder.Services.AddSingleton<CosmosClient>(sp =>
{
    var settings = sp.GetRequiredService<IOptions<CosmosSettings>>().Value;
    return new CosmosClient(settings.Endpoint, settings.Key, new CosmosClientOptions
    {
        ApplicationName = "{{app_name}}",
        ConnectionMode = ConnectionMode.Direct,
        CosmosClientTelemetryOptions = new() { DisableDistributedTracing = false }
    });
});

// Health check
await client.ReadAccountAsync();

// CRUD
await container.CreateItemAsync(item, new PartitionKey(item.PartitionKeyValue));
await container.ReadItemAsync<T>(id, new PartitionKey(pkValue));
await container.ReplaceItemAsync(item, id, new PartitionKey(pkValue));
await container.DeleteItemAsync<T>(id, new PartitionKey(pkValue));

// Query with parameters
var query = new QueryDefinition("SELECT * FROM c WHERE c.userId = @userId")
    .WithParameter("@userId", userId);
```

---

## Language Appendix: Java

**MUST use when `{{language}}` = java**

### Versions & Dependencies
```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-spring-data-cosmos</artifactId>
    <version>5.x</version>
</dependency>
<!-- Spring Boot 3.x parent -->
```

### File Structure (MANDATORY)
```
{{app_name}}/
├── src/main/java/com/example/{{app_name}}/
│   ├── Application.java
│   ├── config/CosmosConfig.java
│   ├── model/{Entity}.java          # @Container annotation
│   ├── repository/{Entity}Repository.java  # extends CosmosRepository
│   ├── service/{Entity}Service.java
│   └── controller/{Entity}Controller.java
├── src/main/resources/application.yml
├── pom.xml
├── iteration-config.yaml
└── README.md
```

### Key Annotations
```java
@Container(containerName = "users", ru = "400", autoScale = true)
public class User {
    @Id
    private String id;
    @PartitionKey
    private String userId;
}
```

---

## Language Appendix: Node.js

**MUST use when `{{language}}` = node**

### Versions & Dependencies (package.json)
```json
{
  "dependencies": {
    "@azure/cosmos": "^4.0.0",
    "express": "^4.18.0",
    "dotenv": "^16.0.0",
    "uuid": "^9.0.0"
  }
}
```

### File Structure (MANDATORY)
```
{{app_name}}/
├── src/
│   ├── index.js           # Express app setup + graceful shutdown
│   ├── config.js          # Environment variable loading
│   ├── models/            # Schema definitions/validation (joi or zod)
│   ├── repositories/      # Cosmos data access
│   ├── services/          # Business logic
│   └── routes/            # Express routers
├── package.json
├── .env.example
├── iteration-config.yaml
└── README.md
```

### SDK Patterns
```javascript
const { CosmosClient } = require("@azure/cosmos");

// Singleton client
const client = new CosmosClient({ endpoint, key, connectionPolicy: { requestTimeout: 10000 } });

// Health check
await client.getDatabaseAccount();

// CRUD
await container.items.create(item);
const { resource } = await container.item(id, partitionKey).read();
await container.item(id, partitionKey).replace(updatedItem);
await container.item(id, partitionKey).delete();

// Query (parameterized)
const { resources } = await container.items.query({
    query: "SELECT * FROM c WHERE c.userId = @userId",
    parameters: [{ name: "@userId", value: userId }]
}, { partitionKey }).fetchAll();
```

---

## Output Checklist (ALL items MUST be generated)

Before finishing, verify every item is present:
- [ ] All files from the language-specific file structure
- [ ] Partition key justification comment in models
- [ ] iteration-config.yaml
- [ ] .env.example with all required environment variables
- [ ] README.md with setup instructions, required env vars, and how to run
- [ ] Health check endpoint at `/api/health`
- [ ] Proper client lifecycle (create on startup, close on shutdown)
- [ ] Parameterized queries (no string interpolation)
- [ ] Error mapping (Cosmos errors → HTTP status codes)

Generate the complete application following ALL constraints above. Every file must be production-ready.
