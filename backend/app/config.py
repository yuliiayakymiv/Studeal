from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://studeal:studeal@localhost:5432/studeal"
    # Cognito sign-in (as in spry, Lab 4). Empty issuer = auth off: every request acts as one
    # local user (docker compose, tests). In AWS both are set, and /api/me needs a valid token.
    cognito_issuer: str = ""  # https://cognito-idp.eu-central-1.amazonaws.com/<user pool id>
    cognito_client_id: str = ""
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]
    # CSV files for `make seed`: docs/data/ in the repo (mounted at /docs/data in Docker).
    seed_dir: Path = Path(__file__).resolve().parents[2] / "docs" / "data"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()
