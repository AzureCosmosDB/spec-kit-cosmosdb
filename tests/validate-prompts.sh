#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")/.."

PASS=0
FAIL=0
WARN=0

echo "=== Validating prompt quality ==="

for f in commands/speckit.cosmosdb.*.md; do
  name=$(basename "$f" .md)

  # Check not empty
  if [ "$(wc -c < "$f")" -lt 10 ]; then
    echo "FAIL: $name is empty/near-empty"; ((FAIL++)); continue
  fi

  # Valid frontmatter
  if ! head -1 "$f" | grep -q '^---$'; then
    echo "FAIL: $name has broken frontmatter"; ((FAIL++)); continue
  fi
  ((PASS++))

  # Scaffold commands should reference user_agent_suffix
  if echo "$name" | grep -q 'scaffold'; then
    if grep -qi 'user_agent_suffix\|ApplicationName' "$f"; then
      ((PASS++))
    else
      echo "WARN: $name (scaffold) does not reference user_agent_suffix"; ((WARN++))
    fi
  fi
done

echo ""
echo "Results: $PASS passed, $FAIL failed, $WARN warnings"
if [ "$FAIL" -eq 0 ]; then echo "ALL CHECKS PASSED ✓"; exit 0; else exit 1; fi
