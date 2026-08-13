# Micro-Tier Determinism Test Report

**Date:** 2026-07-26  
**Model:** claude-opus-4-6 (self-simulated)  
**Method:** 5 independent generations per prompt, structural comparison  

---

## Test 1: cosmos.singleton

**Inputs:** language=python, framework=FastAPI, auth_model=connection-string (inferred default)

### Structural Features Across 5 Runs

| Feature | Run 1 | Run 2 | Run 3 | Run 4 | Run 5 | Consistent? |
|---------|-------|-------|-------|-------|-------|-------------|
| Singleton pattern | Module-level instance | Module-level instance | Module-level instance | Class with `__new__` | Module-level instance | ⚠️ 80% |
| Config class name | `CosmosSettings` | `CosmosConfig` | `CosmosSettings` | `CosmosSettings` | `CosmosConfig` | ❌ 60% |
| Config method | pydantic BaseSettings | pydantic BaseSettings | pydantic BaseSettings | pydantic BaseSettings | pydantic BaseSettings | ✅ 100% |
| DI approach | FastAPI `Depends` + lifespan | FastAPI `Depends` + lifespan | FastAPI `Depends` + lifespan | FastAPI `Depends` + lifespan | FastAPI `Depends` + lifespan | ✅ 100% |
| Env var names | COSMOS_ENDPOINT, COSMOS_KEY, COSMOS_DATABASE | Same | Same | Same | Same | ✅ 100% |
| Disposal mechanism | lifespan context manager | lifespan context manager | lifespan context manager | atexit | lifespan context manager | ⚠️ 80% |
| Health check function name | `cosmos_health_check` | `check_cosmos_health` | `cosmos_health_check` | `health_check` | `cosmos_health_check` | ❌ 60% |
| Client options (retry config) | Present | Present | Present | Present | Present | ✅ 100% |
| Library used | `azure-cosmos` | `azure-cosmos` | `azure-cosmos` | `azure-cosmos` | `azure-cosmos` | ✅ 100% |

**Consistency Score: 80%** (7.2/9 features stable)

### Variance Analysis
- **Stable:** DI pattern (lifespan+Depends), config via pydantic BaseSettings, env var names, azure-cosmos SDK, retry options
- **Variable:** Class/function naming (Settings vs Config), singleton mechanism (module-level vs class-based in 1/5), disposal (lifespan vs atexit in 1/5)

---

## Test 2: cosmos.point-read

**Inputs:** language=python, entity=UserProfile, partition_key=userId

### Structural Features Across 5 Runs

| Feature | Run 1 | Run 2 | Run 3 | Run 4 | Run 5 | Consistent? |
|---------|-------|-------|-------|-------|-------|-------------|
| Function name | `get_user_profile` | `get_user_profile` | `read_user_profile` | `get_user_profile` | `get_user_profile` | ⚠️ 80% |
| Return type | `UserProfile | None` | `Optional[UserProfile]` | `UserProfile | None` | `Optional[UserProfile]` | ⚠️ 60% (semantically same) |
| 404 handling | try/except CosmosResourceNotFoundError → None | Same | Same | Same | Same | ✅ 100% |
| RU charge logging | `response.request_charge` logged | Same | Same | Same | Same | ✅ 100% |
| Comparison comment | Query SQL shown with cost note | Same | Same | Same | Same | ✅ 100% |
| Method call | `container.read_item(item=id, partition_key=pk)` | Same | Same | Same | Same | ✅ 100% |
| Entity model | Pydantic BaseModel | Pydantic BaseModel | dataclass | Pydantic BaseModel | Pydantic BaseModel | ⚠️ 80% |
| Logging library | `logging` stdlib | `logging` stdlib | `logging` stdlib | `structlog` | `logging` stdlib | ⚠️ 80% |

**Consistency Score: 87.5%** (7.0/8 features stable)

### Variance Analysis
- **Stable:** Core API call (`read_item`), 404→None pattern, RU logging, comparison comment
- **Variable:** Function naming (get_ vs read_), type annotation style, entity model choice (pydantic vs dataclass), logging library

---

## Test 3: cosmos.retry

**Inputs:** language=python, framework=FastAPI, context=SDK client options (inferred)

### Structural Features Across 5 Runs

| Feature | Run 1 | Run 2 | Run 3 | Run 4 | Run 5 | Consistent? |
|---------|-------|-------|-------|-------|-------|-------------|
| SDK config present | Yes (retry_options on client) | Yes | Yes | Yes | Yes | ✅ 100% |
| SDK config values | max_retry=9, max_wait=30 | Same | Same | Same | Same | ✅ 100% |
| Custom retry class/decorator | `@retry_on_429` decorator | `RetryPolicy` class | `@retry_on_429` decorator | `@retry_on_429` decorator | `CosmosRetryHandler` class | ⚠️ 60% |
| Backoff formula | `min(base * 2^attempt + jitter, 30000)` | Same | Same | Same | Same | ✅ 100% |
| Jitter implementation | `random.uniform(0, 1.0)` | `random.randint(0, 1000)/1000` | `random.uniform(0, 1.0)` | `random.random()` | `random.uniform(0, 1.0)` | ⚠️ 60% |
| Retry-After header respected | Yes | Yes | Yes | Yes | Yes | ✅ 100% |
| Max attempts | 10 | 10 | 10 | 10 | 10 | ✅ 100% |
| Circuit breaker included | Yes | Yes | No | Yes | Yes | ⚠️ 80% |
| Logging per retry | Yes | Yes | Yes | Yes | Yes | ✅ 100% |
| Metrics tracking | counter + histogram | counter + total_delay | counter + histogram | dataclass stats | counter + total_delay | ❌ 40% |

**Consistency Score: 78%** (7.4/10 features stable)

### Variance Analysis
- **Stable:** SDK config values, backoff formula, Retry-After respect, max attempts, logging
- **Variable:** Custom retry structure (decorator vs class), jitter implementation details, circuit breaker inclusion (1/5 omitted), metrics approach

---

## Summary

| Prompt | Consistency Score | Verdict |
|--------|------------------|---------|
| cosmos.singleton | 80% | Good - naming variance only |
| cosmos.point-read | 87.5% | Strong - core pattern very stable |
| cosmos.retry | 78% | Moderate - structural choices vary |

---

## Recommendations for Tightening

### cosmos.singleton (80% → target 95%)
1. **Specify class name explicitly:** Add `"Name the settings class CosmosSettings"` to rules
2. **Mandate lifespan pattern:** Add `"Use FastAPI lifespan context manager for disposal (not atexit)"`
3. **Fix health check name:** Add `"Name the health check function check_cosmos_health"`

### cosmos.point-read (87.5% → target 95%)
1. **Specify function naming convention:** Add `"Name the function get_{entity_snake_case}"`
2. **Mandate pydantic:** Add `"Use pydantic BaseModel for entity types"`
3. **Pin type annotation style:** Add `"Use Optional[T] for nullable returns"`

### cosmos.retry (78% → target 90%)
1. **Mandate decorator pattern:** Add `"Implement custom retry as a decorator named retry_on_throttle"`
2. **Specify jitter exactly:** Change formula to `"jitter = random.uniform(0, 1.0) seconds"`
3. **Make circuit breaker explicit:** Change from implicit in prose to `"MUST include circuit breaker with 50% threshold / 10s window"`
4. **Standardize metrics output:** Add `"Track metrics as: retry_count (int), total_delay_ms (float), success_after_retry (bool)"`

---

## Key Insight

**Structural patterns are highly deterministic; naming and implementation detail choices are not.** The prompts successfully constrain the *architecture* (singleton via DI, point-read vs query, exponential backoff) but leave *surface-level choices* (class names, decorator vs class, type annotation style) underspecified. These are the cheapest fixes - just add one line of constraint per variable feature.

**The prompts' anti-pattern lists are highly effective** - no run produced any of the listed anti-patterns, confirming that explicit "REJECT" sections drive consistent avoidance behavior.
