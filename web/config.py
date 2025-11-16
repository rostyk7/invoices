import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):   
    # Environment: development or production
    # Reads from ENVIRONMENT env var, defaults to "development"
    environment: str = "development"
    
    # Database URL (optional - if not set, will use SQLite or individual PostgreSQL vars)
    # Reads from DATABASE_URL env var
    database_url: Optional[str] = None
    
    sqlite_db_path: str = "invoices.db"
    
    postgres_host: Optional[str] = None
    postgres_port: int = 5432
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_db: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_prefix = "" 


def get_database_url() -> str:
    settings = Settings()
    
    database_url = os.getenv("DATABASE_URL") or settings.database_url
    if database_url:
        # Handle postgres:// vs postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return database_url
    
    if settings.environment == "production":
        if not all([
            settings.postgres_host,
            settings.postgres_user,
            settings.postgres_password,
            settings.postgres_db
        ]):
            raise ValueError(
                "Production environment requires either DATABASE_URL or "
                "POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB environment variables"
            )
        
        return (
            f"postgresql://{settings.postgres_user}:{settings.postgres_password}"
            f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
        )
    
    db_path = settings.sqlite_db_path
    if not os.path.isabs(db_path):
        web_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(web_dir, db_path)
    
    return f"sqlite:///{db_path}"


settings = Settings()

