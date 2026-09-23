from pathlib import Path
from typing import List, Union, Optional
from urllib.parse import quote_plus
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from backend.app.core.constants import Environment

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(BASE_DIR / ".env"), ".env"),
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

    # AI & Groq Configuration
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    GROQ_API_URL: str = "https://api.groq.com/openai/v1/chat/completions"


    # Embedding & RAG Configuration
    EMBEDDING_PROVIDER: str = "local"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIMENSION: int = 384
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    RAG_TOP_K: int = 4
    UPLOAD_DIR: str = "uploads"

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
