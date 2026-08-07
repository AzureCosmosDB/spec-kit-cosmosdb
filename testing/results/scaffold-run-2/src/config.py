import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    COSMOS_ENDPOINT: str = "https://localhost:8081"
    COSMOS_KEY: str = ""
    DATABASE_NAME: str = "game_leaderboard"
    ENVIRONMENT: str = "dev"
    APP_NAME: str = "leaderboard-service"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
