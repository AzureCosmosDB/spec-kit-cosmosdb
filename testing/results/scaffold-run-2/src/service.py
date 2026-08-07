from datetime import datetime
import uuid
from .repository import LeaderboardRepository
from .models import Score, Player


class LeaderboardService:
    def __init__(self):
        self.repo = LeaderboardRepository()

    async def record_score(self, player_id: str, display_name: str, region: str, value: int, game_mode: str = "standard"):
        now = datetime.utcnow()
        iso = now.isocalendar()

        score = Score(
            id=str(uuid.uuid4()),
            player_id=player_id,
            region=region,
            value=value,
            game_mode=game_mode,
            week=iso[1],
            year=iso[0],
            timestamp=now,
        )
        await self.repo.add_score(score)

        player = await self.repo.get_player(player_id, region)
        if player is None:
            player = Player(
                id=player_id,
                player_id=player_id,
                display_name=display_name,
                region=region,
            )
        player.lifetime_score += value
        player.current_week_score += value
        await self.repo.upsert_player(player)
        return score

    async def global_leaderboard(self, limit: int = 100):
        return await self.repo.top_global(limit)

    async def regional_leaderboard(self, region: str, limit: int = 100):
        return await self.repo.top_by_region(region, limit)

    async def perform_weekly_reset(self, regions: list[str]):
        total = 0
        for region in regions:
            total += await self.repo.reset_weekly_scores(region)
        return total
