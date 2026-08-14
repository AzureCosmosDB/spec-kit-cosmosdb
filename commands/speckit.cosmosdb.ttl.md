---
description: "Configure Time-to-Live policies for automatic data expiration."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.ttl

> Configure Time-to-Live policies for automatic data expiration.

## Intent

Set up TTL policies on Azure Cosmos DB containers and items for automatic cleanup of session data, caches, audit logs, and other time-bounded data.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{use_case}}` | What data expires | "session tokens" or "cache entries" or "audit logs" |
| `{{language}}` | Target language | "TypeScript" or "C#" or "Python" |
| `{{retention_period}}` | How long to keep items | "24 hours" or "90 days" or "varies per item" |

## Prescriptive Prompt

Generate TTL configuration for {{use_case}} with {{retention_period}} retention. Follow these constraints:

### Container-Level TTL

1. **Enable TTL on container**: Set `DefaultTimeToLive` to enable the feature
   - `-1` = TTL enabled but no default expiration (per-item only)
   - `N` (seconds) = default expiration for all items without explicit `ttl`
2. **Choose strategy**:
   - Uniform retention → set container default to `{{retention_period}}` in seconds
   - Per-item retention → set container default to `-1`, set `ttl` on each item

### Per-Item TTL

1. **Property name**: Must be `ttl` (lowercase, root-level property)
2. **Value**: Seconds until expiration from last modified time (`_ts`)
3. **Override**: Item `ttl` overrides container default
4. **Never expire**: Set item `ttl` to `-1` to exempt from container default

### Common Patterns

| Use Case | Container Default | Item TTL |
|----------|------------------|----------|
| Session data | 3600 (1 hour) | Override for "remember me" sessions |
| Cache | 300 (5 min) | Vary by cache key type |
| Audit logs | 7776000 (90 days) | `-1` for compliance-flagged entries |
| Event sourcing | -1 | Set per event type |
| Temp uploads | 86400 (24 hours) | - |

### Implementation

1. Container creation/update with TTL enabled
2. Model class with `ttl` property (integer, seconds)
3. Helper to calculate TTL from desired expiry time: `ttl = (expiryTime - now).TotalSeconds`
4. For {{use_case}}: apply the pattern above with {{retention_period}}

### Monitoring

1. TTL deletions do NOT consume RU/s (free background cleanup)
2. TTL deletions do NOT appear in change feed (they are silent)
3. Monitor with `CosmosDB.TotalDocuments` metric to see count decreasing
4. Expired items may linger briefly - TTL is best-effort, not instant

### Output

1. Container configuration with TTL enabled
2. Model/document class with `ttl` property
3. Helper function to set TTL based on expiry requirements
4. Example usage for {{use_case}}

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="speckit-cosmosdb/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "speckit-cosmosdb/0.1.0"`. For Java, use `.userAgentSuffix("speckit-cosmosdb/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Relying on TTL for instant deletion (it's eventual, not immediate)
- ❌ Using TTL as a security boundary (item may be readable briefly after expiry)
- ❌ Forgetting to enable TTL at container level (item `ttl` is ignored without it)
- ❌ Storing TTL as a string or nested property (must be root-level integer `ttl`)
- ❌ Using change feed to detect TTL deletions (they don't appear)
- ❌ Manual cleanup jobs when TTL would suffice (wasted RU/s)
