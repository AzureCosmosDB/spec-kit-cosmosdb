from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceExistsError
from src.config import settings

# Singleton client
client = CosmosClient(
    url=settings.cosmos_endpoint,
    credential=settings.cosmos_key,
)


def init_database():
    """Create database and containers if they don't exist."""
    database = client.create_database_if_not_exists(id=settings.database_name)
    
    # Users container - partitioned by user_id
    database.create_container_if_not_exists(
        id="users",
        partition_key=PartitionKey(path="/user_id"),
        offer_throughput=400,
    )
    
    # Tasks container - partitioned by user_id (query pattern: get tasks for a user)
    database.create_container_if_not_exists(
        id="tasks",
        partition_key=PartitionKey(path="/user_id"),
        offer_throughput=400,
    )
    
    return database


def get_database():
    return client.get_database_client(settings.database_name)
