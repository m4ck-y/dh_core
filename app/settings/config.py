from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Digital Hospital - Core Service"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    ROOT_PATH: str = "/api/core"
    CORS_ORIGINS: list[str] = ["*"]

    POSTGRES_URL: str

    SERVICE_LOGGER_URL: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
