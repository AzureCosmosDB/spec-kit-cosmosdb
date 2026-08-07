## Intent Analysis

- **Matched scaffold:** cosmos.scaffold-inventory
  - *Reasoning:* "track orders and inventory" — the primary verb is "track" which implies monitoring/management, closer to inventory management. Orders are part of the inventory workflow (stock in, stock out).
  - *Secondary influence:* cosmos.scaffold-ecommerce
- **Inferred language:** Python (FastAPI)
- **Inferred scale:** ~1K users, ~100K documents ("my business" — single business, small scale)
- **Generated query patterns:**
  1. Get current stock levels by SKU/product (read-heavy) ← PARTITION KEY DRIVER
  2. Get recent orders for a product
  3. Get low-stock alerts by warehouse
  4. Record order / Update stock level (write)
- **Partition key decision:** /sku for inventory container (optimizes for query #1 — checking stock by product)
- **Containers:**
  - `inventory` — partition key: `/sku`
  - `orders` — partition key: `/productId`
  - `warehouses` — partition key: `/id`

Proceeding with generation...
