from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from ..services.leaderboard_service import LeaderboardService

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])
service = LeaderboardService()


class SubmitScoreRequest(BaseModel):
    player_id: str
    username: str
    region: str
    score: int
    game_mode: str = "classic"


@router.post("/scores")
async def submit_score(request: SubmitScoreRequest):
    result = await service.submit_score(
        player_id=request.player_id,
        username=request.username,
        region=request.region,
        score=request.score,
        game_mode=request.game_mode,
    )
    return {"status": "ok", "score_id": result.id}


@router.get("/rankings/global")
async def global_rankings(limit: int = Query(default=100, le=500)):
    rankings = await service.get_global_rankings(limit)
    return {"rankings": [r.model_dump() for r in rankings]}


@router.get("/rankings/regional/{region}")
async def regional_rankings(region: str, limit: int = Query(default=100, le=500)):
    rankings = await service.get_regional_rankings(region, limit)
    return {"rankings": [r.model_dump() for r in rankings]}


@router.post("/weekly-reset")
async def weekly_reset():
    await service.weekly_reset()
    return {"status": "reset_complete"}
