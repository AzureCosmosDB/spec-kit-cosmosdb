"""Appointment Booking System API - Azure Cosmos DB"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from config import get_settings
from repository import ScheduleRepository, ProviderRepository, CustomerRepository
from service import BookingService, AvailabilityService
from azure.cosmos.aio import CosmosClient

settings = get_settings()
cosmos_client = None
booking_service = None
availability_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global cosmos_client, booking_service, availability_service
    cosmos_client = CosmosClient(settings.cosmos_endpoint, settings.cosmos_key)
    database = cosmos_client.get_database_client(settings.cosmos_database)
    
    schedule_repo = ScheduleRepository(database.get_container_client("schedule"))
    provider_repo = ProviderRepository(database.get_container_client("providers"))
    customer_repo = CustomerRepository(database.get_container_client("customers"))
    
    booking_service = BookingService(schedule_repo)
    availability_service = AvailabilityService(schedule_repo)
    
    yield
    
    await cosmos_client.close()


app = FastAPI(title="Booking System", lifespan=lifespan)


@app.get("/api/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/providers/{provider_id}/availability")
async def get_availability(provider_id: str, date: str):
    slots = await availability_service.get_available_slots(provider_id, date)
    return slots


@app.get("/api/providers/{provider_id}/bookings")
async def get_provider_bookings(provider_id: str, date: str):
    bookings = await booking_service.get_provider_bookings(provider_id, date)
    return bookings


@app.get("/api/providers/{provider_id}/services")
async def get_provider_services(provider_id: str):
    from repository import ProviderRepository
    services = await provider_repo.get_services(provider_id)
    return services


@app.post("/api/bookings", status_code=201)
async def create_booking(booking_request: dict):
    result = await booking_service.create_booking(booking_request)
    return result


@app.delete("/api/bookings/{booking_id}", status_code=204)
async def cancel_booking(booking_id: str, provider_id: str):
    await booking_service.cancel_booking(booking_id, provider_id)


@app.get("/api/customers/{customer_id}/bookings")
async def get_customer_bookings(customer_id: str):
    bookings = await booking_service.get_customer_bookings(customer_id)
    return bookings


@app.post("/api/providers/{provider_id}/slots/generate", status_code=201)
async def generate_slots(provider_id: str, request: dict):
    slots = await availability_service.generate_slots(provider_id, request["startDate"], request["endDate"], request.get("intervalMinutes", 30))
    return slots


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
