"""Application configuration using pydantic-settings."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cosmos_endpoint: str = "https://localhost:8081"
    cosmos_key: str = ""
    cosmos_database: str = "leaderboard"
    app_name: str = "game-leaderboard"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
