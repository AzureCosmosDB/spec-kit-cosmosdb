---
description: "Generate a complete Azure Cosmos DB multi-tenant SaaS platform with deterministic, production-ready architecture."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.scaffold-saas

> Generate a complete Azure Cosmos DB multi-tenant SaaS platform with deterministic, production-ready architecture.

## Intent

Scaffold a full multi-tenant SaaS platform that uses Azure Cosmos DB as its primary data store with strict tenant isolation. The output must be structurally identical across runs given the same inputs.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{app_description}}` | What the application does | "A multi-tenant SaaS platform API" |
| `{{language}}` | Target language/framework | "python", "dotnet", "java", "node" |
| `{{entities}}` | Core domain entities (pre-set) | "Tenants, Users, Subscriptions, UsageMetrics" |
| `{{primary_queries}}` | **The 3-5 most frequent read queries** | "Get all users for a tenant; Get user by ID within tenant; Get subscription for a tenant; Get usage metrics for tenant in date range; List tenants by plan" |
| `{{scale}}` | Expected throughput | "100 RPS" or "10K RPS" |
| `{{auth_model}}` | Authentication approach | "Azure AD" or "Connection string" |

## Domain: Multi-Tenant SaaS Platform

### Entities

| Entity | Container | Description |
|--------|-----------|-------------|
| Tenant | tenants | Tenant profile, plan, settings |
| User | tenantData | Users scoped to a tenant |
| Subscription | tenantData | Billing subscription per tenant |
| UsageMetric | tenantData | Daily/hourly usage counters per tenant |

### Tenant Isolation

- **ALL tenant-scoped data lives in a single `tenantData` container** with hierarchical partition key `/tenantId/type`.
- Every query MUST include `tenantId` in the partition key path - no cross-tenant data leakage.
- Service layer MUST validate that the authenticated tenant matches the requested `tenantId`.
- `type` discriminator separates Users, Subscriptions, and UsageMetrics within the same partition.

### Subscription Lifecycle

```
trial → active → past_due → cancelled
                     ↓
                  suspended
```

- Trial auto-converts to active on first payment.
- `past_due` after failed payment → `suspended` after grace period.

### Usage Aggregation

- `UsageMetric` documents store per-tenant daily counters: `apiCalls`, `storageBytes`, `activeUsers`.
- Aggregation for billing = SUM over date range within tenant partition (single-partition query).

## Critical: Partition Key Determination

| Container | Partition Key | Justification |
|-----------|--------------|---------------|
| tenants | `/id` | Tenants accessed by own ID |
| tenantData | `/tenantId` (hierarchical: `/tenantId/type`) | ALL queries are tenant-scoped; type discriminator enables efficient within-tenant filtering |

```
# PARTITION KEY: /tenantId (hierarchical: /tenantId/type)
# JUSTIFICATION: 100% of queries on tenantData filter by tenantId first. Hierarchical
# key with /type enables efficient queries for "all users in tenant" vs "subscription for tenant".
# Cross-partition required for: admin list-all-tenants (opt-in, paginated).
```

## API Convention (MANDATORY - no deviation)

```
GET    /api/{resource}           → 200 + array
POST   /api/{resource}           → 201 + created object + Location header
GET    /api/{resource}/{id}      → 200 + object | 404
PATCH  /api/{resource}/{id}      → 200 + updated object | 404
DELETE /api/{resource}/{id}      → 204 | 404
GET    /api/health               → 200 + {"status": "healthy"}
```

### Domain-Specific Endpoints

```
GET    /api/tenants/{tenantId}/users                    → 200 + users for tenant
POST   /api/tenants/{tenantId}/users                    → 201 + created user
GET    /api/tenants/{tenantId}/subscription              → 200 + subscription
PATCH  /api/tenants/{tenantId}/subscription              → 200 + updated subscription
GET    /api/tenants/{tenantId}/usage?from=&to=           → 200 + usage metrics
POST   /api/tenants/{tenantId}/usage/record              → 201 + recorded metric
```

Rules:
- Resource names are **plural**
- All request/response bodies use **camelCase**
- Every tenant-scoped endpoint MUST validate tenant ownership in middleware/service layer
- Standard status codes: 201 create, 200 read/update, 204 delete, 403 tenant mismatch, 404 not found, 409 conflict, 429 throttled

## Architecture Requirements

1. **Layering**: Handlers/Routes → Services → Repository → Cosmos SDK
2. **CosmosClient**: Single instance, singleton.
3. **Tenant middleware**: Extract and validate tenantId from auth token. Inject into service calls.
4. **Error handling**: Map Cosmos status codes to HTTP status codes
5. **Health check**: `/api/health`

## Data Modeling Constraints

- ALL documents in `tenantData` MUST include `tenantId` and `type` fields
- `User`: `id`, `tenantId`, `type: "user"`, `email`, `role`, `createdAt`, `updatedAt`
- `Subscription`: `id`, `tenantId`, `type: "subscription"`, `plan` (trial/basic/pro/enterprise), `status`, `currentPeriodStart`, `currentPeriodEnd`, `createdAt`
- `UsageMetric`: `id`, `tenantId`, `type: "usageMetric"`, `date` (YYYY-MM-DD), `apiCalls`, `storageBytes`, `activeUsers`
- `Tenant`: `id`, `name`, `plan`, `createdAt`, `updatedAt`

## Connection & Resilience

- Retry configuration: max 9 attempts, 30s max wait on 429s
- Connection mode: Direct for production, Gateway for emulator
- ⚠️ Linux emulator (vnext) uses HTTP not HTTPS - set `connection_verify=False` or `disable_ssl_verification=True` for local dev
- Client shutdown/cleanup on app termination

## Anti-Patterns (REJECT - never generate these)

- ❌ Hardcoded connection strings or keys
- ❌ Cross-partition queries without explicit comment
- ❌ Deprecated SDK methods
- ❌ Creating CosmosClient per-request
- ❌ Queries that omit `tenantId` filter (data leakage risk)
- ❌ f-string interpolation in Cosmos SQL queries
- ❌ Loading unbounded result sets without pagination
- ❌ Missing client.close() / dispose on shutdown
- ❌ Separate containers per tenant (use partition isolation instead)
- ❌ Trusting client-supplied tenantId without auth validation

## Scale Considerations for `{{scale}}`

- If < 1000 RPS: Shared throughput, hierarchical partition key
- If 1000-10000 RPS: Dedicated throughput on tenantData, autoscale
- If > 10000 RPS: Multi-region, per-tenant throughput budgeting via control plane

---

## iteration-config.yaml (ALWAYS generate this file)

```yaml
version: 1
scaffold:
  prompt: speckit.cosmosdb.scaffold-saas
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
  - name: tenant-isolation
    script: tests/tenant-isolation.sh

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
aiohttp>=3.9.0
```

### File Structure (MANDATORY)
```
{{app_name}}/
├── main.py
├── config.py
├── models.py            # Tenant, User, Subscription, UsageMetric
├── repository.py        # TenantRepository, TenantDataRepository
├── service.py           # TenantService, UserService, SubscriptionService, UsageService
├── middleware.py         # Tenant extraction and validation middleware
├── requirements.txt
├── .env.example
├── iteration-config.yaml
└── README.md
```

### NEVER use these
- ❌ `client.read_account()` - does not exist; use `client.get_database_account()`
- ❌ `ConnectionMode.Direct`

---

## Language Appendix: .NET (C#)

**MUST use when `{{language}}` = dotnet**

### File Structure (MANDATORY)
```
{{app_name}}/
├── Program.cs
├── Models/
│   ├── Tenant.cs
│   ├── User.cs
│   ├── Subscription.cs
│   └── UsageMetric.cs
├── Repositories/
├── Services/
├── Middleware/
│   └── TenantMiddleware.cs
├── Configuration/
│   └── CosmosSettings.cs
├── {{app_name}}.csproj
├── appsettings.json
├── iteration-config.yaml
└── README.md
```

### SDK Patterns - Hierarchical Partition Key
```csharp
// Hierarchical partition key
var pk = new PartitionKeyBuilder()
    .Add(tenantId)
    .Add(type)
    .Build();
await container.ReadItemAsync<User>(id, pk);
```

---

## Language Appendix: Java

**MUST use when `{{language}}` = java**

### File Structure (MANDATORY)
```
{{app_name}}/
├── src/main/java/com/example/{{app_name}}/
│   ├── Application.java
│   ├── config/CosmosConfig.java
│   ├── model/Tenant.java
│   ├── model/User.java
│   ├── model/Subscription.java
│   ├── model/UsageMetric.java
│   ├── repository/TenantDataRepository.java
│   ├── service/TenantService.java
│   ├── filter/TenantFilter.java
│   └── controller/TenantController.java
├── src/main/resources/application.yml
├── pom.xml
├── iteration-config.yaml
└── README.md
```

---

## Language Appendix: Node.js

**MUST use when `{{language}}` = node**

### File Structure (MANDATORY)
```
{{app_name}}/
├── src/
│   ├── index.js
│   ├── config.js
│   ├── middleware/
│   │   └── tenantMiddleware.js
│   ├── models/
│   ├── repositories/
│   ├── services/
│   └── routes/
├── package.json
├── .env.example
├── iteration-config.yaml
└── README.md
```

### SDK Patterns - Hierarchical Partition Key
```javascript
// Hierarchical partition key
const pk = new PartitionKey([tenantId, type]);
const { resource } = await container.item(id, pk).read();
```

---

## Output Checklist

- [ ] All files from language-specific file structure
- [ ] Partition key justification comments
- [ ] iteration-config.yaml
- [ ] .env.example
- [ ] README.md
- [ ] Health check at `/api/health`
- [ ] Hierarchical partition key implementation
- [ ] Tenant isolation middleware
- [ ] Subscription lifecycle state machine
- [ ] Usage aggregation queries
- [ ] Proper client lifecycle
- [ ] Parameterized queries
- [ ] Error mapping

## Telemetry

- **Always** set `user_agent_suffix` (Python/Java) or `ApplicationName` (.NET) to `"speckit-cosmosdb"` on the `CosmosClient` for diagnostics and telemetry tracking.
