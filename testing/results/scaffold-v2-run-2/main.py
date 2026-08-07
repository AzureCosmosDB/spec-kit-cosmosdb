"""Game Leaderboard API - FastAPI with Azure Cosmos DB"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

from config import settings
from service import ScoreService
from repository import ScoreRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create cosmos client (singleton)
    app.state.cosmos_client = CosmosClient(
        settings.cosmos_endpoint,
        credential=settings.cosmos_key
    )
    app.state.database = app.state.cosmos_client.get_database_client(settings.cosmos_database)
    container = app.state.database.get_container_client("scores")
    app.state.score_repository = ScoreRepository(container)
    app.state.score_service = ScoreService(app.state.score_repository)
    yield
    # Shutdown: close client
    await app.state.cosmos_client.close()


app = FastAPI(title="Game Leaderboard API", lifespan=lifespan)


def get_service(request: Request) -> ScoreService:
    return request.app.state.score_service


@app.get("/api/health")
async def health_check(request: Request):
    """Verify Cosmos DB connectivity."""
    try:
        await request.app.state.cosmos_client.get_database_account()
        return {"status": "healthy"}
    except Exception:
        raise HTTPException(status_code=503, detail="Cosmos DB unavailable")


@app.get("/api/scores")
async def get_global_leaderboard(request: Request, limit: int = 100):
    """Get global top 100 by score. CROSS-PARTITION: global ranking spans all regions."""
    service = get_service(request)
    results = await service.get_global_top(limit)
    return results


@app.get("/api/scores/regions/{region}")
async def get_regional_leaderboard(request: Request, region: str, limit: int = 100):
    """Get regional top 100 by score."""
    service = get_service(request)
    results = await service.get_regional_top(region, limit)
    return results


@app.get("/api/scores/players/{player_id}")
async def get_player_score(request: Request, player_id: str):
    """Get a single player's score and rank."""
    service = get_service(request)
    result = await service.get_player_score(player_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return result


@app.post("/api/scores", status_code=201)
async def submit_score(request: Request):
    """Submit a new score for a player."""
    body = await request.json()
    service = get_service(request)
    try:
        result = await service.submit_score(body)
        return result
    except CosmosHttpResponseError as e:
        if e.status_code == 409:
            raise HTTPException(status_code=409, detail="Conflict")
        if e.status_code == 429:
            raise HTTPException(status_code=429, detail="Too many requests",
                                headers={"Retry-After": str(e.headers.get("x-ms-retry-after-ms", 1000))})
        raise HTTPException(status_code=500, detail="Internal error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
