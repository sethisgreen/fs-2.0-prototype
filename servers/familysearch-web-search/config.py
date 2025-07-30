"""
Configuration for FamilySearch Web Search MCP Server
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Server Configuration
    server_name: str = "familysearch-web-search"
    server_url: str = "http://localhost:8002/mcp"
    server_port: int = 8002
    
    # FamilySearch Configuration
    familysearch_base_url: str = "https://www.familysearch.org"
    custom_user_agent: Optional[str] = None
    
    # Rate Limiting
    requests_per_minute: int = 30
    requests_per_hour: int = 1000
    delay_between_requests: float = 2.0  # seconds
    
    # Caching
    cache_ttl: int = 3600  # 1 hour in seconds
    max_cache_size: int = 1000
    
    # Search Configuration
    default_max_results: int = 20
    max_results_limit: int = 100
    
    # Timeouts
    request_timeout: float = 30.0
    connection_timeout: float = 10.0
    
    # Retry Configuration
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff: float = 2.0
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = ".env"
        env_prefix = "FAMILYSEARCH_WEB_"

# Global settings instance
settings = Settings()

# Default user agent if not provided
if not settings.custom_user_agent:
    settings.custom_user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )