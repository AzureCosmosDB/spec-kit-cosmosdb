"""Domain models for the booking system."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Provider(BaseModel):
    id: str
    name: str
    specialty: str
    timezone: str
    createdAt: str


class Service(BaseModel):
    id: str
    providerId: str
    type: str = "service"
    name: str
    durationMinutes: int
    price: float


class TimeSlot(BaseModel):
    id: str
    providerId: str
    type: str = "slot"
    date: str  # YYYY-MM-DD
    startTime: str  # HH:MM
    endTime: str  # HH:MM
    isBooked: bool = False


class Booking(BaseModel):
    id: str
    providerId: str
    type: str = "booking"
    slotId: str
    customerId: str
    serviceId: str
    date: str
    startTime: str
    endTime: str
    status: str = "confirmed"  # confirmed | cancelled
    createdAt: str


class Customer(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    createdAt: str
