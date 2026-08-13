---
description: "Generate a complete Azure Cosmos DB e-commerce order API with deterministic, production-ready architecture."
---

# /cosmos.scaffold-ecommerce

> Generate a complete Azure Cosmos DB e-commerce order API with deterministic, production-ready architecture.

## Intent

Scaffold a full e-commerce order management application that uses Azure Cosmos DB as its primary data store. The output must be structurally identical across runs given the same inputs — partition keys, file structure, API paths, and SDK usage are all locked down by this prompt.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{app_description}}` | What the application does | "An e-commerce order API" |
| `{{language}}` | Target language/framework | "python", "dotnet", "java", "node" |
| `{{entities}}` | Core domain entities (pre-set) | "Customers, Orders, OrderItems, Products" |
| `{{primary_queries}}` | **The 3-5 most frequent read queries** | "Get all orders for a customer; Get order by ID; Get order items for an order; Get product by ID; List orders by status for a customer" |
| `{{scale}}` | Expected throughput | "100 RPS" or "10K RPS" |
| `{{auth_model}}` | Authentication approach | "Azure AD" or "Connection string" |

## Domain: E-commerce Order API

### Entities

| Entity | Container | Description |
|--------|-----------|-------------|
| Customer | customers | Buyer profiles and preferences |
| Order | orders | Order header with lifecycle status |
| OrderItem | orders | Line items embedded or co-located with parent order |
| Product | products | Product catalog with pricing and inventory counts |

### Order Lifecycle (state machine)

```
placed → paid → shipped → delivered
          ↓         ↓
       cancelled  returned
```

Status transitions MUST be enforced in the service layer. Invalid transitions return 409.

### Inventory Management

- `Product.stockCount` is decremented atomically on order placement via optimistic concurrency (etag check).
- If etag mismatch on stock decrement → retry up to 3 times → 409 to client.
- Restocking on cancellation MUST increment `stockCount` with same etag pattern.

## Critical: Partition Key Determination

**You MUST determine partition keys from `{{primary_queries}}` BEFORE generating any code.**

### Default Partition Key Algorithm (override only if `{{primary_queries}}` dictates otherwise)

| Container | Partition Key | Justification |
|-----------|--------------|---------------|
| customers | `/id` | Customers are always accessed by their own ID |
| orders | `/customerId` | >70% of queries filter by customerId (order history, orders by status for customer) |
| products | `/categoryId` | Products are queried by category; point-reads use id+categoryId |

Output a justification comment at the top of every data model file:

```
# PARTITION KEY: /customerId
# JUSTIFICATION: 4 of 5 primary queries filter by customerId (get orders for customer,
# get order by id within customer, get orders by status for customer, get order items for order).
# Cross-partition required for: admin order search (opt-in, paginated).
```

## API Convention (MANDATORY — no deviation)

All endpoints MUST follow this exact pattern:

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
POST   /api/orders/{orderId}/pay      → 200 + updated order (status: paid)
POST   /api/orders/{orderId}/ship     → 200 + updated order (status: shipped)
POST   /api/orders/{orderId}/deliver  → 200 + updated order (status: delivered)
POST   /api/orders/{orderId}/cancel   → 200 + updated order (status: cancelled)
GET    /api/customers/{customerId}/orders → 200 + array of orders
GET    /api/orders/{orderId}/items    → 200 + array of order items
```

Rules:
- Resource names are **plural** (e.g., `/api/orders`, `/api/products`)
- Nested resources: `/api/{parent}/{parentId}/{child}`
- All request/response bodies use **camelCase** field names in JSON
- No API versioning in URL (use headers if needed later)
- Standard status codes: 201 create, 200 read/update, 204 delete, 404 not found, 409 conflict (etag mismatch or invalid state transition), 429 throttled

## Architecture Requirements

1. **Layering**: Handlers/Routes → Services → Repository → Cosmos SDK (no skipping layers)
2. **CosmosClient**: Single instance, registered as singleton. NEVER create per-request.
3. **Configuration**: Environment variables with typed config. Support both emulator and production.
4. **Error handling**: Map Cosmos status codes to HTTP status codes (404→404, 409→409, 429→429 with Retry-After)
5. **Health check**: Verify Cosmos connectivity at `/api/health`
6. **Order state machine**: Service layer validates transitions, rejects invalid ones with 409.
7. **Inventory atomicity**: Etag-based optimistic concurrency on stock updates.

## Data Modeling Constraints

For each entity:
- Include partition key justification comment
- Include `id` field (string, auto-generated UUID)
- Include `type` discriminator field if container holds multiple entity types
- Include `createdAt` and `updatedAt` timestamps (ISO 8601)
- OrderItem MUST include `type: "orderItem"` discriminator (co-located in orders container)
- Order MUST include `status` field with enum validation

## Connection & Resilience

- Retry configuration: max 9 attempts, 30s max wait on 429s
- Connection mode: Direct for production, Gateway for emulator
- ⚠️ Linux emulator (vnext) uses HTTP not HTTPS — set `connection_verify=False` or `disable_ssl_verification=True` for local dev
- Client shutdown/cleanup on app termination
- Application name set in client options

## User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="cosmos-intent-sdk/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "cosmos-intent-sdk/0.1.0"`. For Java, use `.userAgentSuffix("cosmos-intent-sdk/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

## Anti-Patterns (REJECT — never generate these)

- ❌ Hardcoded connection strings or keys in source code
- ❌ Cross-partition queries without explicit `# CROSS-PARTITION: reason` comment
- ❌ Deprecated SDK methods (see language appendix)
- ❌ Creating CosmosClient per-request
- ❌ Using `/id` as partition key for orders (customerId is the access pattern)
- ❌ f-string interpolation in Cosmos SQL queries (use parameters)
- ❌ Loading unbounded result sets without pagination (max 100 items default)
- ❌ Missing client.close() / dispose on shutdown
- ❌ Decrementing inventory without etag check
- ❌ Allowing invalid order state transitions

## Scale Considerations for `{{scale}}`

- If < 1000 RPS: Single database, autoscale throughput, shared throughput containers
- If 1000-10000 RPS: Dedicated throughput for orders container, consider hierarchical partition key `/customerId/orderId`
- If > 10000 RPS: Multi-region writes, dedicated throughput, change feed for inventory sync

---

## iteration-config.yaml (ALWAYS generate this file)

```yaml
# iteration-config.yaml — controls iterative refinement of this scaffold
version: 1
scaffold:
  prompt: cosmos.scaffold-ecommerce
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
  - name: order-lifecycle
    script: tests/order-lifecycle.sh

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

### File Structure (MANDATORY — generate ALL files)
```
{{app_name}}/
├── main.py              # FastAPI app, lifespan, router includes
├── config.py            # Settings class (pydantic-settings BaseSettings)
├── models.py            # Pydantic v2 models: Customer, Order, OrderItem, Product
├── repository.py        # CosmosDB data access (OrderRepository, ProductRepository, CustomerRepository)
├── service.py           # Business logic + order state machine + inventory management
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
database = client.get_database_client(db_name)
container = database.get_container_client(container_name)

await container.create_item(body=item)
await container.read_item(item=item_id, partition_key=pk_value)
await container.replace_item(item=item_id, body=updated_item)
await container.delete_item(item=item_id, partition_key=pk_value)

query = "SELECT * FROM c WHERE c.customerId = @customerId AND c.type = @type"
parameters = [{"name": "@customerId", "value": cid}, {"name": "@type", "value": "order"}]
items = container.query_items(query=query, parameters=parameters, partition_key=pk_value)
results = [item async for item in items]

await client.close()
```

### Pydantic v2 Patterns
```python
from pydantic import BaseModel, Field
from enum import Enum

class OrderStatus(str, Enum):
    PLACED = "placed"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"

class Order(CosmosDocument):
    # PARTITION KEY: /customerId
    # JUSTIFICATION: Orders are queried by customer >70% of the time
    type: str = "order"
    customer_id: str = Field(alias="customerId")
    status: OrderStatus = OrderStatus.PLACED
    total_amount: float = Field(alias="totalAmount")
```

### FastAPI Lifespan Pattern
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.cosmos_client = CosmosClient(settings.cosmos_endpoint, credential=settings.cosmos_key)
    app.state.database = app.state.cosmos_client.get_database_client(settings.cosmos_database)
    yield
    await app.state.cosmos_client.close()

app = FastAPI(lifespan=lifespan)
```

### NEVER use these (deprecated/wrong in Python SDK)
- ❌ `client.read_account()` — does not exist; use `client.get_database_account()`
- ❌ `ConnectionMode.Direct` — Python async client only supports Gateway mode
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
│   ├── Customer.cs
│   ├── Order.cs
│   ├── OrderItem.cs
│   └── Product.cs
├── Repositories/
│   ├── OrderRepository.cs
│   ├── ProductRepository.cs
│   └── CustomerRepository.cs
├── Services/
│   ├── OrderService.cs
│   └── InventoryService.cs
├── Configuration/
│   └── CosmosSettings.cs
├── {{app_name}}.csproj
├── appsettings.json
├── appsettings.Development.json
├── iteration-config.yaml
└── README.md
```

### SDK Patterns
```csharp
builder.Services.AddSingleton<CosmosClient>(sp =>
{
    var settings = sp.GetRequiredService<IOptions<CosmosSettings>>().Value;
    return new CosmosClient(settings.Endpoint, settings.Key, new CosmosClientOptions
    {
        ApplicationName = "{{app_name}}",
        ConnectionMode = ConnectionMode.Direct
    });
});

await container.CreateItemAsync(item, new PartitionKey(item.CustomerId));
await container.ReadItemAsync<Order>(id, new PartitionKey(customerId));
await container.ReplaceItemAsync(item, id, new PartitionKey(customerId),
    new ItemRequestOptions { IfMatchEtag = etag });
```

---

## Language Appendix: Java

**MUST use when `{{language}}` = java**

### Versions & Dependencies
```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-spring-data-cosmos</artifactId>
    <version>5.x</version>
</dependency>
```

### File Structure (MANDATORY)
```
{{app_name}}/
├── src/main/java/com/example/{{app_name}}/
│   ├── Application.java
│   ├── config/CosmosConfig.java
│   ├── model/Customer.java
│   ├── model/Order.java
│   ├── model/OrderItem.java
│   ├── model/Product.java
│   ├── model/OrderStatus.java
│   ├── repository/OrderRepository.java
│   ├── repository/ProductRepository.java
│   ├── service/OrderService.java
│   ├── service/InventoryService.java
│   └── controller/OrderController.java
├── src/main/resources/application.yml
├── pom.xml
├── iteration-config.yaml
└── README.md
```

### Key Annotations
```java
@Container(containerName = "orders", autoScale = true)
public class Order {
    @Id
    private String id;
    @PartitionKey
    private String customerId;
    private OrderStatus status;
}
```

---

## Language Appendix: Node.js

**MUST use when `{{language}}` = node**

### Versions & Dependencies (package.json)
```json
{
  "dependencies": {
    "@azure/cosmos": "^4.0.0",
    "express": "^4.18.0",
    "dotenv": "^16.0.0",
    "uuid": "^9.0.0"
  }
}
```

### File Structure (MANDATORY)
```
{{app_name}}/
├── src/
│   ├── index.js
│   ├── config.js
│   ├── models/
│   │   ├── order.js
│   │   ├── product.js
│   │   └── customer.js
│   ├── repositories/
│   │   ├── orderRepository.js
│   │   ├── productRepository.js
│   │   └── customerRepository.js
│   ├── services/
│   │   ├── orderService.js
│   │   └── inventoryService.js
│   └── routes/
│       ├── orders.js
│       ├── products.js
│       └── customers.js
├── package.json
├── .env.example
├── iteration-config.yaml
└── README.md
```

### SDK Patterns
```javascript
const { CosmosClient } = require("@azure/cosmos");
const client = new CosmosClient({ endpoint, key });

await container.items.create(order);
const { resource } = await container.item(id, customerId).read();
await container.item(id, customerId).replace(updatedOrder, { ifMatch: etag });
```

---

## Output Checklist (ALL items MUST be generated)

- [ ] All files from the language-specific file structure
- [ ] Partition key justification comment in models
- [ ] iteration-config.yaml
- [ ] .env.example with all required environment variables
- [ ] README.md with setup instructions
- [ ] Health check endpoint at `/api/health`
- [ ] Order state machine with valid transitions
- [ ] Inventory management with etag-based concurrency
- [ ] Proper client lifecycle
- [ ] Parameterized queries
- [ ] Error mapping (Cosmos errors → HTTP status codes)

Generate the complete application following ALL constraints above.
