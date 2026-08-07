from datetime import datetime
import uuid
from .repository import LeaderboardRepository
from .models import LeaderboardEntry


class GameService:
    def __init__(self):
        self.repo = LeaderboardRepository()

    async def submit_score(self, player_id: str, player_name: str, region: str, score: int, game_mode: str):
        now = datetime.utcnow()
        iso = now.isocalendar()
        region_week = f"{region}_{iso[0]}W{iso[1]:02d}"

        entry = LeaderboardEntry(
            id=str(uuid.uuid4()),
            player_id=player_id,
            player_name=player_name,
            region=region,
            region_week=region_week,
            score=score,
            game_mode=game_mode,
            week=iso[1],
            year=iso[0],
            submitted_at=now,
        )
        await self.repo.insert_entry(entry)

        # Update player aggregate
        player = await self.repo.get_or_create_player(player_id, player_name, region)
        player.all_time_score += score
        player.games_count += 1
        if score > player.weekly_high:
            player.weekly_high = score
        await self.repo.update_player(player)

        return entry

    async def get_global_leaderboard(self, limit: int = 100):
        return await self.repo.get_global_top(limit)

    async def get_regional_leaderboard(self, region: str, limit: int = 100):
        now = datetime.utcnow()
        iso = now.isocalendar()
        return await self.repo.get_regional_weekly(region, iso[1], iso[0], limit)
