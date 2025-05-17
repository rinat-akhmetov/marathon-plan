from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GOOGLE_CLIENT_ID: str = Field(..., env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = Field(..., env="GOOGLE_CLIENT_SECRET")
    DATABASE_URL: str = Field("sqlite:///./app.db", env="DATABASE_URL")
    SECRET_KEY: str = Field("change_me_secret")

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()
