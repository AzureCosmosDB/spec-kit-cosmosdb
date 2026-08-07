"""Pet Adoption Platform — Cosmos Intent SDK (cosmos.scaffold-social)"""
from fastapi import FastAPI
from app.routers import shelters, animals, applications
from app.config.cosmos import get_cosmos_client
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.cosmos = get_cosmos_client()
    yield
    await app.state.cosmos.close()

app = FastAPI(title="Pet Adoption Platform", lifespan=lifespan)
app.include_router(shelters.router, prefix="/api/shelters", tags=["shelters"])
app.include_router(animals.router, prefix="/api/animals", tags=["animals"])
app.include_router(applications.router, prefix="/api/applications", tags=["applications"])

@app.get("/api/health")
async def health(): return {"status": "healthy"}
