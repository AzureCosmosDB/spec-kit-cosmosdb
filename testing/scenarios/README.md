# Test Scenarios

## What is a Scenario?

A scenario is a reproducible test case consisting of:

1. **A prompt template** — which template to execute
2. **Fixed input variables** — deterministic inputs that don't change between runs
3. **Expected structural invariants** — what must remain consistent across N runs

## Scenario File Format

```json
{
  "name": "ecommerce-order-container",
  "template": "prompts/design-container/prompt.yaml",
  "variables": {
    "entity": "e-commerce order with line items, shipping address, payment info",
    "access_patterns": [
      "get order by ID",
      "list orders by customer sorted by date",
      "get all orders in date range for reporting"
    ]
  },
  "invariants": {
    "partition_keys": {
      "must_include": ["customerId"],
      "must_not_include": ["createdAt"]
    },
    "field_names": {
      "must_include": ["orderId", "customerId", "items"]
    },
    "patterns": {
      "must_include": ["denormalization"]
    }
  },
  "min_consistency": 0.85
}
```

## Running Scenarios

```bash
# Run a single scenario
python testing/harness/run-iterations.py \
  --template prompts/design-container/prompt.yaml \
  --variables "$(jq -c .variables testing/scenarios/ecommerce-order.scenario.json)" \
  --iterations 5 --model gpt-4o

# Run all scenarios (bash loop)
for f in testing/scenarios/*.scenario.json; do
  vars=$(jq -c .variables "$f")
  tmpl=$(jq -r .template "$f")
  python testing/harness/run-iterations.py -t "$tmpl" -v "$vars" -n 5 -m gpt-4o \
    -o "testing/reports/$(basename "$f" .scenario.json)-$(date +%s).json"
done
```

## Mapping to Prompt Templates

| Scenario | Template | Key Invariants |
|----------|----------|----------------|
| `ecommerce-order` | `design-container` | PK=customerId, embed line items |
| `iot-telemetry` | `design-container` | PK=deviceId, TTL, time-series pattern |
| `multi-tenant-saas` | `design-container` | PK=tenantId, hierarchical partition key |
| `social-feed` | `design-container` | PK=userId, change feed for fan-out |
| `product-catalog` | `design-container` | PK=categoryId, vector search |

## Writing Good Invariants

- Focus on **architectural decisions**, not wording
- Partition key choice is the highest-signal invariant
- Field names should only check critical fields (not every property)
- Pattern detection should check the primary pattern, not every mention
- Set `min_consistency` lower (0.7) for open-ended prompts, higher (0.95) for constrained ones
