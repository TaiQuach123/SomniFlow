from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    POSTGRES_DB_URL: str = Field(..., env="POSTGRES_DB_URL")
    ASYNC_POSTGRES_DB_URL: str = Field(..., env="ASYNC_POSTGRES_DB_URL")
    REDIS_HOST: str = Field(..., env="REDIS_HOST")
    REDIS_PORT: int = Field(..., env="REDIS_PORT")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


Config = Settings()
