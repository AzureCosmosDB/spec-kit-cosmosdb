"""Configuration for Cosmos DB connection."""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cosmos_endpoint: str
    cosmos_key: str
    cosmos_database: str = "saasdb"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
