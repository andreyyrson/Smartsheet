from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SMARTSHEET_API_TOKEN: str = ""
    DATABASE_URL: str = "postgresql+psycopg2://aip:aip@postgres:5432/aip"
    REDIS_URL: str = "redis://redis:6379/0"
    SYNC_INTERVAL_MINUTES: int = 15
    FULL_SYNC_INTERVAL_HOURS: int = 24
    JWT_SECRET: str = "change-me-in-production"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
