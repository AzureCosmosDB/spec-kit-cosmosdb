from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid


class BaseDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    _etag: Optional[str] = None
    _ts: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Player(BaseDocument):
    type: str = "player"
    player_id: str
    display_name: str
    region: str  # partition key
    lifetime_score: int = 0
    current_week_score: int = 0
    rank_global: Optional[int] = None
    rank_regional: Optional[int] = None


class Score(BaseDocument):
    type: str = "score"
    player_id: str
    region: str  # partition key
    value: int
    game_mode: str
    week: int
    year: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
