import os
from pydantic_settings import BaseSettings
import secrets


class Settings(BaseSettings):
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL", "postgresql://user:password@db/mydatabase"
    )

    # --- JWT Settings ---
    # To generate a good secret key, run this in a Python shell:
    # import secrets
    # secrets.token_urlsafe(32)
    SECRET_KEY: str = os.environ.get("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # One week

    class Config:
        env_file = ".env"


settings = Settings()