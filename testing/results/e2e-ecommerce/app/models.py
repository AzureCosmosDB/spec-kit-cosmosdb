from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, List
from datetime import datetime
import uuid


class OrderStatus(str, Enum):
    PLACED = "placed"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"


# Valid transitions
VALID_TRANSITIONS = {
    OrderStatus.PLACED: [OrderStatus.PAID, OrderStatus.CANCELLED],
    OrderStatus.PAID: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
    OrderStatus.SHIPPED: [OrderStatus.DELIVERED, OrderStatus.RETURNED],
    OrderStatus.DELIVERED: [],
    OrderStatus.CANCELLED: [],
    OrderStatus.RETURNED: [],
}


class Customer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class OrderItemCreate(BaseModel):
    productId: str
    productName: str
    quantity: int
    unitPrice: float


class OrderCreate(BaseModel):
    customerId: str
    items: List[OrderItemCreate]


class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str = "order"
    customerId: str
    status: OrderStatus = OrderStatus.PLACED
    totalAmount: float = 0.0
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class OrderItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str = "orderItem"
    orderId: str
    customerId: str
    productId: str
    productName: str
    quantity: int
    unitPrice: float
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    categoryId: str
    name: str
    price: float
    stockCount: int = 0
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
