from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "JobAPI"
    ENVIRONMENT: str = "production"
    LOG_LEVEL: str = "info"

    DATABASE_URL: str  # REQUIRED — no default

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
