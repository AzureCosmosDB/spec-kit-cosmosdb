---
description: "Generate a complete Azure Cosmos DB event analytics pipeline with deterministic, production-ready architecture."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.scaffold-analytics

> Generate a complete Azure Cosmos DB event analytics pipeline with deterministic, production-ready architecture.

## Intent

Scaffold a full event analytics application that uses Azure Cosmos DB as its primary data store with high-volume ingestion and pre-computed rollups. The output must be structurally identical across runs given the same inputs.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{app_description}}` | What the application does | "An event analytics pipeline API" |
| `{{language}}` | Target language/framework | "python", "dotnet", "java", "node" |
| `{{entities}}` | Core domain entities (pre-set) | "Events, Sessions, Users, Aggregations" |
| `{{primary_queries}}` | **The 3-5 most frequent read queries** | "Get events for a session; Get sessions for a user in date range; Get aggregated metrics for date range; Get user by ID; Get event counts by type for date" |
| `{{scale}}` | Expected throughput | "1K RPS" or "100K RPS" |
| `{{auth_model}}` | Authentication approach | "Azure AD" or "Connection string" |

## Domain: Event Analytics Pipeline

### Entities

| Entity | Container | Description |
|--------|-----------|-------------|
| Event | events | Raw analytics events (page views, clicks, custom events) |
| Session | sessions | Reconstructed user sessions |
| User | users | User profiles with first/last seen timestamps |
| Aggregation | aggregations | Pre-computed rollups (hourly/daily counts, funnels) |

### High-Volume Event Ingestion

- Events container MUST have TTL enabled. Default `defaultTtl: 7776000` (90 days).
- Bulk ingestion endpoint accepts arrays of up to 500 events per request.
- Use `AllowBulkExecution = true` (.NET) or equivalent for batch writes.
- Events are append-only — no updates or deletes on raw events.

### Session Reconstruction

- Sessions are built from events via change feed processor (stub in code).
- A session groups events from the same user within a 30-minute inactivity window.
- Session documents contain: `startTime`, `endTime`, `eventCount`, `pageViews`, `duration`.

### Pre-Computed Rollups via Change Feed

- Change feed processor on `events` container computes:
  - Hourly event counts by type
  - Daily unique user counts
  - Session duration averages
- Rollups written to `aggregations` container.
- Document in README, stub handler in code.

## Critical: Partition Key Determination

| Container | Partition Key | Justification |
|-----------|--------------|---------------|
| events | `/sessionId` | Events queried per-session for reconstruction; high cardinality avoids hot partitions |
| sessions | `/userId` | Sessions queried per-user (user journey analysis) |
| users | `/id` | Users accessed by own ID |
| aggregations | `/granularity` | Aggregations queried by granularity (hourly/daily) + date range |

For `{{scale}}` > 10K RPS: Use hierarchical partition key `/sessionId/eventType` on events.

```
# PARTITION KEY: /sessionId
# JUSTIFICATION: Session reconstruction reads all events for a session. High-cardinality
# sessionId distributes writes evenly across partitions for high-volume ingestion.
```

## API Convention (MANDATORY — no deviation)

```
GET    /api/{resource}           → 200 + array
POST   /api/{resource}           → 201 + created object + Location header
GET    /api/{resource}/{id}      → 200 + object | 404
PATCH  /api/{resource}/{id}      → 200 + updated object | 404
DELETE /api/{resource}/{id}      → 204 | 404
GET    /api/health               → 200 + {"status": "healthy"}
```

### Domain-Specific Endpoints

```
POST   /api/events/ingest                                → 201 + { "accepted": count } (bulk)
GET    /api/sessions/{sessionId}/events                   → 200 + events for session
GET    /api/users/{userId}/sessions?from=&to=             → 200 + sessions in range
GET    /api/aggregations?granularity=daily&from=&to=      → 200 + rollup data
GET    /api/aggregations?granularity=hourly&date=&type=   → 200 + hourly breakdown
GET    /api/users/{userId}                                → 200 + user profile with first/last seen
```

## Architecture Requirements

1. **Layering**: Handlers/Routes → Services → Repository → Cosmos SDK
2. **CosmosClient**: Single instance, singleton.
3. **Bulk writes**: Ingestion endpoint uses bulk execution mode.
4. **Change feed**: Stub processor for session reconstruction and rollup computation.
5. **Error handling**: Map Cosmos status codes to HTTP status codes
6. **Health check**: `/api/health`
7. **TTL**: Events container default TTL = 90 days.

## Data Modeling Constraints

- `Event`: `id`, `sessionId` (PK), `userId`, `type` (pageView/click/custom), `name`, `properties` (object), `timestamp` (ISO 8601), `ttl` (optional override)
- `Session`: `id`, `userId` (PK), `startTime`, `endTime`, `eventCount`, `pageViews`, `duration` (seconds), `createdAt`
- `User`: `id`, `firstSeenAt`, `lastSeenAt`, `totalSessions`, `createdAt`
- `Aggregation`: `id`, `granularity` (PK — "hourly" or "daily"), `date` (YYYY-MM-DD), `hour` (nullable, 0-23), `eventType`, `count`, `uniqueUsers`, `avgSessionDuration`, `computedAt`

## Connection & Resilience

- Retry configuration: max 9 attempts, 30s max wait on 429s
- Connection mode: Direct for production, Gateway for emulator
- ⚠️ Linux emulator (vnext) uses HTTP not HTTPS — set `connection_verify=False` or `disable_ssl_verification=True` for local dev
- Client shutdown/cleanup on app termination

## Anti-Patterns (REJECT — never generate these)

- ❌ Hardcoded connection strings or keys
- ❌ Cross-partition queries without explicit comment
- ❌ Deprecated SDK methods
- ❌ Creating CosmosClient per-request
- ❌ f-string interpolation in Cosmos SQL queries
- ❌ Loading unbounded event sets without time range AND pagination
- ❌ Missing client.close() / dispose on shutdown
- ❌ Computing aggregations at query time from raw events (use pre-computed rollups)
- ❌ Storing raw events indefinitely without TTL
- ❌ Single-item event ingestion endpoint as primary (must support bulk)

## Scale Considerations for `{{scale}}`

- If < 1000 RPS: Shared throughput, autoscale
- If 1000-10000 RPS: Dedicated throughput on events, autoscale on aggregations
- If > 10000 RPS: Multi-region, hierarchical partition key, change feed with lease container

---

## iteration-config.yaml (ALWAYS generate this file)

```yaml
version: 1
scaffold:
  prompt: speckit.cosmosdb.scaffold-analytics
  language: "{{language}}"
  generated_at: "{{ISO_8601_TIMESTAMP}}"

validation:
  - name: app-starts
    command: "{{start_command}}"
    expect: "listening on"
    timeout: 15s
  - name: health-check
    command: "curl -sf http://localhost:8000/api/health"
    expect: '{"status":"healthy"}'
  - name: crud-cycle
    script: tests/smoke.sh
  - name: bulk-ingest
    script: tests/bulk-ingest.sh

iteration:
  max_rounds: 3
  on_failure: fix-and-retry
  on_success: commit
```

---

## Language Appendix: Python

**MUST use when `{{language}}` = python**

### Versions & Dependencies (requirements.txt)
```
azure-cosmos>=4.9.0
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
aiohttp>=3.9.0
```

### File Structure (MANDATORY)
```
{{app_name}}/
├── main.py
├── config.py
├── models.py            # Event, Session, User, Aggregation
├── repository.py        # EventRepository, SessionRepository, AggregationRepository
├── service.py           # IngestionService, AnalyticsService, SessionReconstructionService (stub)
├── requirements.txt
├── .env.example
├── iteration-config.yaml
└── README.md
```

### NEVER use these
- ❌ `client.read_account()` — does not exist; use `client.get_database_account()`
- ❌ `ConnectionMode.Direct`

---

## Language Appendix: .NET (C#)

**MUST use when `{{language}}` = dotnet**

### File Structure (MANDATORY)
```
{{app_name}}/
├── Program.cs
├── Models/
│   ├── Event.cs, Session.cs, User.cs, Aggregation.cs
├── Repositories/
├── Services/
│   ├── IngestionService.cs
│   ├── AnalyticsService.cs
│   └── ChangeFeedProcessor.cs (stub)
├── Configuration/
│   └── CosmosSettings.cs
├── {{app_name}}.csproj
├── appsettings.json
├── iteration-config.yaml
└── README.md
```

### SDK Patterns — Change Feed Processor
```csharp
var processor = container.GetChangeFeedProcessorBuilder<Event>("sessionBuilder", HandleChangesAsync)
    .WithInstanceName("instance-1")
    .WithLeaseContainer(leaseContainer)
    .Build();
await processor.StartAsync();
```

---

## Language Appendix: Java

**MUST use when `{{language}}` = java**

### File Structure (MANDATORY)
```
{{app_name}}/
├── src/main/java/com/example/{{app_name}}/
│   ├── Application.java
│   ├── config/CosmosConfig.java
│   ├── model/Event.java, Session.java, User.java, Aggregation.java
│   ├── repository/
│   ├── service/IngestionService.java, AnalyticsService.java
│   └── controller/AnalyticsController.java
├── src/main/resources/application.yml
├── pom.xml
├── iteration-config.yaml
└── README.md
```

---

## Language Appendix: Node.js

**MUST use when `{{language}}` = node**

### File Structure (MANDATORY)
```
{{app_name}}/
├── src/
│   ├── index.js
│   ├── config.js
│   ├── models/
│   ├── repositories/
│   ├── services/
│   │   ├── ingestionService.js
│   │   └── changeFeedProcessor.js (stub)
│   └── routes/
├── package.json
├── .env.example
├── iteration-config.yaml
└── README.md
```

---

## Output Checklist

- [ ] All files from language-specific file structure
- [ ] Partition key justification comments
- [ ] iteration-config.yaml
- [ ] .env.example
- [ ] README.md
- [ ] Health check at `/api/health`
- [ ] Bulk ingestion endpoint
- [ ] TTL on events container (90 days)
- [ ] Change feed processor stub for session reconstruction
- [ ] Pre-computed aggregation queries
- [ ] Proper client lifecycle
- [ ] Parameterized queries
- [ ] Error mapping

## Telemetry

- **Always** set `user_agent_suffix` (Python/Java) or `ApplicationName` (.NET) to `"cosmos-intent-sdk"` on the `CosmosClient` for diagnostics and telemetry tracking.
