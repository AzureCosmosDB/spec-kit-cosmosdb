#!/usr/bin/env bash
set -euo pipefail

# Integration test — requires spec-kit (specify) to be installed
if ! command -v specify &>/dev/null; then
  echo "SKIP: 'specify' CLI not found. Install spec-kit first."
  exit 0
fi

EXTENSION_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

echo "=== Integration test ==="

cd "$TMPDIR"
specify init test-project --integration copilot
cd test-project

specify extension add cosmosdb --from "$EXTENSION_DIR"

# Verify commands appear
OUTPUT=$(specify extension list 2>&1)
if echo "$OUTPUT" | grep -q "cosmosdb"; then
  echo "✓ Extension installed and visible"
else
  echo "FAIL: Extension not visible in 'specify extension list'"
  exit 1
fi

echo "ALL INTEGRATION CHECKS PASSED ✓"
