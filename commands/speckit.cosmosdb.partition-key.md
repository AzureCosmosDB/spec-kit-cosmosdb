---
description: "Recommend an optimal partition key for a container based on access patterns."
---

<!-- User arguments: $ARGUMENTS -->

# /speckit.cosmosdb.partition-key

> Recommend an optimal partition key for a container based on access patterns.

## Intent

Analyze entity structure and access patterns to recommend the best partition key strategy.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{entity}}` | Entity and its fields | "Order: id, customerId, status, region, createdAt" |
| `{{access_patterns}}` | Ranked query patterns | "1. Get orders by customerId 2. Get order by id 3. Filter by status+region" |
| `{{write_pattern}}` | How data is written | "Orders created uniformly across customers" |
| `{{cardinality_info}}` | Cardinality estimates | "10K customers, 5 statuses, 20 regions, 1M orders" |

## Prescriptive Prompt

Recommend a partition key. Follow this decision framework:

### Selection Criteria (in priority order)

1. **Most frequent equality filter** in queries → candidate
2. **High cardinality** (> 1000 distinct values) → validates candidate
3. **Even write distribution** → confirms candidate
4. **Not too hot** (no single value > 20GB logical partition) → confirms candidate

### Analysis Format

For each candidate field, evaluate:

| Field | Query Alignment | Cardinality | Write Distribution | Max Partition Size | Verdict |
|-------|----------------|-------------|-------------------|-------------------|---------|

### Decision Output

```
RECOMMENDED: /{{field}}
REASONING: [1-2 sentences connecting to access patterns]
RISK: [any known risks, e.g., "large customers may approach 20GB limit"]
MITIGATION: [hierarchical partition key or TTL strategy if needed]
```

### Hierarchical Partition Key

If no single field satisfies all criteria, recommend hierarchical:
```
Partition key: /region, /customerId, /orderId
```
- Level 1: coarse grouping (even distribution)
- Level 2: query filter alignment
- Level 3: uniqueness within partition

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ `/id` as partition key (random distribution but zero query alignment)
- ❌ Low-cardinality fields (status, boolean, enum < 10 values)
- ❌ Timestamp as sole partition key (hot partition on current time)
- ❌ Choosing based only on write distribution (ignoring read patterns)
