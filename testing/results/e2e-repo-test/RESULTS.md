# E2E Repository Prompt Test Results

**Date**: 2026-07-26  
**Prompt**: `prompts/component/cosmos.repository.md`  
**Target**: Cosmos DB Emulator (localhost:8081)  
**Language**: Python (azure-cosmos 4.9+)

## Results

| Operation | Status |
|-----------|--------|
| Create product (×3) | ✅ PASS |
| Read by ID (point read) | ✅ PASS |
| List by category | ✅ PASS |
| Update stock (with ETag) | ✅ PASS |
| Delete | ✅ PASS |
| Verify delete | ✅ PASS |
| Search by name (cross-partition) | ✅ PASS |

**Overall: 9/9 PASS**

## Observations

1. **Prompt is effective** - following its prescriptive patterns produced a working repository on first attempt.
2. **Point read pattern** works correctly with `read_item(item=id, partition_key=pk)`.
3. **ETag-based optimistic concurrency** on `update_stock` worked as expected with `if_match`.
4. **Parameterized queries** with partition key scoping worked for `list_by_category`.
5. **Cross-partition query** with `enable_cross_partition_query=True` worked for name search.

## Prompt Gaps / Improvement Suggestions

1. **Python not explicitly covered** - The prompt references TypeScript (`createItem`) and C# (`CreateItemAsync`) method names but not Python SDK equivalents (`create_item`, `read_item`, etc.). Add Python examples.
2. **Exception class names are language-specific** - Prompt says `CosmosException` but Python SDK uses `CosmosResourceExistsError`, `CosmosResourceNotFoundError`, `CosmosAccessConditionFailedError`. A language-mapping table would help.
3. **Soft delete vs hard delete** - Prompt prefers soft delete but doesn't give enough guidance for when hard delete is acceptable. Our test used hard delete successfully.
4. **No guidance on `id` field** - Cosmos requires an `id` field. The prompt doesn't mention that the entity needs `id` mapped from a domain identifier (we set `id = productId`). This is a common source of bugs.
5. **Pagination** - Prompt mentions "continuation token support" but doesn't specify the pattern. Python SDK uses iterator-based pagination, not explicit tokens in the same way as JS/C#.

## No Failures

No code changes were needed. The prompt's anti-patterns list effectively guided correct implementation choices.
