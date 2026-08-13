---
description: "Configure multi-region writes, conflict resolution, and preferred regions."
---

<!-- User arguments: $ARGUMENTS -->

# /speckit.cosmosdb.global-distribution

> Configure multi-region writes, conflict resolution, and preferred regions.

## Intent

Set up Cosmos DB global distribution with multi-region replication, write region selection, conflict resolution policies, and SDK preferred-region configuration.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{regions}}` | Target regions | "East US, West Europe, Southeast Asia" |
| `{{consistency_level}}` | Consistency model | "Session" or "Strong" or "BoundedStaleness" |
| `{{conflict_policy}}` | How to resolve write conflicts | "LastWriterWins" or "Custom (stored proc)" |
| `{{language}}` | Target language | "TypeScript" or "C#" or "Python" |

## Prescriptive Prompt

Generate multi-region configuration for regions: {{regions}} with {{consistency_level}} consistency and {{conflict_policy}} conflict resolution. Follow these constraints:

### Multi-Region Architecture

1. **Single-write region** (default): One write region, reads from closest replica
2. **Multi-write regions**: All regions accept writes — enables lower write latency but requires conflict resolution
3. **Choose multi-write ONLY if**: write latency SLA < 10ms AND geo-distributed writers exist

### Region Configuration

1. **Add regions** in priority order (first = primary write region for single-write)
2. **SDK preferred regions**: Configure `ApplicationPreferredRegions` in client options to match deployment region
3. **Failover priority**: Set explicit priorities; region with priority 0 is the write region
4. **Automatic failover**: Enable for production (account fails over to next priority region)

### Consistency Level: {{consistency_level}}

| Level | Trade-off | Use When |
|-------|-----------|----------|
| Strong | Highest latency, linearizable | Financial transactions (single-write only, max 2 regions) |
| Bounded Staleness | Consistent prefix + bounded lag | Near-strong with multi-region |
| Session | Read-your-own-writes | Most applications (recommended default) |
| Consistent Prefix | Order guaranteed, may be stale | Event logs, activity feeds |
| Eventual | Lowest latency, may reorder | Counters, non-critical reads |

**Strong consistency is NOT available with multi-write regions.**

### Conflict Resolution: {{conflict_policy}}

**Last Writer Wins (LWW)**:
- Default policy; uses `_ts` (timestamp) as conflict resolution path
- Can use custom numeric path (e.g., `/version`, `/priority`)
- Higher value wins; loser is written to conflict feed

**Custom (Stored Procedure)**:
- Register a merge stored procedure on the container
- Procedure receives conflicting documents and decides outcome
- Use for: merge strategies, domain-specific rules, union semantics

### Implementation

1. Account-level: Enable multi-region, set consistency
2. Container-level: Set conflict resolution policy
3. SDK client: Configure preferred regions and connection mode
4. Failover testing: Manual failover script for DR drills

### Output

1. Infrastructure configuration (Bicep/Terraform/ARM for regions + consistency)
2. Container conflict resolution policy
3. SDK client options in {{language}} with preferred regions
4. Manual failover trigger script

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Strong consistency with multi-write (not supported)
- ❌ Not setting `ApplicationPreferredRegions` (SDK defaults to account write region for reads)
- ❌ Ignoring conflict feed (lost writes in LWW go undetected)
- ❌ More than 2 regions with Strong consistency (not supported)
- ❌ Not testing failover before production
- ❌ Using Gateway mode for multi-region (Direct mode is required for proper region routing)
