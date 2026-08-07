"""
Order Repository - Cosmos DB Data Access Layer
Container: orders
Partition Key: /customerId
Operations: CRUD, list by customer, list by status, update status
"""

from azure.cosmos import ContainerProxy, exceptions
from typing import Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


# --- Domain Exceptions ---

class OrderNotFoundError(Exception):
    """Order does not exist."""
    def __init__(self, order_id: str):
        super().__init__(f"Order '{order_id}' not found")
        self.order_id = order_id


class OrderAlreadyExistsError(Exception):
    """Order with this ID already exists."""
    def __init__(self, order_id: str):
        super().__init__(f"Order '{order_id}' already exists")
        self.order_id = order_id


class OptimisticConcurrencyError(Exception):
    """ETag mismatch during update."""
    pass


# --- Entity Type ---

@dataclass
class Order:
    id: str
    order_id: str
    customer_id: str
    items: list[dict]
    status: str
    total: float
    created_at: str
    updated_at: str
    type: str = "order"


# --- Repository ---

class OrderRepository:
    """
    Data access layer for Order entities in Cosmos DB.
    All operations are partition-scoped to customerId.
    """

    def __init__(self, container: ContainerProxy) -> None:
        """
        Args:
            container: Cosmos DB container proxy (injected, not self-created).
        """
        self._container = container

    def create_order(self, customer_id: str, items: list[dict], status: str, total: float) -> dict:
        """
        Create a new order document.

        Args:
            customer_id: Customer who placed the order (partition key).
            items: List of order line items.
            status: Initial order status.
            total: Order total amount.

        Returns:
            The created order document.

        Raises:
            OrderAlreadyExistsError: If duplicate id (409).
        """
        now = datetime.utcnow().isoformat() + "Z"
        order_id = f"ord-{uuid4().hex[:12]}"
        doc = {
            "id": order_id,
            "orderId": order_id,
            "customerId": customer_id,
            "items": items,
            "status": status,
            "total": total,
            "type": "order",
            "createdAt": now,
            "updatedAt": now,
        }
        try:
            result = self._container.create_item(body=doc, partition_key=customer_id)
            return result
        except exceptions.CosmosResourceExistsError:
            raise OrderAlreadyExistsError(order_id)

    def get_order(self, order_id: str, customer_id: str) -> Optional[dict]:
        """
        Point read a single order by ID + partition key.

        Args:
            order_id: Unique order identifier.
            customer_id: Partition key value.

        Returns:
            Order document or None if not found.
        """
        try:
            return self._container.read_item(item=order_id, partition_key=customer_id)
        except exceptions.CosmosResourceNotFoundError:
            return None

    def list_by_customer(self, customer_id: str, page_size: int = 25, continuation_token: Optional[str] = None) -> dict:
        """
        List all orders for a customer, paginated.

        Args:
            customer_id: Customer ID (partition key).
            page_size: Number of results per page.
            continuation_token: Continuation token for next page.

        Returns:
            Dict with 'items' and 'continuation_token'.
        """
        query = (
            "SELECT c.id, c.orderId, c.customerId, c.items, c.status, c.total, c.createdAt "
            "FROM c WHERE c.customerId = @customerId "
            "ORDER BY c.createdAt DESC"
        )
        parameters = [{"name": "@customerId", "value": customer_id}]

        results = self._container.query_items(
            query=query,
            parameters=parameters,
            partition_key=customer_id,
            max_item_count=page_size,
        )
        items = list(results)
        return {"items": items, "continuation_token": None}

    def list_by_status(self, customer_id: str, status: str, page_size: int = 25) -> list[dict]:
        """
        List orders filtered by status within a customer partition.

        Args:
            customer_id: Partition key.
            status: Status to filter (e.g., "pending", "shipped").
            page_size: Max results.

        Returns:
            List of matching order documents.
        """
        query = (
            "SELECT c.id, c.orderId, c.customerId, c.status, c.total, c.createdAt "
            "FROM c WHERE c.customerId = @customerId AND c.status = @status "
            "ORDER BY c.createdAt DESC"
        )
        parameters = [
            {"name": "@customerId", "value": customer_id},
            {"name": "@status", "value": status},
        ]
        return list(self._container.query_items(
            query=query,
            parameters=parameters,
            partition_key=customer_id,
            max_item_count=page_size,
        ))

    def update_status(self, order_id: str, customer_id: str, new_status: str) -> dict:
        """
        Update the status of an order with optimistic concurrency.

        Args:
            order_id: Order to update.
            customer_id: Partition key.
            new_status: New status value.

        Returns:
            Updated order document.

        Raises:
            OrderNotFoundError: If order doesn't exist.
            OptimisticConcurrencyError: If concurrent modification detected.
        """
        current = self.get_order(order_id, customer_id)
        if current is None:
            raise OrderNotFoundError(order_id)

        etag = current["_etag"]
        current["status"] = new_status
        current["updatedAt"] = datetime.utcnow().isoformat() + "Z"

        try:
            return self._container.replace_item(
                item=order_id,
                body=current,
                partition_key=customer_id,
                etag=etag,
                match_condition="IfMatch",
            )
        except exceptions.CosmosAccessConditionFailedError:
            raise OptimisticConcurrencyError(
                f"Order {order_id} was modified by another process"
            )

    def delete_order(self, order_id: str, customer_id: str) -> bool:
        """
        Soft-delete an order (mark deleted, set TTL for automatic cleanup).

        Args:
            order_id: Order to delete.
            customer_id: Partition key.

        Returns:
            True if soft-deleted, False if not found.
        """
        current = self.get_order(order_id, customer_id)
        if current is None:
            return False

        current["deleted"] = True
        current["ttl"] = 60 * 60 * 24 * 30  # 30 days
        current["updatedAt"] = datetime.utcnow().isoformat() + "Z"

        self._container.replace_item(
            item=order_id,
            body=current,
            partition_key=customer_id,
        )
        return True
