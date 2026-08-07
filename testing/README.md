# Determinism Testing Framework

## Problem

LLM outputs are non-deterministic. When a prompt asks "design a container for an e-commerce order system," two runs may produce different wording but should agree on **structural decisions**: the same partition key, same field names, same architectural patterns.

## Approach

Run each prompt template **N times** with identical inputs. Compare outputs not for exact text match, but for **structural consistency** — the invariants that matter for correctness.

## What We Measure

| Feature Type | Example | Extraction Method |
|---|---|---|
| Partition key choices | `/orderId`, `/customerId` | Regex + JSON path extraction |
| Field names | `orderId`, `createdAt`, `items[]` | Parse generated schemas |
| Architectural patterns | Event sourcing, change feed | Keyword/phrase detection |
| SDK patterns | Bulk operations, transactional batch | Code block analysis |
| Index recommendations | Composite index on (tenantId, createdAt) | Structured section parsing |
| Consistency level | Session, Eventual | Enum detection |

## Scoring

```
consistency_score = matching_invariants / total_invariants
```

- **1.0** = perfect structural agreement across all N runs
- **≥ 0.9** = acceptable for production prompt templates
- **< 0.7** = prompt needs refinement (too ambiguous, under-constrained)

## Usage

```bash
# Run 5 iterations of the design-container prompt
python testing/harness/run-iterations.py \
  --template prompts/design-container/prompt.yaml \
  --variables '{"entity": "e-commerce orders", "access_patterns": ["by customer", "by date range"]}' \
  --iterations 5 \
  --model gpt-4o

# Output: a JSON report at the path supplied with --output
```

## Directory Structure

```
testing/
├── README.md              # This file
├── harness/
│   └── run-iterations.py  # Test runner
├── scenarios/
│   └── README.md          # Scenario format documentation
└── results/               # Retained comparisons, generated source, and E2E evidence
```

Do not commit local execution residue under `results/`. Virtual environments, `__pycache__` directories, bytecode, and runtime logs are reproducible and ignored by Git. Keep generated source, dependency manifests, test scripts, and concise result reports when they provide evidence for a compatibility or determinism claim.

## Interpreting Results

The JSON report contains per-feature consistency and an overall score. Low-scoring features indicate where prompts are ambiguous and need additional rules or constraints.
