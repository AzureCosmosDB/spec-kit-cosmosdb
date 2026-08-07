from pydantic_settings import BaseSettings


class Config(BaseSettings):
    cosmos_uri: str = "https://localhost:8081"
    cosmos_primary_key: str = ""
    cosmos_db_name: str = "leaderboards"
    application_name: str = "mobile-game-leaderboard"
    max_retry_attempts: int = 9
    max_retry_wait_seconds: int = 30
    connection_mode: str = "Direct"

    class Config:
        env_prefix = "APP_"
        env_file = ".env"


config = Config()
