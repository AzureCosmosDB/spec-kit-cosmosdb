"""CosmosClient singleton. Retry: max 9, 30s max on 429s."""
import os
from azure.cosmos.aio import CosmosClient
_client = None
def get_cosmos_client() -> CosmosClient:
    global _client
    if _client is None:
        _client = CosmosClient(
            url=os.environ["COSMOS_ENDPOINT"],
            credential=os.environ["COSMOS_KEY"],
            user_agent_suffix="cosmos-intent-sdk/0.1.0",
            retry_total=9, retry_backoff_max=30,
        )
    return _client
