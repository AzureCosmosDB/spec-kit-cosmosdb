from pydantic_settings import BaseSettings


class CosmosSettings(BaseSettings):
    cosmos_endpoint: str = "https://localhost:8081"
    cosmos_key: str = ""
    cosmos_database: str = "leaderboard_db"
    cosmos_connection_mode: str = "Direct"
    app_name: str = "game-leaderboard-api"

    class Config:
        env_file = ".env"


class AppSettings(BaseSettings):
    environment: str = "development"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = CosmosSettings()
app_settings = AppSettings()
