"""Order & Inventory Tracker — Cosmos Intent SDK"""
from fastapi import FastAPI
from app.config.cosmos import get_cosmos_client
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.cosmos = get_cosmos_client()
    yield
    await app.state.cosmos.close()

app = FastAPI(title="Order & Inventory Tracker", lifespan=lifespan)

@app.get("/api/health")
async def health(): return {"status": "healthy"}
