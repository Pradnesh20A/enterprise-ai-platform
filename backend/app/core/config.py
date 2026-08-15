"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration for the Enterprise AI Platform.

    All values can be overridden via environment variables or a .env file.
    """

    # Application
    APP_NAME: str = "Enterprise AI Platform"
    APP_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/enterprise_ai"
    )

    # File Upload
    UPLOAD_DIR: str = "data/uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS: set[str] = {"pdf", "docx", "txt", "jpg", "jpeg", "png"}

    # Vector Store (Milestone 2)
    VECTOR_STORE_DIR: str = "data/vector_store"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
