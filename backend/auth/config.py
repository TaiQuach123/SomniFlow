from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class JWTConfig(BaseSettings):
    JWT_SECRET: str = Field(..., env="JWT_SECRET")
    JWT_ALGORITHM: str = Field(..., env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(..., env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(..., env="REFRESH_TOKEN_EXPIRE_DAYS")
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class OAuthConfig(BaseSettings):
    GOOGLE_CLIENT_ID: str = Field(..., env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = Field(..., env="GOOGLE_CLIENT_SECRET")
    GOOGLE_ACCESS_TOKEN_URL: str = "https://oauth2.googleapis.com/token"
    GOOGLE_AUTHORIZE_URL: str = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_API_BASE_URL: str = "https://www.googleapis.com/oauth2/v2/"
    GOOGLE_USERINFO_ENDPOINT: str = "https://openidconnect.googleapis.com/v2/userinfo"
    SESSION_SECRET_KEY: str = Field(..., env="SESSION_SECRET_KEY")
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


jwt_config = JWTConfig()
oauth_config = OAuthConfig()
