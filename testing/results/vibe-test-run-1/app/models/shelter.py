"""Shelter model.
Partition key: /id
Justification: Shelters are accessed by their unique ID for profile views.
"""
from pydantic import BaseModel
from typing import Optional

class Shelter(BaseModel):
    id: str
    name: str
    location: str
    contact_email: str
    description: Optional[str] = None
    type: str = "shelter"
