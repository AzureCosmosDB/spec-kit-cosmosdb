"""Inventory model. Partition key: /sku
Justification: Most frequent read is checking stock level by SKU."""
from pydantic import BaseModel
class InventoryItem(BaseModel):
    id: str
    sku: str
    product_name: str
    quantity: int
    warehouse_id: str
    reorder_threshold: int = 10
