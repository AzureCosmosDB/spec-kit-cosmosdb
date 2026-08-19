# GitHub Copilot Coding Agent Integration

Use the Azure Cosmos DB Spec Kit extension with the GitHub Copilot coding agent
(`@copilot` in issues/PRs) for issue-driven Azure Cosmos DB work.

## How it works

The coding agent runs autonomously from an issue, so it does not interactively invoke
slash commands. The reliable way to reach it is the always-on file it loads at session
start: `.github/copilot-instructions.md`. Add your Azure Cosmos DB best-practice rules
there and the agent applies them across the whole task.

> **Why not the extension's commands directly?** The extension delivers guidance through
> Spec Kit **commands and hooks**, which are invoked on demand. An autonomous coding agent
> typically writes code without invoking them, so for `@copilot` the durable channel is
> always-on instructions.

## Setup

1. (Optional, for local Spec Kit workflows) initialize Spec Kit and add the extension so
   the `/speckit.cosmosdb.*` commands and hooks are available when you drive it
   interactively:

   ```bash
   specify init --integration copilot
   specify extension add cosmosdb --from https://github.com/AzureCosmosDB/spec-kit-cosmosdb/archive/refs/tags/v0.1.0.zip
   ```

2. Add Azure Cosmos DB rules to `.github/copilot-instructions.md` so the coding agent
   applies them automatically. A compact, validated starter rule block is maintained in
   this repository at
   [`.github/copilot-instructions.md`](../../.github/copilot-instructions.md) — copy the
   Azure Cosmos DB rules into your own project's file. Example:

   ```markdown
   ## Azure Cosmos DB

   - Choose a high-cardinality partition key present in most query filters.
   - Use point reads (id + partition key) when possible; return null/None on 404.
   - Parameterize queries, keep them partition-scoped, and project specific fields — never SELECT *.
   - Handle 429 (TooManyRequests) with exponential backoff; use ETag optimistic concurrency.
   - Match the indexing policy to the query patterns; don't ship default indexing to production.
   ```

## Example issue

> **Title:** Design container for order management
>
> **Entity:** E-commerce orders with line items, shipping address, payment status
> **Access patterns:**
> - Get order by orderId (point read)
> - List orders by customerId sorted by date
> - Get orders by status for the fulfillment dashboard
>
> **Constraints:** 500K orders/month, Session consistency, single region
>
> @copilot please implement this following the Azure Cosmos DB rules in our copilot-instructions.

## Tips

- Copilot respects `.github/copilot-instructions.md` automatically — no special invocation
  needed.
- For a larger passive ruleset (100+ rules), install the
  [`cosmosdb-agent-kit`](https://github.com/AzureCosmosDB/cosmosdb-agent-kit) skill.
- For complex multi-container designs, break the work into separate issues and link them.

## Compatibility

See [COMPATIBILITY.md](../../COMPATIBILITY.md) for supported languages, frameworks, and
AI coding agents.
