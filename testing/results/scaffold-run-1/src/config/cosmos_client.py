from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from .settings import settings

_client: AsyncCosmosClient | None = None


def get_cosmos_client() -> AsyncCosmosClient:
    """Singleton CosmosClient instance."""
    global _client
    if _client is None:
        _client = AsyncCosmosClient(
            url=settings.cosmos_endpoint,
            credential=settings.cosmos_key,
            connection_retry_policy={
                "retry_total": 9,
                "retry_backoff_max": 30,
            },
        )
    return _client


async def get_database():
    client = get_cosmos_client()
    return client.get_database_client(settings.cosmos_database)


async def get_scores_container():
    db = await get_database()
    return db.get_container_client("scores")


async def get_players_container():
    db = await get_database()
    return db.get_container_client("players")
