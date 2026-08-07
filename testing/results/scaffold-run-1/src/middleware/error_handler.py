from fastapi import Request
from fastapi.responses import JSONResponse
from azure.cosmos.exceptions import CosmosHttpResponseError


async def cosmos_exception_handler(request: Request, exc: CosmosHttpResponseError):
    status_map = {
        400: 400,
        401: 401,
        403: 403,
        404: 404,
        409: 409,
        412: 412,
        429: 503,  # Rate limited -> Service Unavailable
        500: 502,
    }
    http_status = status_map.get(exc.status_code, 500)
    return JSONResponse(
        status_code=http_status,
        content={
            "error": exc.message,
            "cosmos_status": exc.status_code,
        },
    )
