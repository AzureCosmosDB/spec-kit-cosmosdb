# GitHub Copilot CLI Integration

The Azure Cosmos DB Spec Kit extension is designed for Spec Kit's agent workflow
(commands + hooks). When you drive Spec Kit from the terminal with the GitHub Copilot
CLI agent, the extension's `/speckit.cosmosdb.*` commands and its `before_implement` →
`advise` / `after_implement` → `review` hooks are available to that agent the same way
they are in the IDE.

## Setup

1. Initialize Spec Kit with the Copilot integration in your project:

   ```bash
   specify init --integration copilot
   ```

2. Add the Azure Cosmos DB extension:

   ```bash
   specify extension add cosmosdb --from https://github.com/AzureCosmosDB/spec-kit-cosmosdb/archive/refs/tags/v0.1.0.zip
   ```

   This installs the 53 `/speckit.cosmosdb.*` commands (micro patterns, component
   patterns, scaffolds, and meta tools) plus the two implement-time hooks.

## Usage

Run the Copilot CLI agent in the project and invoke the commands as part of the normal
Spec Kit loop:

```
/speckit.specify   An order service that stores orders and returns a customer's history
/speckit.cosmosdb.recommend        # optional: propose a Cosmos design from the spec
/speckit.plan
/speckit.cosmosdb.model
/speckit.cosmosdb.container
/speckit.tasks
/speckit.implement                 # before_implement hook auto-fires `advise`
/speckit.cosmosdb.point-read       # invoke the recommended commands for best-practice code
/speckit.cosmosdb.query
                                   # after_implement hook auto-fires `review`
```

Not sure which command to run? `/speckit.cosmosdb.advise` inspects the active spec/tasks
and recommends only the relevant subset for your feature. See the
[top-level README](../../README.md) for the full command list and workflow.

## Always-on best-practice rules

Commands and hooks are invoked on demand. To apply Azure Cosmos DB best-practices
automatically on every request — including autonomous flows where no command is invoked —
add them to your repository's `.github/copilot-instructions.md`, which Copilot loads at
session start. A compact, validated starter rule block is maintained in this repository at
[`.github/copilot-instructions.md`](../../.github/copilot-instructions.md).

For a larger passive ruleset (100+ rules), install the
[`cosmosdb-agent-kit`](https://github.com/AzureCosmosDB/cosmosdb-agent-kit) skill
separately.

## Compatibility

See [COMPATIBILITY.md](../../COMPATIBILITY.md) for supported languages, frameworks, and
AI coding agents.
