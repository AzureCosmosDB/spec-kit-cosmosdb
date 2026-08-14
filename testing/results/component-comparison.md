# Component-Tier Prompt Comparison (Round 2)

## Test A: cosmos.model

### Structural Invariants (Consistent Across All 3 Runs)
- All produce 3 entities: Organization, User, Document
- All use `dataclass` for entity definitions
- All partition Organization by `/id`, User by `/orgId`
- All include `type` discriminator, `createdAt`, `updatedAt` fields
- All store large content externally (Blob Storage reference)
- All include example JSON documents
- All include container configuration with indexing policies
- All apply bounded arrays (tags)

### Variations
| Aspect | Run 1 | Run 2 | Run 3 |
|--------|-------|-------|-------|
| Document partition key | `/userId` | `/orgId` | `/userId` |
| Enums for roles/plans | No (strings) | No (strings) | Yes (Python Enum) |
| Extra fields on Org | `plan` only | `slug`, `maxUsers` | `ownerUserId` |
| Document blob field name | `content_ref` | `blob_url` | `blob_reference` |
| Container config format | dict of dicts | list of dicts | dict of dicts |
| Composite indexes | Yes (documents) | Yes (documents, users) | Yes (documents, users) |

### Key Divergence: Document Partition Key
- Run 1 & 3: `/userId` - optimizes for "query docs by user" (primary pattern)
- Run 2: `/orgId` - optimizes for "query docs by org"
- The prompt's description says "queried by user AND by org" without prioritizing. This ambiguity causes the main architectural divergence.

### Bugs / Anti-Patterns Found
- **Run 1**: Python `datetime.utcnow().isoformat()` missing "Z" suffix (inconsistent with JSON examples that include it)
- **Run 2**: `excludedPaths` includes `{"path": "/blobUrl/?"}` AND `{"path": "/*"}` - the wildcard already covers blobUrl, so the specific exclude is redundant
- **All runs**: Using `datetime.utcnow()` which is deprecated in Python 3.12+

### Recommendations for Tightening the Prompt
1. **Add `access_patterns` as required input** - the cosmos.model prompt expects it but the test description doesn't explicitly rank query frequency. Add: "Primary access pattern: [most frequent query]"
2. **Mandate partition key for each entity explicitly** or require a decision matrix showing access patterns → partition key selection
3. **Specify Python naming convention** - prompt doesn't say whether JSON output should be camelCase or snake_case, causing mismatch between dataclass fields and example JSON
4. **Add datetime guidance** - specify `datetime.now(timezone.utc)` vs `utcnow()` and whether "Z" suffix is required

---

## Test B: cosmos.repository

### Structural Invariants (Consistent Across All 3 Runs)
- All define 3 custom exceptions (NotFound, Conflict/AlreadyExists, Concurrency)
- All have `OrderRepository` class with injected `ContainerProxy`
- All implement: create, get_by_id (point read), list_by_customer, list_by_status, update_status, delete
- All use point read (not query) for get-by-id
- All use parameterized queries with `@param` syntax
- All pass `partition_key=customer_id` on every operation
- All use ETag-based optimistic concurrency on update_status
- All implement soft delete with `deleted=True` + TTL of 30 days
- All handle 409 on create, 404 on read, 412 on update
- All use `datetime.utcnow().isoformat() + "Z"` for timestamps
- All return `Optional[dict]` / `None` for not-found reads

### Variations
| Aspect | Run 1 | Run 2 | Run 3 |
|--------|-------|-------|-------|
| Method names | `create`, `get_by_id` | `create_order`, `get_order` | `create`, `get_by_id` |
| Entity dataclass | No | Yes (Order dataclass) | No (helper function) |
| ID generation | `uuid4()` raw | `ord-{uuid4().hex[:12]}` | `uuid4()` raw |
| Pagination approach | continuation_token (returned None) | continuation_token (returned None) | OFFSET/LIMIT params |
| list_by_customer return | `tuple[list, Optional[str]]` | `dict` with items+token | `list[dict]` |
| Type filter in queries | No | No | Yes (`c.type = @type`) |
| Unit tests included | No | No | No |

### Bugs / Anti-Patterns Found
- **Run 1 & 2**: Continuation token handling is fake - returns `None` always. The Python SDK uses iterator-based pagination, not explicit token returns in `query_items()`
- **Run 1**: `list_by_customer` redundantly includes `WHERE c.customerId = @customerId` when already scoped by `partition_key=customer_id` - not wrong but query filter is duplicative
- **All runs**: `match_condition="IfMatch"` - the Python SDK actually uses `match_condition` as a kwarg but the type is `MatchConditions` enum, not a string
- **No run includes unit tests** despite the prompt requiring them

### Recommendations for Tightening the Prompt
1. **Specify method naming convention** - `create` vs `create_order` vs `create_item`
2. **Clarify pagination strategy for Python** - SDK-specific (Python uses paged iterator, not continuation tokens in the same way as .NET)
3. **Enforce unit test generation** - prompt says "Unit test file with mocked container" but none produced one. Make it a separate output section with explicit test structure
4. **Specify return types precisely** - `dict` vs typed dataclass vs TypedDict
5. **Add SDK version note** - `match_condition` API differs between SDK versions; prompt should specify `azure-cosmos>=4.x` patterns
6. **Add type discriminator filter requirement** - Run 3 correctly adds `c.type = @type` to prevent reading non-order docs from shared containers

---

## Test C: cosmos.query

### Structural Invariants (Consistent Across All 3 Runs)
- Identical SQL query structure: `SELECT c.orderId, c.status, c.total, c.createdAt FROM c WHERE c.customerId = @customerId ORDER BY c.createdAt DESC OFFSET 0 LIMIT 10`
- All pass `partition_key=customer_id` in query options
- All use `@customerId` as the parameter name
- All set `max_item_count=10`
- All include a composite index requirement: `(customerId ASC, createdAt DESC)`
- All estimate RU cost at 3-6 range
- All wrap in a function taking `ContainerProxy` + `customer_id`
- All return `list[dict]`

### Variations
| Aspect | Run 1 | Run 2 | Run 3 |
|--------|-------|-------|-------|
| Function name | `get_recent_orders` | `find_top_10_recent_orders` | `get_top_recent_orders` |
| Query constant name | `QUERY` | `SQL_QUERY` | `TOP_RECENT_ORDERS_QUERY` |
| Index included paths | 5 paths | 5 paths + excludedPaths | 2 paths only |
| Usage example | No | Yes (commented `__main__`) | No |
| Module docstring detail | Minimal | Detailed | Moderate |

### Bugs / Anti-Patterns Found
- **Run 1 & 2**: Include `/customerId/?` in indexing policy `includedPaths` - unnecessary since the partition key is always indexed automatically
- **Run 1 & 2**: Include `/orderId/?`, `/status/?`, `/total/?` in included paths - these are in SELECT projection, not WHERE/ORDER BY, so indexing them provides no query benefit
- **All runs**: Using both `OFFSET 0 LIMIT 10` AND `max_item_count=10` is redundant - LIMIT in SQL already bounds results; `max_item_count` controls page size of the iterator

### Recommendations for Tightening the Prompt
1. **Clarify indexing guidance** - distinguish between "fields that need indexing for WHERE/ORDER BY" vs "fields in SELECT projection" (projections don't need indexes)
2. **Specify that partition key is auto-indexed** - don't include it in custom indexing policy
3. **Choose one pagination mechanism** - either OFFSET/LIMIT in SQL or SDK-level `max_item_count` + continuation, not both
4. **Add a note about `max_item_count` semantics** - it's a page size hint, not a hard limit; the SQL LIMIT is the actual bound
5. **Query was highly consistent** - this is the most deterministic prompt of the three, likely because the input is very specific and the output is a single query (not a full architecture)

---

## Overall Findings

| Prompt | Consistency Score | Main Risk |
|--------|------------------|-----------|
| cosmos.model | Medium (6/10) | Partition key divergence due to ambiguous access patterns |
| cosmos.repository | High (8/10) | SDK API details wrong (match_condition type, pagination model) |
| cosmos.query | Very High (9/10) | Minor over-indexing; otherwise nearly identical |

### Pattern: Specificity → Determinism
- cosmos.query has the most specific inputs (single intent, single output) → most consistent
- cosmos.model has the most ambiguous inputs (multi-entity, competing access patterns) → most variation
- cosmos.repository is in between - structure is prescribed but SDK details drift

### Top Recommendations Across All Prompts
1. **Add language-specific SDK guidance** (Python `azure-cosmos` 4.x patterns, correct types)
2. **Require explicit ranking of access patterns** (primary vs secondary)
3. **Pin naming conventions** (camelCase JSON, snake_case Python, method naming style)
4. **Add "do not index projection-only fields" to anti-patterns**
5. **Partition key auto-indexing note** in cosmos.query anti-patterns
