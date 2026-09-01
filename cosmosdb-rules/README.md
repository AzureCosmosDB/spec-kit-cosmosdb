# Azure Cosmos DB Always-On Rules (preset)

A Spec Kit **preset** that carries the Azure Cosmos DB best-practice rules as an
always-on instruction block. When this preset is enabled and the opt-in
[`agent-context`](https://github.com/github/spec-kit/tree/main/extensions/agent-context)
extension is installed, the rules are composed into the coding agent's context
file (for example `.github/copilot-instructions.md`) inside a namespaced
`<!-- SPECKIT PRESET:cosmosdb-rules START/END -->` block, so they apply to the
agent's work generally, including outside a Spec Kit workflow.

This uses the preset `provides.instructions` capability proposed in
[github/spec-kit#4389](https://github.com/github/spec-kit/pull/4389) — core
validates the metadata only; `agent-context` owns the writes. Nothing changes
the agent's context unless you install `agent-context` and enable this preset.

## Enable always-on Cosmos rules (opt-in)

Getting the always-on rules requires **three pieces**, and nothing touches your
agent's context until you install `agent-context` and enable this preset — it is
fully opt-in:

1. the **Azure Cosmos DB extension** (you likely have this already),
2. the opt-in **`agent-context` extension**, which owns the always-on file, and
3. this **preset**, which supplies the Cosmos rules `agent-context` composes.

```bash
# 1. The Azure Cosmos DB extension (existing step)
specify extension add cosmosdb --from https://github.com/AzureCosmosDB/spec-kit-cosmosdb/archive/refs/tags/v0.1.0.zip

# 2. The opt-in agent-context extension — writes the managed always-on block
specify extension add agent-context

# 3. This preset — supplies the Cosmos rules that agent-context composes.
#    The URL is the cosmosdb-rules-<tag>.zip asset attached to each release
#    (produced by .github/workflows/release-preset.yml).
specify preset add cosmosdb-rules --from https://github.com/AzureCosmosDB/spec-kit-cosmosdb/releases/download/v0.1.0/cosmosdb-rules-v0.1.0.zip
#    Before a release is cut, install from a local checkout instead:
#    specify preset add cosmosdb-rules --dev ./cosmosdb-rules

# 4. Compose now (also runs automatically after /speckit.specify or /speckit.plan)
specify speckit.agent-context.update
```

After this, your agent's context file (for example `.github/copilot-instructions.md`)
contains the Cosmos rules inside a `<!-- SPECKIT PRESET:cosmosdb-rules START/END -->`
block, applied to all of the agent's work in the project — including outside a
Spec Kit workflow.

Turn it off any time: `specify preset disable cosmosdb-rules` (or `remove`); the
block is dropped on the next `agent-context` update.

## What is delivered

The block is the same compact rule set shipped in the extension's always-on
[`.github/copilot-instructions.md`](../.github/copilot-instructions.md) (auth,
user-agent, client singleton, partition-key design, point reads, parameterized
partition-scoped queries, ETag concurrency, 429 backoff, indexing, bulk).
