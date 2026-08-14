from models import (
    Order, OrderItem, OrderCreate, OrderStatus, VALID_TRANSITIONS,
    Customer, Product, OrderItemCreate
)
from repository import OrderRepository, ProductRepository, CustomerRepository
from azure.cosmos import exceptions
from datetime import datetime
from typing import List, Optional


class OrderService:
    def __init__(self, order_repo: OrderRepository, product_repo: ProductRepository):
        self.order_repo = order_repo
        self.product_repo = product_repo

    async def create_order(self, order_create: OrderCreate) -> dict:
        # Decrement stock for each item with etag concurrency
        for item in order_create.items:
            await self._decrement_stock(item)

        total = sum(i.quantity * i.unitPrice for i in order_create.items)
        order = Order(customerId=order_create.customerId, totalAmount=total)
        order_dict = order.model_dump()
        created_order = await self.order_repo.create(order_dict)

        # Create order items in same container (co-located)
        for item in order_create.items:
            oi = OrderItem(
                orderId=created_order["id"],
                customerId=order_create.customerId,
                productId=item.productId,
                productName=item.productName,
                quantity=item.quantity,
                unitPrice=item.unitPrice,
            )
            await self.order_repo.create(oi.model_dump())

        return created_order

    async def _decrement_stock(self, item: OrderItemCreate, retries: int = 3):
        for attempt in range(retries):
            # We need category to read product - store category lookup
            # For simplicity, we do cross-partition read
            result = await self._find_product(item.productId)
            if not result:
                raise ValueError(f"Product {item.productId} not found")
            product, etag = result
            if product["stockCount"] < item.quantity:
                raise ValueError(f"Insufficient stock for {item.productId}")
            product["stockCount"] -= item.quantity
            product["updatedAt"] = datetime.utcnow().isoformat() + "Z"
            try:
                await self.product_repo.replace(
                    product["id"], product, product["categoryId"], etag
                )
                return
            except exceptions.CosmosAccessConditionFailedError:
                if attempt == retries - 1:
                    raise ValueError("Stock update conflict after retries")
                continue

    async def _find_product(self, product_id: str):
        # Need to find product by ID across categories
        query = "SELECT * FROM c WHERE c.id = @id"
        parameters = [{"name": "@id", "value": product_id}]
        items = self.product_repo.container.query_items(
            query=query, parameters=parameters, partition_key=None, max_item_count=1
        )
        results = [item async for item in items]
        if not results:
            return None
        product = results[0]
        etag = product.get("_etag")
        return product, etag

    async def transition_status(self, order_id: str, customer_id: str, new_status: OrderStatus) -> dict:
        order = await self.order_repo.get_by_id(order_id, customer_id)
        if not order:
            return None
        current = OrderStatus(order["status"])
        if new_status not in VALID_TRANSITIONS[current]:
            raise ValueError(f"Cannot transition from {current.value} to {new_status.value}")
        order["status"] = new_status.value
        order["updatedAt"] = datetime.utcnow().isoformat() + "Z"
        updated = await self.order_repo.replace(order_id, order, customer_id)

        # If cancelled, restock
        if new_status == OrderStatus.CANCELLED:
            items = await self.order_repo.get_order_items(order_id, customer_id)
            for oi in items:
                await self._restock(oi["productId"], oi["quantity"])

        return updated

    async def _restock(self, product_id: str, quantity: int, retries: int = 3):
        for attempt in range(retries):
            result = await self._find_product(product_id)
            if not result:
                return
            product, etag = result
            product["stockCount"] += quantity
            product["updatedAt"] = datetime.utcnow().isoformat() + "Z"
            try:
                await self.product_repo.replace(product["id"], product, product["categoryId"], etag)
                return
            except exceptions.CosmosAccessConditionFailedError:
                if attempt == retries - 1:
                    raise ValueError("Restock conflict after retries")

    async def get_orders_by_customer(self, customer_id: str) -> List[dict]:
        return await self.order_repo.get_orders_by_customer(customer_id)

    async def get_orders_by_status(self, status: str) -> List[dict]:
        return await self.order_repo.get_orders_by_status(status)

    async def get_order(self, order_id: str, customer_id: str) -> Optional[dict]:
        return await self.order_repo.get_by_id(order_id, customer_id)

    async def get_order_items(self, order_id: str, customer_id: str) -> List[dict]:
        return await self.order_repo.get_order_items(order_id, customer_id)


class CustomerService:
    def __init__(self, customer_repo: CustomerRepository):
        self.customer_repo = customer_repo

    async def create(self, customer: Customer) -> dict:
        return await self.customer_repo.create(customer.model_dump())

    async def get_by_id(self, customer_id: str) -> Optional[dict]:
        return await self.customer_repo.get_by_id(customer_id)

    async def list_all(self) -> List[dict]:
        return await self.customer_repo.list_all()


class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    async def create(self, product: Product) -> dict:
        return await self.product_repo.create(product.model_dump())

    async def get_by_category(self, category_id: str) -> List[dict]:
        return await self.product_repo.get_by_category(category_id)

    async def list_all(self) -> List[dict]:
        return await self.product_repo.list_all()
