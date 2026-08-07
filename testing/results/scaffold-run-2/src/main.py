from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from azure.cosmos.exceptions import CosmosHttpResponseError
from .service import LeaderboardService
from .database import get_client

app = FastAPI(title="Leaderboard Service", version="0.1.0")
svc = LeaderboardService()


class ScoreSubmission(BaseModel):
    player_id: str
    display_name: str
    region: str
    value: int
    game_mode: str = "standard"


class WeeklyResetRequest(BaseModel):
    regions: list[str]


@app.exception_handler(CosmosHttpResponseError)
async def handle_cosmos_error(request, exc: CosmosHttpResponseError):
    if exc.status_code == 404:
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    if exc.status_code == 429:
        return JSONResponse(status_code=429, content={"detail": "Rate limited, retry later"})
    return JSONResponse(status_code=500, content={"detail": "Database error"})


@app.get("/health")
async def health():
    client = get_client()
    props = await client.read_account()
    return {"status": "ok", "region": props.get("writableLocations", [{}])[0].get("name", "unknown")}


@app.post("/v1/scores")
async def post_score(body: ScoreSubmission):
    score = await svc.record_score(
        player_id=body.player_id,
        display_name=body.display_name,
        region=body.region,
        value=body.value,
        game_mode=body.game_mode,
    )
    return {"id": score.id, "status": "recorded"}


@app.get("/v1/leaderboard/global")
async def get_global(limit: int = Query(100, le=500)):
    results = await svc.global_leaderboard(limit)
    return [p.model_dump(mode="json") for p in results]


@app.get("/v1/leaderboard/{region}")
async def get_regional(region: str, limit: int = Query(100, le=500)):
    results = await svc.regional_leaderboard(region, limit)
    return [p.model_dump(mode="json") for p in results]


@app.post("/v1/admin/weekly-reset")
async def weekly_reset(body: WeeklyResetRequest):
    count = await svc.perform_weekly_reset(body.regions)
    return {"reset_count": count}
