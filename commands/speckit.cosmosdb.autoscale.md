---
description: "Configure autoscale throughput for variable workloads."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.autoscale

> Configure autoscale throughput for variable workloads.

## Intent

Set up autoscale provisioned throughput on Cosmos DB containers, choosing between autoscale and manual provisioning, calculating max RU/s, and optimizing cost.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{workload_pattern}}` | Traffic shape | "spiky" or "predictable" or "diurnal" or "event-driven" |
| `{{peak_rps}}` | Peak requests per second | "500" |
| `{{avg_rps}}` | Average requests per second | "50" |
| `{{item_size_kb}}` | Average item size in KB | "2" |

## Prescriptive Prompt

Generate autoscale configuration for a {{workload_pattern}} workload with {{peak_rps}} peak RPS, {{avg_rps}} average RPS, and {{item_size_kb}}KB items. Follow these constraints:

### When to Use Autoscale vs Manual

| Criteria | Autoscale | Manual |
|----------|-----------|--------|
| Peak/Avg ratio > 3x | ✅ | ❌ |
| Predictable flat traffic | ❌ | ✅ |
| New workload (unknown pattern) | ✅ | ❌ |
| Cost-sensitive + steady load | ❌ | ✅ |
| Spiky or event-driven | ✅ | ❌ |

**Rule**: If `{{peak_rps}} / {{avg_rps}} > 3`, use autoscale. Otherwise, manual may be cheaper.

### RU/s Calculation

1. **Estimate RU per operation**:
   - Point read (1KB): 1 RU
   - Point read ({{item_size_kb}}KB): ~{{item_size_kb}} RU
   - Write (1KB): 5.33 RU
   - Write ({{item_size_kb}}KB): ~5.33 × {{item_size_kb}} RU
   - Query (varies): 3-50+ RU depending on complexity and result set
2. **Peak RU/s** = {{peak_rps}} × estimated_RU_per_op
3. **Max autoscale RU/s** = Peak RU/s rounded up to nearest 1000 (minimum 1000)

### Autoscale Behavior

1. **Range**: Scales between 10% of max and max (e.g., max=10000 → range is 1000-10000)
2. **Billing**: Billed per hour at highest RU/s reached in that hour
3. **Scale-up**: Instant (within partition)
4. **Scale-down**: Gradual (drops to 10% of max if no traffic)
5. **Minimum**: 1000 RU/s max (scales 100-1000)

### Cost Optimization

1. **Autoscale premium**: ~50% more expensive per RU than manual at full utilization
2. **Break-even**: If utilization is consistently > 66% of max, manual is cheaper
3. **Strategy**: Start with autoscale, analyze metrics after 7 days, switch to manual if steady
4. **Shared throughput**: Use database-level autoscale for multiple low-traffic containers

### Output

1. Autoscale vs manual recommendation with justification
2. Calculated max RU/s value
3. Container creation configuration with throughput settings
4. Cost estimate (monthly) for both autoscale and manual options
5. Monitoring alerts: set alert at 70% of max RU/s to detect if max needs increase

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="speckit-cosmosdb/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "speckit-cosmosdb/0.1.0"`. For Java, use `.userAgentSuffix("speckit-cosmosdb/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ Setting max RU/s too low (causes 429s at peak)
- ❌ Using manual throughput for unpredictable workloads (under-provision → 429s, over-provision → waste)
- ❌ Not monitoring `NormalizedRUConsumption` (won't know if you're hitting the ceiling)
- ❌ Autoscale on steady-state workloads with > 66% utilization (paying autoscale premium unnecessarily)
- ❌ Forgetting minimum is 10% of max (you pay at least 10% even at zero traffic)
