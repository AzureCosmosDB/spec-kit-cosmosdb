#!/usr/bin/env bash
set -e
BASE="http://localhost:8000"

echo "=== IoT E2E Test ==="

echo "1. Health check"
curl -sf "$BASE/api/health" && echo " OK"

echo "2. Register device"
DEV=$(curl -sf -X POST "$BASE/api/devices" -H "Content-Type: application/json" -d '{"name":"sensor-01","location":"warehouse","status":"active"}')
DEVICE_ID=$(echo "$DEV" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "  Device ID: $DEVICE_ID"

echo "3. Ingest bulk telemetry"
READINGS='[
  {"deviceId":"'$DEVICE_ID'","sensorType":"temperature","value":23.5,"unit":"celsius","timestamp":"2026-07-27T10:00:00Z"},
  {"deviceId":"'$DEVICE_ID'","sensorType":"temperature","value":24.1,"unit":"celsius","timestamp":"2026-07-27T11:00:00Z"},
  {"deviceId":"'$DEVICE_ID'","sensorType":"humidity","value":65.2,"unit":"percent","timestamp":"2026-07-27T12:00:00Z"}
]'
INGEST=$(curl -sf -X POST "$BASE/api/telemetry/ingest" -H "Content-Type: application/json" -d "$READINGS")
echo "  Ingest result: $INGEST"

echo "4. Query telemetry by device (time range)"
RANGE=$(curl -sf "$BASE/api/devices/$DEVICE_ID/telemetry?from=2026-07-27T00:00:00Z&to=2026-07-27T23:59:59Z")
COUNT=$(echo "$RANGE" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")
echo "  Readings in range: $COUNT"

echo "5. Get latest telemetry"
LATEST=$(curl -sf "$BASE/api/devices/$DEVICE_ID/telemetry/latest")
echo "  Latest: $(echo $LATEST | python3 -c "import sys,json;d=json.load(sys.stdin);print(f'{d[\"sensorType\"]}={d[\"value\"]}')")"

echo "6. Create alert"
ALERT=$(curl -sf -X POST "$BASE/api/alerts" -H "Content-Type: application/json" -d '{"deviceId":"'$DEVICE_ID'","severity":"critical","threshold":30.0,"actualValue":35.2,"message":"Temp exceeded"}')
ALERT_ID=$(echo "$ALERT" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "  Alert ID: $ALERT_ID"

echo "7. Get active alerts for device"
ALERTS=$(curl -sf "$BASE/api/devices/$DEVICE_ID/alerts")
ALERT_COUNT=$(echo "$ALERTS" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")
echo "  Active alerts: $ALERT_COUNT"

echo "8. Acknowledge alert"
ACK=$(curl -sf -X POST "$BASE/api/devices/$DEVICE_ID/alerts/$ALERT_ID/acknowledge")
ACK_STATUS=$(echo "$ACK" | python3 -c "import sys,json; print(json.load(sys.stdin)['acknowledged'])")
echo "  Acknowledged: $ACK_STATUS"

echo "9. Verify no active alerts after acknowledge"
ALERTS2=$(curl -sf "$BASE/api/devices/$DEVICE_ID/alerts")
ALERT_COUNT2=$(echo "$ALERTS2" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")
echo "  Active alerts after ack: $ALERT_COUNT2"

echo ""
echo "=== ALL IoT TESTS PASSED ==="
