## Intent Analysis

- **Matched scaffold:** cosmos.scaffold-social
  - *Reasoning:* "shelters can list animals" → profiles + posts pattern; "browse" → feed pattern; "apply to adopt" → interaction (like comments/follows). Social scaffold best captures the entity relationships (shelters as profiles, animals as posts, applications as interactions).
  - *Secondary influence:* cosmos.scaffold-ecommerce (browse/catalog pattern)
- **Inferred language:** Python (FastAPI)
- **Inferred scale:** ~100K users, ~10M documents
- **Generated query patterns:**
  1. Get all animals listed by a specific shelter (read-heavy) ← PARTITION KEY DRIVER
  2. Browse all available animals by species/breed (cross-partition, filtered)
  3. Get all applications for a specific animal
  4. Create new animal listing / Submit adoption application (write)
- **Partition key decision:** /shelterId (optimizes for query #1 — most frequent read is "show me this shelter's animals")
- **Containers:**
  - `shelters` — partition key: `/id`
  - `animals` — partition key: `/shelterId`
  - `applications` — partition key: `/animalId`

Proceeding with generation...
