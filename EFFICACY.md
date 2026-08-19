# Efficacy evidence

This document summarizes how the Azure Cosmos DB Spec Kit extension was evaluated — **what was tested, why, and what the results show** — along with honest limitations. The goal was to answer a simple question: *does the extension actually make an AI coding agent produce better Azure Cosmos DB (NoSQL API) code?*

## How it was evaluated

Two complementary methods were used.

1. **Best-practice conformance (direct model-call harness).**
   For each command, the code it targets was generated **two ways — with and without the extension's guidance** — across multiple frontier models, four languages (Python, C#, TypeScript, Java), and three feature-complexity levels. Each output was scored against a fixed set of Azure Cosmos DB best-practice checks (application-name/user-agent on the client, `id` + partition-key point reads, 404-handled-as-null, parameterized and partition-scoped queries, ETag / transactional-batch writes, keyless auth, intentional partition keys, etc.). We recorded the best-practice **pass-rate difference** and **run-to-run determinism**. This isolates the value of the *prompts themselves*, independent of any application build.

2. **At-scale application execution (Microsoft-internal benchmarking tool).**
   A Microsoft-internal tool for testing AI coding-agent execution **at scale** builds complete applications with a coding agent against a **live Azure Cosmos DB account** and grades them with automated tests. This was used to check whether the extension's guidance actually reaches an agent working **autonomously** on a realistic task.

## What was tested, and why

### 1. Do the command prompts encode real best-practice value?
**Why:** the core claim is "deterministic, best-practice Cosmos DB code, with any agent."

**Result — yes.** With the command guidance applied, best-practice conformance improved by **+0.10 mean pass-rate**, with the extension better in **19 of 24** model × language × complexity cells, and improved determinism. The single largest and most consistent gain was reliably setting the client **application-name / user-agent (+0.79)** — something base models routinely omit. Measured per command in isolation, many individual commands added **+0.14 to +0.37**. Weaker / older models benefited most; the strongest frontier models already do much of this unaided.

### 2. Does the advisor (command recommender) recommend well?
**Why:** it routes the agent to the few relevant commands for a feature.

**Result.** It returns a bounded, low-cost shortlist (no code, small constant context cost). A tightening of its selection discipline raised recommendation **precision from 0.57 to 0.68** and brought the shortlist size back into its intended 3–8 range (from ~10–16 on the strongest model), at a modest, disclosed recall trade-off.

### 3. Does the guidance actually reach an autonomous agent? (delivery)
**Why:** guidance only helps if the model actually sees it.

**Result — the most important finding.** When an autonomous agent was given a realistic build task with the extension installed exactly as intended, it **did not invoke the on-demand commands at all** (0 of 30 runs), so the — genuinely good — guidance never reached the model and the output was no better than baseline. Delivering the **same** best-practice rules as an **always-on context block** instead improved conformance by **+0.16 mean** (higher than the +0.10 from on-demand commands), improved determinism, and helped in **every** measured cell — because always-on context can't be bypassed.

This is why the extension ships a compact always-on best-practice file (`.github/copilot-instructions.md`) alongside its commands, and why a first-class always-on-instructions capability has been proposed upstream in Spec Kit so this installs automatically for each agent.

## What this proves

- The extension's prompts carry **real, measurable** Azure Cosmos DB best-practice value — strongest exactly where models are weakest.
- **Delivery matters as much as content.** On-demand commands don't reach hands-off / autonomous agents; an always-on rule block does, and delivers the largest, most consistent gains.
- The advisor and the individual commands are each effective, and were tightened where measurement showed headroom.

## Honest limitations

- The best-practice checks are automated heuristics; treat the magnitudes as **directional**, not exact.
- Some per-check regressions reflect a **grading asymmetry** — guided code attempts more Cosmos DB work, so it is graded on more code paths than a minimal baseline — rather than worse code.
- The prompt-level measurements used frontier OpenAI-family models across four languages; the at-scale execution runs additionally covered other frontier models (Python).
- The at-scale execution harness runs a **single time-boxed attempt** per task, which does not fit a multi-step spec → plan → tasks → implement ceremony; those specific numbers are therefore **not** a fair test of that full workflow and are not the basis for the conclusions above.

## Reproducibility

The prompt-level results come from a scripted harness (generate → score against fixed best-practice checks → aggregate) run across models, languages, and complexity levels; the delivery finding comes from the same harness plus the at-scale application-execution benchmark. The best-practice checks and the always-on rule block are versioned alongside the extension.

---

*Summary:* the extension produces measurably better Azure Cosmos DB code, and **how** the guidance is delivered is as important as the guidance itself — which is why the extension pairs on-demand commands with an always-on best-practice rule set.
