"""IoT Telemetry API - FastAPI + Azure Cosmos DB"""
import uuid
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, Field
from azure.cosmos.aio import CosmosClient
from azure.cosmos import exceptions

ENDPOINT = "http://localhost:8081"
KEY = "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
DATABASE_NAME = "iot_db"

client: Optional[CosmosClient] = None
db = None
devices_container = None
telemetry_container = None
alerts_container = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, db, devices_container, telemetry_container, alerts_container
    client = CosmosClient(ENDPOINT, credential=KEY)
    # Create database
    db = await client.create_database_if_not_exists(DATABASE_NAME)
    # Create containers
    devices_container = await db.create_container_if_not_exists(id="devices", partition_key={"paths": ["/id"], "kind": "Hash"})
    telemetry_container = await db.create_container_if_not_exists(
        id="telemetry",
        partition_key={"paths": ["/deviceId"], "kind": "Hash"},
        default_ttl=2592000
    )
    alerts_container = await db.create_container_if_not_exists(id="alerts", partition_key={"paths": ["/deviceId"], "kind": "Hash"})
    yield
    await client.close()


app = FastAPI(lifespan=lifespan)


# Models
class DeviceCreate(BaseModel):
    name: str
    location: Optional[str] = None
    status: str = "active"

class TelemetryReading(BaseModel):
    deviceId: str
    sensorType: str
    value: float
    unit: str
    timestamp: Optional[str] = None
    ttl: Optional[int] = None

class AlertCreate(BaseModel):
    deviceId: str
    severity: str = "warning"
    threshold: float
    actualValue: float
    message: str = ""


@app.get("/api/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/devices", status_code=201)
async def create_device(device: DeviceCreate):
    doc = {
        "id": str(uuid.uuid4()),
        "name": device.name,
        "location": device.location,
        "status": device.status,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    result = await devices_container.create_item(body=doc)
    return result


@app.get("/api/devices")
async def list_devices():
    items = devices_container.query_items(query="SELECT * FROM c", enable_cross_partition_query=True)
    return [item async for item in items]


@app.get("/api/devices/{device_id}")
async def get_device(device_id: str):
    try:
        return await devices_container.read_item(item=device_id, partition_key=device_id)
    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail="Device not found")


@app.post("/api/telemetry/ingest", status_code=201)
async def ingest_telemetry(readings: list[TelemetryReading]):
    count = 0
    for r in readings:
        doc = {
            "id": str(uuid.uuid4()),
            "deviceId": r.deviceId,
            "sensorType": r.sensorType,
            "value": r.value,
            "unit": r.unit,
            "timestamp": r.timestamp or datetime.now(timezone.utc).isoformat(),
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }
        if r.ttl:
            doc["ttl"] = r.ttl
        await telemetry_container.create_item(body=doc)
        count += 1
    return {"accepted": count}


@app.get("/api/devices/{device_id}/telemetry")
async def get_telemetry_range(device_id: str, f: str = Query(..., alias="from"), to: str = Query(...)):
    query = "SELECT * FROM c WHERE c.deviceId = @deviceId AND c.timestamp >= @from AND c.timestamp <= @to ORDER BY c.timestamp DESC"
    parameters = [
        {"name": "@deviceId", "value": device_id},
        {"name": "@from", "value": f},
        {"name": "@to", "value": to},
    ]
    items = telemetry_container.query_items(query=query, parameters=parameters, partition_key=device_id)
    return [item async for item in items]


@app.get("/api/devices/{device_id}/telemetry/latest")
async def get_latest_telemetry(device_id: str):
    query = "SELECT TOP 1 * FROM c WHERE c.deviceId = @deviceId ORDER BY c.timestamp DESC"
    parameters = [{"name": "@deviceId", "value": device_id}]
    items = telemetry_container.query_items(query=query, parameters=parameters, partition_key=device_id)
    results = [item async for item in items]
    if not results:
        raise HTTPException(status_code=404, detail="No telemetry found")
    return results[0]


@app.post("/api/alerts", status_code=201)
async def create_alert(alert: AlertCreate):
    doc = {
        "id": str(uuid.uuid4()),
        "deviceId": alert.deviceId,
        "severity": alert.severity,
        "threshold": alert.threshold,
        "actualValue": alert.actualValue,
        "message": alert.message,
        "acknowledged": False,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    result = await alerts_container.create_item(body=doc)
    return result


@app.get("/api/devices/{device_id}/alerts")
async def get_device_alerts(device_id: str):
    query = "SELECT * FROM c WHERE c.deviceId = @deviceId AND c.acknowledged = false"
    parameters = [{"name": "@deviceId", "value": device_id}]
    items = alerts_container.query_items(query=query, parameters=parameters, partition_key=device_id)
    return [item async for item in items]


@app.post("/api/devices/{device_id}/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(device_id: str, alert_id: str):
    try:
        item = await alerts_container.read_item(item=alert_id, partition_key=device_id)
        item["acknowledged"] = True
        result = await alerts_container.replace_item(item=alert_id, body=item)
        return result
    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail="Alert not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
