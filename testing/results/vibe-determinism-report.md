# Vibe Determinism Report

> Empirical testing of `/cosmos.vibe` with vague/ambiguous inputs across 3 scenarios × 3 runs each.

## Test 1: Pet Adoption Platform

**Input:** "I want to build a pet adoption platform where shelters can list animals and people can browse and apply to adopt them"

| Dimension | Run 1 | Run 2 | Run 3 | Consistent? |
|-----------|-------|-------|-------|-------------|
| **Scaffold** | `scaffold-social` | `scaffold-ecommerce` | `scaffold-social` | ❌ 2/3 |
| **Language** | Python (FastAPI) | Python (FastAPI) | Python (FastAPI) | ✅ 3/3 |
| **Scale** | ~100K users | ~100K users | ~100K users | ✅ 3/3 |
| **Primary query** | Animals by shelter | Animals by category | Animals by shelter | ❌ 2/3 |
| **Partition key (animals)** | `/shelterId` | `/category` | `/shelterId` | ❌ 2/3 |
| **Container list** | shelters, animals, applications | shelters, animals, applications | shelters, animals, applications | ✅ 3/3 |
| **File structure** | app/{main,models,routers,config} | app/{main,models,routers,config} | app/{main,models,routers,config} | ✅ 3/3 |

**Overall consistency: ~71%** (5/7 dimensions consistent)

### Key Finding
The scaffold match split between `social` and `ecommerce` - both are defensible interpretations. The partition key divergence (`/shelterId` vs `/category`) is a **direct consequence** of the scaffold mismatch, since each scaffold implies different primary access patterns. Language, scale, container list, and file structure were stable.

---

## Test 2: Orders & Inventory Tracker

**Input:** "I need something to track orders and inventory for my business"

| Dimension | Run 1 | Run 2 | Run 3 | Consistent? |
|-----------|-------|-------|-------|-------------|
| **Scaffold** | `scaffold-ecommerce` | `scaffold-inventory` | `scaffold-ecommerce` | ❌ 2/3 |
| **Language** | Python (FastAPI) | Python (FastAPI) | Python (FastAPI) | ✅ 3/3 |
| **Scale** | ~1K users | ~1K users | ~1K users | ✅ 3/3 |
| **Primary query** | Orders by customer | Stock by SKU | Orders by status | ❌ All different |
| **Partition key (orders)** | `/customerId` | `/productId` | `/status` | ❌ All different |
| **Container list** | orders, products, inventory | inventory, orders, warehouses | orders, products, inventory | ❌ 2/3 |
| **File structure** | app/{main,models,routers,config} | app/{main,models,routers,config} | app/{main,models,routers,config} | ✅ 3/3 |

**Overall consistency: ~43%** (3/7 dimensions consistent)

### Key Finding
This is the worst-performing test. The input has **dual scaffold triggers** ("orders" → ecommerce, "inventory" → inventory) with no signal about which is primary. The partition key diverged across ALL THREE runs - `/customerId`, `/productId`, and `/status` - meaning the most architecturally critical decision was completely non-deterministic. Note: `/status` is a particularly bad partition key (low cardinality, hot partition risk), showing that vibe-inferred partition keys can be **actively harmful**.

---

## Test 3: Very Vague ("app with a database")

**Input:** "I want to build an app with a database"

| Dimension | Run 1 | Run 2 | Run 3 | Consistent? |
|-----------|-------|-------|-------|-------------|
| **Scaffold** | ❌ None (stopped) | ❌ None (stopped) | ❌ None (stopped) | ✅ 3/3 |
| **Language** | Python (FastAPI) | Python (FastAPI) | Python (FastAPI) | ✅ 3/3 |
| **Scale** | ~100K default | ~100K default | ~100K default | ✅ 3/3 |
| **Action taken** | Asked clarifying Q | Asked clarifying Q | Asked clarifying Q | ✅ 3/3 |
| **Question asked** | "What do users see first?" | "What data + access pattern?" | "Read-heavy or write-heavy?" | ❌ All different |
| **Code generated** | None | None | None | ✅ 3/3 |

**Overall consistency: ~83%** (5/6 dimensions consistent)

### Key Finding
The vibe prompt's **guardrail worked perfectly** - all 3 runs correctly identified this as too ambiguous and stopped. However, the specific clarifying question varied each time, which could lead users down different paths in subsequent interactions. The safeguard behavior itself was 100% deterministic.

---

## Comparative Analysis

| Scenario | Consistency | Scaffold Match | Partition Key Match | Code Generated |
|----------|------------|----------------|--------------------|----|
| Test 1: Pet adoption (vague) | **71%** | 2/3 | 2/3 | Yes (all 3) |
| Test 2: Orders+inventory (ambiguous) | **43%** | 2/3 | 0/3 ⚠️ | Yes (all 3) |
| Test 3: App+database (very vague) | **83%** | N/A (stopped) | N/A | No (correctly) |

### vs. Scaffold v1 and v2 (explicit inputs)

| Input Type | v1 Consistency | v2 Consistency | Vibe Consistency |
|------------|---------------|----------------|------------------|
| Explicit (scaffold + queries provided) | ~40% | ~95% | N/A |
| Vague (one clear domain) | N/A | N/A | **~71%** |
| Ambiguous (dual-domain) | N/A | N/A | **~43%** |
| Too vague (no domain) | N/A | N/A | **~83%** (stops correctly) |

**Key observations:**
1. Vibe with vague-but-directional input (~71%) falls **between** v1 and v2 explicit inputs
2. Vibe with ambiguous input (~43%) is **worse than v1** - the scaffold selection ambiguity cascades into partition key chaos
3. Vibe's guardrail for "too vague" is the most reliable behavior (~83%), but the follow-up question varies
4. **The partition key is the most volatile dimension** - it's the most architecturally important decision and the least deterministic one

---

## Conclusion

### Is `/cosmos.vibe` deterministic enough to be a generator?

**No.** `/cosmos.vibe` should be **triage-only**, not a generator.

**Evidence:**
1. **Partition key non-determinism is disqualifying.** The partition key is the single most consequential Cosmos DB decision (it cannot be changed without a container migration). In Test 2, all 3 runs produced different partition keys - including one (`/status`) that would cause production hot-partition issues. Generating code with a wrong partition key is worse than generating no code at all.

2. **Scaffold ambiguity cascades.** When the scaffold match is uncertain, every downstream decision (queries, partition keys, container structure, model fields) inherits that uncertainty. The vibe prompt has no mechanism to resolve ties between equally-weighted scaffold triggers.

3. **The guardrail works, but inconsistently.** The "stop and ask" behavior for very vague inputs is good, but the question varies, meaning subsequent generations would diverge anyway.

### Recommended Architecture

```
/cosmos.vibe (triage-only)
    ↓ Analyzes intent, shows plan
    ↓ Asks clarifying question if ambiguous
    ↓ Outputs: matched scaffold + inferred parameters
    ↓
/cosmos.scaffold-{type} (generator)
    ↓ Takes EXPLICIT inputs from vibe's triage
    ↓ Generates deterministic code (v2: 95%)
```

**Action items:**
1. Modify `/cosmos.vibe` to output a **recommended command** instead of generating code directly
2. Add a **scaffold confidence score** - if <80% confidence, require user confirmation before proceeding
3. Add **partition key validation rules** (reject low-cardinality keys like `/status`, `/type`)
4. Consider requiring the user to confirm the Intent Analysis plan before generation proceeds (currently it says "Proceeding with generation..." without waiting)
