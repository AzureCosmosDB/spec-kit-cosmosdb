"""
Cosmos DB Query: Top 10 most recent orders for a customer
Container: orders
Partition Key: /customerId
Projection: orderId, status, total, createdAt
"""

from azure.cosmos import ContainerProxy


# --- SQL Query ---

QUERY = (
    "SELECT c.orderId, c.status, c.total, c.createdAt "
    "FROM c "
    "WHERE c.customerId = @customerId "
    "ORDER BY c.createdAt DESC "
    "OFFSET 0 LIMIT 10"
)

PARAMETERS = [
    {"name": "@customerId", "value": None}  # Set at runtime
]


def get_recent_orders(container: ContainerProxy, customer_id: str) -> list[dict]:
    """
    Find the top 10 most recent orders for a customer.

    Query characteristics:
    - Partition-scoped (customerId in WHERE + passed as partition_key)
    - Projected fields only (no SELECT *)
    - Bounded results via LIMIT
    - Requires composite index on (customerId ASC, createdAt DESC)

    Estimated RU cost: 3-5 RUs (single-partition, indexed ORDER BY, small result set)

    Args:
        container: Cosmos DB container proxy.
        customer_id: The customer's ID (partition key value).

    Returns:
        List of order dicts with orderId, status, total, createdAt.
    """
    parameters = [{"name": "@customerId", "value": customer_id}]

    results = container.query_items(
        query=QUERY,
        parameters=parameters,
        partition_key=customer_id,
        max_item_count=10,
    )
    return list(results)


# --- Required Indexing Policy ---

REQUIRED_INDEXING = {
    "includedPaths": [
        {"path": "/customerId/?"},
        {"path": "/createdAt/?"},
        {"path": "/orderId/?"},
        {"path": "/status/?"},
        {"path": "/total/?"},
    ],
    "compositeIndexes": [
        [
            {"path": "/customerId", "order": "ascending"},
            {"path": "/createdAt", "order": "descending"},
        ]
    ],
}
