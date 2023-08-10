from pydantic_settings import BaseSettings
import os 


class Settings(BaseSettings):
    SECRET_KEY:str = os.getenv("SECRET_KEY", "1234567890")
    DEBUG:bool = os.getenv("DEBUG", True)
    AUTH_TOKEN:str = os.getenv("AUTH_TOKEN", "1234567890")
    
    DATABASE_USERNAME:str = os.getenv("DATABASE_USERNAME", "postgres")
    DATABASE_NAME:str = os.getenv("DATABASE_NAME", "postgres")
    DATABASE_PASSWORD:str = os.getenv("DATABASE_PASSWORD", "postgres")
    DATABASE_HOST:str = os.getenv("DATABASE_HOST", "db")
    DATABASE_PORT:str = os.getenv("DATABASE_PORT", "5432")
    
    @property
    def DB_ROUTER(self):
        return f"postgres://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

settings = Settings()