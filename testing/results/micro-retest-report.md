# Micro Prompt Re-Test Report: Tightened Versions

**Date**: 2026-07-26  
**Inputs**: `language=python`, `framework=FastAPI`  
**Method**: 3 generations per prompt, structural comparison

---

## Test Results

### cosmos.singleton.md (Tightened)

| Dimension | Run 1 | Run 2 | Run 3 | Consistent? |
|-----------|-------|-------|-------|-------------|
| File name | `cosmos_client.py` | `cosmos_client.py` | `cosmos_client.py` | ✅ |
| Function name | `get_cosmos_client()` | `get_cosmos_client()` | `get_cosmos_client()` | ✅ |
| Settings class | `CosmosSettings` | `CosmosSettings` | `CosmosSettings` | ✅ |
| Health check name | `check_cosmos_health` | `check_cosmos_health` | `check_cosmos_health` | ✅ |
| Pattern | Module-level singleton | Module-level singleton | Module-level singleton | ✅ |
| Disposal | FastAPI lifespan | FastAPI lifespan | FastAPI lifespan | ✅ |
| Type hints | Full | Full | Full | ✅ |
| Env vars | COSMOS_ENDPOINT, COSMOS_KEY, COSMOS_DATABASE | Same | Same | ✅ |

**Consistency Score: 100% (8/8 dimensions)**  
**Previous Score: 80%**  
**Improvement: +20 percentage points**

---

### cosmos.retry.md (Tightened)

| Dimension | Run 1 | Run 2 | Run 3 | Consistent? |
|-----------|-------|-------|-------|-------------|
| File name | `retry.py` | `retry.py` | `retry.py` | ✅ |
| Pattern | `@cosmos_retry` decorator | `@cosmos_retry` decorator | `@cosmos_retry` decorator | ✅ |
| Default retries | 3 | 3 | 3 | ✅ |
| Jitter | `random.uniform(0, 1.0)` | `random.uniform(0, 1.0)` | `random.uniform(0, 1.0)` | ✅ |
| Logging | stdlib `logging` | stdlib `logging` | stdlib `logging` | ✅ |
| Exception type | `CosmosHttpResponseError` 429 | Same | Same | ✅ |
| Circuit breaker | 50% / 10s window | 50% / 10s window | 50% / 10s window | ✅ |
| Metrics | retry_count, total_delay_ms, success_after_retry | Same | Same | ✅ |

**Consistency Score: 100% (8/8 dimensions)**  
**Previous Score: 78%**  
**Improvement: +22 percentage points**

---

### cosmos.point-read.md (Tightened)

| Dimension | Run 1 | Run 2 | Run 3 | Consistent? |
|-----------|-------|-------|-------|-------------|
| Function name | `get_order_by_id()` | `get_order_by_id()` | `get_order_by_id()` | ✅ |
| Return type | `Optional[dict]` | `Optional[dict]` | `Optional[dict]` | ✅ |
| 404 handling | Return `None` | Return `None` | Return `None` | ✅ |
| PK parameter | Explicit `partition_key` param | Same | Same | ✅ |
| Model | pydantic `BaseModel` | pydantic `BaseModel` | pydantic `BaseModel` | ✅ |
| Type annotation | `Optional[T]` style | `Optional[T]` style | `Optional[T]` style | ✅ |
| RU logging | stdlib `logging` | stdlib `logging` | stdlib `logging` | ✅ |
| Comparison comment | Query vs point-read | Query vs point-read | Query vs point-read | ✅ |

**Consistency Score: 100% (8/8 dimensions)**  
**Previous Score: 87.5%**  
**Improvement: +12.5 percentage points**

---

## Summary

| Prompt | Before Tightening | After Tightening | Delta |
|--------|-------------------|------------------|-------|
| cosmos.singleton | 80% | 100% | **+20%** |
| cosmos.retry | 78% | 100% | **+22%** |
| cosmos.point-read | 87.5% | 100% | **+12.5%** |
| **Average** | **81.8%** | **100%** | **+18.2%** |

## Analysis

### What Worked

The explicit naming constraints dramatically improved determinism:

1. **Mandatory names** (`MUST be named X`) eliminated all naming variation - previously the biggest source of inconsistency
2. **Explicit pattern choices** (e.g., "module-level singleton, NOT class-based `__new__`") removed ambiguity about implementation approach
3. **Specific library constraints** (e.g., "stdlib `logging`, NOT structlog") prevented random library selection
4. **Anti-patterns listing specific alternatives** (e.g., "NOT `T | None` union syntax") caught edge-case style drift
5. **Framework-specific disposal** (e.g., "FastAPI lifespan, NOT atexit") locked in lifecycle management

### Conclusion

Adding explicit naming and structural constraints to micro prompts achieves **perfect structural determinism** across multiple generations. The key insight: LLMs respect `MUST` constraints on names/patterns far more reliably than vague guidance like "use a singleton pattern." Every dimension of variation should have an explicit, named constraint.

### Recommendation

Apply the same tightening pattern to remaining micro prompts:
- `cosmos.upsert.md` - constrain function name, error handling pattern
- `cosmos.transaction.md` - constrain batch builder pattern
- `cosmos.pagination.md` - constrain cursor encoding scheme
