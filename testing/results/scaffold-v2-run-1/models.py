"""Pydantic v2 models for the leaderboard application."""
from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime, timezone


# PARTITION KEY: /region
# JUSTIFICATION: Primary queries filter by region (regional top 100) which is the
# most performance-critical read query. Global top 100 is cross-partition by nature.
# Player lookups by playerId require cross-partition query but are less frequent
# than regional leaderboard reads at 500K active players across regions.
# Weekly resets are batch operations that benefit from region-based partitioning.


class ScoreDocument(BaseModel):
    """Represents a player's score entry in the leaderboard."""
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
    """Request body for submitting a new score."""
    model_config = {"populate_by_name": True}

    player_id: str = Field(alias="playerId")
    player_name: str = Field(alias="playerName")
    region: str
    score: int


class PlayerScoreResponse(BaseModel):
    """Response for player score with rank."""
    model_config = {"populate_by_name": True}

    player_id: str = Field(alias="playerId")
    player_name: str = Field(alias="playerName")
    region: str
    score: int
    global_rank: int = Field(alias="globalRank")
