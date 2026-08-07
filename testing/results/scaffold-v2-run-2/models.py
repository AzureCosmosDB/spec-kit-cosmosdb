"""Pydantic v2 data models for the leaderboard."""
from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime, timezone


# PARTITION KEY: /region
# JUSTIFICATION: Query 2 (regional top 100) is the highest-frequency read query
# and filters by region. Query 1 (global top 100) is inherently cross-partition.
# Partitioning by region enables efficient regional reads and supports weekly
# reset batch operations per region. Player lookups (Query 3) require
# cross-partition but are point-read frequency, not fan-out heavy.


class ScoreDocument(BaseModel):
    """A player score entry in the leaderboard."""
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
    """Request body for submitting a score."""
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
