from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "JobAPI"
    ENVIRONMENT: str = "production"
    LOG_LEVEL: str = "info"

    class Config:
        env_file = ".env"

settings = Settings()