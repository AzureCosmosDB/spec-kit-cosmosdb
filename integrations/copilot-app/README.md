# GitHub Copilot Coding Agent Integration

## Overview

Use speckit-cosmosdb with the GitHub Copilot coding agent (`@copilot` in issues/PRs) for issue-driven Cosmos DB design and implementation.

## How It Works

1. Open a GitHub issue describing the Cosmos DB work needed
2. Assign or mention `@copilot` 
3. Copilot reads `.github/copilot-instructions.md` for speckit-cosmosdb context
4. Copilot creates a PR with container designs, SDK code, and infrastructure

## Setup

### 1. Add Copilot Instructions

`.github/copilot-instructions.md`:
```markdown
## Cosmos DB Development

When implementing Cosmos DB containers or data access code:

1. Read `speckit-cosmosdb/prompts/` for design templates
2. Follow rules in `speckit-cosmosdb/rules/` - especially:
   - partition-*: High cardinality keys, avoid hot partitions
   - model-*: Embed related data, denormalize for reads
   - sdk-*: Use bulk for >10 items, transactional batch for ACID
   - query-*: Always filter on partition key, project only needed fields
3. Generate both the container schema (JSON) and the C#/TypeScript SDK code
4. Include indexing policy in ARM/Bicep template
5. Add estimated RU costs as code comments
```

### 2. Create Issue Templates

`.github/ISSUE_TEMPLATE/cosmos-container.md`:
```markdown
---
name: Cosmos DB Container Design
about: Request a new container design from Copilot
labels: cosmos-db, copilot
assignees: copilot
---

## Entity Description
<!-- What data does this container store? -->

## Access Patterns
<!-- How will the data be queried? List operations. -->
- 

## Constraints
- Expected volume: <!-- e.g., 1M documents, 10K writes/sec -->
- Consistency requirement: <!-- Session / Strong / Eventual -->
- Multi-region: <!-- yes/no, which regions -->

## Expected Output
- [ ] Container schema (JSON)
- [ ] Partition key recommendation with justification
- [ ] Indexing policy
- [ ] SDK code (C# or TypeScript)
- [ ] Bicep/ARM deployment template
- [ ] RU cost estimates
```

### 3. Example Issue

> **Title:** Design container for order management
>
> **Entity:** E-commerce orders with line items, shipping address, payment status  
> **Access Patterns:**
> - Get order by orderId (point read)
> - List orders by customerId sorted by date
> - Get orders by status for fulfillment dashboard
>
> **Constraints:** 500K orders/month, Session consistency, single region
>
> @copilot please implement this following our speckit-cosmosdb templates

### 4. What Copilot Produces

Copilot will create a PR with:
```
src/
├── cosmos/
│   ├── containers/orders.json        # Container definition
│   ├── models/Order.cs               # Data model
│   ├── repositories/OrderRepository.cs  # SDK access code
│   └── indexing/orders-policy.json   # Indexing policy
├── infra/
│   └── cosmos-orders.bicep           # Deployment template
└── docs/
    └── orders-design-decision.md     # Partition key justification
```

## Tips

- Reference specific rules in issues: "Follow `partition-003` for multi-tenant key selection"
- Use labels to route different template types: `cosmos-design`, `cosmos-query`, `cosmos-migrate`
- Copilot respects `.github/copilot-instructions.md` automatically - no special invocation needed
- For complex multi-container designs, break into separate issues and link them
