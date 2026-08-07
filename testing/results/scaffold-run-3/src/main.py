from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from azure.cosmos.exceptions import CosmosHttpResponseError
from .service import GameService
from .cosmos import cosmos

app = FastAPI(title="Mobile Game Leaderboard", version="2.0.0")
game_svc = GameService()


class SubmitRequest(BaseModel):
    player_id: str
    player_name: str
    region: str
    score: int
    game_mode: str = "battle_royale"


@app.exception_handler(CosmosHttpResponseError)
async def cosmos_error(request, exc: CosmosHttpResponseError):
    mapping = {404: 404, 409: 409, 429: 503}
    return JSONResponse(
        status_code=mapping.get(exc.status_code, 500),
        content={"error": str(exc.message), "code": exc.status_code},
    )


@app.get("/healthz")
async def healthz():
    await cosmos.client.read_account()
    return {"healthy": True}


@app.post("/api/scores")
async def submit(body: SubmitRequest):
    entry = await game_svc.submit_score(
        player_id=body.player_id,
        player_name=body.player_name,
        region=body.region,
        score=body.score,
        game_mode=body.game_mode,
    )
    return {"id": entry.id}


@app.get("/api/rankings/global")
async def global_rankings(limit: int = Query(100, le=1000)):
    results = await game_svc.get_global_leaderboard(limit)
    return [r.model_dump(mode="json") for r in results]


@app.get("/api/rankings/{region}")
async def regional_rankings(region: str, limit: int = Query(100, le=1000)):
    results = await game_svc.get_regional_leaderboard(region, limit)
    return [r.model_dump(mode="json") for r in results]


@app.on_event("shutdown")
async def shutdown():
    await cosmos.close()
