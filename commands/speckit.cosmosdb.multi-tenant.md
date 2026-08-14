---
description: "Generate multi-tenant data isolation patterns for Azure Cosmos DB."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Spec Context (optional)

If the current project has an active Spec Kit specification (e.g. `.specify/specs/<feature>/spec.md`, or a path provided in the user input), **read it first** and use it as the source of intent: entity names, fields, access patterns, scale, and consistency requirements. Prefer values from the spec over generic defaults. If no spec is present, fall back to the inputs below. **Do not modify the spec.**


# /speckit.cosmosdb.multi-tenant

> Generate multi-tenant data isolation patterns for Azure Cosmos DB.

## Intent

Design and implement a multi-tenant data architecture in Azure Cosmos DB, choosing the right isolation strategy based on tenant count, compliance requirements, and cost constraints.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{tenant_count}}` | Expected number of tenants | "50" or "10000" or "1M+" |
| `{{isolation_level}}` | Required isolation | "logical" or "container" or "account" |
| `{{language}}` | Target language | "Python" or "C#" or "TypeScript" |
| `{{data_model}}` | Tenant data structure | "{ userId, orders[], profile, preferences }" |

## Prescriptive Prompt

Generate multi-tenant isolation for {{tenant_count}} tenants with {{isolation_level}} isolation. Follow these constraints:

### Decision Tree

| Tenant Count | Isolation Need | Strategy |
|-------------|----------------|----------|
| < 50 | High (compliance/regulatory) | Container-per-tenant |
| < 50 | Medium | Shared container, tenant PK |
| 50–10,000 | Any | Shared container, tenant as PK prefix |
| 10,000+ | Logical only | Shared container, hierarchical PK with tenant at L1 |
| Any | Account-level (rare) | Separate Cosmos accounts |

### Strategy: Shared Container with Tenant Partition Key

**When**: {{tenant_count}} > 50 OR cost-sensitive

1. **Partition key**: `/tenantId` (simple) or hierarchical `/tenantId/entityType` (if mixed entities)
2. **Document schema**: ALL documents MUST include `tenantId` at root level
3. **Query isolation**: EVERY query MUST include `WHERE c.tenantId = @tenantId`
4. **Throughput**: Shared autoscale; monitor per-tenant consumption via diagnostics
5. **Cross-tenant protection**: Application layer enforces tenant scope - never rely on Cosmos alone

### Strategy: Container-per-Tenant

**When**: {{tenant_count}} < 50 AND high isolation required

1. **Naming**: Container per tenant: `data-{tenantId}`
2. **Provisioning**: Automate container creation on tenant onboarding
3. **Throughput**: Per-container autoscale (400–4000 RU/s typical)
4. **Routing**: Tenant → container mapping via config or lookup table
5. **Cleanup**: Delete container on tenant offboarding (immediate, no residual data)

### Strategy: Hierarchical Partition Key

**When**: {{tenant_count}} > 10,000 AND mixed entity types per tenant

1. **PK definition**: `["/tenantId", "/entityType", "/entityId"]`
2. **Benefit**: Sub-partitioning prevents hot partitions for large tenants
3. **Query scope**: Target specific tenant + entity type for minimal fan-out

### Cross-Cutting Concerns

1. **Tenant context**: Inject tenant ID from auth token - NEVER from request body
2. **Row-level security**: Middleware validates every DB response belongs to requesting tenant
3. **Noisy neighbor**: Monitor RU consumption per tenant; implement per-tenant rate limiting
4. **Backup/restore**: Per-tenant point-in-time restore requires container-per-tenant; shared = all-or-nothing
5. **Data residency**: If tenants span regions, use multi-region writes with preferred region per tenant

### Output

1. Container/database design based on decision tree outcome
2. Tenant-aware repository/data access layer
3. Tenant context injection from auth
4. Per-tenant query scoping (middleware or base repository)
5. Tenant onboarding/offboarding automation
6. Noisy neighbor detection pattern

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="speckit-cosmosdb/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "speckit-cosmosdb/0.1.0"`. For Java, use `.userAgentSuffix("speckit-cosmosdb/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Trusting client-supplied tenant ID (must come from auth token)
- ❌ Queries without tenant filter (data leak risk)
- ❌ Container-per-tenant for 10,000+ tenants (management nightmare)
- ❌ No noisy-neighbor monitoring (one tenant can starve others)
- ❌ Storing tenant ID only in metadata (must be in partition key path)
- ❌ Using database-per-tenant in serverless tier (25 container limit)
