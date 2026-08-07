"""Domain models for the SaaS platform."""
from pydantic import BaseModel
from typing import Optional


class Tenant(BaseModel):
    id: str
    name: str
    plan: str  # trial | basic | pro | enterprise
    createdAt: str
    updatedAt: str


class User(BaseModel):
    id: str
    tenantId: str
    type: str = "user"
    email: str
    role: str
    createdAt: str
    updatedAt: str


class Subscription(BaseModel):
    id: str
    tenantId: str
    type: str = "subscription"
    plan: str  # trial | basic | pro | enterprise
    status: str  # trial | active | past_due | cancelled | suspended
    currentPeriodStart: str
    currentPeriodEnd: str
    createdAt: str


class UsageMetric(BaseModel):
    id: str
    tenantId: str
    type: str = "usageMetric"
    date: str  # YYYY-MM-DD
    apiCalls: int
    storageBytes: int
    activeUsers: int
