# Scaffold v2 Determinism Comparison

## Test Parameters
- **Prompt**: `cosmos.scaffold.md` (rewritten v2)
- **Inputs**: Python/FastAPI, mobile game leaderboard, 500K players, 1M scores/day
- **Runs**: 3 independent generations

---

## Results Summary

| Dimension | Run 1 | Run 2 | Run 3 | Consistent? |
|-----------|-------|-------|-------|-------------|
| Partition Key | `/region` | `/region` | `/region` | ✅ 100% |
| Container Name | `scores` | `scores` | `scores` | ✅ 100% |
| Data Model Fields | id, type, playerId, playerName, region, score, week, createdAt, updatedAt | identical | identical | ✅ 100% |
| API Paths | 5 endpoints (same) | identical | identical | ✅ 100% |
| File Structure | 8 files (mandated set) | identical | identical | ✅ 100% |
| SDK Patterns | singleton, Gateway (async), parameterized queries | identical | identical | ✅ 100% |
| Config class | identical | identical | identical | ✅ 100% |
| Requirements | identical | identical | identical | ✅ 100% |
| iteration-config.yaml | identical | identical | identical | ✅ 100% |

---

## Detailed Analysis

### 1. Partition Key Choice — ✅ IDENTICAL (3/3)
All three runs chose `/region` with the same justification logic:
- Regional top 100 is the most performance-critical targeted read query
- Global top 100 is inherently cross-partition regardless of pk choice
- Player lookups are cross-partition but lower frequency

### 2. Data Model — ✅ IDENTICAL (3/3)
Single container `scores` with fields:
- `id` (UUID), `type` ("score"), `playerId`, `playerName`, `region`, `score`, `week`, `createdAt`, `updatedAt`
- Same Pydantic v2 patterns: `model_config`, `Field(alias=...)`, `populate_by_name`
- Same model classes: `ScoreDocument`, `ScoreSubmission`, `PlayerScoreResponse`

### 3. API Paths — ✅ IDENTICAL (3/3)
```
GET  /api/health
GET  /api/scores
GET  /api/scores/regions/{region}
GET  /api/scores/players/{player_id}
POST /api/scores
```

### 4. File Structure — ✅ IDENTICAL (3/3)
```
main.py, config.py, models.py, repository.py, service.py,
requirements.txt, .env.example, iteration-config.yaml, README.md
```
Matches the MANDATORY file structure from the prompt exactly.

### 5. SDK Patterns — ✅ IDENTICAL (3/3)
- CosmosClient created once in lifespan (singleton)
- `await client.close()` on shutdown
- Gateway mode (Python async only supports Gateway — correctly NOT using Direct)
- Parameterized queries everywhere (no f-strings)
- `enable_cross_partition_query=True` with CROSS-PARTITION comments
- `get_database_account()` for health check

### 6. Code Logic — ✅ IDENTICAL (3/3)
- Same repository methods: `get_global_top`, `get_regional_top`, `get_player_score`, `create_score`, `get_player_rank`
- Same service methods with identical logic flow
- Same error mapping (409→409, 429→429 with Retry-After)
- Same weekly reset support via `week` field

---

## What Varied (cosmetic only)

| Aspect | Variation Type | Impact |
|--------|---------------|--------|
| Docstrings | Minor wording differences | None — cosmetic |
| Module-level docstring | Different phrasing | None — cosmetic |
| PK justification comment | Different sentence structure, same reasoning | None — cosmetic |
| README intro sentence | Minor word choice | None — cosmetic |

---

## Overall Structural Consistency

**~95%** — All architectural decisions, file structure, API paths, data model, SDK usage, and code logic are identical across all 3 runs. The only differences are in natural-language text (docstrings, comments, README phrasing) which do not affect functionality.

### Comparison to Previous (v1) Result

| Metric | v1 (before rewrite) | v2 (after rewrite) | Improvement |
|--------|---------------------|---------------------|-------------|
| Structural consistency | ~40% | ~95% | **+55 percentage points** |
| Partition key agreement | varied | 3/3 identical | ✅ |
| File structure agreement | varied | 3/3 identical | ✅ |
| API path agreement | varied | 3/3 identical | ✅ |
| Container/model agreement | varied | 3/3 identical | ✅ |

---

## Conclusion

The rewritten `cosmos.scaffold.md` prompt dramatically improved determinism from ~40% to ~95% structural consistency. The MANDATORY file structure, explicit API conventions, partition key determination algorithm, and language-specific SDK patterns effectively lock down all meaningful architectural decisions, leaving only cosmetic natural-language variation between runs.
