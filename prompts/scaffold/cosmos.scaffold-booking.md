# /cosmos.scaffold-booking

> Generate a complete Azure Cosmos DB appointment/reservation system with deterministic, production-ready architecture.

## Intent

Scaffold a full appointment booking application that uses Azure Cosmos DB as its primary data store. The output must be structurally identical across runs given the same inputs.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{app_description}}` | What the application does | "An appointment/reservation system API" |
| `{{language}}` | Target language/framework | "python", "dotnet", "java", "node" |
| `{{entities}}` | Core domain entities (pre-set) | "Providers, Services, TimeSlots, Bookings, Customers" |
| `{{primary_queries}}` | **The 3-5 most frequent read queries** | "Get available slots for provider on date; Get bookings for a provider on date; Get bookings for a customer; Get provider by ID; Get services offered by provider" |
| `{{scale}}` | Expected throughput | "100 RPS" or "10K RPS" |
| `{{auth_model}}` | Authentication approach | "Azure AD" or "Connection string" |

## Domain: Appointment/Reservation System

### Entities

| Entity | Container | Description |
|--------|-----------|-------------|
| Provider | providers | Service providers (doctors, stylists, consultants) |
| Service | providers | Co-located with provider (type discriminator) |
| TimeSlot | schedule | Available time windows per provider per date |
| Booking | schedule | Confirmed reservations (co-located with slots) |
| Customer | customers | Customer profiles |

### Booking Conflict Prevention

- A booking request MUST check for existing bookings in the same time window via **optimistic concurrency**:
  1. Read the TimeSlot document (includes `isBooked` flag and `_etag`).
  2. If `isBooked == true` → return 409 Conflict.
  3. If `isBooked == false` → replace with `isBooked = true` using `IfMatch: etag`.
  4. If etag mismatch → another booking won the race → return 409.
  5. Create the Booking document in the same partition.

### Availability Query

- Slots are pre-generated per provider per date (e.g., 30-minute intervals).
- Availability = slots where `isBooked == false` for a given provider+date.
- Single-partition query since slots are partitioned by `providerId`.

## Critical: Partition Key Determination

| Container | Partition Key | Justification |
|-----------|--------------|---------------|
| providers | `/id` | Providers accessed by own ID; services co-located |
| schedule | `/providerId` | >80% queries: "slots for provider on date", "bookings for provider on date" |
| customers | `/id` | Customers accessed by own ID |

For customer booking history: maintain a denormalized `customerBookings` container with partition key `/customerId`, or accept cross-partition query on `schedule` with explicit comment.

```
# PARTITION KEY: /providerId
# JUSTIFICATION: Availability and booking queries are always scoped to a provider.
# TimeSlots and Bookings co-located for transactional batch on booking creation.
# Cross-partition required for: customer booking history (use denormalized container).
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
GET    /api/providers/{providerId}/availability?date=YYYY-MM-DD   → 200 + available slots
GET    /api/providers/{providerId}/bookings?date=YYYY-MM-DD       → 200 + bookings for date
GET    /api/providers/{providerId}/services                        → 200 + services offered
POST   /api/bookings                                               → 201 + booking | 409 conflict
DELETE /api/bookings/{bookingId}                                   → 204 (cancel, frees slot)
GET    /api/customers/{customerId}/bookings                        → 200 + customer booking history
POST   /api/providers/{providerId}/slots/generate                  → 201 + generated slots for date range
```

## Architecture Requirements

1. **Layering**: Handlers/Routes → Services → Repository → Cosmos SDK
2. **CosmosClient**: Single instance, singleton.
3. **Conflict prevention**: Etag-based optimistic concurrency on slot booking.
4. **Error handling**: Map Cosmos status codes to HTTP status codes
5. **Health check**: `/api/health`
6. **Slot generation**: Service method to pre-generate TimeSlot documents for a provider+date range.

## Data Modeling Constraints

- `Provider`: `id`, `name`, `specialty`, `timezone`, `createdAt`
- `Service`: `id`, `providerId` (co-located in providers), `type: "service"`, `name`, `durationMinutes`, `price`
- `TimeSlot`: `id`, `providerId` (PK), `type: "slot"`, `date` (YYYY-MM-DD), `startTime` (HH:MM), `endTime` (HH:MM), `isBooked` (boolean), `_etag`
- `Booking`: `id`, `providerId` (PK), `type: "booking"`, `slotId`, `customerId`, `serviceId`, `date`, `startTime`, `endTime`, `status` (confirmed/cancelled), `createdAt`
- `Customer`: `id`, `name`, `email`, `phone`, `createdAt`

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
- ❌ Loading unbounded result sets without pagination
- ❌ Missing client.close() / dispose on shutdown
- ❌ Booking without checking slot availability first
- ❌ Booking without etag-based concurrency (race condition)
- ❌ Querying all slots across all providers for availability (must be provider-scoped)

## Scale Considerations for `{{scale}}`

- If < 1000 RPS: Shared throughput, autoscale
- If 1000-10000 RPS: Dedicated throughput on schedule container
- If > 10000 RPS: Multi-region reads, hierarchical partition key `/providerId/date`

---

## iteration-config.yaml (ALWAYS generate this file)

```yaml
version: 1
scaffold:
  prompt: cosmos.scaffold-booking
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
  - name: booking-conflict
    script: tests/booking-conflict.sh

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
├── models.py            # Provider, Service, TimeSlot, Booking, Customer
├── repository.py        # ScheduleRepository, ProviderRepository, CustomerRepository
├── service.py           # BookingService (conflict check, slot generation), AvailabilityService
├── requirements.txt
├── .env.example
├── iteration-config.yaml
└── README.md
```

### SDK Method Reference — Etag Concurrency
```python
# Read slot with etag
slot = await container.read_item(item=slot_id, partition_key=provider_id)
etag = slot["_etag"]

# Conditional replace
slot["isBooked"] = True
await container.replace_item(
    item=slot_id,
    body=slot,
    match_condition=etag,
    etag=etag
)
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
│   ├── Provider.cs, Service.cs, TimeSlot.cs, Booking.cs, Customer.cs
├── Repositories/
├── Services/
│   ├── BookingService.cs
│   └── AvailabilityService.cs
├── Configuration/
│   └── CosmosSettings.cs
├── {{app_name}}.csproj
├── appsettings.json
├── iteration-config.yaml
└── README.md
```

### SDK Patterns — Transactional Batch
```csharp
var batch = container.CreateTransactionalBatch(new PartitionKey(providerId));
batch.ReplaceItem(slot.Id, bookedSlot, new TransactionalBatchItemRequestOptions { IfMatchEtag = etag });
batch.CreateItem(booking);
var response = await batch.ExecuteAsync();
if (!response.IsSuccessStatusCode) { /* conflict handling */ }
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
│   ├── model/Provider.java, TimeSlot.java, Booking.java, Customer.java
│   ├── repository/
│   ├── service/BookingService.java
│   └── controller/BookingController.java
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
│   │   └── bookingService.js
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
- [ ] Slot generation endpoint
- [ ] Availability query (unbooked slots for provider+date)
- [ ] Booking with etag-based conflict prevention
- [ ] Customer booking history
- [ ] Proper client lifecycle
- [ ] Parameterized queries
- [ ] Error mapping
