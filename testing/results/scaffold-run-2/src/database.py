from azure.cosmos.aio import CosmosClient
from .config import get_settings

settings = get_settings()

_cosmos_client: CosmosClient | None = None


def get_client() -> CosmosClient:
    global _cosmos_client
    if _cosmos_client is None:
        _cosmos_client = CosmosClient(
            url=settings.COSMOS_ENDPOINT,
            credential=settings.COSMOS_KEY,
        )
    return _cosmos_client


def get_database():
    return get_client().get_database_client(settings.DATABASE_NAME)


def get_container(name: str):
    return get_database().get_container_client(name)
