## Intent Analysis

- **Matched scaffold:** cosmos.scaffold-ecommerce
  - *Reasoning:* "orders" is the strongest keyword match (direct ecommerce trigger). "inventory" supports the ecommerce flow — you need inventory to fulfill orders. The primary use case is order management with inventory as supporting data.
  - *Secondary influence:* cosmos.scaffold-inventory
- **Inferred language:** Python (FastAPI)
- **Inferred scale:** ~1K users, ~100K documents ("my business" — small/SMB)
- **Generated query patterns:**
  1. Get all orders by status (read-heavy) ← PARTITION KEY DRIVER
  2. Get inventory count for a product
  3. Get order history for a customer
  4. Create order / Adjust inventory (write)
- **Partition key decision:** /status for orders container (optimizes for query #1 — business owner checking pending/shipped/completed orders)
- **Containers:**
  - `orders` — partition key: `/status`
  - `products` — partition key: `/categoryId`
  - `inventory` — partition key: `/productId`

Proceeding with generation...
