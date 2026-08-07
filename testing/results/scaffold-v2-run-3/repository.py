"""Cosmos DB repository for score operations."""
from azure.cosmos.aio import ContainerProxy
from azure.cosmos.exceptions import CosmosResourceNotFoundError


class ScoreRepository:
    """Data access layer for the scores container."""

    def __init__(self, container: ContainerProxy):
        self._container = container

    async def get_global_top(self, limit: int = 100) -> list[dict]:
        """Get global top scores. CROSS-PARTITION: global ranking requires all regions."""
        query = "SELECT TOP @limit c.playerId, c.playerName, c.region, c.score FROM c ORDER BY c.score DESC"
        parameters = [{"name": "@limit", "value": limit}]
        items = self._container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True  # CROSS-PARTITION: global ranking
        )
        return [item async for item in items]

    async def get_regional_top(self, region: str, limit: int = 100) -> list[dict]:
        """Get top scores for a specific region."""
        query = "SELECT TOP @limit c.playerId, c.playerName, c.region, c.score FROM c WHERE c.region = @region ORDER BY c.score DESC"
        parameters = [
            {"name": "@limit", "value": limit},
            {"name": "@region", "value": region}
        ]
        items = self._container.query_items(
            query=query,
            parameters=parameters,
            partition_key=region
        )
        return [item async for item in items]

    async def get_player_score(self, player_id: str) -> dict | None:
        """Get a player's best score. CROSS-PARTITION: player lookup across all regions."""
        query = "SELECT TOP 1 c.id, c.playerId, c.playerName, c.region, c.score FROM c WHERE c.playerId = @playerId ORDER BY c.score DESC"
        parameters = [{"name": "@playerId", "value": player_id}]
        items = self._container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True  # CROSS-PARTITION: player lookup across regions
        )
        results = [item async for item in items]
        return results[0] if results else None

    async def create_score(self, item: dict) -> dict:
        """Create a new score entry."""
        return await self._container.create_item(body=item)

    async def get_player_rank(self, score: int) -> int:
        """Get global rank for a given score. CROSS-PARTITION: counting all higher scores."""
        query = "SELECT VALUE COUNT(1) FROM c WHERE c.score > @score"
        parameters = [{"name": "@score", "value": score}]
        items = self._container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True  # CROSS-PARTITION: global rank calculation
        )
        results = [item async for item in items]
        return results[0] + 1 if results else 1
