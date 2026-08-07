"""
Cosmos DB Query: Top 10 Most Recent Orders for a Customer
Container: orders
Partition Key: /customerId
"""

from azure.cosmos import ContainerProxy
from typing import Any


# ============================================================
# Query Definition
# ============================================================

SQL_QUERY = """
SELECT
    c.orderId,
    c.status,
    c.total,
    c.createdAt
FROM c
WHERE c.customerId = @customerId
ORDER BY c.createdAt DESC
OFFSET 0 LIMIT 10
"""

# Parameters (values set at call time)
QUERY_PARAMETERS = [
    {"name": "@customerId", "value": ""}
]


# ============================================================
# Execution Function
# ============================================================

def find_top_10_recent_orders(container: ContainerProxy, customer_id: str) -> list[dict[str, Any]]:
    """
    Find the top 10 most recent orders for a given customer.

    This query is:
    - Partition-scoped: customerId is both a filter and the partition key
    - Projection-only: returns only orderId, status, total, createdAt
    - Bounded: OFFSET/LIMIT prevents unbounded results
    - Index-aligned: requires composite index (createdAt DESC) within partition

    Estimated RU cost: ~3-6 RUs (single-partition query with ORDER BY on indexed field)

    Args:
        container: The Cosmos DB container proxy for 'orders'.
        customer_id: Customer ID to query (partition key value).

    Returns:
        List of up to 10 order dictionaries.
    """
    parameters = [{"name": "@customerId", "value": customer_id}]

    items = container.query_items(
        query=SQL_QUERY.strip(),
        parameters=parameters,
        partition_key=customer_id,
        max_item_count=10,
    )

    return list(items)


# ============================================================
# Required Indexing Policy
# ============================================================

INDEXING_POLICY = {
    "includedPaths": [
        {"path": "/customerId/?"},
        {"path": "/createdAt/?"},
        {"path": "/status/?"},
        {"path": "/total/?"},
        {"path": "/orderId/?"},
    ],
    "excludedPaths": [
        {"path": "/*"},
    ],
    "compositeIndexes": [
        [
            {"path": "/customerId", "order": "ascending"},
            {"path": "/createdAt", "order": "descending"},
        ]
    ],
}


# ============================================================
# Usage Example
# ============================================================

if __name__ == "__main__":
    # Example usage (requires configured container)
    # container = database.get_container_client("orders")
    # orders = find_top_10_recent_orders(container, "cust-12345")
    # for order in orders:
    #     print(f"{order['orderId']}: {order['status']} - ${order['total']}")
    pass
