## Intent Analysis

- **Matched scaffold:** cosmos.scaffold-social
  - *Reasoning:* The platform connects two user types (shelters and adopters) with content (animal listings) and interactions (applications). This is fundamentally a social/marketplace pattern. "Browse" maps to feed, "apply" maps to engagement.
  - *Secondary influence:* cosmos.scaffold-ecommerce (listing/browse pattern)
- **Inferred language:** Python (FastAPI)
- **Inferred scale:** ~100K users, ~10M documents
- **Generated query patterns:**
  1. Get all animals for a shelter (read-heavy) ← PARTITION KEY DRIVER
  2. Get all available animals by species
  3. Get application status for a user
  4. Create listing / Submit application (write)
- **Partition key decision:** /shelterId (optimizes for query #1 — shelter dashboard showing their animals is the most frequent view)
- **Containers:**
  - `shelters` — partition key: `/id`
  - `animals` — partition key: `/shelterId`
  - `applications` — partition key: `/animalId`

Proceeding with generation...
