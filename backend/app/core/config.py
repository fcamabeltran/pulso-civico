from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Pulso Civico API"
    app_env: str = "development"
    debug: bool = True
    api_prefix: str = "/api"

    postgres_server: str = "db"
    postgres_user: str = "pulso"
    postgres_password: str = "pulso"
    postgres_db: str = "pulso_civico"
    postgres_port: int = 5432
    database_url: str | None = None

    chroma_path: str = "/app/chroma"
    embeddings_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    rag_collection_name: str = "proposals"
    rag_top_k: int = 4

    llm_provider: Literal["groq", "openai", "mock"] = "mock"
    groq_api_key: str | None = None
    groq_model: str = "llama-3.1-8b-instant"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    share_image_width: int = 1080
    share_image_height: int = 1350

    scrape_timeout_seconds: int = 30
    scrape_user_agent: str = "Pulso-Civico-Bot/0.1 (+https://localhost)"
    scrape_raw_dir: str = "/app/data/raw"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
