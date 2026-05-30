from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///data/games.db"
    GAMES_DIR: str = "data/games"
    SCREENSHOTS_DIR: str = "data/screenshots"
    RUNNER_IMAGE: str = "pygame-runner:latest"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-v4-pro"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()


def ensure_dirs() -> None:
    Path(settings.GAMES_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.SCREENSHOTS_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.DATABASE_URL.replace("sqlite:///", "")).parent.mkdir(
        parents=True, exist_ok=True
    )
