"""Business logic layer for the leaderboard."""
from datetime import datetime, timezone
from uuid import uuid4

from repository import ScoreRepository
from models import ScoreDocument, ScoreSubmission


class ScoreService:
    """Service layer for score operations."""

    def __init__(self, repository: ScoreRepository):
        self._repository = repository

    async def get_global_top(self, limit: int = 100) -> list[dict]:
        """Get global top scores."""
        return await self._repository.get_global_top(limit)

    async def get_regional_top(self, region: str, limit: int = 100) -> list[dict]:
        """Get regional top scores."""
        return await self._repository.get_regional_top(region, limit)

    async def get_player_score(self, player_id: str) -> dict | None:
        """Get player's score and rank."""
        score_data = await self._repository.get_player_score(player_id)
        if score_data is None:
            return None
        rank = await self._repository.get_player_rank(score_data["score"])
        return {
            "playerId": score_data["playerId"],
            "playerName": score_data["playerName"],
            "region": score_data["region"],
            "score": score_data["score"],
            "globalRank": rank
        }

    async def submit_score(self, body: dict) -> dict:
        """Submit a new score."""
        submission = ScoreSubmission(**body)
        now = datetime.now(timezone.utc).isoformat()
        doc = ScoreDocument(
            id=str(uuid4()),
            playerId=submission.player_id,
            playerName=submission.player_name,
            region=submission.region,
            score=submission.score,
            week=self._current_week(),
            createdAt=now,
            updatedAt=now
        )
        result = await self._repository.create_score(doc.model_dump(by_alias=True))
        return result

    @staticmethod
    def _current_week() -> str:
        """Get current ISO week string for weekly resets."""
        now = datetime.now(timezone.utc)
        return f"{now.year}-W{now.isocalendar()[1]:02d}"
