"""Pydantic v2 models for leaderboard data."""
from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime, timezone


# PARTITION KEY: /region
# JUSTIFICATION: The regional top 100 query (Query 2) is the most frequent
# targeted read and filters exclusively by region. Global top 100 (Query 1)
# is cross-partition by design. Player lookups (Query 3) are cross-partition
# but lower frequency. Region partitioning also enables efficient weekly
# reset operations scoped to region.


class ScoreDocument(BaseModel):
    """Player score document stored in Cosmos DB."""
    model_config = {"populate_by_name": True}

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str = "score"
    player_id: str = Field(alias="playerId")
    player_name: str = Field(alias="playerName")
    region: str
    score: int
    week: str = Field(default="", alias="week")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), alias="createdAt")
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), alias="updatedAt")


class ScoreSubmission(BaseModel):
    """Request body for score submission."""
    model_config = {"populate_by_name": True}

    player_id: str = Field(alias="playerId")
    player_name: str = Field(alias="playerName")
    region: str
    score: int


class PlayerScoreResponse(BaseModel):
    """Response with player score and global rank."""
    model_config = {"populate_by_name": True}

    player_id: str = Field(alias="playerId")
    player_name: str = Field(alias="playerName")
    region: str
    score: int
    global_rank: int = Field(alias="globalRank")
