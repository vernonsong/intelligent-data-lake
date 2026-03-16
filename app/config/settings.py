from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置"""
    
    app_name: str = "智能入湖系统"
    debug: bool = True
    api_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000
    ai_model_api_key: str = ""
    ai_model_endpoint: str = ""
    ai_model_name: str = "qwen3.5-plus"
    skills_dir: str = "./skills"
    mock_enabled: bool = True
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
