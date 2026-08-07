from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid


class LeaderboardEntry(BaseModel):
    """Single container 'leaderboard' with partition key /region_week (composite).
    
    This enables efficient queries for regional+weekly leaderboards without cross-partition queries.
    Global rankings use a materialized view in a separate container.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str = "entry"
    player_id: str
    player_name: str
    region: str
    region_week: str  # Partition key: "{region}_{year}W{week}" e.g. "NA_2024W05"
    score: int
    game_mode: str
    week: int
    year: int
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    _etag: Optional[str] = None
    _ts: Optional[int] = None


class PlayerAggregate(BaseModel):
    """Container 'players' with partition key /player_id for player lookups."""
    id: str  # same as player_id
    type: str = "aggregate"
    player_id: str  # partition key
    player_name: str
    region: str
    all_time_score: int = 0
    weekly_high: int = 0
    games_count: int = 0
    _etag: Optional[str] = None
    _ts: Optional[int] = None


class GlobalRanking(BaseModel):
    """Container 'global_rankings' with partition key /rank_bucket.
    Materialized by change feed processor. Bucket = rank // 100."""
    id: str
    type: str = "ranking"
    rank_bucket: int  # partition key: 0 for ranks 1-100, 1 for 101-200, etc.
    player_id: str
    player_name: str
    region: str
    all_time_score: int
    rank: int
