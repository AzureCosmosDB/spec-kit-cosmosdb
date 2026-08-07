"""Order model. Partition key: /productId"""
from pydantic import BaseModel
from datetime import datetime
class Order(BaseModel):
    id: str
    productId: str
    quantity: int
    customer_name: str
    status: str = "pending"
    created_at: datetime = datetime.utcnow()
