from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cosmos_endpoint: str = "http://localhost:8081"
    cosmos_key: str = "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
    database_name: str = "todo_app"
    app_name: str = "todo-api"

    class Config:
        env_prefix = "COSMOS_"


settings = Settings()
