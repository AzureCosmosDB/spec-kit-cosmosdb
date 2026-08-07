# /cosmos.hierarchical-pk

> Design hierarchical (sub-partitioned) partition keys for multi-tenant and high-cardinality scenarios.

## Intent

Design hierarchical partition keys (up to 3 levels) for scenarios where a single partition key leads to hot partitions or where multi-tenant data isolation and query efficiency matter.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{entities}}` | Documents/entities to partition | "orders, line items" |
| `{{access_patterns}}` | Common query patterns | "by tenant, by tenant+user, by tenant+user+date" |
| `{{tenant_model}}` | Tenancy model | "multi-tenant SaaS" or "IoT device fleet" or "single-tenant" |

## Prescriptive Prompt

Design hierarchical partition keys for {{entities}} with access patterns: {{access_patterns}} in a {{tenant_model}} model. Follow these constraints:

### When to Use Hierarchical Partition Keys

- ✅ Multi-tenant with large tenants (single tenant > 20GB)
- ✅ IoT with high-volume devices under a fleet/region hierarchy
- ✅ Queries commonly filter by multiple levels (tenant → category → id)
- ❌ NOT when single-level partition key provides even distribution
- ❌ NOT for cross-partition key queries (hierarchical doesn't help if you query without the first level)

### Design Principles

1. **Order: Broad → Narrow** (highest cardinality prefix first for distribution)
   - Level 1: Broadest grouping (e.g., `tenantId`)
   - Level 2: Mid-level grouping (e.g., `userId` or `category`)
   - Level 3: Narrowest grouping (e.g., `date` or `sessionId`)
2. **Maximum 3 levels** (Cosmos DB limit)
3. **First level determines physical partitioning** — ensures even data distribution
4. **Queries benefit from prefix matching** — providing levels 1+2 targets fewer partitions than level 1 alone

### Hierarchical PK for {{tenant_model}}

**Multi-tenant SaaS**:
```
/tenantId → /userId → /category
```
- Small tenants share physical partitions (synthetic sub-partitions)
- Large tenants get dedicated physical partitions automatically

**IoT Device Fleet**:
```
/region → /deviceId → /date
```
- Region provides broad distribution
- DeviceId prevents hot partitions within a region

### Query Implications

| Filter Provided | Partition Targeting |
|----------------|-------------------|
| Level 1 only | Targets subset of physical partitions |
| Level 1 + 2 | Narrower targeting |
| Level 1 + 2 + 3 | Single logical partition (most efficient) |
| Level 2 only (skip 1) | Cross-partition query (fan-out) |

### Implementation

1. Container definition with hierarchical partition key paths
2. Document model with all partition key levels as root properties
3. SDK usage: Build `PartitionKeyBuilder` with all levels for point operations
4. Query examples showing prefix-based partition targeting

### Output

1. Recommended hierarchy with justification
2. Container creation with hierarchical partition key definition
3. Document model showing partition key properties
4. CRUD operations using `PartitionKeyBuilder`
5. Query examples for each access pattern

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Ordering narrow → broad (low-cardinality first = hot partitions)
- ❌ Using hierarchical PK when single key suffices (unnecessary complexity)
- ❌ Skipping level 1 in queries without understanding fan-out cost
- ❌ More than 3 levels (not supported)
- ❌ Mutable partition key values (partition key is immutable after creation)
- ❌ Using hierarchical PK to avoid proper data modeling (it's not a substitute for good schema design)
