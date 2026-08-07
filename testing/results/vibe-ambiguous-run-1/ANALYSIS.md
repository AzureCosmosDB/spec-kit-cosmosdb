## Intent Analysis

- **Matched scaffold:** cosmos.scaffold-ecommerce
  - *Reasoning:* "orders" is a direct ecommerce trigger. "inventory" is secondary — inventory tracking is part of order fulfillment. "my business" suggests a single-tenant business tool.
  - *Secondary influence:* cosmos.scaffold-inventory
- **Inferred language:** Python (FastAPI)
- **Inferred scale:** ~1K users, ~100K documents (small — "my business" implies SMB/prototype)
- **Generated query patterns:**
  1. Get all orders for a customer (read-heavy) ← PARTITION KEY DRIVER
  2. Get current inventory levels by product
  3. Get order details by order ID
  4. Place order / Update inventory (write — transactional)
- **Partition key decision:** /customerId for orders container (optimizes for query #1)
- **Containers:**
  - `orders` — partition key: `/customerId`
  - `products` — partition key: `/categoryId`
  - `inventory` — partition key: `/warehouseId`

Proceeding with generation...
