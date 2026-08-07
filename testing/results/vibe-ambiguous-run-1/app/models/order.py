"""Order model. Partition key: /customerId
Justification: Most frequent read is "get all orders for a customer"."""
from pydantic import BaseModel
from datetime import datetime
class Order(BaseModel):
    id: str
    customerId: str
    items: list[dict]
    total: float
    status: str = "pending"
    created_at: datetime = datetime.utcnow()
