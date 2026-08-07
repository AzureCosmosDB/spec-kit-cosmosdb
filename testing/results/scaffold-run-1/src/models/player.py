from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PlayerDocument(BaseModel):
    id: str
    player_id: str
    username: str
    region: str
    total_score: int = 0
    weekly_score: int = 0
    games_played: int = 0
    last_active: datetime = Field(default_factory=datetime.utcnow)
    type: str = "player"
    _etag: Optional[str] = None
    _ts: Optional[int] = None

    # Partition key: /region
