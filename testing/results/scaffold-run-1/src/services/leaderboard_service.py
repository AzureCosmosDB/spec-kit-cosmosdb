from datetime import datetime
import uuid
from ..repositories.score_repository import ScoreRepository
from ..repositories.player_repository import PlayerRepository
from ..models.score import ScoreDocument
from ..models.player import PlayerDocument


class LeaderboardService:
    def __init__(self):
        self.score_repo = ScoreRepository()
        self.player_repo = PlayerRepository()

    async def submit_score(self, player_id: str, username: str, region: str, score: int, game_mode: str) -> ScoreDocument:
        now = datetime.utcnow()
        iso_calendar = now.isocalendar()

        score_doc = ScoreDocument(
            id=str(uuid.uuid4()),
            player_id=player_id,
            score=score,
            game_mode=game_mode,
            region=region,
            week_number=iso_calendar[1],
            year=iso_calendar[0],
            submitted_at=now,
        )
        await self.score_repo.create_score(score_doc)

        # Update player aggregate
        player = await self.player_repo.get_player(player_id, region)
        if player is None:
            player = PlayerDocument(
                id=player_id,
                player_id=player_id,
                username=username,
                region=region,
            )
        player.total_score += score
        player.weekly_score += score
        player.games_played += 1
        player.last_active = now
        await self.player_repo.upsert_player(player)

        return score_doc

    async def get_global_rankings(self, limit: int = 100) -> list[PlayerDocument]:
        return await self.player_repo.get_global_leaderboard(limit)

    async def get_regional_rankings(self, region: str, limit: int = 100) -> list[PlayerDocument]:
        return await self.player_repo.get_regional_leaderboard(region, limit)

    async def weekly_reset(self):
        """Reset weekly scores for all players. Should be called by a scheduled job."""
        # Cross-partition query to get all players - acceptable for weekly batch
        players = await self.player_repo.get_global_leaderboard(limit=10000)
        for player in players:
            player.weekly_score = 0
            await self.player_repo.upsert_player(player)
