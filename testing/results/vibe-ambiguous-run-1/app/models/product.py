"""Product model. Partition key: /categoryId"""
from pydantic import BaseModel
class Product(BaseModel):
    id: str
    categoryId: str
    name: str
    price: float
    stock_count: int = 0
