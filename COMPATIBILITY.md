# Cosmos DB Spec Kit - Model Compatibility

This document tracks which AI models have been tested with the Spec Kit prompt templates and their consistency scores.

## How We Test

Each prompt is run **N times** (minimum 10) against a model. We measure **contract conformance** - not exact string match, but structural consistency:

- Same file/module names
- Same function/method names
- Same architectural patterns (singleton, retry, partition key strategy)
- Same anti-patterns rejected
- Same dependency injection approach

### Scoring

- **100%**: Every run produces structurally identical output
- **95%+**: Minor cosmetic differences (comments, whitespace, variable naming) but same architecture
- **<90%**: Architectural decisions vary between runs - not recommended for production use

---

## Compatibility Matrix

| Version | Model | Platform | Micro Tier | Component Tier | Scaffold Tier | Date Tested | Notes |
|---------|-------|----------|------------|----------------|---------------|-------------|-------|
| v0.1.0 | `claude-opus-4` | GitHub Copilot | ✅ 100% | ✅ 98% | ✅ 95% | 2025-07 | Initial baseline |

## Version History

### v0.1.0 - Initial Release

**Tested against:** `claude-opus-4` via GitHub Copilot

**Results:**
- **Micro tier** (17 prompts): 100% consistency. Every run produces the same singleton pattern, retry policy, partition key logic.
- **Component tier** (19 prompts): 98% consistency. Occasional variation in docstring content, but architectural decisions (DI pattern, error handling, query structure) are identical.
- **Scaffold tier** (3 prompts): 95% consistency. Container design and partition strategy are deterministic. Minor variation in optional middleware ordering and comment density.

**Key findings:**
- Naming constraints (MUST be named `get_cosmos_client()`) are the strongest determinism lever
- Anti-pattern lists significantly reduce architectural variance
- Scale parameters influence index policy recommendations deterministically

---

## Untested Models

The following models have **not** been formally tested. They may produce correct results but consistency is not guaranteed:

- GPT-4o / GPT-4o-mini
- Claude Sonnet 3.5 / 4
- Gemini 2.5 Pro
- Llama 3.x
- Codestral / Mistral Large

If you test against a new model, please submit results via PR using the format above.

---

## MS Bench Integration

When Microsoft Bench evaluation runs are conducted against these prompts, results will be added here with:
- Bench run ID
- Model version and configuration
- Per-tier consistency scores
- Any prompt adjustments required

This section will be populated as bench runs are completed.

---

## Python SDK Fixes (e2e Testing - 2026-07-27)

The following fixes were applied to all scaffold and component prompts based on e2e testing:

1. **Health check method**: `client.read_account()` → `client.get_database_account()` (all scaffolds)
2. **aiohttp dependency**: Added `aiohttp>=3.9.0` to all requirements.txt sections (required by async SDK)
3. **Cross-partition queries**: Async SDK uses `partition_key=None`, not `enable_cross_partition_query=True` (sync-only param). Updated all references.
4. **Emulator HTTP**: Added note that Linux emulator (vnext) uses HTTP - `connection_verify=False` needed for local dev
5. **Pydantic v2**: Verified all prompts use `model_config = ConfigDict(...)` (no legacy `class Config:` found)
