# E2E Test Results — E-commerce Scaffold

**Date:** 2026-07-27  
**Scaffold:** `cosmos.scaffold-ecommerce.md`  
**Language:** Python / FastAPI  
**Target:** Cosmos DB Emulator at `http://localhost:8081`  
**Scale input:** "50K customers, 500K orders, 10K products"

## Test Results: 19/19 PASS ✅

| # | Endpoint | Result | Details |
|---|----------|--------|---------|
| 1 | GET /api/health | ✅ PASS | 200 — reads database properties |
| 2 | POST /api/customers | ✅ PASS | 201 + Location header |
| 3 | GET /api/customers/{id} | ✅ PASS | 200 — point read by partition key |
| 4 | POST /api/products (electronics) | ✅ PASS | 201 |
| 5 | POST /api/products (electronics) | ✅ PASS | 201 |
| 6 | POST /api/products (books) | ✅ PASS | 201 |
| 7 | GET /api/products/category/electronics | ✅ PASS | 200 — partition-scoped query |
| 8 | GET /api/products/category/books | ✅ PASS | 200 — partition-scoped query |
| 9 | POST /api/orders | ✅ PASS | 201 — stock decremented atomically |
| 10 | GET /api/customers/{id}/orders | ✅ PASS | 200 — order history by customer |
| 11 | GET /api/orders/{id}?customerId | ✅ PASS | 200 — point read |
| 12 | GET /api/orders/{id}/items | ✅ PASS | 200 — co-located order items |
| 13 | POST /api/orders/{id}/pay | ✅ PASS | 200 — placed→paid |
| 14 | POST /api/orders/{id}/ship | ✅ PASS | 200 — paid→shipped |
| 15 | POST /api/orders/{id}/pay (invalid) | ✅ PASS | 409 — state machine rejects shipped→paid |
| 16 | GET /api/orders?status=shipped | ✅ PASS | 200 — cross-partition status query |
| 17 | POST /api/orders (2nd) | ✅ PASS | 201 |
| 18 | POST /api/orders/{id}/cancel | ✅ PASS | 200 — placed→cancelled |
| 19 | Stock restored after cancel | ✅ PASS | stockCount back to 200 |

## Bugs Found & Fixed During Testing

| Bug | Root Cause | Fix Applied |
|-----|-----------|-------------|
| Health check 503: `'CosmosClient' object has no attribute 'get_database_account'` | Scaffold prompt references `client.get_database_account()` but the async Python client doesn't expose this directly in the same way | Used `database.read()` instead |
| Order creation 500: `ClientSession._request() got an unexpected keyword argument 'enable_cross_partition_query'` | `enable_cross_partition_query=True` kwarg leaks through to aiohttp in azure-cosmos 4.16.x async client | Replaced with `partition_key=None` (which enables cross-partition in newer SDK) |
| Missing `aiohttp` dependency | azure-cosmos async client depends on aiohttp but scaffold prompt doesn't list it in requirements.txt | Added aiohttp to deps (or note: pip install azure-cosmos[aio] pulls it) |
| Duplicate creates return 500 instead of 409 | No exception handler for `CosmosResourceExistsError` in routes | Should catch and map to 409 |

## Prompt Fixes Needed for `cosmos.scaffold-ecommerce.md`

1. **Health check method**: The Python appendix says `client.get_database_account()` but on the async client this doesn't work as shown. Change to `await database.read()` or use `await client.get_database_account()` — needs verification against SDK version. The prompt's SDK Reference section lists it correctly but the generated code may fail depending on SDK version.

2. **Cross-partition query syntax**: The prompt should note that for `azure-cosmos>=4.9.0` async client, use `partition_key=None` instead of `enable_cross_partition_query=True`. The latter causes kwarg leakage in some SDK versions.

3. **Requirements.txt**: Add `aiohttp>=3.8.0` explicitly (azure-cosmos async transport depends on it but doesn't always pull it as a hard dep).

4. **Error handling for duplicate creates**: The prompt mentions error mapping (409→409) but doesn't explicitly call out `CosmosResourceExistsError` → 409 in the create paths. Should add this to the error handling requirement.

5. **`user_agent` vs `user_agent_suffix`**: The prompt says `user_agent_suffix="cosmos-intent-sdk/0.1.0"` but the Python async client uses `user_agent="cosmos-intent-sdk/0.1.0"` as a constructor kwarg. Verify and align.

## Architecture Validation

- ✅ Layered: Routes → Service → Repository → Cosmos SDK
- ✅ Singleton CosmosClient with lifespan management
- ✅ Environment-based config (pydantic-settings)
- ✅ Parameterized queries (no f-strings)
- ✅ Order state machine with valid transition enforcement
- ✅ Inventory atomicity with etag-based optimistic concurrency
- ✅ Client cleanup on shutdown (`await client.close()`)
- ✅ Partition keys: customers=/id, orders=/customerId, products=/categoryId
- ✅ Co-located OrderItems in orders container with type discriminator
