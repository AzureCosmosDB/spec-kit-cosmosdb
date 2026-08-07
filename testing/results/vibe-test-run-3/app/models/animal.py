"""Animal model.
Partition key: /shelterId
Justification: Most frequent read is fetching animals by shelterId (shelter dashboard or category browse).
This ensures all animals for a given shelterId are co-located for efficient single-partition queries.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Animal(BaseModel):
    id: str
    shelterId: str
    name: str
    species: str
    breed: Optional[str] = None
    age: Optional[int] = None
    description: Optional[str] = None
    status: str = "available"
    photos: list[str] = []
    created_at: datetime = datetime.utcnow()
    type: str = "animal"
