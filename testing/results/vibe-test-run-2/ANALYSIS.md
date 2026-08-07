## Intent Analysis

- **Matched scaffold:** cosmos.scaffold-ecommerce
  - *Reasoning:* "shelters can list animals" → sellers listing products; "browse" → catalog browsing; "apply to adopt" → order/checkout flow analog. The browse-and-acquire pattern maps closely to ecommerce.
  - *Secondary influence:* cosmos.scaffold-social (community/profile aspects)
- **Inferred language:** Python (FastAPI)
- **Inferred scale:** ~100K users, ~10M documents
- **Generated query patterns:**
  1. Browse available animals by category/location (read-heavy) ← PARTITION KEY DRIVER
  2. Get animal details by ID
  3. Get all applications submitted by a user
  4. List animal / Submit adoption application (write)
- **Partition key decision:** /category (optimizes for query #1 — most frequent read is browsing by animal type: dogs, cats, etc.)
- **Containers:**
  - `shelters` — partition key: `/region`
  - `animals` — partition key: `/category`
  - `applications` — partition key: `/applicantId`

Proceeding with generation...
