---
description: "Generate a complete Azure Cosmos DB IoT device telemetry application with deterministic, production-ready architecture."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.scaffold-iot

> Generate a complete Azure Cosmos DB IoT device telemetry application with deterministic, production-ready architecture.

## Intent

Scaffold a full IoT telemetry ingestion and query application that uses Azure Cosmos DB as its primary data store. The output must be structurally identical across runs given the same inputs - partition keys, file structure, API paths, and SDK usage are all locked down by this prompt.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{app_description}}` | What the application does | "An IoT telemetry ingestion and query API" |
| `{{language}}` | Target language/framework | "python", "dotnet", "java", "node" |
| `{{entities}}` | Core domain entities (pre-set) | "Devices, TelemetryReadings, Alerts" |
| `{{primary_queries}}` | **The 3-5 most frequent read queries** | "Get latest telemetry for a device; Get telemetry for device in time range; Get active alerts for a device; Get device by ID; List all devices by status" |
| `{{scale}}` | Expected throughput | "1K RPS" or "100K RPS" |
| `{{auth_model}}` | Authentication approach | "Azure AD" or "Connection string" |

## Domain: IoT Device Telemetry

### Entities

| Entity | Container | Description |
|--------|-----------|-------------|
| Device | devices | Device registration, metadata, and status |
| TelemetryReading | telemetry | Time-series sensor readings (high volume) |
| Alert | alerts | Threshold-breach alerts generated from telemetry |

### High-Volume Ingestion Patterns

- Telemetry container MUST have TTL enabled. Default `defaultTtl: 2592000` (30 days). Each reading MAY override with its own `ttl` field.
- Bulk ingestion endpoint accepts arrays of up to 100 readings per request.
- Use `AllowBulkExecution = true` (.NET) or equivalent for batch writes.

### Aggregation Windows

- Pre-computed hourly/daily rollups SHOULD be generated via change feed processor (document in README, stub handler in code).
- Aggregation documents stored in a separate `aggregations` container with partition key `/deviceId`.

## Critical: Partition Key Determination

### Default Partition Key Algorithm

| Container | Partition Key | Justification |
|-----------|--------------|---------------|
| devices | `/id` | Devices are accessed by their own ID for registration and status |
| telemetry | `/deviceId` | >80% of queries filter by deviceId (latest telemetry, time-range queries) |
| alerts | `/deviceId` | Alerts are always queried per-device |
| aggregations | `/deviceId` | Rollups are always queried per-device |

For `{{scale}}` > 10K RPS: Use hierarchical partition key `/deviceId/yearMonth` on telemetry to avoid hot partitions on high-frequency devices.

Output a justification comment at the top of every data model file:

```
# PARTITION KEY: /deviceId
# JUSTIFICATION: >80% of queries filter by deviceId (get latest telemetry,
# time-range queries, active alerts). Hot device mitigation via hierarchical key at scale.
```

## API Convention (MANDATORY - no deviation)

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
POST   /api/telemetry/ingest          → 201 + { "accepted": count } (bulk ingestion, array body)
GET    /api/devices/{deviceId}/telemetry?from=&to=  → 200 + array (time-range query)
GET    /api/devices/{deviceId}/telemetry/latest     → 200 + single reading
GET    /api/devices/{deviceId}/alerts               → 200 + array of active alerts
POST   /api/devices/{deviceId}/alerts/{alertId}/acknowledge → 200 + updated alert
GET    /api/devices/{deviceId}/aggregations?granularity=hourly&from=&to= → 200 + array
```

Rules:
- Resource names are **plural**
- All request/response bodies use **camelCase** field names in JSON
- Telemetry time-range queries MUST require both `from` and `to` query params (ISO 8601)
- Standard status codes: 201 create, 200 read/update, 204 delete, 404 not found, 429 throttled

## Architecture Requirements

1. **Layering**: Handlers/Routes → Services → Repository → Cosmos SDK (no skipping layers)
2. **CosmosClient**: Single instance, registered as singleton. NEVER create per-request.
3. **Configuration**: Environment variables with typed config.
4. **Error handling**: Map Cosmos status codes to HTTP status codes
5. **Health check**: Verify Cosmos connectivity at `/api/health`
6. **TTL**: Telemetry container default TTL = 30 days. Document override mechanism.
7. **Bulk writes**: Ingestion endpoint uses bulk execution mode.

## Data Modeling Constraints

For each entity:
- Include partition key justification comment
- Include `id` field (string, auto-generated UUID)
- Include `type` discriminator if container holds multiple types
- Include `createdAt` timestamp (ISO 8601)
- TelemetryReading MUST include `timestamp` (ISO 8601), `deviceId`, `sensorType`, `value`, `unit`
- TelemetryReading MAY include `ttl` (integer seconds) to override container default
- Alert MUST include `severity` (info/warning/critical), `acknowledged` (boolean), `threshold`, `actualValue`

## Connection & Resilience

- Retry configuration: max 9 attempts, 30s max wait on 429s
- Connection mode: Direct for production, Gateway for emulator
- ⚠️ Linux emulator (vnext) uses HTTP not HTTPS - set `connection_verify=False` or `disable_ssl_verification=True` for local dev
- Client shutdown/cleanup on app termination
- Application name set in client options

## Anti-Patterns (REJECT - never generate these)

- ❌ Hardcoded connection strings or keys in source code
- ❌ Cross-partition queries without explicit `# CROSS-PARTITION: reason` comment
- ❌ Deprecated SDK methods (see language appendix)
- ❌ Creating CosmosClient per-request
- ❌ Using `/id` as partition key for telemetry
- ❌ f-string interpolation in Cosmos SQL queries (use parameters)
- ❌ Loading unbounded telemetry without time-range filter AND pagination
- ❌ Missing client.close() / dispose on shutdown
- ❌ Querying telemetry without `from`/`to` bounds (unbounded time-series scan)
- ❌ Storing raw telemetry indefinitely without TTL

## Scale Considerations for `{{scale}}`

- If < 1000 RPS: Shared throughput, single-level partition key `/deviceId`
- If 1000-10000 RPS: Dedicated throughput on telemetry, autoscale
- If > 10000 RPS: Hierarchical partition key `/deviceId/yearMonth`, multi-region, change feed for aggregations

---

## iteration-config.yaml (ALWAYS generate this file)

```yaml
version: 1
scaffold:
  prompt: speckit.cosmosdb.scaffold-iot
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

### File Structure (MANDATORY - generate ALL files)
```
{{app_name}}/
├── main.py
├── config.py
├── models.py            # Device, TelemetryReading, Alert, Aggregation
├── repository.py        # DeviceRepository, TelemetryRepository, AlertRepository
├── service.py           # Ingestion service, alert service, aggregation service
├── requirements.txt
├── .env.example
├── iteration-config.yaml
└── README.md
```

### SDK Method Reference (use ONLY these)
```python
from azure.cosmos.aio import CosmosClient
client = CosmosClient(endpoint, credential=key)
await client.get_database_account()

# Bulk-style ingestion (loop with create_item; true bulk not available in async Python)
for reading in readings:
    await container.create_item(body=reading)

# Time-range query
query = "SELECT * FROM c WHERE c.deviceId = @deviceId AND c.timestamp >= @from AND c.timestamp <= @to ORDER BY c.timestamp DESC"
parameters = [{"name": "@deviceId", "value": did}, {"name": "@from", "value": ts_from}, {"name": "@to", "value": ts_to}]
items = container.query_items(query=query, parameters=parameters, partition_key=did, max_item_count=100)

await client.close()
```

### NEVER use these (deprecated/wrong in Python SDK)
- ❌ `client.read_account()` - does not exist; use `client.get_database_account()`
- ❌ `ConnectionMode.Direct` - Python async client only supports Gateway mode
- ❌ `offer_throughput` on serverless accounts

---

## Language Appendix: .NET (C#)

**MUST use when `{{language}}` = dotnet**

### Versions & Dependencies
```xml
<PackageReference Include="Microsoft.Azure.Cosmos" Version="3.39.*" />
<PackageReference Include="Microsoft.Extensions.Hosting" Version="8.*" />
```

### File Structure (MANDATORY)
```
{{app_name}}/
├── Program.cs
├── Models/
│   ├── Device.cs
│   ├── TelemetryReading.cs
│   └── Alert.cs
├── Repositories/
│   ├── DeviceRepository.cs
│   ├── TelemetryRepository.cs
│   └── AlertRepository.cs
├── Services/
│   ├── IngestionService.cs
│   └── AlertService.cs
├── Configuration/
│   └── CosmosSettings.cs
├── {{app_name}}.csproj
├── appsettings.json
├── iteration-config.yaml
└── README.md
```

### SDK Patterns
```csharp
// Bulk ingestion
var options = new CosmosClientOptions { AllowBulkExecution = true };
var tasks = readings.Select(r => container.CreateItemAsync(r, new PartitionKey(r.DeviceId)));
await Task.WhenAll(tasks);

// TTL - set on container creation
var containerProperties = new ContainerProperties(id, "/deviceId") { DefaultTimeToLive = 2592000 };
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
│   ├── model/Device.java
│   ├── model/TelemetryReading.java
│   ├── model/Alert.java
│   ├── repository/TelemetryRepository.java
│   ├── service/IngestionService.java
│   └── controller/TelemetryController.java
├── src/main/resources/application.yml
├── pom.xml
├── iteration-config.yaml
└── README.md
```

### Key Annotations
```java
@Container(containerName = "telemetry", autoScale = true)
public class TelemetryReading {
    @Id private String id;
    @PartitionKey private String deviceId;
    private String timestamp;
    private double value;
    private int ttl;
}
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
│   └── routes/
├── package.json
├── .env.example
├── iteration-config.yaml
└── README.md
```

### SDK Patterns
```javascript
const { CosmosClient, BulkOperationType } = require("@azure/cosmos");

// Bulk ingestion
const operations = readings.map(r => ({
    operationType: BulkOperationType.Create,
    resourceBody: r
}));
await container.items.bulk(operations);
```

---

## Output Checklist (ALL items MUST be generated)

- [ ] All files from the language-specific file structure
- [ ] Partition key justification comment in models
- [ ] iteration-config.yaml
- [ ] .env.example with all required environment variables
- [ ] README.md with setup instructions
- [ ] Health check endpoint at `/api/health`
- [ ] TTL configured on telemetry container (30 days default)
- [ ] Bulk ingestion endpoint
- [ ] Time-range query with mandatory from/to params
- [ ] Proper client lifecycle
- [ ] Parameterized queries
- [ ] Error mapping

Generate the complete application following ALL constraints above.

## Telemetry

- **Always** set `user_agent_suffix` (Python/Java) or `ApplicationName` (.NET) to `"speckit-cosmosdb"` on the `CosmosClient` for diagnostics and telemetry tracking.
