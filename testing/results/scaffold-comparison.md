# Scaffold Prompt Empirical Comparison

## Test Parameters
- **Prompt**: `cosmos.scaffold.md`
- **Language**: Python / FastAPI
- **Use case**: Mobile game leaderboard (500K players, 1M scores/day)
- **Runs**: 3

---

## 1. Partition Key Choices

| Container | Run 1 | Run 2 | Run 3 |
|-----------|-------|-------|-------|
| Scores | `/player_id` | `/region` | `/region_week` (composite string) |
| Players | `/region` | `/region` | `/player_id` |
| Global Rankings | N/A | N/A | `/rank_bucket` (materialized view) |

**Verdict: HIGH VARIANCE.** The prompt does NOT produce deterministic partition key decisions. Run 1 partitions scores by player (good for "my scores" queries), Run 2 by region, Run 3 uses a synthetic composite key. This is the single biggest architectural decision and it varies every time.

---

## 2. Data Model Structure

| Aspect | Run 1 | Run 2 | Run 3 |
|--------|-------|-------|-------|
| Containers | 2 (scores, players) | 2 (scores, players) | 3 (leaderboard, players, global_rankings) |
| Score fields | score, game_mode, week_number, year | value, game_mode, week, year | score, game_mode, week, year, region_week |
| Player fields | total_score, weekly_score, games_played | lifetime_score, current_week_score | all_time_score, weekly_high, games_count |
| Discriminator (`type`) | ✅ | ✅ | ✅ |
| `_etag`/`_ts` | ✅ | ✅ | ✅ |

**Verdict: MODERATE VARIANCE.** All runs include discriminator and system fields (prompt compliance). But field naming and container count differ. Run 3 introduces a materialized view pattern the others lack.

---

## 3. API Endpoint Paths

| Action | Run 1 | Run 2 | Run 3 |
|--------|-------|-------|-------|
| Submit score | `POST /api/leaderboard/scores` | `POST /v1/scores` | `POST /api/scores` |
| Global ranking | `GET /api/leaderboard/rankings/global` | `GET /v1/leaderboard/global` | `GET /api/rankings/global` |
| Regional ranking | `GET /api/leaderboard/rankings/regional/{region}` | `GET /v1/leaderboard/{region}` | `GET /api/rankings/{region}` |
| Weekly reset | `POST /api/leaderboard/weekly-reset` | `POST /v1/admin/weekly-reset` | Not exposed (implicit via partition) |
| Health | `GET /health` | `GET /health` | `GET /healthz` |

**Verdict: HIGH VARIANCE.** No consistent URL scheme. Versioning strategy differs (none vs `/v1`). Health endpoint naming inconsistent.

---

## 4. SDK Patterns

| Pattern | Run 1 | Run 2 | Run 3 |
|---------|-------|-------|-------|
| Singleton | Global `_client` variable | Global `_cosmos_client` variable | Class-based singleton (`__new__`) |
| Retry config | `connection_retry_policy` dict (incorrect API) | ❌ Not configured | Config attributes defined but not passed to client |
| Connection mode | Not passed to client | Not passed to client | Not passed to client |
| Health check | `client.read_account()` | `client.read_account()` | `cosmos.client.read_account()` |
| Shutdown cleanup | ✅ `client.close()` | ❌ Missing | ✅ `cosmos.close()` |

**Verdict: CRITICAL FINDING.** The prompt specifies `ConnectionMode = Direct` and retry config, but the Python SDK equivalent (`connection_policy`) was NOT correctly implemented in ANY run. Run 1 uses a made-up parameter. Run 2 skips it entirely. Run 3 defines config values but never passes them. This is a **prompt gap** - the prescriptive instructions are C#-centric and don't translate to Python SDK.

---

## 5. Indexing Policy

| Run | Indexing Policy Defined? |
|-----|-------------------------|
| 1 | ❌ No infrastructure/Bicep files generated |
| 2 | ❌ No infrastructure files |
| 3 | ❌ No infrastructure files |

**Verdict: PROMPT NON-COMPLIANCE.** The prompt specifies an `infrastructure/` directory with Bicep templates, but none of the runs produced it. The prompt's output structure section is treated as optional.

---

## 6. Code Organization

| Aspect | Run 1 | Run 2 | Run 3 |
|--------|-------|-------|-------|
| File structure | `src/config/`, `src/models/`, `src/repositories/`, `src/services/`, `src/handlers/`, `src/middleware/` | Flat: `src/config.py`, `src/models.py`, `src/repository.py`, `src/service.py`, `src/main.py` | Flat: `src/config.py`, `src/cosmos.py`, `src/models.py`, `src/repository.py`, `src/service.py`, `src/main.py` |
| Layering | Full clean architecture | Simplified 3-layer | 3-layer + connection class |
| Tests | ❌ Not generated | ❌ Not generated | ❌ Not generated |

**Verdict: MODERATE VARIANCE.** Run 1 follows the prescribed directory structure most closely. Runs 2-3 use a pragmatic flat layout. No run generated tests despite the prompt requiring them.

---

## 7. Bugs & Anti-Patterns

### Run 1
- ⚠️ `connection_retry_policy` is not a valid parameter for the async CosmosClient - will cause TypeError
- ⚠️ `weekly_reset()` loads ALL players (up to 10K) and updates one-by-one - O(n) writes, no batching
- ⚠️ Missing `from fastapi.responses import JSONResponse` in main.py (used in health fallback)

### Run 2
- ⚠️ No retry configuration at all - violates prompt requirements
- ⚠️ f-string in query (`SELECT TOP {limit}`) - SQL injection risk (Cosmos parameterizes differently than SQL but still poor practice)
- ⚠️ No client shutdown/cleanup

### Run 3
- ⚠️ `global_rankings` container assumes change feed processor exists but doesn't implement it - data would be empty
- ⚠️ Retry/connection mode config defined but never wired to CosmosClient constructor
- ✅ Best partition key strategy of the three (regional+weekly avoids cross-partition for the hottest query)

---

## Summary & Prompt Improvement Recommendations

1. **Partition key guidance is too vague** - the prompt says "align with most common query pattern" but different interpretations produce radically different architectures. Add explicit examples for common use cases or require the model to state the primary query pattern before choosing.

2. **Language-specific SDK details are missing** - retry config instructions are C#-specific (`MaxRetryAttemptsOnRateLimitedRequests`). Python SDK uses different parameters. The prompt needs per-language SDK appendices.

3. **Output compliance is weak** - infrastructure files, tests, and README were specified but never generated. The prompt should either enforce "generate ALL listed files" more strongly or reduce the required output set.

4. **Weekly reset pattern is under-specified** - each run invented a different (suboptimal) approach. The prompt should prescribe change feed or scheduled bulk operations for this scale.

5. **Consistency score**: ~40% structural consistency across runs. The prompt produces valid-looking code each time but with fundamentally different architectural decisions that would be incompatible in production.
