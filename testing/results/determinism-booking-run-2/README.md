# Booking System API

Azure Cosmos DB-powered appointment booking system built with FastAPI.

## Architecture

- **Language**: Python / FastAPI
- **Database**: Azure Cosmos DB
- **Scale**: 1K providers, 50K customers, 200K bookings/year

## Containers & Partition Keys

| Container | Partition Key | Justification |
|-----------|--------------|---------------|
| providers | `/id` | Providers accessed by own ID; services co-located |
| schedule | `/providerId` | >80% queries: slots/bookings for provider on date |
| customers | `/id` | Customers accessed by own ID |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Cosmos DB credentials
uvicorn main:app --reload --port 8000
```

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/providers/{id}/availability?date=YYYY-MM-DD` - Available slots
- `GET /api/providers/{id}/bookings?date=YYYY-MM-DD` - Provider bookings
- `GET /api/providers/{id}/services` - Provider services
- `POST /api/bookings` - Create booking (etag-based conflict prevention)
- `DELETE /api/bookings/{id}` - Cancel booking
- `GET /api/customers/{id}/bookings` - Customer booking history
- `POST /api/providers/{id}/slots/generate` - Generate time slots
