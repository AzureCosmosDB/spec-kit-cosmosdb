from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cosmos_endpoint: str = "http://localhost:8081"
    cosmos_key: str = ""
    cosmos_database: str = "ecommerce"
    app_name: str = "cosmos-intent-sdk/0.1.0"

    class Config:
        env_file = ".env"


settings = Settings()
