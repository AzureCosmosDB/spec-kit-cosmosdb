# VS Code + GitHub Copilot Integration

Use the Azure Cosmos DB Spec Kit extension from GitHub Copilot Chat in VS Code. Once
installed, the extension's `/speckit.cosmosdb.*` commands and its two implement-time
hooks are available directly in Copilot Chat.

## Setup

1. Initialize Spec Kit in your project with the Copilot integration:

   ```bash
   specify init --integration copilot
   ```

   This installs the standard Spec Kit commands as Copilot prompt files under
   `.github/prompts/` so they appear as `/speckit.*` slash commands in Copilot Chat.

2. Add the Azure Cosmos DB extension:

   ```bash
   specify extension add cosmosdb --from https://github.com/AzureCosmosDB/spec-kit-cosmosdb/archive/refs/tags/v0.1.0.zip
   ```

   This installs the 53 `/speckit.cosmosdb.*` commands (micro patterns, component
   patterns, scaffolds, and meta tools) plus the `before_implement` → `advise` and
   `after_implement` → `review` hooks.

3. Reload VS Code so Copilot Chat picks up the new prompt files.

## Using the commands

Type `/speckit.cosmosdb.` in Copilot Chat to see the available commands, or invoke one
directly. They read your active spec/plan for intent, so you don't have to re-type
everything:

```
/speckit.cosmosdb.recommend  I want a real-time chat app with message history
/speckit.cosmosdb.model
/speckit.cosmosdb.partition-key
/speckit.cosmosdb.point-read
/speckit.cosmosdb.query
```

Not sure which command to run? `/speckit.cosmosdb.advise` inspects the active
spec/tasks and recommends only the relevant subset for your feature. Whole-app
skeletons are available via the `scaffold-*` commands (e.g.
`/speckit.cosmosdb.scaffold-chat`).

## Typical flow in Copilot Chat

The extension's commands sit alongside the standard Spec Kit loop:

```
/speckit.specify   An e-commerce service that stores orders and lets customers
                   look up their order history quickly
/speckit.cosmosdb.recommend        # optional: propose a Cosmos design from the spec
/speckit.plan
/speckit.cosmosdb.model            # document model + partition key strategy
/speckit.cosmosdb.container        # container with indexing + PK
/speckit.tasks
/speckit.implement                 # before_implement hook auto-fires `advise`
/speckit.cosmosdb.point-read       # invoke the recommended commands for best-practice code
/speckit.cosmosdb.query
                                   # after_implement hook auto-fires `review`
```

When you run `/speckit.implement`, the `before_implement` hook fires
`speckit.cosmosdb.advise`, which injects a compact command *index* (~1.5K tokens) and a
short shortlist — not the full library — so implementation becomes Cosmos-aware without
bloating the context window. You then invoke the recommended commands to upgrade the
data layer to best-practice code. After implementation, the `after_implement` hook fires
`speckit.cosmosdb.review`.

See the [top-level README](../../README.md) for the full command list and the complete
end-to-end workflow.

## Always-on best-practice rules

The extension delivers guidance through **commands and hooks**, which are invoked on
demand. If you want Azure Cosmos DB best-practices applied automatically on every Copilot
request — including in autonomous flows where no command is invoked — add them to your
repository's `.github/copilot-instructions.md`, which Copilot loads at session start. A
compact, validated starter rule block is maintained in this repository at
[`.github/copilot-instructions.md`](../../.github/copilot-instructions.md); copy the
Azure Cosmos DB rules into your own project's file.

For a larger passive ruleset (100+ rules), install the
[`cosmosdb-agent-kit`](https://github.com/AzureCosmosDB/cosmosdb-agent-kit) skill
separately.

## Compatibility

See [COMPATIBILITY.md](../../COMPATIBILITY.md) for supported languages, frameworks, and
AI coding agents.
