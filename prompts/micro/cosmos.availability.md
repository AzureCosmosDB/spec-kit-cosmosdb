# /cosmos.availability

> Configure availability strategy and circuit breaker for resilient Cosmos DB access.

## Intent

Set up SDK-level availability configuration including preferred regions, failover behavior, circuit breaker patterns, and health checks for high-availability applications.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{language}}` | Target language | "TypeScript" or "C#" or "Python" or "Java" |
| `{{regions}}` | Available regions | "East US, West US" |
| `{{failover_policy}}` | Failover behavior | "automatic" or "manual" or "read-only fallback" |

## Prescriptive Prompt

Generate availability configuration for {{language}} with regions {{regions}} and {{failover_policy}} failover. Follow these constraints:

### SDK Availability Features

1. **Preferred regions list**: SDK routes requests to first available region
2. **Cross-region retry**: On region failure, SDK retries in next preferred region
3. **Partition-level circuit breaker** (v3.35+ .NET): Isolates unhealthy partitions
4. **Exclude regions**: Dynamically exclude a region without restarting

### Configuration

1. Set `ApplicationPreferredRegions` in order of proximity to deployment
2. Enable `AvailabilityStrategy` for read operations (parallel hedged requests)
3. Configure `CosmosClientOptions.LimitToEndpoint = false` (allow multi-region routing)
4. Set `ConnectionMode.Direct` for proper region-aware routing

### Circuit Breaker Pattern

1. **Track consecutive failures** per region per partition
2. **Open circuit** after N failures (e.g., 5 consecutive 503/408/449)
3. **Half-open**: After cooldown (30s), send one probe request
4. **Close circuit**: On probe success, resume normal traffic
5. **SDK built-in** (.NET SDK 3.35+): Enable `CosmosClientOptions.EnablePartitionLevelCircuitBreaker`

### Failover Policy: {{failover_policy}}

**Automatic**: SDK handles region failover transparently; client sees increased latency but no errors
**Manual**: Application decides when to switch regions based on custom health checks
**Read-only fallback**: On write region failure, continue reads from replica; queue writes for retry

### Output

1. SDK client configuration with availability settings
2. Circuit breaker setup (SDK-native or custom)
3. Health check endpoint that validates Cosmos DB connectivity
4. Failover testing helper (simulate region outage)

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Single-region configuration in production (no failover possible)
- ❌ Not setting preferred regions (SDK defaults may route to distant region)
- ❌ Aggressive circuit breaker thresholds (opening on transient blips)
- ❌ No health check endpoint (can't monitor availability externally)
- ❌ Retrying on all errors without distinguishing transient vs permanent
