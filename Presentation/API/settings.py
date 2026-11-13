from functools import lru_cache
from pathlib import Path
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str = 'sqlite:///./data/doc-rag.db'
    documents_path: Path = Path('examples/documents')
    vector_path: str = './data/chroma'
    ollama_url: str = 'http://localhost:11434'
    chat_model: str = 'qwen2.5:3b'
    embedding_model: str = 'nomic-embed-text'
    api_token: str = ''
    require_review: bool = True
    scan_interval: int = Field(default=30, ge=1)
    chunk_size: int = Field(default=1800, ge=200, le=10000)
    chunk_overlap: int = Field(default=250, ge=0)
    max_file_bytes: int = Field(default=20 * 1024 * 1024, ge=1)
    min_similarity: float = Field(default=0.35, ge=-1, le=1)
    cors_origins: list[str] = ['http://localhost:5173', 'http://localhost:8080']

    @model_validator(mode='after')
    def validate_overlap(self):
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError('chunk_overlap deve ser menor que chunk_size')
        return self


@lru_cache
def get_settings():
    return Settings()
