from azure.cosmos.aio import CosmosClient
from .config import config


class CosmosConnection:
    """Singleton connection manager for Cosmos DB."""

    _instance: "CosmosConnection | None" = None
    _client: CosmosClient | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def client(self) -> CosmosClient:
        if self._client is None:
            self._client = CosmosClient(
                url=config.cosmos_uri,
                credential=config.cosmos_primary_key,
            )
        return self._client

    @property
    def database(self):
        return self.client.get_database_client(config.cosmos_db_name)

    def container(self, name: str):
        return self.database.get_container_client(name)

    async def close(self):
        if self._client:
            await self._client.close()
            self._client = None


cosmos = CosmosConnection()
