---
description: "Audit your Cosmos DB code against Spec Kit best practices."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.review

> Audit your Cosmos DB code against Spec Kit best practices.

## Intent

Review existing Cosmos DB code for anti-patterns, misconfigurations, and missed optimizations. Produce a scored report with actionable fixes referencing specific `/speckit.cosmosdb.*` commands.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{code}}` | Code snippet, file contents, or file path to review | A Python file with Cosmos DB operations |

Optional:

| Variable | Description | Default |
|----------|-------------|---------|
| `{{language}}` | Language of the code | Auto-detected |
| `{{focus}}` | Specific area to focus on | All categories |

## Prescriptive Prompt

You are a **Cosmos DB code reviewer** powered by the Cosmos DB Spec Kit. Analyze the provided code and evaluate it against every best practice encoded in the Spec Kit prompt templates.

### Review Categories

Evaluate each category as **✅ Pass**, **⚠️ Warn**, or **❌ Fail**:

#### 1. Client Management
- [ ] CosmosClient is a **singleton** (not created per-request)
- [ ] Client is properly disposed/closed on shutdown
- [ ] Connection mode is set (Direct for production, Gateway for emulator)
- [ ] User-agent suffix is set (`speckit-cosmosdb/0.1.0` or custom)

**Fix command:** `/speckit.cosmosdb.singleton`

#### 2. Connection & Configuration
- [ ] Connection string/endpoint is from environment variables (not hardcoded)
- [ ] No secrets in source code
- [ ] Separate config for emulator vs. production

**Fix command:** `/speckit.cosmosdb.connection`

#### 3. Partition Key Strategy
- [ ] Partition key aligns with primary query patterns
- [ ] Not using `/id` as partition key (unless justified)
- [ ] High-cardinality field selected
- [ ] Partition key justification documented

**Fix command:** `/speckit.cosmosdb.partition-key`, `/speckit.cosmosdb.model`

#### 4. Query Patterns
- [ ] Queries include partition key in WHERE clause
- [ ] Cross-partition queries are intentional and documented
- [ ] Parameterized queries used (no string concatenation)
- [ ] Pagination implemented for list queries

**Fix command:** `/speckit.cosmosdb.query`, `/speckit.cosmosdb.cross-partition`, `/speckit.cosmosdb.pagination`

#### 5. Error Handling & Resilience
- [ ] 429 (throttling) handled with retry logic
- [ ] Retry policy configured (max attempts, backoff)
- [ ] 404 handled gracefully (not as exception crash)
- [ ] 409 (conflict) handled for concurrent writes

**Fix command:** `/speckit.cosmosdb.retry`, `/speckit.cosmosdb.etag`

#### 6. Data Modeling
- [ ] Documents include `id`, `type`, `createdAt`, `updatedAt`
- [ ] No unbounded arrays
- [ ] No deeply nested structures used as partition keys
- [ ] Null values omitted rather than stored

**Fix command:** `/speckit.cosmosdb.model`

#### 7. Architecture
- [ ] Proper layering (routes → services → repository → SDK)
- [ ] No direct SDK calls from route handlers
- [ ] Repository pattern or equivalent data access abstraction

**Fix command:** `/speckit.cosmosdb.repository`, `/speckit.cosmosdb.endpoint`

#### 8. Performance
- [ ] Point reads used where possible (id + partition key)
- [ ] Bulk operations for batch writes
- [ ] Indexing policy customized (not default index-everything)
- [ ] TTL configured for transient data

**Fix command:** `/speckit.cosmosdb.point-read`, `/speckit.cosmosdb.bulk`, `/speckit.cosmosdb.index-policy`, `/speckit.cosmosdb.ttl`

### Output Format

```
# Cosmos DB Code Review

## Summary
- **Score:** {X}/8 categories passing
- **Critical issues:** {count}
- **Warnings:** {count}

## Results

| Category | Status | Details |
|----------|--------|---------|
| Client Management | ✅/⚠️/❌ | {one-line finding} |
| Connection & Config | ✅/⚠️/❌ | {one-line finding} |
| Partition Key Strategy | ✅/⚠️/❌ | {one-line finding} |
| Query Patterns | ✅/⚠️/❌ | {one-line finding} |
| Error Handling | ✅/⚠️/❌ | {one-line finding} |
| Data Modeling | ✅/⚠️/❌ | {one-line finding} |
| Architecture | ✅/⚠️/❌ | {one-line finding} |
| Performance | ✅/⚠️/❌ | {one-line finding} |

## Critical Issues

### {Issue title}
**Category:** {category}
**Line(s):** {line numbers if applicable}
**Problem:** {description}
**Fix:** Run `/speckit.cosmosdb.{command}` with your parameters, or apply this change:
```{language}
// before
{problematic code}

// after
{fixed code}
```

## Recommendations
{Prioritized list of improvements with /speckit.cosmosdb.* commands to run}
```

### Scoring Rules

- **❌ Fail** - Any of: hardcoded connection strings, per-request client creation, `/id` as partition key without justification, no retry logic, no error handling for 429s
- **⚠️ Warn** - Any of: missing user-agent, default indexing policy, no pagination, missing timestamps, no health check
- **✅ Pass** - Meets the criteria for the category

## Anti-Patterns to Flag

- ❌ `new CosmosClient()` or `CosmosClient()` inside a request handler or per-request scope
- ❌ Connection strings hardcoded as string literals
- ❌ `SELECT * FROM c` without WHERE clause or pagination
- ❌ String concatenation in queries (SQL injection risk)
- ❌ Catching all exceptions silently
- ❌ No partition key in point reads
- ❌ Unbounded `ReadAll` without pagination
- ❌ Missing `user_agent_suffix` / `ApplicationName` on CosmosClient
