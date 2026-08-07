"""
Order Repository - Azure Cosmos DB
Entity: Order
Container: orders
Partition Key: /customerId
"""

from azure.cosmos import ContainerProxy, exceptions
from typing import Optional
from datetime import datetime
from uuid import uuid4


# ===== Domain Exceptions =====

class OrderNotFoundException(Exception):
    """Raised when an order cannot be found."""
    pass


class OrderConflictException(Exception):
    """Raised when creating a duplicate order."""
    pass


class ConcurrencyConflictException(Exception):
    """Raised when an ETag mismatch occurs during update."""
    pass


# ===== Order Entity =====

ORDER_TYPE = "order"


def _new_order_doc(
    customer_id: str,
    items: list[dict],
    status: str,
    total: float,
    order_id: Optional[str] = None,
) -> dict:
    """Build a new order document."""
    now = datetime.utcnow().isoformat() + "Z"
    oid = order_id or str(uuid4())
    return {
        "id": oid,
        "orderId": oid,
        "customerId": customer_id,
        "items": items,
        "status": status,
        "total": total,
        "type": ORDER_TYPE,
        "createdAt": now,
        "updatedAt": now,
    }


# ===== Repository =====

class OrderRepository:
    """
    Encapsulates Cosmos DB operations for the Order entity.
    
    All queries are scoped to the customerId partition key for optimal performance.
    Uses optimistic concurrency (ETags) for updates.
    """

    def __init__(self, container: ContainerProxy) -> None:
        """
        Initialize repository with an injected container.

        Args:
            container: Azure Cosmos DB ContainerProxy instance.
        """
        self._container = container

    def create(
        self,
        customer_id: str,
        items: list[dict],
        status: str,
        total: float,
        order_id: Optional[str] = None,
    ) -> dict:
        """
        Create a new order.

        Args:
            customer_id: Customer placing the order (partition key).
            items: Order line items.
            status: Initial status (e.g., "pending").
            total: Order total.
            order_id: Optional custom order ID; auto-generated if omitted.

        Returns:
            Created order document.

        Raises:
            OrderConflictException: If an order with the same ID exists.
        """
        doc = _new_order_doc(customer_id, items, status, total, order_id)
        try:
            return self._container.create_item(body=doc, partition_key=customer_id)
        except exceptions.CosmosResourceExistsError:
            raise OrderConflictException(f"Order '{doc['id']}' already exists for customer '{customer_id}'")

    def get_by_id(self, order_id: str, customer_id: str) -> Optional[dict]:
        """
        Point-read an order by ID and partition key.

        Args:
            order_id: The order's unique ID.
            customer_id: The customer ID (partition key).

        Returns:
            Order document, or None if not found.
        """
        try:
            return self._container.read_item(item=order_id, partition_key=customer_id)
        except exceptions.CosmosResourceNotFoundError:
            return None

    def list_by_customer(
        self,
        customer_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """
        List orders for a customer, ordered by creation date (newest first).

        Args:
            customer_id: Customer ID (partition key).
            limit: Max number of results.
            offset: Number of results to skip.

        Returns:
            List of order documents (projected fields).
        """
        query = (
            "SELECT c.id, c.orderId, c.customerId, c.status, c.total, c.createdAt "
            "FROM c "
            "WHERE c.customerId = @customerId AND c.type = @type "
            "ORDER BY c.createdAt DESC "
            "OFFSET @offset LIMIT @limit"
        )
        parameters = [
            {"name": "@customerId", "value": customer_id},
            {"name": "@type", "value": ORDER_TYPE},
            {"name": "@offset", "value": offset},
            {"name": "@limit", "value": limit},
        ]
        return list(self._container.query_items(
            query=query,
            parameters=parameters,
            partition_key=customer_id,
        ))

    def list_by_status(self, customer_id: str, status: str, limit: int = 50) -> list[dict]:
        """
        List orders by status within a customer's partition.

        Args:
            customer_id: Partition key.
            status: Status to filter by.
            limit: Max results.

        Returns:
            List of matching orders.
        """
        query = (
            "SELECT c.id, c.orderId, c.customerId, c.status, c.total, c.createdAt "
            "FROM c "
            "WHERE c.customerId = @customerId AND c.status = @status AND c.type = @type "
            "ORDER BY c.createdAt DESC "
            "OFFSET 0 LIMIT @limit"
        )
        parameters = [
            {"name": "@customerId", "value": customer_id},
            {"name": "@status", "value": status},
            {"name": "@type", "value": ORDER_TYPE},
            {"name": "@limit", "value": limit},
        ]
        return list(self._container.query_items(
            query=query,
            parameters=parameters,
            partition_key=customer_id,
        ))

    def update_status(self, order_id: str, customer_id: str, new_status: str) -> dict:
        """
        Update the status of an order using optimistic concurrency.

        Args:
            order_id: Order to update.
            customer_id: Partition key.
            new_status: New status value.

        Returns:
            Updated order document.

        Raises:
            OrderNotFoundException: If order doesn't exist.
            ConcurrencyConflictException: If ETag mismatch.
        """
        order = self.get_by_id(order_id, customer_id)
        if order is None:
            raise OrderNotFoundException(f"Order '{order_id}' not found")

        etag = order["_etag"]
        order["status"] = new_status
        order["updatedAt"] = datetime.utcnow().isoformat() + "Z"

        try:
            return self._container.replace_item(
                item=order_id,
                body=order,
                partition_key=customer_id,
                etag=etag,
                match_condition="IfMatch",
            )
        except exceptions.CosmosAccessConditionFailedError:
            raise ConcurrencyConflictException(
                f"Order '{order_id}' was concurrently modified"
            )

    def delete(self, order_id: str, customer_id: str) -> bool:
        """
        Soft-delete an order by marking it deleted and setting TTL.

        Args:
            order_id: Order to delete.
            customer_id: Partition key.

        Returns:
            True if marked deleted, False if order not found.
        """
        order = self.get_by_id(order_id, customer_id)
        if order is None:
            return False

        order["deleted"] = True
        order["ttl"] = 30 * 24 * 60 * 60  # 30 days
        order["updatedAt"] = datetime.utcnow().isoformat() + "Z"

        self._container.replace_item(
            item=order_id,
            body=order,
            partition_key=customer_id,
        )
        return True
