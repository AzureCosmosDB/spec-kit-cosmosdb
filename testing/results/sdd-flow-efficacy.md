# SDD-flow efficacy: does the guidance help *inside* the spec-driven workflow?

This report covers a round of testing that is different from, and complementary to, the
command-level conformance results summarized in [`EFFICACY.md`](../../EFFICACY.md). It is the
basis for the extension changes in the pull request that introduces this file.

> **Scope / honesty note.** This round asks a specifically *harder* question than the
> command-level tests, and the headline is nuanced rather than a clean win. Read the
> **Interpretation** and **Limitations** sections before quoting any number.

## The two questions (don't conflate them)

1. **Do the command prompts encode real best-practice value?** — Answered previously
   (`EFFICACY.md`): yes. Generating the target code with vs. without a command's guidance and
   scoring against fixed best-practice checks gives **+0.10 mean pass-rate** (individual commands
   +0.14–0.37, client application-name +0.79), better in 19/24 model × language × complexity
   cells. That validates the command **content** — *when the guidance reaches the model*. It is a
   conformance measurement (heuristic checks, not execution), largely on OpenAI-family models.

2. **Does that guidance actually help when injected into the autonomous
   `specify → plan → tasks → implement` ceremony and the resulting app is built and graded?** —
   This report. It is a much harder thing to demonstrate, and it splits into a *delivery* problem
   and an *end-to-end validation* problem.

## Method

A Microsoft-internal tool for testing AI-coding-agent execution **at scale** was used to build
complete applications with a coding agent and grade them with automated behavioral tests against
a **live Azure Cosmos DB (NoSQL) account**, each attempt isolated on its own clean database.

- **Arms (identical prompt; only the delivery payload differs):**
  - `bare` — freestyle agent, no Spec Kit (reference baseline; see caveat below).
  - `sdd-base` — full Spec Kit ceremony, **no** Cosmos extension (isolates the ceremony).
  - `sdd-cosmos` — ceremony **+ the shipped extension** (both hooks).
  - `sdd-cosmos-inject` — ceremony + the **modified extension in this PR** (advise inlines rules;
    hooks non-optional; review applies fixes).
- **Scenarios:** one saturated control (RAG) + five "headroom" apps designed so that
  Cosmos-specific correctness matters (multi-tenant hierarchical partitioning, no-oversell under
  concurrent booking, e-commerce orders, IoT telemetry, inventory transfer).
- **Models:** frontier models (a Claude Opus-class and a GPT-5-class model reported here; see
  Limitations for a third model lost to an agent-infrastructure fault).
- **Budget:** every arm gets the **same** build-and-fix budget (the app must actually start), so
  we compare post-boot application quality, not first-try boot luck.
- **Grading:** behavioral tests vs. live Cosmos DB. Each scenario's **reference ("gold") app
  scores 100%** through the harness, so a low agent score reflects app quality, not a harness bug.
- Metric = fraction of a scenario's behavioral tests that pass. n ≈ 137–147 graded attempts per
  arm per model on the headroom set.

## Finding 1 — the delivery gap (why the shipped extension under-delivers autonomously)

Parsing the agent trajectories on the shipped extension:

| Signal | rate |
| --- | --- |
| Reached `/speckit.implement` | **94%** |
| `before_implement` → `advise` recommended commands | **71%** |
| Agent actually **invoked a code-generating Cosmos command** | **~15%** |

The ceremony runs and the advisor recommends the right commands, but an autonomous agent
**writes the data layer itself and rarely invokes the recommended commands** — so the (genuinely
good) guidance seldom reaches the code. Attempts that *did* invoke a generative command scored
higher (0.583 vs 0.498), but that path fires only ~15% of the time. The recommend-only,
optional-invocation design is the bottleneck.

## The change in this PR

Extension-only (no core Spec Kit change), targeting delivery:

1. **`advise` inlines** a compact best-practice rule digest for the selected patterns (instead of
   only naming commands), so the rules reach the implementation without a second invocation.
2. **`before_implement` / `after_implement` hooks are non-optional**, so guidance and review fire.
3. **`review` applies fixes**, not just an audit.

Mechanism confirmed on real attempts: `advise` fires 100%, emits the inlined rules, and the
generated code applies them (e.g. optimistic-concurrency ETags, point reads, keyless auth).

## Finding 2 — results (headroom scenarios, mean test pass-rate, bootstrap 95% CI)

| Model | bare | sdd-base | sdd-cosmos | sdd-cosmos-inject | ext Δ (cosmos−base) | inject Δ (inject−cosmos) |
| --- | --- | --- | --- | --- | --- | --- |
| Claude Opus-class | 0.755 | 0.638 | 0.573 | 0.653 | −0.065 [−0.15, +0.02] | **+0.080 [+0.00, +0.16]** |
| GPT-5-class | 0.729 | 0.678 | 0.645 | 0.681 | −0.033 [−0.12, +0.05] | +0.036 [−0.05, +0.12] |

Per-scenario (pooled), `inject` vs the shipped `sdd-cosmos`: booking-concurrency 0.686 vs 0.638,
inventory 0.685 vs 0.543, IoT 0.696 vs 0.649, saas/hierarchical-pk 0.737 vs 0.646, RAG 0.447 vs
0.351 — **wins 5 of 6**, loses only e-commerce (0.517 vs 0.571).

**What it says:**
- The change **improves on the shipped extension** — positive for both models, directionally
  consistent, 5/6 scenarios. The Opus-class headroom lift is borderline-significant.
- It **erases the shipped extension's penalty**: the unmodified extension trailed the plain
  ceremony (`cosmos − base` ≈ −0.03 to −0.07); the modified extension returns it to **≈parity
  with `sdd-base`**.
- It **does not beat the `bare` one-shot** in this harness.

## Interpretation — what's validated vs. what's hard

- **Delivery: largely solved and validated.** Getting the guidance to fire and reach the code in
  an autonomous run was the real gap (15% → reliable). This PR fixes it.
- **End-to-end behavioral validation: frame-limited and still open.** Even with delivery fixed,
  the reward lift is modest and doesn't beat `bare`. The limiting factor is now the **test
  frame**, not the mechanism.

### On "`bare` one-shot wins" — how to read it

This is the **least-controlled** comparison in the study and the easiest to over-read:

1. **Not apples-to-apples** — `bare` differs from the SDD arms on several axes at once (no
   ceremony, different prompt, different app style). The controlled contrasts are the within-SDD
   ones (`cosmos − base`, `inject − cosmos`).
2. **No human in the loop — the point of SDD is absent.** SDD's value is a developer reviewing the
   spec, correcting the plan, and catching design mistakes at the gate where they are cheap to fix.
   This harness runs the whole ceremony autonomously and grades only the final artifact, removing
   the mechanism that repays the ceremony's cost and then measuring the cost.
3. **Task scale and metric both work against the ceremony** — the scenarios are single-service,
   one-shottable apps; SDD's advantage grows with project complexity. Grading is functional
   pass-rate on a fresh, lightly-loaded database, which barely rewards what the extension optimizes
   (partition design for scale, RU efficiency, resilience) — notably the extension does *better* on
   the two most concurrency/partition-sensitive scenarios.

## Limitations

- **Two models.** A third frontier (Claude Sonnet-class) model was excluded: every attempt failed
  at agent startup due to an agent-runtime fault unrelated to the extension (it affected the
  no-extension arms equally). The reported models graded ~97% of attempts.
- **Autonomous, no human review** at the gates — not how spec-driven development is meant to be
  used.
- **Behavioral metric** rewards functional correctness on a fresh database more than the
  scale/RU/resilience properties the extension targets, so it likely **under-credits** the
  extension's intended value.
- The "reward is higher when a command is invoked" comparison is **correlational**, not randomized.
- Missing attempts (agent-startup crashes) are independent of the task, so the graded subset is
  unbiased; ungraded rate is balanced across arms.

## Conclusion and suggested next steps

The command **content** is validated (conformance). **Delivering** it reliably inside the
autonomous ceremony was the real gap, and this PR closes it — a real, if modest, improvement that
neutralizes the shipped extension's deficit. **Proving an end-to-end behavioral win** from the
ceremony is harder, and in this autonomous, functional-grading, small-task frame the ceiling is
low by construction.

A faithful test of the value proposition would change the **frame**, not just the extension:

1. **Human-in-the-loop gates** (approve/correct the spec and plan between phases) — the most
   faithful to real SDD usage and the most likely to move the verdict.
2. **Larger, multi-feature tasks** where early design mistakes compound.
3. **Metrics that score best-practice/scale/resilience** (partition quality, RU cost, behavior
   under concurrency and throttling), not just functional pass on an empty database.
