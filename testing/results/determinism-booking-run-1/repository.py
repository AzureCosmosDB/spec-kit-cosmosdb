"""Cosmos DB repositories for the booking system."""
from azure.cosmos import exceptions


class ScheduleRepository:
    """Repository for schedule container (TimeSlots + Bookings).
    
    # PARTITION KEY: /providerId
    # JUSTIFICATION: Availability and booking queries are always scoped to a provider.
    # TimeSlots and Bookings co-located for transactional batch on booking creation.
    # Cross-partition required for: customer booking history (use denormalized container).
    """

    def __init__(self, container):
        self.container = container

    async def get_available_slots(self, provider_id: str, date: str):
        query = "SELECT * FROM c WHERE c.providerId = @providerId AND c.date = @date AND c.type = 'slot' AND c.isBooked = false"
        params = [
            {"name": "@providerId", "value": provider_id},
            {"name": "@date", "value": date},
        ]
        items = []
        async for item in self.container.query_items(
            query=query, parameters=params, partition_key=provider_id
        ):
            items.append(item)
        return items

    async def get_bookings_by_provider(self, provider_id: str, date: str):
        query = "SELECT * FROM c WHERE c.providerId = @providerId AND c.date = @date AND c.type = 'booking'"
        params = [
            {"name": "@providerId", "value": provider_id},
            {"name": "@date", "value": date},
        ]
        items = []
        async for item in self.container.query_items(
            query=query, parameters=params, partition_key=provider_id
        ):
            items.append(item)
        return items

    async def read_slot(self, slot_id: str, provider_id: str):
        return await self.container.read_item(item=slot_id, partition_key=provider_id)

    async def replace_slot(self, slot_id: str, body: dict, etag: str):
        return await self.container.replace_item(
            item=slot_id, body=body, match_condition=etag, etag=etag
        )

    async def create_booking(self, booking: dict):
        return await self.container.create_item(body=booking)

    async def get_bookings_by_customer(self, customer_id: str):
        # Cross-partition query - explicit: customer booking history
        query = "SELECT * FROM c WHERE c.customerId = @customerId AND c.type = 'booking'"
        params = [{"name": "@customerId", "value": customer_id}]
        items = []
        async for item in self.container.query_items(
            query=query, parameters=params, enable_cross_partition_query=True
        ):
            items.append(item)
        return items

    async def create_slot(self, slot: dict):
        return await self.container.create_item(body=slot)


class ProviderRepository:
    """Repository for providers container.
    
    # PARTITION KEY: /id
    # JUSTIFICATION: Providers accessed by own ID; services co-located.
    """

    def __init__(self, container):
        self.container = container

    async def get_services(self, provider_id: str):
        query = "SELECT * FROM c WHERE c.providerId = @providerId AND c.type = 'service'"
        params = [{"name": "@providerId", "value": provider_id}]
        items = []
        async for item in self.container.query_items(
            query=query, parameters=params, partition_key=provider_id
        ):
            items.append(item)
        return items


class CustomerRepository:
    """Repository for customers container.
    
    # PARTITION KEY: /id
    # JUSTIFICATION: Customers accessed by own ID.
    """

    def __init__(self, container):
        self.container = container

    async def get_customer(self, customer_id: str):
        return await self.container.read_item(item=customer_id, partition_key=customer_id)
