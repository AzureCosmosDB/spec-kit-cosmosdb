"""
Query: Find top 10 most recent orders for a customer
Container: orders
Partition key: /customerId
Projected fields: orderId, status, total, createdAt
"""

from azure.cosmos import ContainerProxy


# SQL Query
TOP_RECENT_ORDERS_QUERY = (
    "SELECT c.orderId, c.status, c.total, c.createdAt "
    "FROM c "
    "WHERE c.customerId = @customerId "
    "ORDER BY c.createdAt DESC "
    "OFFSET 0 LIMIT 10"
)


def get_top_recent_orders(container: ContainerProxy, customer_id: str) -> list[dict]:
    """
    Retrieve the 10 most recent orders for a specific customer.

    Query details:
    - Single-partition query (partition key = customerId)
    - Projects only orderId, status, total, createdAt
    - Results ordered by createdAt descending
    - Bounded to 10 results via OFFSET/LIMIT

    Estimated RU cost: 3-5 RUs
    - Single partition scope
    - Composite index on (customerId, createdAt DESC) avoids sort cost
    - Small projection reduces response size

    Required composite index:
        [("/customerId", ascending), ("/createdAt", descending)]

    Args:
        container: Cosmos DB container proxy for 'orders'.
        customer_id: The customer ID (partition key value).

    Returns:
        List of up to 10 order documents with projected fields.
    """
    parameters = [
        {"name": "@customerId", "value": customer_id},
    ]

    results = container.query_items(
        query=TOP_RECENT_ORDERS_QUERY,
        parameters=parameters,
        partition_key=customer_id,
        max_item_count=10,
    )

    return list(results)


# Required indexing policy for this query
REQUIRED_INDEX_POLICY = {
    "includedPaths": [
        {"path": "/customerId/?"},
        {"path": "/createdAt/?"},
    ],
    "compositeIndexes": [
        [
            {"path": "/customerId", "order": "ascending"},
            {"path": "/createdAt", "order": "descending"},
        ]
    ],
}
