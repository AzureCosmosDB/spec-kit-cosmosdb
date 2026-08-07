"""Business logic for booking and availability."""
import uuid
from datetime import datetime, timedelta
from azure.cosmos import exceptions


class BookingService:
    def __init__(self, schedule_repo):
        self.schedule_repo = schedule_repo

    async def create_booking(self, request: dict):
        """Book a slot with etag-based optimistic concurrency."""
        slot = await self.schedule_repo.read_slot(request["slotId"], request["providerId"])
        
        if slot.get("isBooked"):
            raise Exception("409: Slot already booked")
        
        etag = slot["_etag"]
        slot["isBooked"] = True
        
        try:
            await self.schedule_repo.replace_slot(slot["id"], slot, etag)
        except exceptions.CosmosAccessConditionFailedError:
            raise Exception("409: Conflict - slot was booked by another request")
        
        booking = {
            "id": str(uuid.uuid4()),
            "providerId": request["providerId"],
            "type": "booking",
            "slotId": request["slotId"],
            "customerId": request["customerId"],
            "serviceId": request["serviceId"],
            "date": slot["date"],
            "startTime": slot["startTime"],
            "endTime": slot["endTime"],
            "status": "confirmed",
            "createdAt": datetime.utcnow().isoformat(),
        }
        
        await self.schedule_repo.create_booking(booking)
        return booking

    async def cancel_booking(self, booking_id: str, provider_id: str):
        # Read booking, mark cancelled, free the slot
        pass

    async def get_provider_bookings(self, provider_id: str, date: str):
        return await self.schedule_repo.get_bookings_by_provider(provider_id, date)

    async def get_customer_bookings(self, customer_id: str):
        return await self.schedule_repo.get_bookings_by_customer(customer_id)


class AvailabilityService:
    def __init__(self, schedule_repo):
        self.schedule_repo = schedule_repo

    async def get_available_slots(self, provider_id: str, date: str):
        return await self.schedule_repo.get_available_slots(provider_id, date)

    async def generate_slots(self, provider_id: str, start_date: str, end_date: str, interval_minutes: int = 30):
        """Generate time slots for a provider over a date range."""
        slots = []
        current = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        while current <= end:
            hour = 9  # 9 AM start
            while hour < 17:  # 5 PM end
                start_time = f"{hour:02d}:{0:02d}"
                end_dt = datetime(current.year, current.month, current.day, hour) + timedelta(minutes=interval_minutes)
                end_time = f"{end_dt.hour:02d}:{end_dt.minute:02d}"
                
                slot = {
                    "id": str(uuid.uuid4()),
                    "providerId": provider_id,
                    "type": "slot",
                    "date": current.strftime("%Y-%m-%d"),
                    "startTime": start_time,
                    "endTime": end_time,
                    "isBooked": False,
                }
                await self.schedule_repo.create_slot(slot)
                slots.append(slot)
                hour += interval_minutes // 60
                if interval_minutes % 60:
                    break  # simplified
            current += timedelta(days=1)
        
        return slots
