---
description: "Generate a complete Azure Cosmos DB warehouse inventory management application with deterministic, production-ready architecture."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.scaffold-inventory

> Generate a complete Azure Cosmos DB warehouse inventory management application with deterministic, production-ready architecture.

## Intent

Scaffold a full warehouse inventory management application that uses Azure Cosmos DB as its primary data store. The output must be structurally identical across runs given the same inputs.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{app_description}}` | What the application does | "A warehouse inventory management API" |
| `{{language}}` | Target language/framework | "python", "dotnet", "java", "node" |
| `{{entities}}` | Core domain entities (pre-set) | "Warehouses, Products, StockLevels, Transfers" |
| `{{primary_queries}}` | **The 3-5 most frequent read queries** | "Get stock level for product in warehouse; Get all stock for a warehouse; Get transfer history for a warehouse; Get low-stock items for a warehouse; Get product by ID" |
| `{{scale}}` | Expected throughput | "100 RPS" or "10K RPS" |
| `{{auth_model}}` | Authentication approach | "Azure AD" or "Connection string" |

## Domain: Warehouse Inventory Management

### Entities

| Entity | Container | Description |
|--------|-----------|-------------|
| Warehouse | warehouses | Warehouse metadata and location |
| Product | products | Product catalog (global, not per-warehouse) |
| StockLevel | stock | Current quantity of a product in a specific warehouse |
| Transfer | transfers | Stock movement between warehouses or inbound/outbound |

### Stock Management

- `StockLevel` is the canonical source of truth for quantity. Composite key: `warehouseId` + `productId`.
- All stock mutations go through `Transfer` documents. A transfer adjusts source and destination StockLevels atomically (batch/transactional batch within same partition, or compensating transaction across partitions).
- Low-stock alerts: query StockLevels where `quantity < reorderThreshold` within a warehouse partition.

### Transfer Types

| Type | Description |
|------|-------------|
| `inbound` | Stock received from supplier (no source warehouse) |
| `outbound` | Stock shipped to customer (no destination warehouse) |
| `inter-warehouse` | Transfer between two warehouses |
| `adjustment` | Manual count correction |

## Critical: Partition Key Determination

| Container | Partition Key | Justification |
|-----------|--------------|---------------|
| warehouses | `/id` | Warehouses accessed by own ID |
| products | `/id` | Products accessed by own ID (global catalog) |
| stock | `/warehouseId` | >80% of queries are "stock for warehouse" or "stock for product in warehouse" |
| transfers | `/warehouseId` | Transfer history always queried per-warehouse |

```
# PARTITION KEY: /warehouseId
# JUSTIFICATION: Stock is always queried within a warehouse context (stock by warehouse,
# low-stock for warehouse, stock for product in warehouse).
# Cross-partition required for: global product stock across all warehouses.
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
GET    /api/warehouses/{warehouseId}/stock                        → 200 + all stock levels
GET    /api/warehouses/{warehouseId}/stock/{productId}            → 200 + stock level | 404
GET    /api/warehouses/{warehouseId}/stock/low                    → 200 + items below reorder threshold
POST   /api/transfers                                             → 201 + transfer (adjusts stock)
GET    /api/warehouses/{warehouseId}/transfers?from=&to=          → 200 + transfer history
GET    /api/products/{productId}/stock                            → 200 + stock across all warehouses (CROSS-PARTITION)
```

## Architecture Requirements

1. **Layering**: Handlers/Routes → Services → Repository → Cosmos SDK
2. **CosmosClient**: Single instance, singleton.
3. **Stock atomicity**: Use transactional batch for stock adjustments within same warehouse. Use compensating transactions for inter-warehouse transfers.
4. **Error handling**: Map Cosmos status codes to HTTP status codes
5. **Health check**: `/api/health`

## Data Modeling Constraints

- `StockLevel`: `id` (composite: `{warehouseId}_{productId}`), `warehouseId` (PK), `productId`, `quantity`, `reorderThreshold`, `updatedAt`
- `Transfer`: `id`, `warehouseId` (PK - source warehouse, or destination for inbound), `type`, `sourceWarehouseId` (nullable), `destinationWarehouseId` (nullable), `productId`, `quantity`, `note`, `createdAt`
- `Warehouse`: `id`, `name`, `location`, `createdAt`
- `Product`: `id`, `name`, `sku`, `category`, `createdAt`

## Connection & Resilience

- Retry configuration: max 9 attempts, 30s max wait on 429s
- Connection mode: Direct for production, Gateway for emulator
- ⚠️ Linux emulator (vnext) uses HTTP not HTTPS - set `connection_verify=False` or `disable_ssl_verification=True` for local dev
- Client shutdown/cleanup on app termination

## Anti-Patterns (REJECT - never generate these)

- ❌ Hardcoded connection strings or keys
- ❌ Cross-partition queries without explicit comment
- ❌ Deprecated SDK methods
- ❌ Creating CosmosClient per-request
- ❌ f-string interpolation in Cosmos SQL queries
- ❌ Loading unbounded result sets without pagination
- ❌ Missing client.close() / dispose on shutdown
- ❌ Modifying stock levels directly without a Transfer document (audit trail required)
- ❌ Non-atomic stock decrements (must use etag or transactional batch)

## Scale Considerations for `{{scale}}`

- If < 1000 RPS: Shared throughput, autoscale
- If 1000-10000 RPS: Dedicated throughput on stock and transfers containers
- If > 10000 RPS: Multi-region, hierarchical partition key `/warehouseId/productId`

---

## iteration-config.yaml (ALWAYS generate this file)

```yaml
version: 1
scaffold:
  prompt: speckit.cosmosdb.scaffold-inventory
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
  - name: transfer-cycle
    script: tests/transfer-cycle.sh

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
├── models.py            # Warehouse, Product, StockLevel, Transfer
├── repository.py        # StockRepository, TransferRepository, WarehouseRepository
├── service.py           # InventoryService (transfer logic, low-stock queries)
├── requirements.txt
├── .env.example
├── iteration-config.yaml
└── README.md
```

### NEVER use these
- ❌ `client.read_account()` - does not exist; use `client.get_database_account()`
- ❌ `ConnectionMode.Direct`

---

## Language Appendix: .NET (C#)

**MUST use when `{{language}}` = dotnet**

### File Structure (MANDATORY)
```
{{app_name}}/
├── Program.cs
├── Models/
│   ├── Warehouse.cs, Product.cs, StockLevel.cs, Transfer.cs
├── Repositories/
├── Services/
│   └── InventoryService.cs
├── Configuration/
│   └── CosmosSettings.cs
├── {{app_name}}.csproj
├── appsettings.json
├── iteration-config.yaml
└── README.md
```

### SDK Patterns - Transactional Batch
```csharp
// Transactional batch for stock adjustment within same warehouse
var batch = container.CreateTransactionalBatch(new PartitionKey(warehouseId));
batch.ReplaceItem(stockLevel.Id, updatedStockLevel, new TransactionalBatchItemRequestOptions { IfMatchEtag = etag });
batch.CreateItem(transfer);
var response = await batch.ExecuteAsync();
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
│   ├── model/Warehouse.java, Product.java, StockLevel.java, Transfer.java
│   ├── repository/
│   ├── service/InventoryService.java
│   └── controller/InventoryController.java
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
│   │   └── inventoryService.js
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
- [ ] Transfer-based stock mutations (audit trail)
- [ ] Atomic stock adjustments (etag or transactional batch)
- [ ] Low-stock alert query
- [ ] Proper client lifecycle
- [ ] Parameterized queries
- [ ] Error mapping

## Telemetry

- **Always** set `user_agent_suffix` (Python/Java) or `ApplicationName` (.NET) to `"cosmos-intent-sdk"` on the `CosmosClient` for diagnostics and telemetry tracking.
