"""Order model. Partition key: /status
Justification: Most frequent read is filtering orders by status (pending/shipped/completed)."""
from pydantic import BaseModel
from datetime import datetime
class Order(BaseModel):
    id: str
    customerId: str
    items: list[dict]
    total: float
    status: str = "pending"
    created_at: datetime = datetime.utcnow()
