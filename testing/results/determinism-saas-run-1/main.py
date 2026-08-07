"""Multi-Tenant SaaS Platform API - Azure Cosmos DB"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from config import get_settings
from repository import TenantRepository, TenantDataRepository
from service import TenantService, UserService, SubscriptionService, UsageService
from middleware import validate_tenant
from azure.cosmos.aio import CosmosClient

settings = get_settings()
cosmos_client = None
tenant_service = None
user_service = None
subscription_service = None
usage_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global cosmos_client, tenant_service, user_service, subscription_service, usage_service
    cosmos_client = CosmosClient(settings.cosmos_endpoint, settings.cosmos_key)
    database = cosmos_client.get_database_client(settings.cosmos_database)
    
    tenant_repo = TenantRepository(database.get_container_client("tenants"))
    tenant_data_repo = TenantDataRepository(database.get_container_client("tenantData"))
    
    tenant_service = TenantService(tenant_repo)
    user_service = UserService(tenant_data_repo)
    subscription_service = SubscriptionService(tenant_data_repo)
    usage_service = UsageService(tenant_data_repo)
    
    yield
    
    await cosmos_client.close()


app = FastAPI(title="SaaS Platform", lifespan=lifespan)


@app.get("/api/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/tenants/{tenant_id}/users")
async def get_tenant_users(tenant_id: str):
    users = await user_service.get_users_for_tenant(tenant_id)
    return users


@app.post("/api/tenants/{tenant_id}/users", status_code=201)
async def create_user(tenant_id: str, user: dict):
    result = await user_service.create_user(tenant_id, user)
    return result


@app.get("/api/tenants/{tenant_id}/subscription")
async def get_subscription(tenant_id: str):
    sub = await subscription_service.get_subscription(tenant_id)
    return sub


@app.patch("/api/tenants/{tenant_id}/subscription")
async def update_subscription(tenant_id: str, update: dict):
    result = await subscription_service.update_subscription(tenant_id, update)
    return result


@app.get("/api/tenants/{tenant_id}/usage")
async def get_usage(tenant_id: str, from_date: str = None, to_date: str = None):
    metrics = await usage_service.get_usage_metrics(tenant_id, from_date, to_date)
    return metrics


@app.post("/api/tenants/{tenant_id}/usage/record", status_code=201)
async def record_usage(tenant_id: str, metric: dict):
    result = await usage_service.record_metric(tenant_id, metric)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
