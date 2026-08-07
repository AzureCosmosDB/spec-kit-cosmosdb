# Cosmos Intent SDK

**Natural Language is the New Programming Language.**

> If traditional SDKs are the instruction manual, Intent SDK is the expert sitting next to you who already read the manual.

---

## Meet Developers Where They Are

Software development is no longer exclusive to trained engineers. The circle of people who can build software is growing exponentially — from professional developers to designers, product managers, domain experts, and hobbyists. This framework meets **all of them** where they are:

| Developer | Entry Point | Experience |
|-----------|-------------|------------|
| **Non-technical vibe coders** | `/cosmos.vibe` | Formulate intent in plain language → get guided to the right scaffold with pre-filled parameters |
| **Junior developers** | Scaffolds with natural language | Describe what you're building, get complete apps with best practices baked in |
| **Experienced devs new to Cosmos DB** | Component commands | Get best-practice patterns (singleton, partition key, retry) without reading 200 pages of docs |
| **Cosmos DB experts** | Micro commands | A library of prompt shortcuts for building discrete pieces quickly |

The framework doesn't gatekeep — it **elevates**. A vibe coder using `/cosmos.vibe` → `/cosmos.scaffold-chat` gets the **same architectural quality** as an expert writing the queries manually. This is the democratization of expertise: the template encodes years of Cosmos DB knowledge; the developer provides domain intent.

### The Full Spectrum: Intent SDK + Agent Kit

| | **Intent SDK** (this project) | **Agent Kit** ([cosmosdb-agent-kit](https://github.com/AzureCosmosDB/agent-kit)) |
|---|---|---|
| **For** | Intent-based development — declare what you want | Safety net — catches mistakes when you're freestyle coding |
| **Approach** | Prescriptive generation from explicit intent | Passive correction of existing code |
| **Spectrum** | "I know what I want" → deterministic output | "I'm figuring it out" → guardrails while you explore |

Together they cover the entire spectrum from *"I don't know what I'm doing"* to *"I know exactly what I want."* Start with `/cosmos.vibe` if you're unsure. Use Agent Kit if you're already coding and want a safety net. Use specific `/cosmos.*` commands when you know precisely what you need.

---

## The Concept

The way developers interact with SDKs has evolved:

```
Assembly → High-level Languages → Frameworks → SDKs → Intent SDKs
```

Traditional SDKs give you **methods to call**. Intent SDKs give you **intents to declare**.

You describe **WHAT** you want. The prompt template encodes **HOW** — best practices, anti-patterns, SDK specifics, partition key strategy, retry policies, and every lesson learned from thousands of Cosmos DB deployments.

### Vibe Coding Welcome

While the Intent SDK is built for developers who want to be **mindful and explicit** about what they're building, we provide a **conversational entry point** for anyone — see [For Vibe Coders](#for-vibe-coders) below. `/cosmos.vibe` analyzes your intent and guides you to the right command with pre-filled parameters. Every slash command is a declaration of intent with specific parameters. The prompt template is the contract that turns that intent into deterministic, production-grade code.

### Intent SDK vs. Skills

| | **Skills** (e.g., cosmosdb-agent-kit) | **Intent SDK** (this project) |
|---|---|---|
| **Developer has** | Vague prompt | Clear intent |
| **Approach** | Passively corrects mistakes | Prescriptively generates correct code |
| **Analogy** | Spell-check while you type | Expert dictation from your specification |
| **Determinism** | Best-effort | Contract-enforced |

Through extensive testing with the [cosmosdb-agent-kit](https://github.com/AzureCosmosDB/agent-kit), we discovered that **highly prescriptive prompt templates** — ones that encode architectural constraints, anti-patterns, and output contracts — produce structurally consistent code across runs. Not identical code, but code that makes the **same architectural decisions** every time.

---

## Natural Language Programming — Examples

Each `/cosmos.*` command combines a **prescriptive template** (encoding Cosmos DB expertise) with **YOUR natural language** (encoding your domain knowledge). The template ensures best practices — singleton patterns, partition key alignment, retry policies, ETags. Your words ensure the output fits your exact use case. This is natural language programming: you write English, constrained by domain-expert templates, and get deterministic, production-grade code.

**The slash command is the expert guardrail. Your natural language is the custom intent.** Together they produce code that is both correct by construction and tailored to your specific domain.

### Example 1: Micro — Singleton Client with Custom Context

```
/cosmos.singleton
Python FastAPI app, but I need the client configured for
multi-region with West US as primary and East US as failover.
Session consistency. Running behind Azure API Management
so connection should use Gateway mode.
```

**What you get:** The template's mandatory patterns stay fixed — module-level singleton, `CosmosSettings` via Pydantic `BaseSettings`, FastAPI lifespan context manager, health check via `ReadAccountAsync()`, 9 retries on 429, distributed tracing, `user_agent_suffix`. But your custom context changes the configuration:
- `preferred_regions=["West US", "East US"]` with West US as primary
- `consistency_level=ConsistencyLevel.Session` (not the default Eventual)
- `connection_mode=ConnectionMode.Gateway` (not Direct) because you're behind APIM
- Multi-region write detection enabled

The template encodes *how* to build a singleton. You encode *what your infrastructure looks like*.

### Example 2: Component — Data Model with Bespoke Domain Logic

```
/cosmos.model
I'm building a healthcare patient records system. Patients belong
to clinics. Each patient has visit records, prescriptions, and lab
results. Doctors query by patient within their clinic. Billing
queries across all patients in a clinic monthly. Lab results need
7-year retention. Prescriptions are updated frequently.
```

**What you get:** The prompt forces partition key to `/clinicId` — not `/patientId`, not `/id` — because your stated primary query pattern is "patients within their clinic." The template **encodes the expertise** that query patterns drive partition key selection, not entity identity. Your domain description also triggers:
- TTL of ~220M seconds on lab results (7 years) via default TTL on the container
- Prescriptions in a container with higher throughput allocation (frequent updates)
- Composite index on `(clinicId, visitDate)` for the billing monthly aggregation
- Hierarchical partition key consideration: `/clinicId/patientId` if scale warrants it

You described your domain in plain English. The template translated it into Cosmos DB architecture decisions.

### Example 3: Repository — Custom Requirements Merged with Mandatory Patterns

```
/cosmos.repository
I need a repository for the Patient entity from the model above.
Include soft-delete with 90-day recovery window. Add a method to
find patients with overdue lab work (last lab > 12 months ago).
Billing needs to aggregate visit costs by month.
```

**What you get:** Your custom requirements get merged with the template's mandatory patterns:
- **From the template (non-negotiable):** Singleton client injection, point reads by `id + partitionKey`, ETag-based optimistic concurrency on every write, retry with exponential backoff, typed `Patient` dataclass, `async` throughout
- **From your words (custom intent):** `soft_delete()` that sets `is_deleted=True` and `deleted_at=now()` with a TTL of 90 days, `find_overdue_lab_patients()` using a cross-partition query with `last_lab_date < 12_months_ago`, `aggregate_visit_costs(clinic_id, month)` using a parameterized query with `GROUP BY`

The template guarantees the repository is structurally correct. Your description makes it *functionally* correct for your domain.

### Example 4: Scaffold — Full Application from Natural Language

```
/cosmos.scaffold
I'm building an internal tool for our support team. Agents handle
tickets from customers. Each ticket has a conversation thread with
messages from both the agent and customer. We need to search tickets
by customer email, view all open tickets for an agent, and see
response time metrics. About 50 agents, 10K tickets/month. Python, FastAPI.
```

**What you get:** The scaffold performs intent analysis from your description (the same analysis `cosmos.vibe` would produce automatically):

| Derived Decision | Reasoning from Your Words |
|---|---|
| Partition key: `/agentId` on tickets | "view all open tickets for an agent" = primary query pattern |
| Secondary index on `customerEmail` | "search tickets by customer email" = cross-partition, needs index |
| Messages embedded in ticket document | 10K tickets/month × ~20 messages = well within 2MB doc limit |
| Single container `tickets` | 50 agents × 10K/month = low cardinality, one container suffices |
| No change feed | No real-time requirement stated |
| `response_time_ms` computed field | "response time metrics" = derived from first agent reply timestamp |

Then it generates the full stack: models, repositories, endpoints, singleton client — all deterministic, all following the same structural contracts.

### Example 5: Bespoke Composition — Multi-Step Workflow

For maximum control, chain commands where each step adds your domain knowledge:

```
/cosmos.model
I'm building a veterinary clinic management system. We have clinics,
vets, pet owners, pets, and appointments. A pet belongs to an owner,
an owner belongs to a clinic. Appointments are between a vet and a pet
at a specific clinic. We do about 200 appointments/day across 5 clinics.
Most queries: "show me today's appointments for this vet" and
"show me all visits for this pet."
```

```
/cosmos.partition-key
I'm not sure about the partition key for appointments. Here are my
query patterns:
1. All appointments for a vet today (80% of reads)
2. All visits for a specific pet (15% of reads)
3. Clinic-wide schedule for a day (5% of reads, admin only)
Writes are always single appointments.
```

→ The template analyzes your access patterns and recommends `/vetId` with a composite index on `(vetId, appointmentDate)` for pattern 1, accepting cross-partition queries for patterns 2 and 3 given their lower frequency.

```
/cosmos.repository
Generate repositories for Appointment and Pet entities. Appointments
need: book, cancel (soft-cancel, keep record), reschedule (must
preserve original time for audit), and find-available-slots (given a
vet and date, return gaps in their schedule). Pets need: register,
update medical notes, and get-visit-history with pagination.
```

→ Your custom methods (`find_available_slots`, `reschedule` with audit trail) get merged with the template's mandatory patterns (singleton injection, ETag concurrency, point reads, retry).

```
/cosmos.endpoint
Create REST endpoints for appointments. I need custom validation:
can't book two appointments for the same vet at overlapping times.
Reschedule should return both old and new appointment in the response.
Cancel requires a reason field. All endpoints need clinic_id in the
URL path for our API gateway routing.
```

→ Each command produces code that **composes cleanly** because every prompt follows the same structural contracts, while your custom requirements are woven into the business logic layer.

### Example 5: Vibe — Just Describe It

```
/cosmos.vibe
I need to track orders for my online store. Customers should see their order history
and I need to search orders by status for my admin panel.
```

**What you get:** The system identifies this as an e-commerce scaffold, infers the primary query is "orders by customer" (making `/customerId` the partition key), generates all supporting queries, shows you the Intent Analysis, and outputs the exact `/cosmos.scaffold-ecommerce` command pre-filled with all the parameters — ready to copy-paste and run. No partition keys, RUs, or consistency levels required from you.

---

## Command Reference

### Meta Tier — Conversational Entry Points

| Command | Purpose |
|---------|--------|
| `/cosmos.vibe` | Describe what you want in plain language — get a full app |
| `/cosmos.review` | Audit existing Cosmos DB code against best practices |
| `/cosmos.explain` | Learn any Cosmos DB concept with examples and anti-patterns |

### Scaffold Tier — Full Application Generation

| Command | Purpose |
|---------|---------|
| `/cosmos.scaffold` | Generate a complete Cosmos DB application from a use-case description |
| `/cosmos.migrate` | Generate migration tooling for schema evolution or data migration |
| `/cosmos.rag` | Generate a RAG (Retrieval-Augmented Generation) application with vector search |

### Component Tier — Single-Concern Generation

| Command | Purpose |
|---------|---------|
| `/cosmos.api-pagination` | API-level pagination with continuation tokens |
| `/cosmos.autoscale` | Autoscale throughput configuration |
| `/cosmos.bulk` | Bulk import/export operations |
| `/cosmos.changefeed` | Change feed consumer |
| `/cosmos.changefeed-processor` | Change feed processor with lease management |
| `/cosmos.container` | Container creation with indexing and partition strategy |
| `/cosmos.cqrs` | CQRS (Command Query Responsibility Segregation) pattern |
| `/cosmos.endpoint` | REST/API endpoint for a Cosmos DB entity |
| `/cosmos.event-sourcing` | Event sourcing pattern implementation |
| `/cosmos.global-distribution` | Multi-region distribution configuration |
| `/cosmos.hierarchical-pk` | Hierarchical partition key design |
| `/cosmos.model` | Data model with partition key strategy |
| `/cosmos.multi-tenant` | Multi-tenant data isolation patterns |
| `/cosmos.query` | Parameterized query with best practices |
| `/cosmos.repository` | Repository/data access layer for an entity |
| `/cosmos.session-state` | Session state management with Cosmos DB |
| `/cosmos.stored-proc` | Stored procedure with transaction support |
| `/cosmos.ttl` | TTL (Time-to-Live) configuration and patterns |
| `/cosmos.vector` | Vector search / embedding storage |

### Micro Tier — Surgical Patterns

| Command | Purpose |
|---------|---------|
| `/cosmos.availability` | High-availability configuration |
| `/cosmos.conditional-create` | Conditional create with conflict detection |
| `/cosmos.connection` | Connection configuration and modes |
| `/cosmos.cross-partition` | Cross-partition query patterns |
| `/cosmos.diagnostics` | Diagnostics and logging setup |
| `/cosmos.etag` | ETag-based optimistic concurrency |
| `/cosmos.index-policy` | Custom indexing policy |
| `/cosmos.pagination` | Query-level pagination with continuation tokens |
| `/cosmos.partition-key` | Partition key selection guidance |
| `/cosmos.patch` | Partial document updates (patch operations) |
| `/cosmos.point-read` | Optimized point read by id + partition key |
| `/cosmos.retry` | Retry policy and 429 handling |
| `/cosmos.serialization` | Custom serialization configuration |
| `/cosmos.singleton` | CosmosClient singleton for dependency injection |
| `/cosmos.stream-query` | Streaming query results |
| `/cosmos.transaction` | Transactional batch operations |
| `/cosmos.upsert` | Upsert patterns and conflict resolution |

**Total: 42 commands** across 4 tiers.

---

## For Vibe Coders

Don't know partition keys from primary keys? That's fine.

**`/cosmos.vibe`** is your entry point. Just describe what you want:

```
/cosmos.vibe
I want to build a chat app where users can have group conversations
```

That's it. The system will:

1. **Figure out what you need** — match your description to the right scaffold (chat, e-commerce, IoT, etc.)
2. **Reason about your queries** — the data access patterns that determine how your data should be organized
3. **Show you the Intent Analysis** — before recommending anything, you'll see exactly what architectural decisions are being made and why
4. **Give you the exact command to run** — a pre-filled `/cosmos.scaffold-*` command with all parameters derived from your description
5. **Teach you the next step** — every response includes related commands for more control

`/cosmos.vibe` doesn't generate code itself — it's the **triage layer** that ensures you run the right command with the right inputs. The explicit parameters ensure deterministic, best-practice output every time.

The tiers work like this:

| Tier | Who it's for | Example |
|------|-------------|--------|
| **Meta** | Anyone — plain language in, guided to the right command | `/cosmos.vibe` "build me a task tracker" |
| **Scaffold** | Developers who know their use case | `/cosmos.scaffold-chat` with specific parameters |
| **Component** | Developers building piece by piece | `/cosmos.model`, `/cosmos.repository` |
| **Micro** | Developers who need one specific pattern | `/cosmos.singleton`, `/cosmos.retry` |

Start with `/cosmos.vibe`. Graduate to specific commands as you learn. Every command produces the same production-grade code.

---

## Tested Models & Compatibility

Prompt templates are tested for **structural consistency** — same architectural decisions, same patterns, same file/function names across N runs.

### Current Status

| Version | Model | Platform | Micro | Component | Scaffold | Notes |
|---------|-------|----------|-------|-----------|----------|-------|
| v0.1.0 | `claude-opus-4` | GitHub Copilot | ✅ 100% | ✅ 98% | ✅ 95% | Initial release |

**If you're using a tested model, these prompts will produce deterministic results. Untested models may work but aren't guaranteed.**

See [COMPATIBILITY.md](COMPATIBILITY.md) for full testing details, methodology, and historical results.

---

## Usage Tracking

All generated code includes a **User-Agent string** in the CosmosClient initialization, enabling adoption tracking through Cosmos DB service-side telemetry.

### How It Works

Every prompt template instructs the model to include `cosmos-intent-sdk/0.1.0` as the application identifier. This is **visible in generated code** — not hidden telemetry.

### Per-Language Examples

**Python:**
```python
client = CosmosClient(
    url=settings.cosmos_endpoint,
    credential=settings.cosmos_key,
    user_agent_suffix="cosmos-intent-sdk/0.1.0"
)
```

**TypeScript/JavaScript:**
```typescript
const client = new CosmosClient({
    endpoint: process.env.COSMOS_ENDPOINT,
    key: process.env.COSMOS_KEY,
    userAgentSuffix: "cosmos-intent-sdk/0.1.0"
});
```

**C#:**
```csharp
var client = new CosmosClient(connectionString, new CosmosClientOptions
{
    ApplicationName = "cosmos-intent-sdk/0.1.0"
});
```

**Java:**
```java
CosmosClient client = new CosmosClientBuilder()
    .endpoint(endpoint)
    .key(key)
    .userAgentSuffix("cosmos-intent-sdk/0.1.0")
    .buildClient();
```

This allows Microsoft to track how many Cosmos DB requests originate from Intent SDK-generated code, helping prioritize prompt improvements and SDK investment.

---

## Installation

### GitHub Copilot (Recommended)

```bash
# Clone into your project
git clone https://github.com/AzureCosmosDB/cosmosdb-intent-sdk.git .cosmos-intent-sdk

# Add to your Copilot instructions
echo 'Use prompt templates from .cosmos-intent-sdk/prompts/ for all Cosmos DB work' >> .github/copilot-instructions.md
```

### NPM (Multi-Editor CLI)

After the package is published to npm:

```bash
# Interactive — choose which editors to install for
npx cosmos-intent-sdk init

# Install all integrations at once
npx cosmos-intent-sdk init --all

# Install specific integrations
npx cosmos-intent-sdk init --integration copilot --integration claude

# Include agent kit for ongoing protection
npx cosmos-intent-sdk init --all --with-agent-kit

# Update/overwrite existing prompts
npx cosmos-intent-sdk update --all

# List available prompts
npx cosmos-intent-sdk list
```

To test an unpublished checkout exactly as an npm consumer would, build a tarball and install it in a separate project:

```bash
# In this repository
cd cli
npm pack

# In a separate project
npm install /path/to/cosmos-intent-sdk-0.2.0.tgz
npx cosmos-intent-sdk list
npx cosmos-intent-sdk init --integration copilot --with-agent-kit
```

The tarball is the release boundary: testing it catches missing package files that running the CLI directly from this repository can hide.

**Supported integrations:**

| Integration | What gets installed |
|---|---|
| `copilot` | `.github/agents/*.agent.md` + `.github/prompts/*.prompt.md` |
| `cursor` | `.cursor/rules/*.mdc` |
| `claude` | `.claude/commands/*.md` + CLAUDE.md reference |
| `gemini` | `.gemini/prompts/*.md` + GEMINI.md reference |
| `windsurf` | `.windsurf/rules/*.md` |
| `mcp` | MCP server in `.mcp/` + config in `.vscode/mcp.json` & `.cursor/mcp.json` |

### Manual

Copy the `prompts/` directory into your project and reference templates directly in your AI coding tool.

## Quick Start

1. **Install** the prompt templates (see above)
2. **Pick a command** from the [Command Reference](#command-reference)
3. **Declare your intent** with the required parameters
4. **Get deterministic, production-grade code** every time

```
/cosmos.singleton
language: python
framework: FastAPI
auth_model: DefaultAzureCredential
```

That's it. The prompt encodes the expertise. You declare the intent.

## Integration Targets

| Platform | Method |
|----------|--------|
| **VS Code Copilot Chat** | Slash commands in chat |
| **GitHub Copilot CLI** | `gh copilot suggest` with prompt templates |
| **GitHub Copilot Coding Agent** | Issue-to-PR with prescriptive templates |

## Testing Determinism

Each prompt is tested for structural consistency. The retained comparisons and live-emulator evidence are under [`testing/results/`](testing/results/).

The harness accepts an OpenAI-compatible endpoint and a structured YAML or JSON test template:

```bash
python testing/harness/run-iterations.py \
    --template path/to/test-template.yaml \
    --variables '{"entity":"orders"}' \
    --iterations 10 \
    --model gpt-4o
```

We don't test for exact string match. We test for **contract conformance**: same fields, same patterns, same architectural decisions across N runs.

### CLI consumer smoke test

Before publishing the CLI, install the tarball in a clean project and verify:

1. `npx cosmos-intent-sdk list` reports all 52 prompts.
2. `init --integration copilot --with-agent-kit` creates 52 agent files and 52 prompt files.
3. `.vscode/settings.json` enables `github.copilot.chat.promptFiles`.
4. Agent Kit instructions are installed in both Copilot instruction locations.
5. Running the same `init` command again produces no content changes or duplicate Agent Kit section.

This flow was verified on Windows against the local `cosmos-intent-sdk-0.2.0.tgz` package. VS Code command discovery remains a manual UI check: open or reload the consumer project and confirm the installed `/cosmos.*` commands appear in Copilot Chat.

Generated applications and result reports are retained as test evidence. Virtual environments, Python bytecode caches, and runtime logs are excluded; recreate dependencies from each generated app's manifest when rerunning an E2E test.

## /cosmos.vibe and Agent Kit

The SDK offers two paths to Cosmos DB code:

| Path | How it works | Agent Kit needed? |
|------|-------------|-------------------|
| **Explicit** (`/cosmos.scaffold-*`, `/cosmos.model`, etc.) | You provide structured inputs → deterministic, best-practice output | No — the output already encodes best practices |
| **Vibe** (`/cosmos.vibe`) | Plain-language description → triage → scaffold + **Agent Kit rules** | Yes — protects you as you modify generated code |

### Why Agent Kit matters for vibe coders

When you use `/cosmos.vibe`, the SDK generates a scaffold and then activates **session rules** covering singleton clients, partition key usage, retry patterns, concurrency, and cost optimization. These rules stay active while you iterate on the generated code.

To persist these rules permanently (so every AI session in your repo enforces them):

```bash
npx cosmos-intent-sdk init --with-agent-kit
```

This installs Cosmos DB best-practice rules into your editor's AI configuration:
- **Copilot** → `.github/copilot-instructions.md` + `.github/instructions/cosmos-agent-kit.instructions.md`
- **Claude** → `CLAUDE.md`
- **Cursor** → `.cursor/rules/cosmos-agent-kit.mdc`
- **Gemini** → `GEMINI.md`
- **Windsurf** → `.windsurf/rules/cosmos-agent-kit.md`

Agent Kit is most valuable for developers who will modify generated Cosmos DB code without deep knowledge of RU optimization, partition key design, or consistency trade-offs. The rules catch anti-patterns before they ship.

## Philosophy

1. **Prompts are code** — version them, test them, review them
2. **Prescriptive > permissive** — constrain the model, don't hope
3. **Domain expertise compounds** — each prompt encodes months of Cosmos DB learning
4. **Determinism is measurable** — run N times, compare contracts
5. **Intent > instruction** — declare what you want, not how to do it

## Contributing

We welcome contributions! Here's how:

1. **New prompts**: Add to the appropriate tier in `prompts/`. Follow the existing template structure (Intent → Required Inputs → Prescriptive Prompt → Constraints → Anti-Patterns → Output).
2. **Testing**: Run the determinism harness against your prompt. Include results in your PR.
3. **Model testing**: Test against new models and submit results for [COMPATIBILITY.md](COMPATIBILITY.md).
4. **Bug fixes**: If a prompt produces incorrect patterns, open an issue with the model, platform, and generated output.

```bash
# Run tests
python testing/harness/run-iterations.py --prompt your.prompt --iterations 10

# Check consistency
python testing/harness/compare-contracts.py --results ./results/
```

## License

MIT
