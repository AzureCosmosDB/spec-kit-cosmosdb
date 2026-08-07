from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ScoreDocument(BaseModel):
    id: str
    player_id: str
    score: int
    game_mode: str
    region: str
    week_number: int
    year: int
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    type: str = "score"
    _etag: Optional[str] = None
    _ts: Optional[int] = None

    # Partition key: /player_id
