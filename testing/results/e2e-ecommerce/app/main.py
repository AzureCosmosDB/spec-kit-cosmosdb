from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Response
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey, exceptions
from config import settings
from models import Customer, Product, OrderCreate, OrderStatus
from repository import CustomerRepository, OrderRepository, ProductRepository
from service import OrderService, CustomerService, ProductService
import ssl

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE


async def ensure_database(client):
    """Create database and containers if they don't exist."""
    try:
        database = await client.create_database_if_not_exists(id=settings.cosmos_database)
    except Exception:
        database = client.get_database_client(settings.cosmos_database)

    try:
        await database.create_container_if_not_exists(id="customers", partition_key=PartitionKey(path="/id"))
    except Exception:
        pass
    try:
        await database.create_container_if_not_exists(id="orders", partition_key=PartitionKey(path="/customerId"))
    except Exception:
        pass
    try:
        await database.create_container_if_not_exists(id="products", partition_key=PartitionKey(path="/categoryId"))
    except Exception:
        pass
    return database


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.cosmos_client = CosmosClient(
        settings.cosmos_endpoint,
        credential=settings.cosmos_key,
        user_agent="cosmos-intent-sdk/0.1.0",
        connection_verify=False,
    )
    app.state.database = await ensure_database(app.state.cosmos_client)

    customers_container = app.state.database.get_container_client("customers")
    orders_container = app.state.database.get_container_client("orders")
    products_container = app.state.database.get_container_client("products")

    app.state.customer_repo = CustomerRepository(customers_container)
    app.state.order_repo = OrderRepository(orders_container)
    app.state.product_repo = ProductRepository(products_container)

    app.state.customer_service = CustomerService(app.state.customer_repo)
    app.state.order_service = OrderService(app.state.order_repo, app.state.product_repo)
    app.state.product_service = ProductService(app.state.product_repo)

    yield
    await app.state.cosmos_client.close()


app = FastAPI(lifespan=lifespan)


@app.get("/api/health")
async def health():
    try:
        # Verify connectivity by reading database properties
        await app.state.database.read()
        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


# --- Customers ---
@app.post("/api/customers", status_code=201)
async def create_customer(customer: Customer, response: Response):
    result = await app.state.customer_service.create(customer)
    response.headers["Location"] = f"/api/customers/{result['id']}"
    return result


@app.get("/api/customers")
async def list_customers():
    return await app.state.customer_service.list_all()


@app.get("/api/customers/{customer_id}")
async def get_customer(customer_id: str):
    result = await app.state.customer_service.get_by_id(customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    return result


@app.get("/api/customers/{customer_id}/orders")
async def get_customer_orders(customer_id: str):
    return await app.state.order_service.get_orders_by_customer(customer_id)


# --- Products ---
@app.post("/api/products", status_code=201)
async def create_product(product: Product, response: Response):
    result = await app.state.product_service.create(product)
    response.headers["Location"] = f"/api/products/{result['id']}"
    return result


@app.get("/api/products")
async def list_products():
    return await app.state.product_service.list_all()


@app.get("/api/products/category/{category_id}")
async def get_products_by_category(category_id: str):
    return await app.state.product_service.get_by_category(category_id)


# --- Orders ---
@app.post("/api/orders", status_code=201)
async def create_order(order: OrderCreate, response: Response):
    try:
        result = await app.state.order_service.create_order(order)
        response.headers["Location"] = f"/api/orders/{result['id']}"
        return result
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@app.get("/api/orders")
async def list_orders(status: str = None):
    if status:
        return await app.state.order_service.get_orders_by_status(status)
    # No global list without status filter for safety
    return []


@app.get("/api/orders/{order_id}")
async def get_order(order_id: str, customerId: str):
    result = await app.state.order_service.get_order(order_id, customerId)
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return result


@app.get("/api/orders/{order_id}/items")
async def get_order_items(order_id: str, customerId: str):
    return await app.state.order_service.get_order_items(order_id, customerId)


@app.post("/api/orders/{order_id}/pay")
async def pay_order(order_id: str, customerId: str):
    try:
        result = await app.state.order_service.transition_status(order_id, customerId, OrderStatus.PAID)
        if not result:
            raise HTTPException(status_code=404, detail="Order not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@app.post("/api/orders/{order_id}/ship")
async def ship_order(order_id: str, customerId: str):
    try:
        result = await app.state.order_service.transition_status(order_id, customerId, OrderStatus.SHIPPED)
        if not result:
            raise HTTPException(status_code=404, detail="Order not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@app.post("/api/orders/{order_id}/deliver")
async def deliver_order(order_id: str, customerId: str):
    try:
        result = await app.state.order_service.transition_status(order_id, customerId, OrderStatus.DELIVERED)
        if not result:
            raise HTTPException(status_code=404, detail="Order not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@app.post("/api/orders/{order_id}/cancel")
async def cancel_order(order_id: str, customerId: str):
    try:
        result = await app.state.order_service.transition_status(order_id, customerId, OrderStatus.CANCELLED)
        if not result:
            raise HTTPException(status_code=404, detail="Order not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
