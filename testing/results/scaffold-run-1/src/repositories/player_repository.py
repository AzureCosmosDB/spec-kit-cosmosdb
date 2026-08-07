from ..config.cosmos_client import get_players_container
from ..models.player import PlayerDocument


class PlayerRepository:
    async def upsert_player(self, player: PlayerDocument) -> PlayerDocument:
        container = await get_players_container()
        result = await container.upsert_item(body=player.model_dump())
        return PlayerDocument(**result)

    async def get_player(self, player_id: str, region: str) -> PlayerDocument | None:
        container = await get_players_container()
        try:
            result = await container.read_item(item=player_id, partition_key=region)
            return PlayerDocument(**result)
        except Exception:
            return None

    async def get_regional_leaderboard(self, region: str, limit: int = 100) -> list[PlayerDocument]:
        container = await get_players_container()
        query = "SELECT TOP @limit * FROM c WHERE c.region = @region ORDER BY c.total_score DESC"
        items = container.query_items(
            query=query,
            parameters=[
                {"name": "@region", "value": region},
                {"name": "@limit", "value": limit},
            ],
            partition_key=region,
        )
        return [PlayerDocument(**item) async for item in items]

    async def get_global_leaderboard(self, limit: int = 100) -> list[PlayerDocument]:
        container = await get_players_container()
        query = "SELECT TOP @limit * FROM c ORDER BY c.total_score DESC"
        items = container.query_items(
            query=query,
            parameters=[{"name": "@limit", "value": limit}],
            enable_cross_partition_query=True,
        )
        return [PlayerDocument(**item) async for item in items]
