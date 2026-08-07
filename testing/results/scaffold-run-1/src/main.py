from fastapi import FastAPI
from azure.cosmos.exceptions import CosmosHttpResponseError
from .config.cosmos_client import get_cosmos_client
from .handlers.leaderboard_routes import router as leaderboard_router
from .middleware.error_handler import cosmos_exception_handler

app = FastAPI(title="Game Leaderboard API", version="1.0.0")

app.add_exception_handler(CosmosHttpResponseError, cosmos_exception_handler)
app.include_router(leaderboard_router)


@app.get("/health")
async def health_check():
    try:
        client = get_cosmos_client()
        await client.read_account()  # Verifies connectivity
        return {"status": "healthy", "cosmos": "connected"}
    except Exception as e:
        return JSONResponse(status_code=503, content={"status": "unhealthy", "error": str(e)})


@app.on_event("shutdown")
async def shutdown():
    client = get_cosmos_client()
    await client.close()
