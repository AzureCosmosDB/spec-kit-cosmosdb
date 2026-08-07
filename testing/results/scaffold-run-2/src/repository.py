from .database import get_container
from .models import Player, Score
from typing import List


SCORES_CONTAINER = "scores"
PLAYERS_CONTAINER = "players"


class LeaderboardRepository:
    """Data access for leaderboard operations. Both containers partitioned by /region."""

    async def add_score(self, score: Score) -> Score:
        container = get_container(SCORES_CONTAINER)
        result = await container.create_item(body=score.model_dump(mode="json"))
        return Score(**result)

    async def get_player(self, player_id: str, region: str) -> Player | None:
        container = get_container(PLAYERS_CONTAINER)
        query = "SELECT * FROM c WHERE c.player_id = @pid AND c.region = @region"
        items = [
            item async for item in container.query_items(
                query=query,
                parameters=[
                    {"name": "@pid", "value": player_id},
                    {"name": "@region", "value": region},
                ],
                partition_key=region,
            )
        ]
        return Player(**items[0]) if items else None

    async def upsert_player(self, player: Player) -> Player:
        container = get_container(PLAYERS_CONTAINER)
        result = await container.upsert_item(body=player.model_dump(mode="json"))
        return Player(**result)

    async def top_global(self, limit: int = 100) -> List[Player]:
        container = get_container(PLAYERS_CONTAINER)
        query = f"SELECT TOP {limit} * FROM c ORDER BY c.lifetime_score DESC"
        items = [
            item async for item in container.query_items(
                query=query,
                enable_cross_partition_query=True,
            )
        ]
        return [Player(**i) for i in items]

    async def top_by_region(self, region: str, limit: int = 100) -> List[Player]:
        container = get_container(PLAYERS_CONTAINER)
        query = f"SELECT TOP {limit} * FROM c WHERE c.region = @region ORDER BY c.lifetime_score DESC"
        items = [
            item async for item in container.query_items(
                query=query,
                parameters=[{"name": "@region", "value": region}],
                partition_key=region,
            )
        ]
        return [Player(**i) for i in items]

    async def reset_weekly_scores(self, region: str) -> int:
        container = get_container(PLAYERS_CONTAINER)
        query = "SELECT * FROM c WHERE c.region = @region AND c.current_week_score > 0"
        count = 0
        async for item in container.query_items(
            query=query,
            parameters=[{"name": "@region", "value": region}],
            partition_key=region,
        ):
            player = Player(**item)
            player.current_week_score = 0
            await container.upsert_item(body=player.model_dump(mode="json"))
            count += 1
        return count
