# E2E Test Results - cosmos.scaffold.md

**Date:** 2026-07-26  
**Emulator:** Azure Cosmos DB vnext emulator (HTTP mode, localhost:8081)  
**SDK:** azure-cosmos 4.9.0 (Python)  
**Framework:** FastAPI + uvicorn

## Did the app start successfully?

**YES** - after fixing 2 bugs (see below).

## Endpoint Results

| Endpoint | Method | Result |
|----------|--------|--------|
| `/health` | GET | ✅ PASS |
| `/users` | POST | ✅ PASS |
| `/users/{id}` | GET | ✅ PASS |
| `/users` | GET | ✅ PASS |
| `/users/{id}/tasks` | POST | ✅ PASS |
| `/users/{id}/tasks` | GET | ✅ PASS |
| `/users/{id}/tasks/{id}` | GET | ✅ PASS |
| `/users/{id}/tasks/{id}` | PATCH | ✅ PASS |
| `/users/{id}/tasks/{id}` | DELETE | ✅ PASS (204) |

All CRUD operations verified against live Azure Cosmos DB emulator.

## Bugs Found (required fixes before app would start)

### Bug 1: `azure-cosmos` SDK version incompatibility
- **Problem:** The prompt's architecture suggests `client.ReadAccountAsync()` (C# style). The Python equivalent in `azure-cosmos==4.5.1` was `client.read_account()` but that doesn't exist - it's `client.get_database_account()` in 4.9.0.
- **Fix:** Changed health check to `client.get_database_account()`.
- **Prompt gap:** The scaffold prompt is language-agnostic but uses C#-style method names. It should specify the correct SDK method per language.

### Bug 2: Pydantic model required field `user_id` on User
- **Problem:** `User` model had `user_id: str` as required, but in `create_user()` the code sets `user.user_id = user.id` AFTER model instantiation. Pydantic v2 validates on construction, so this fails.
- **Fix:** Changed `user_id` to have a default value (`user_id: str = ""`), then set it post-creation.
- **Prompt gap:** The scaffold prompt says "include partition key in model" but doesn't address the bootstrapping problem where partition key = id and both are auto-generated.

### Bug 3: SDK 4.5.1 double-slash path issue with vnext emulator
- **Problem:** `azure-cosmos==4.5.1` generates `//dbs/todo_app/` paths that the vnext emulator rejects.
- **Fix:** Upgraded to `azure-cosmos==4.9.0`.
- **Prompt gap:** The prompt should specify minimum SDK versions or note emulator compatibility.

## Azure Cosmos DB Errors

- **400 "Invalid path or method"** - double-slash issue with older SDK + vnext emulator (Bug 3)
- No RU/throttling errors, no partition key errors, no other Cosmos-specific issues.

## Recommendations for Prompt Improvement

1. **Add language-specific SDK method references** - The health check guidance uses C# method names. Add a note: "For Python: `client.get_database_account()`"
2. **Address partition key bootstrapping** - When partition key = auto-generated ID, the model needs a default value or a factory pattern. The prompt should include a note about this pattern.
3. **Specify minimum SDK versions** - Add: "Use `azure-cosmos>=4.7.0` for Python" to avoid emulator compatibility bugs.
4. **Add a "common pitfalls" section per language** - Pydantic v2 validation-on-construction is a Python-specific gotcha that the prompt doesn't address.
5. **The `offer_throughput` parameter** - Works on the emulator but may need `ThroughputProperties` for serverless accounts. Prompt should note this.
