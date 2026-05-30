import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEEPSEEK_API_KEY: str = ""
    QDRANT_URL: str = "http://localhost:6333"
    DATABASE_URL: str = "sqlite:///./data/agent_town.db"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    EMBEDDING_MODEL: str = "BAAI/bge-small-zh-v1.5"
    LLM_MODEL: str = "deepseek-chat"
    LLM_BASE_URL: str = "https://api.deepseek.com"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
