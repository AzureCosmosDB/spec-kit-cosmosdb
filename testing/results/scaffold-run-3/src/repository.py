from datetime import datetime
from typing import List, Optional
from .cosmos import cosmos
from .models import LeaderboardEntry, PlayerAggregate, GlobalRanking


class LeaderboardRepository:
    ENTRIES = "leaderboard"
    PLAYERS = "players"
    GLOBAL = "global_rankings"

    async def insert_entry(self, entry: LeaderboardEntry) -> LeaderboardEntry:
        container = cosmos.container(self.ENTRIES)
        result = await container.create_item(body=entry.model_dump(mode="json"))
        return LeaderboardEntry(**result)

    async def get_regional_weekly(self, region: str, week: int, year: int, limit: int = 100) -> List[LeaderboardEntry]:
        partition = f"{region}_{year}W{week:02d}"
        container = cosmos.container(self.ENTRIES)
        query = f"SELECT TOP {limit} * FROM c ORDER BY c.score DESC"
        results = []
        async for item in container.query_items(query=query, partition_key=partition):
            results.append(LeaderboardEntry(**item))
        return results

    async def get_or_create_player(self, player_id: str, player_name: str, region: str) -> PlayerAggregate:
        container = cosmos.container(self.PLAYERS)
        try:
            item = await container.read_item(item=player_id, partition_key=player_id)
            return PlayerAggregate(**item)
        except Exception:
            player = PlayerAggregate(
                id=player_id,
                player_id=player_id,
                player_name=player_name,
                region=region,
            )
            result = await container.create_item(body=player.model_dump(mode="json"))
            return PlayerAggregate(**result)

    async def update_player(self, player: PlayerAggregate):
        container = cosmos.container(self.PLAYERS)
        await container.upsert_item(body=player.model_dump(mode="json"))

    async def get_global_top(self, limit: int = 100) -> List[GlobalRanking]:
        container = cosmos.container(self.GLOBAL)
        # Top 100 are all in bucket 0
        query = f"SELECT TOP {limit} * FROM c ORDER BY c.rank ASC"
        results = []
        async for item in container.query_items(query=query, partition_key=0):
            results.append(GlobalRanking(**item))
        return results
