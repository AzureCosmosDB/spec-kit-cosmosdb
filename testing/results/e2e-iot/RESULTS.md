# E2E IoT Scaffold Test Results

**Date:** 2026-07-27T17:36 UTC  
**Emulator:** Cosmos DB Linux emulator at http://localhost:8081  
**Framework:** Python/FastAPI + azure-cosmos (async)

## Summary: ✅ ALL TESTS PASSED

## Test Results

| # | Test | Result |
|---|------|--------|
| 1 | Health check | ✅ `{"status":"healthy"}` |
| 2 | Register device | ✅ Device created with UUID |
| 3 | Ingest bulk telemetry (3 readings) | ✅ `{"accepted":3}` |
| 4 | Query by device + time range | ✅ 3 readings returned |
| 5 | Get latest telemetry | ✅ Returns most recent reading |
| 6 | Create alert | ✅ Alert created with severity/threshold |
| 7 | Get active alerts | ✅ 1 active alert |
| 8 | Acknowledge alert | ✅ `acknowledged: True` |
| 9 | Verify resolved | ✅ 0 active alerts after ack |

## Architecture Validated

- **Partition keys:** `/id` for devices, `/deviceId` for telemetry and alerts
- **TTL:** 30-day default on telemetry container
- **Bulk ingest:** Array endpoint, parameterized queries
- **Time-range queries:** Mandatory `from`/`to` with parameterized SQL
- **Layered:** FastAPI routes → service logic → Cosmos SDK
- **Client lifecycle:** Singleton CosmosClient, closed on shutdown

## Containers Created

- `iot_db.devices` (PK: `/id`)
- `iot_db.telemetry` (PK: `/deviceId`, TTL: 2592000s)
- `iot_db.alerts` (PK: `/deviceId`)
