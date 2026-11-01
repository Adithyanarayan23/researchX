from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    PROJECT_NAME: str = "ResearchX"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./researchx.db",
        description="SQLAlchemy database URL. e.g. postgresql://user:pass@localhost:5432/researchx or sqlite:///./researchx.db"
    )
    USE_PGVECTOR: bool = Field(default=False, description="Set to True when PostgreSQL + pgvector is available")

    # Redis & Worker
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    CELERY_BROKER_URL: Optional[str] = Field(default="redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: Optional[str] = Field(default="redis://localhost:6379/0")

    # LLM Settings (Multi-provider abstraction)
    LLM_PROVIDER: str = Field(default="mock", description="'gemini', 'openai', or 'mock'")
    LLM_MODEL: str = Field(default="gemini-2.5-flash", description="Default model name")
    GEMINI_API_KEY: Optional[str] = Field(default=None)
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    OPENAI_BASE_URL: Optional[str] = Field(default="https://api.openai.com/v1")
    LLM_TEMPERATURE: float = Field(default=0.2)
    LLM_MAX_TOKENS: int = Field(default=4096)

    # Embedding Settings
    EMBEDDING_PROVIDER: str = Field(default="mock", description="'gemini', 'openai', or 'mock'")
    EMBEDDING_MODEL: str = Field(default="text-embedding-004")
    EMBEDDING_DIMENSION: int = Field(default=768)

    # Search Provider
    SEARCH_PROVIDER: str = Field(default="duckduckgo", description="'duckduckgo', 'tavily', 'serper', or 'mock'")
    TAVILY_API_KEY: Optional[str] = Field(default=None)
    SERPER_API_KEY: Optional[str] = Field(default=None)

    # Hybrid Retrieval Weights
    RAG_SEMANTIC_WEIGHT: float = 0.65
    RAG_KEYWORD_WEIGHT: float = 0.25
    RAG_QUALITY_WEIGHT: float = 0.10

    # Quality Control
    QC_SCORE_THRESHOLD: float = 75.0
    QC_MAX_REVISIONS: int = 2

    # Security & Limits
    MAX_UPLOAD_SIZE_BYTES: int = 20 * 1024 * 1024  # 20 MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "docx", "txt", "md"]
    REQUEST_TIMEOUT_SECONDS: int = 30
    MAX_PARALLEL_RESEARCH_TASKS: int = 5

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "*"]


settings = Settings()
