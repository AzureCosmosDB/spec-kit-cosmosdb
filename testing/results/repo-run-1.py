"""
Order Repository for Cosmos DB
Entity: Order (orderId, customerId, items[], status, total, createdAt)
Partition key: /customerId
Operations: CRUD + list by customer + list by status + update status
"""

from azure.cosmos import ContainerProxy, exceptions
from typing import Optional
from datetime import datetime
from uuid import uuid4


class OrderNotFoundError(Exception):
    """Raised when an order is not found."""
    pass


class OrderConflictError(Exception):
    """Raised when an order already exists (409 Conflict)."""
    pass


class ConcurrencyError(Exception):
    """Raised on ETag mismatch (412 Precondition Failed)."""
    pass


class OrderRepository:
    """Repository for Order entity in Cosmos DB."""

    def __init__(self, container: ContainerProxy):
        """
        Initialize OrderRepository.

        Args:
            container: Injected Cosmos DB container instance.
        """
        self._container = container

    def create(self, order: dict) -> dict:
        """
        Create a new order.

        Args:
            order: Order data with customerId, items, status, total.

        Returns:
            Created order document with generated id and timestamps.

        Raises:
            OrderConflictError: If order with same id already exists.
        """
        if "id" not in order:
            order["id"] = str(uuid4())
        order["type"] = "order"
        order["createdAt"] = datetime.utcnow().isoformat() + "Z"
        order["updatedAt"] = order["createdAt"]

        try:
            result = self._container.create_item(
                body=order,
                partition_key=order["customerId"]
            )
            return result
        except exceptions.CosmosResourceExistsError:
            raise OrderConflictError(f"Order {order['id']} already exists")

    def get_by_id(self, order_id: str, customer_id: str) -> Optional[dict]:
        """
        Point read an order by id and partition key.

        Args:
            order_id: The order ID.
            customer_id: The customer ID (partition key).

        Returns:
            Order document or None if not found.
        """
        try:
            return self._container.read_item(
                item=order_id,
                partition_key=customer_id
            )
        except exceptions.CosmosResourceNotFoundError:
            return None

    def list_by_customer(
        self, customer_id: str, max_items: int = 50, continuation_token: Optional[str] = None
    ) -> tuple[list[dict], Optional[str]]:
        """
        List orders for a customer, paginated.

        Args:
            customer_id: Customer ID (partition key).
            max_items: Maximum items per page.
            continuation_token: Token for next page.

        Returns:
            Tuple of (orders list, next continuation token or None).
        """
        query = "SELECT c.id, c.orderId, c.customerId, c.status, c.total, c.createdAt FROM c WHERE c.customerId = @customerId ORDER BY c.createdAt DESC"
        parameters = [{"name": "@customerId", "value": customer_id}]

        items = list(self._container.query_items(
            query=query,
            parameters=parameters,
            partition_key=customer_id,
            max_item_count=max_items,
        ))
        return items, None  # SDK handles continuation internally

    def list_by_status(
        self, customer_id: str, status: str, max_items: int = 50
    ) -> list[dict]:
        """
        List orders by status within a customer partition.

        Args:
            customer_id: Customer ID (partition key).
            status: Order status to filter by.
            max_items: Maximum items to return.

        Returns:
            List of matching orders.
        """
        query = "SELECT c.id, c.orderId, c.customerId, c.status, c.total, c.createdAt FROM c WHERE c.customerId = @customerId AND c.status = @status"
        parameters = [
            {"name": "@customerId", "value": customer_id},
            {"name": "@status", "value": status},
        ]

        return list(self._container.query_items(
            query=query,
            parameters=parameters,
            partition_key=customer_id,
            max_item_count=max_items,
        ))

    def update_status(self, order_id: str, customer_id: str, new_status: str) -> dict:
        """
        Update order status with optimistic concurrency (ETag).

        Args:
            order_id: The order ID.
            customer_id: The customer ID (partition key).
            new_status: New status value.

        Returns:
            Updated order document.

        Raises:
            OrderNotFoundError: If order not found.
            ConcurrencyError: If ETag mismatch.
        """
        existing = self.get_by_id(order_id, customer_id)
        if existing is None:
            raise OrderNotFoundError(f"Order {order_id} not found")

        etag = existing.get("_etag")
        existing["status"] = new_status
        existing["updatedAt"] = datetime.utcnow().isoformat() + "Z"

        try:
            return self._container.replace_item(
                item=order_id,
                body=existing,
                partition_key=customer_id,
                etag=etag,
                match_condition="IfMatch",
            )
        except exceptions.CosmosAccessConditionFailedError:
            raise ConcurrencyError(f"Order {order_id} was modified concurrently")

    def delete(self, order_id: str, customer_id: str) -> bool:
        """
        Soft delete an order (sets deleted flag, relies on TTL).

        Args:
            order_id: The order ID.
            customer_id: The customer ID (partition key).

        Returns:
            True if deleted, False if not found.
        """
        existing = self.get_by_id(order_id, customer_id)
        if existing is None:
            return False

        existing["deleted"] = True
        existing["updatedAt"] = datetime.utcnow().isoformat() + "Z"
        existing["ttl"] = 2592000  # 30 days

        self._container.replace_item(
            item=order_id,
            body=existing,
            partition_key=customer_id,
        )
        return True
