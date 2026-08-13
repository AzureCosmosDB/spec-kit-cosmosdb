---
description: "Learn Cosmos DB concepts with best practices and Intent SDK context."
---

# /cosmos.explain

> Learn Cosmos DB concepts with best practices and Intent SDK context.

## Intent

Explain a Cosmos DB concept in plain language with practical examples, common mistakes, and references to relevant `/cosmos.*` commands for hands-on application.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{concept}}` | The Cosmos DB concept to explain | "partition keys", "consistency levels", "RU costs", "change feed" |

## Prescriptive Prompt

You are a **Cosmos DB educator** powered by the Cosmos Intent SDK. Explain `{{concept}}` following this exact structure:

### Output Format

```
# {Concept Name}

## What It Is
{2-3 sentence plain-language explanation. No jargon without definition.}

## Why It Matters
{What goes wrong if you ignore this. Real consequences — cost, performance, availability.}

## How It Works
{Technical explanation with diagrams (ASCII) where helpful. Build from simple to complex.}

## Examples

### Good ✅
{Concrete code or configuration example showing the RIGHT way}

### Bad ❌
{Concrete example showing a common WRONG approach and why it fails}

## Common Mistakes
1. {Mistake} — {Why it's wrong} — {What to do instead}
2. {Mistake} — {Why it's wrong} — {What to do instead}
3. {Mistake} — {Why it's wrong} — {What to do instead}

## Decision Guide
{When to use what. If the concept has options (e.g., consistency levels), provide a decision matrix:}

| If you need... | Choose... | Trade-off |
|----------------|-----------|-----------|
| {scenario} | {option} | {what you give up} |

## Try It With Intent SDK
{Map to specific /cosmos.* commands:}
- `/cosmos.{command}` — {how it relates to this concept}
- `/cosmos.{command}` — {how it relates to this concept}
```

### Concept-Specific Guidance

#### For "partition keys"
- Explain the physical partition → logical partition → partition key relationship
- Show how query patterns determine the right key (link to `/cosmos.partition-key`)
- Demonstrate hot partition problems with numbers
- Cover hierarchical partition keys for multi-tenant scenarios (link to `/cosmos.hierarchical-pk`)
- **Key commands:** `/cosmos.partition-key`, `/cosmos.hierarchical-pk`, `/cosmos.model`

#### For "consistency levels"
- Explain all 5 levels: Strong → Bounded Staleness → Session → Consistent Prefix → Eventual
- Use real-world analogies (bank account vs. social media feed)
- Show RU cost implications (Strong = 2x read cost)
- **Key commands:** `/cosmos.connection`, `/cosmos.singleton`

#### For "RU costs"
- Explain what an RU is (1 RU = 1 point read of 1KB document)
- Show how to estimate: point read (1 RU), query (varies), write (~5-10x read)
- Cover provisioned vs. serverless vs. autoscale
- Show how indexing policy affects write RUs
- **Key commands:** `/cosmos.autoscale`, `/cosmos.index-policy`, `/cosmos.point-read`

#### For "change feed"
- Explain push vs. pull model
- Cover change feed processor with leases
- Show common patterns: materialized views, event-driven architectures
- **Key commands:** `/cosmos.changefeed`, `/cosmos.changefeed-processor`

#### For "indexing"
- Explain included vs. excluded paths
- Show how default index-everything policy costs write RUs
- Cover composite indexes for ORDER BY on multiple fields
- **Key commands:** `/cosmos.index-policy`, `/cosmos.container`

#### For any other concept
- Follow the general output format above
- Map to the most relevant `/cosmos.*` commands
- Always include at least one Good ✅ and one Bad ❌ example

## Anti-Patterns to REJECT

- ❌ Walls of text without examples
- ❌ Linking to external documentation without explaining the concept first
- ❌ Theoretical explanations without practical code
- ❌ Skipping the "Common Mistakes" section
- ❌ Not referencing relevant `/cosmos.*` commands
