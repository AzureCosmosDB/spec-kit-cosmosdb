"""Product repository for Cosmos DB."""
from __future__ import annotations
from typing import Optional, List, Tuple
from datetime import datetime, timezone
import uuid

from azure.cosmos import ContainerProxy, exceptions


class ProductNotFoundError(Exception):
    pass

class ProductConflictError(Exception):
    pass

class ConcurrencyError(Exception):
    pass


class Product:
    def __init__(self, productId: str, categoryId: str, name: str, price: float,
                 stock: int, description: str, createdAt: str, **kwargs):
        self.id = productId
        self.productId = productId
        self.categoryId = categoryId
        self.name = name
        self.price = price
        self.stock = stock
        self.description = description
        self.createdAt = createdAt
        self._etag = kwargs.get("_etag")

    def to_dict(self) -> dict:
        d = {
            "id": self.id,
            "productId": self.productId,
            "categoryId": self.categoryId,
            "name": self.name,
            "price": self.price,
            "stock": self.stock,
            "description": self.description,
            "createdAt": self.createdAt,
        }
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        p = cls(
            productId=data["productId"],
            categoryId=data["categoryId"],
            name=data["name"],
            price=data["price"],
            stock=data["stock"],
            description=data["description"],
            createdAt=data["createdAt"],
        )
        p._etag = data.get("_etag")
        return p


class ProductRepository:
    """Repository encapsulating Cosmos DB operations for Product entity."""

    def __init__(self, container: ContainerProxy):
        self._container = container

    def create(self, product: Product) -> Product:
        """Create a new product. Raises ProductConflictError on 409."""
        try:
            result = self._container.create_item(body=product.to_dict())
            return Product.from_dict(result)
        except exceptions.CosmosResourceExistsError:
            raise ProductConflictError(f"Product {product.productId} already exists")

    def read(self, product_id: str, category_id: str) -> Optional[Product]:
        """Point read by id + partition key. Returns None if not found."""
        try:
            result = self._container.read_item(item=product_id, partition_key=category_id)
            return Product.from_dict(result)
        except exceptions.CosmosResourceNotFoundError:
            return None

    def list_by_category(self, category_id: str, max_count: int = 100) -> List[Product]:
        """Query products by category (cross-partition avoided via partition key)."""
        query = "SELECT * FROM c WHERE c.categoryId = @categoryId"
        params = [{"name": "@categoryId", "value": category_id}]
        items = list(self._container.query_items(
            query=query,
            parameters=params,
            partition_key=category_id,
            max_item_count=max_count,
        ))
        return [Product.from_dict(item) for item in items]

    def search_by_name(self, name: str, category_id: Optional[str] = None) -> List[Product]:
        """Search products by name (contains). Cross-partition if no category specified."""
        query = "SELECT * FROM c WHERE CONTAINS(c.name, @name, true)"
        params = [{"name": "@name", "value": name}]
        kwargs = {"query": query, "parameters": params, "enable_cross_partition_query": True}
        if category_id:
            kwargs["partition_key"] = category_id
            kwargs.pop("enable_cross_partition_query")
        items = list(self._container.query_items(**kwargs))
        return [Product.from_dict(item) for item in items]

    def update_stock(self, product_id: str, category_id: str, new_stock: int) -> Product:
        """Update stock with optimistic concurrency (ETag)."""
        current = self.read(product_id, category_id)
        if current is None:
            raise ProductNotFoundError(f"Product {product_id} not found")
        current.stock = new_stock
        try:
            result = self._container.replace_item(
                item=product_id,
                body=current.to_dict(),
                if_match=current._etag,
            )
            return Product.from_dict(result)
        except exceptions.CosmosAccessConditionFailedError:
            raise ConcurrencyError(f"Product {product_id} was modified concurrently")

    def delete(self, product_id: str, category_id: str) -> bool:
        """Delete a product. Returns True if deleted, False if not found."""
        try:
            self._container.delete_item(item=product_id, partition_key=category_id)
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False
