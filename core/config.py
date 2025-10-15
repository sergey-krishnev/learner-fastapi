# app/core/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # ==== App ====
    app_name: str = Field(default="learner", alias="APP_NAME")
    # Разрешим как APP_DEBUG, так и DEBUG (из твоего .env используется DEBUG)
    debug: bool = Field(default=False, alias="DEBUG")

    # ==== Database ====
    db_url: str = Field(alias="APP_DB_URL")

    # ==== CORS ====
    cors_allowed_origins: list[str] = Field(default_factory=list, alias="APP_CORS_ALLOWED_ORIGINS")
    cors_allowed_methods: list[str] = Field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"],
                                            alias="APP_CORS_ALLOWED_METHODS")
    cors_allowed_headers: list[str] = Field(default_factory=lambda: ["*"], alias="APP_CORS_ALLOWED_HEADERS")
    cors_allow_credentials: bool = Field(default=True, alias="APP_CORS_ALLOW_CREDENTIALS")
    cors_max_age: int = Field(default=3600, alias="APP_CORS_MAX_AGE")

    # Поведение загрузки .env
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,   # переменные окружения без учёта регистра
        extra="ignore",         # игнорировать лишние ключи
    )

settings = Settings()
