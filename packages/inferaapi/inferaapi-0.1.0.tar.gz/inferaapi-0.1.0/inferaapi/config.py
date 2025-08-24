from typing import List

from dotenv import load_dotenv
from pydantic import Field, validator
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    app_name: str = "inferaAPI"
    app_version: str = "0.1.0"
    description: str = "A unified REST API framework for multiple LLM providers"
    debug: bool = Field(False, validation_alias="DEBUG")

    # Server settings
    host: str = Field("0.0.0.0", validation_alias="HOST")
    port: int = Field(8000, validation_alias="PORT")
    workers: int = Field(1, validation_alias="WORKERS")

    # API keys (use environment variables in production)
    openai_api_key: str = Field("", validation_alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field("", validation_alias="ANTHROPIC_API_KEY")
    huggingface_api_key: str = Field("", validation_alias="HUGGINGFACE_API_KEY")

    # Model defaults
    default_openai_model: str = "gpt-3.5-turbo"
    default_anthropic_model: str = "claude-2"
    default_huggingface_model: str = "gpt2"

    # Security
    secret_key: str = Field(
        "inferaapi-secret-key-change-in-production", validation_alias="SECRET_KEY"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    cors_origins: List[str] = Field(["*"], validation_alias="CORS_ORIGINS")

    # Rate limiting
    rate_limit_per_minute: int = Field(60, validation_alias="RATE_LIMIT_PER_MINUTE")

    # Logging
    log_level: str = Field("INFO", validation_alias="LOG_LEVEL")

    @validator("cors_origins", pre=True)
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
