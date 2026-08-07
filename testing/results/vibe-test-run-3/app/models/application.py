"""Adoption Application model.
Partition key: /animalId
Justification: Most frequent read is "show all applications for this animal" (shelter reviewing applicants).
"""
from pydantic import BaseModel
from datetime import datetime

class Application(BaseModel):
    id: str
    animalId: str
    applicantId: str
    applicant_name: str
    applicant_email: str
    message: str
    status: str = "pending"
    created_at: datetime = datetime.utcnow()
    type: str = "application"
