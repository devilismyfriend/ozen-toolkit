from typing import List

from pydantic import BaseSettings, AnyHttpUrl

class Settings(BaseSettings):
    # General 
    SECRET_KEY: str
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    DEBUG: bool = True
    
    # STT DB
    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str 
    
    # CELERY route
    
    # File storage 
    
    pass 


settings = Settings() 