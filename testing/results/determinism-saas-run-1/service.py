"""Business logic for SaaS platform."""
import uuid
from datetime import datetime


class TenantService:
    def __init__(self, tenant_repo):
        self.tenant_repo = tenant_repo

    async def get_tenant(self, tenant_id: str):
        return await self.tenant_repo.get_tenant(tenant_id)

    async def list_by_plan(self, plan: str):
        return await self.tenant_repo.list_tenants_by_plan(plan)


class UserService:
    def __init__(self, tenant_data_repo):
        self.repo = tenant_data_repo

    async def get_users_for_tenant(self, tenant_id: str):
        return await self.repo.get_items_by_tenant_and_type(tenant_id, "user")

    async def create_user(self, tenant_id: str, user_data: dict):
        user = {
            "id": str(uuid.uuid4()),
            "tenantId": tenant_id,
            "type": "user",
            "email": user_data["email"],
            "role": user_data.get("role", "member"),
            "createdAt": datetime.utcnow().isoformat(),
            "updatedAt": datetime.utcnow().isoformat(),
        }
        return await self.repo.create_item(user)


class SubscriptionService:
    VALID_TRANSITIONS = {
        "trial": ["active"],
        "active": ["past_due", "cancelled"],
        "past_due": ["active", "suspended", "cancelled"],
        "suspended": ["active", "cancelled"],
        "cancelled": [],
    }

    def __init__(self, tenant_data_repo):
        self.repo = tenant_data_repo

    async def get_subscription(self, tenant_id: str):
        items = await self.repo.get_items_by_tenant_and_type(tenant_id, "subscription")
        return items[0] if items else None

    async def update_subscription(self, tenant_id: str, update: dict):
        sub = await self.get_subscription(tenant_id)
        if not sub:
            raise Exception("404: Subscription not found")
        if "status" in update:
            current = sub["status"]
            target = update["status"]
            if target not in self.VALID_TRANSITIONS.get(current, []):
                raise Exception(f"409: Invalid transition from {current} to {target}")
        sub.update(update)
        return await self.repo.replace_item(sub["id"], sub, tenant_id)


class UsageService:
    def __init__(self, tenant_data_repo):
        self.repo = tenant_data_repo

    async def get_usage_metrics(self, tenant_id: str, from_date: str, to_date: str):
        if from_date and to_date:
            return await self.repo.get_usage_in_range(tenant_id, from_date, to_date)
        return await self.repo.get_items_by_tenant_and_type(tenant_id, "usageMetric")

    async def record_metric(self, tenant_id: str, metric: dict):
        item = {
            "id": str(uuid.uuid4()),
            "tenantId": tenant_id,
            "type": "usageMetric",
            "date": metric.get("date", datetime.utcnow().strftime("%Y-%m-%d")),
            "apiCalls": metric.get("apiCalls", 0),
            "storageBytes": metric.get("storageBytes", 0),
            "activeUsers": metric.get("activeUsers", 0),
        }
        return await self.repo.create_item(item)
