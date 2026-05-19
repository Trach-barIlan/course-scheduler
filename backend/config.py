from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings and environment variable validation.
    """
    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    # Flask/Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    FLASK_SECRET_KEY: Optional[str] = None
    FLASK_ENV: str = "development"
    
    # API Keys
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_API_URL: str = "https://generativelanguage.googleapis.com"
    GEMINI_MODEL: str = "text-bison-001"
    
    # App Config
    PORT: int = 5001
    CORS_ORIGINS: str = "http://localhost:3000"
    SKIP_AI_MODEL: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Global settings instance
settings = Settings()
