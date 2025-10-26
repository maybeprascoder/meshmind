"""Application settings and configuration."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # OpenAI Configuration
    openai_api_key: str
    
    # Database Configuration
    mongodb_uri: str
    redis_url: str
    neo4j_uri: str
    neo4j_user: str
    neo4j_pass: str
    
    # Application Configuration
    jwt_secret: str = "dev-secret"
    llm_model: str = "gpt-4o-mini"
    port_ingest_api: int = 8081
    port_query_api: int = 8082
    
    # Feature Flags
    feature_vector: bool = False
    
    # Google Drive (optional)
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""
    google_drive_page_size: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
