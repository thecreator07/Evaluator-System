from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:4b"
    ollama_embedding_model: str = "nomic-embed-text:latest"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key:str="aman"
    mongo_uri: SecretStr
    mongo_db: str = "lesson_memory"
    delete_finished_threads: bool = True
    output_dir: str = "output"



settings = Settings()