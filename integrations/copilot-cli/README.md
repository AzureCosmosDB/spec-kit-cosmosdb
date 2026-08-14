# GitHub Copilot CLI Integration

## Overview

Use speckit-cosmosdb with `gh copilot suggest` and `gh copilot explain` to get Azure Cosmos DB guidance directly in your terminal.

## Basic Usage

```bash
# Ask for container design guidance
gh copilot suggest "Design a Azure Cosmos DB container for user profiles \
  with lookups by userId and email, following speckit-cosmosdb rules: \
  choose high-cardinality partition key, embed related data, use Session consistency"

# Get query optimization
gh copilot explain "Why is this Azure Cosmos DB query using cross-partition fan-out: \
  SELECT * FROM c WHERE c.status = 'active' ORDER BY c.createdAt DESC"
```

## Shell Wrapper

Create a shell function that injects speckit-cosmosdb context:

```bash
# ~/.bashrc or ~/.zshrc
cosmos-design() {
  local context="You are a Azure Cosmos DB architect. Follow these rules:
- Choose partition keys with high cardinality present in most query WHERE clauses
- Prefer denormalization; embed child entities accessed with parent
- Use change feed for cross-container materialized views
- Default to Session consistency
- Include composite indexes for multi-field ORDER BY
- Estimate RU cost for primary operations

Design a Azure Cosmos DB container for: $*"

  gh copilot suggest "$context"
}

cosmos-query() {
  local context="You are a Azure Cosmos DB query expert. Follow these rules:
- Avoid cross-partition queries; filter on partition key
- Use projections to reduce RU cost
- Prefer point reads (ReadItem) over queries when possible
- Use continuation tokens for pagination, not OFFSET/LIMIT

Write an optimized query for: $*"

  gh copilot suggest "$context"
}
```

Usage:
```bash
cosmos-design "multi-tenant SaaS with per-tenant analytics and shared product catalog"
cosmos-query "get the 10 most recent orders for a customer"
```

## With Prompt Template Files

```bash
# Render a template and pipe to Copilot
render-cosmos-prompt() {
  local template="$1"
  shift
  # Assuming a simple envsubst-based renderer
  cat "$template" | envsubst | gh copilot suggest "$(cat -)"
}
```

## Limitations

- `gh copilot suggest` has input length limits; keep prompts concise
- No streaming or multi-turn; each invocation is stateless
- For complex design sessions, prefer the VS Code integration
- CLI output is optimized for shell commands; architectural advice may be truncated
