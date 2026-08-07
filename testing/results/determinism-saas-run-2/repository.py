"""Cosmos DB repositories for the SaaS platform."""


class TenantRepository:
    """Repository for tenants container.
    
    # PARTITION KEY: /id
    # JUSTIFICATION: Tenants accessed by own ID.
    """

    def __init__(self, container):
        self.container = container

    async def get_tenant(self, tenant_id: str):
        return await self.container.read_item(item=tenant_id, partition_key=tenant_id)

    async def list_tenants_by_plan(self, plan: str):
        # Cross-partition query - explicit: admin operation, paginated
        query = "SELECT * FROM c WHERE c.plan = @plan"
        params = [{"name": "@plan", "value": plan}]
        items = []
        async for item in self.container.query_items(
            query=query, parameters=params, enable_cross_partition_query=True
        ):
            items.append(item)
        return items


class TenantDataRepository:
    """Repository for tenantData container.
    
    # PARTITION KEY: /tenantId (hierarchical: /tenantId/type)
    # JUSTIFICATION: 100% of queries on tenantData filter by tenantId first. Hierarchical
    # key with /type enables efficient queries for "all users in tenant" vs "subscription for tenant".
    # Cross-partition required for: admin list-all-tenants (opt-in, paginated).
    """

    def __init__(self, container):
        self.container = container

    async def get_items_by_tenant_and_type(self, tenant_id: str, item_type: str):
        query = "SELECT * FROM c WHERE c.tenantId = @tenantId AND c.type = @type"
        params = [
            {"name": "@tenantId", "value": tenant_id},
            {"name": "@type", "value": item_type},
        ]
        items = []
        async for item in self.container.query_items(
            query=query, parameters=params, partition_key=tenant_id
        ):
            items.append(item)
        return items

    async def get_usage_in_range(self, tenant_id: str, from_date: str, to_date: str):
        query = "SELECT * FROM c WHERE c.tenantId = @tenantId AND c.type = 'usageMetric' AND c.date >= @from AND c.date <= @to"
        params = [
            {"name": "@tenantId", "value": tenant_id},
            {"name": "@from", "value": from_date},
            {"name": "@to", "value": to_date},
        ]
        items = []
        async for item in self.container.query_items(
            query=query, parameters=params, partition_key=tenant_id
        ):
            items.append(item)
        return items

    async def create_item(self, item: dict):
        return await self.container.create_item(body=item)

    async def replace_item(self, item_id: str, body: dict, partition_key: str):
        return await self.container.replace_item(item=item_id, body=body)
