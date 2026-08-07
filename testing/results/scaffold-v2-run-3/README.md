# Game Leaderboard API

A mobile game leaderboard that tracks player scores, shows global and regional rankings, and supports weekly resets.

## Architecture

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: Azure Cosmos DB (scores container, partition key: `/region`)
- **Scale**: 500K active players, 1M scores/day

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in credentials:
   ```bash
   cp .env.example .env
   ```

3. Required environment variables:
   - `COSMOS_ENDPOINT` - Azure Cosmos DB endpoint URL
   - `COSMOS_KEY` - Azure Cosmos DB primary key
   - `COSMOS_DATABASE` - Database name (default: `leaderboard`)

4. Run the application:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/scores` | Global top 100 leaderboard |
| GET | `/api/scores/regions/{region}` | Regional top 100 leaderboard |
| GET | `/api/scores/players/{player_id}` | Player score and rank |
| POST | `/api/scores` | Submit new score |

## Data Model

### Scores Container (Partition Key: `/region`)

```json
{
  "id": "uuid",
  "type": "score",
  "playerId": "player-123",
  "playerName": "PlayerOne",
  "region": "us-east",
  "score": 9500,
  "week": "2026-W30",
  "createdAt": "2026-07-26T21:32:00Z",
  "updatedAt": "2026-07-26T21:32:00Z"
}
```
