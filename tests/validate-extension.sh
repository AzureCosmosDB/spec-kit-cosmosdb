#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")/.."

PASS=0
FAIL=0

echo "=== Validating extension structure ==="

# 1. extension.yml exists
if [ -f extension.yml ]; then echo "✓ extension.yml exists"; ((PASS++)); else echo "FAIL: extension.yml missing"; ((FAIL++)); fi

# 2. Required fields
for field in schema_version "id:" "name:" "version:" "description:"; do
  if grep -q "$field" extension.yml; then ((PASS++)); else echo "FAIL: missing '$field'"; ((FAIL++)); fi
done

# 3. Every command in extension.yml has a file
commands=$(grep '^ *- name: speckit\.cosmosdb\.' extension.yml | sed 's/.*name: //')
for cmd in $commands; do
  if [ -f "commands/${cmd}.md" ]; then ((PASS++)); else echo "FAIL: missing commands/${cmd}.md"; ((FAIL++)); fi
done

# 4. Every file in commands/ is listed in extension.yml
for f in commands/speckit.cosmosdb.*.md; do
  name=$(basename "$f" .md)
  if echo "$commands" | grep -qx "$name"; then ((PASS++)); else echo "FAIL: orphan file $f not in extension.yml"; ((FAIL++)); fi
done

# 5. All command files have frontmatter with description
for f in commands/*.md; do
  if head -1 "$f" | grep -q '^---$' && head -3 "$f" | grep -q 'description:'; then
    ((PASS++))
  else
    echo "FAIL: $(basename "$f") missing frontmatter/description"; ((FAIL++))
  fi
done

echo ""
echo "Results: $PASS passed, $FAIL failed"
if [ "$FAIL" -eq 0 ]; then echo "ALL CHECKS PASSED ✓"; exit 0; else exit 1; fi
