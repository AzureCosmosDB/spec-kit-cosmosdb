# Changelog

All notable changes to the Azure Cosmos DB Spec Kit Extension are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-09-14

### Changed

- **`speckit.cosmosdb.advise` now inlines guidance instead of only recommending commands.**
  The `before_implement` advisor selects the relevant Azure Cosmos DB patterns and inlines
  their compact best-practice rules (from a new rule digest) directly into its output, so
  `/speckit.implement` applies them without a second command invocation. It still names the
  full `/speckit.cosmosdb.*` command for deeper guidance. This closes a delivery gap where
  an autonomous agent rarely invoked the recommended commands, so the guidance seldom
  reached the generated code.
- **Both hooks are now non-optional.** `before_implement` (advise) and `after_implement`
  (review) run as part of the flow rather than being skippable, so best-practice guidance
  and the review consistently fire.
- **`speckit.cosmosdb.review` now applies fixes, not just an audit.** After scoring, it edits
  the code to correct every Fail/Warn and re-checks until the critical issues are resolved.

## [0.1.0] - 2026-08-14

Initial **preview** release. APIs, command names, and prompt behavior may change
before a stable 1.0.0.

### Added

- 53 prescriptive commands for Azure Cosmos DB spanning micro patterns, component
  patterns, full application scaffolds, and meta tools (recommend, review, explain).
- Multi-entity aggregate design guidance in `speckit.cosmosdb.model`: access-pattern
  RPS analysis, identifying-relationship checks, consolidation decision framework,
  RU cost reasoning, and a massive-scale warning.
- Vector search command (`speckit.cosmosdb.vector`) aligned with current Azure Cosmos DB
  guidance: index-type selection by per-query vector count, dimension limits, the
  1,000-vector index activation threshold, embedding normalization, and parameterized
  `ORDER BY VectorDistance(...)` queries.
- `after_implement` hook that optionally runs `speckit.cosmosdb.review`.
- Guidance to tag `user_agent_suffix` / application name in generated
  `CosmosClient` initialization code (instructed across the command set; agent
  adherence may vary — see #9).

### Changed

- Branding: all documentation and user-facing descriptions use "Azure Cosmos DB".

### Removed

- `speckit.cosmosdb.agent-kit` command and its `after_plan` hook. For always-on
  best-practice rules, install the standalone
  [`cosmosdb-agent-kit`](https://github.com/AzureCosmosDB/cosmosdb-agent-kit) skill
  separately; this extension focuses on prescriptive workflows.

[0.1.0]: https://github.com/AzureCosmosDB/spec-kit-cosmosdb/releases/tag/v0.1.0
