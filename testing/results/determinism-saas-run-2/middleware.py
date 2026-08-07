"""Tenant extraction and validation middleware."""
from fastapi import Request, HTTPException


async def validate_tenant(request: Request, tenant_id: str):
    """Validate that authenticated user belongs to the requested tenant.
    
    In production, extract tenantId from JWT token and compare
    against the path parameter.
    """
    # TODO: Extract tenant from auth token
    auth_tenant = request.headers.get("X-Tenant-Id")
    if auth_tenant and auth_tenant != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant mismatch")
    return tenant_id
