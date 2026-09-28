from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Knowva AI"

    # OpenAI
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    # PostgreSQL
    database_url: str = (
        "postgresql+psycopg://"
        "knowva:knowva_local_password@localhost:5433/knowva"
    )

    # ChromaDB
    chroma_path: str = "./data/chroma"

    # Document processing
    max_upload_mb: int = 10
    chunk_size: int = 2500
    chunk_overlap: int = 300
    retrieval_count: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()