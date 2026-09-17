from typing import List, Union
from urllib.parse import quote_plus
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from backend.app.core.constants import Environment


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

    APP_NAME: str = "Employee Support Assistant"
    ENVIRONMENT: str = Environment.DEVELOPMENT.value
    HOST: str = "0.0.0.0"
    PORT: int = 3001
    API_V1_STR: str = "/api/v1"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == Environment.DEVELOPMENT.value

    # Database
    DB_DIALECT: str = "postgresql+asyncpg"
    DB_SYNC_DIALECT: str = "postgresql+psycopg2"
    DB_HOST_NAME: str = "localhost"
    DB_PORT: int = 5432
    DB_USER_NAME: str = "postgres"
    DB_PASSWORD: str = "Mind@123"
    DB_DATABASE: str = "employee_support_assistant"

    # CORS
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://localhost:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            import json
            if isinstance(v, str):
                return json.loads(v)
            return v
        return []

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        encoded_pw = quote_plus(self.DB_PASSWORD)
        return (
            f"{self.DB_DIALECT}://{self.DB_USER_NAME}:{encoded_pw}"
            f"@{self.DB_HOST_NAME}:{self.DB_PORT}/{self.DB_DATABASE}"
        )

    @property
    def SYNC_DATABASE_URL(self) -> str:
        encoded_pw = quote_plus(self.DB_PASSWORD)
        return (
            f"{self.DB_SYNC_DIALECT}://{self.DB_USER_NAME}:{encoded_pw}"
            f"@{self.DB_HOST_NAME}:{self.DB_PORT}/{self.DB_DATABASE}"
        )


settings = Settings()
