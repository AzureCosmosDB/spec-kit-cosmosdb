# PARTITION KEY for orders: /customerId
# JUSTIFICATION: 4 of 4 primary queries filter by customerId (order history by customer,
# order by ID within customer context, orders by status). Cross-partition for admin status listing.

# PARTITION KEY for products: /categoryId
# JUSTIFICATION: Product catalog queried by category.

# PARTITION KEY for customers: /id
# JUSTIFICATION: Customers accessed by their own ID.

from azure.cosmos.aio import CosmosClient
from azure.cosmos import exceptions
from typing import List, Optional, Tuple


class CustomerRepository:
    def __init__(self, container):
        self.container = container

    async def create(self, customer: dict) -> dict:
        return await self.container.create_item(body=customer)

    async def get_by_id(self, customer_id: str) -> Optional[dict]:
        try:
            return await self.container.read_item(item=customer_id, partition_key=customer_id)
        except exceptions.CosmosResourceNotFoundError:
            return None

    async def list_all(self) -> List[dict]:
        query = "SELECT * FROM c"
        items = self.container.query_items(query=query, partition_key=None, max_item_count=100)
        return [item async for item in items]


class OrderRepository:
    def __init__(self, container):
        self.container = container

    async def create(self, order: dict) -> dict:
        return await self.container.create_item(body=order)

    async def get_by_id(self, order_id: str, customer_id: str) -> Optional[dict]:
        try:
            return await self.container.read_item(item=order_id, partition_key=customer_id)
        except exceptions.CosmosResourceNotFoundError:
            return None

    async def get_orders_by_customer(self, customer_id: str) -> List[dict]:
        query = "SELECT * FROM c WHERE c.customerId = @customerId AND c.type = @type"
        parameters = [
            {"name": "@customerId", "value": customer_id},
            {"name": "@type", "value": "order"}
        ]
        items = self.container.query_items(
            query=query, parameters=parameters, partition_key=customer_id, max_item_count=100
        )
        return [item async for item in items]

    async def get_orders_by_status(self, status: str) -> List[dict]:
        # CROSS-PARTITION: Admin/fulfillment team needs all orders by status regardless of customer
        query = "SELECT * FROM c WHERE c.status = @status AND c.type = @type"
        parameters = [
            {"name": "@status", "value": status},
            {"name": "@type", "value": "order"}
        ]
        items = self.container.query_items(
            query=query, parameters=parameters, partition_key=None, max_item_count=100
        )
        return [item async for item in items]

    async def replace(self, order_id: str, order: dict, customer_id: str, etag: Optional[str] = None) -> dict:
        kwargs = {}
        if etag:
            kwargs["if_match"] = etag
        return await self.container.replace_item(item=order_id, body=order, **kwargs)

    async def get_order_items(self, order_id: str, customer_id: str) -> List[dict]:
        query = "SELECT * FROM c WHERE c.orderId = @orderId AND c.type = @type"
        parameters = [
            {"name": "@orderId", "value": order_id},
            {"name": "@type", "value": "orderItem"}
        ]
        items = self.container.query_items(
            query=query, parameters=parameters, partition_key=customer_id, max_item_count=100
        )
        return [item async for item in items]


class ProductRepository:
    def __init__(self, container):
        self.container = container

    async def create(self, product: dict) -> dict:
        return await self.container.create_item(body=product)

    async def get_by_id(self, product_id: str, category_id: str) -> Optional[Tuple[dict, str]]:
        try:
            resp = await self.container.read_item(item=product_id, partition_key=category_id)
            etag = resp.get("_etag")
            return resp, etag
        except exceptions.CosmosResourceNotFoundError:
            return None

    async def get_by_category(self, category_id: str) -> List[dict]:
        query = "SELECT * FROM c WHERE c.categoryId = @categoryId"
        parameters = [{"name": "@categoryId", "value": category_id}]
        items = self.container.query_items(
            query=query, parameters=parameters, partition_key=category_id, max_item_count=100
        )
        return [item async for item in items]

    async def replace(self, product_id: str, product: dict, category_id: str, etag: str) -> dict:
        return await self.container.replace_item(
            item=product_id, body=product,
            if_match=etag
        )

    async def list_all(self) -> List[dict]:
        query = "SELECT * FROM c"
        items = self.container.query_items(query=query, partition_key=None, max_item_count=100)
        return [item async for item in items]
