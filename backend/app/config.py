from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = "CodeCrew API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    cors_origins: tuple[str, ...] = (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    )


def load_settings() -> Settings:
    configured_origins = os.getenv("CORS_ORIGINS")
    if not configured_origins:
        return Settings()

    origins = tuple(
        origin.strip()
        for origin in configured_origins.split(",")
        if origin.strip()
    )
    return Settings(cors_origins=origins)


settings = load_settings()
