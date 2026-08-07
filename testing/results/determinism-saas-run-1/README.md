# SaaS Platform API

Azure Cosmos DB-powered multi-tenant SaaS platform built with FastAPI.

## Architecture

- **Language**: Python / FastAPI
- **Database**: Azure Cosmos DB
- **Scale**: 500 tenants, 50K users, 1M usage records/month

## Containers & Partition Keys

| Container | Partition Key | Justification |
|-----------|--------------|---------------|
| tenants | `/id` | Tenants accessed by own ID |
| tenantData | `/tenantId` (hierarchical: `/tenantId/type`) | 100% of queries filter by tenantId first |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Cosmos DB credentials
uvicorn main:app --reload --port 8000
```

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/tenants/{id}/users` - Users for tenant
- `POST /api/tenants/{id}/users` - Create user
- `GET /api/tenants/{id}/subscription` - Subscription status
- `PATCH /api/tenants/{id}/subscription` - Update subscription
- `GET /api/tenants/{id}/usage?from=&to=` - Usage metrics
- `POST /api/tenants/{id}/usage/record` - Record usage
