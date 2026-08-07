from azure.cosmos.exceptions import CosmosHttpResponseError
from ..config.cosmos_client import get_scores_container
from ..models.score import ScoreDocument


class ScoreRepository:
    async def create_score(self, score: ScoreDocument) -> ScoreDocument:
        container = await get_scores_container()
        result = await container.create_item(body=score.model_dump())
        return ScoreDocument(**result)

    async def get_player_scores(self, player_id: str, limit: int = 50) -> list[ScoreDocument]:
        container = await get_scores_container()
        query = "SELECT TOP @limit * FROM c WHERE c.player_id = @player_id ORDER BY c.score DESC"
        items = container.query_items(
            query=query,
            parameters=[
                {"name": "@player_id", "value": player_id},
                {"name": "@limit", "value": limit},
            ],
            partition_key=player_id,
        )
        return [ScoreDocument(**item) async for item in items]

    async def get_weekly_top_scores(self, week_number: int, year: int, limit: int = 100) -> list[ScoreDocument]:
        container = await get_scores_container()
        query = """
            SELECT TOP @limit * FROM c 
            WHERE c.week_number = @week AND c.year = @year 
            ORDER BY c.score DESC
        """
        items = container.query_items(
            query=query,
            parameters=[
                {"name": "@week", "value": week_number},
                {"name": "@year", "value": year},
                {"name": "@limit", "value": limit},
            ],
            enable_cross_partition_query=True,
        )
        return [ScoreDocument(**item) async for item in items]
