from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "TruthLens OSINT Platform"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    # PostgreSQL Configuration
    POSTGRES_USER: str = "truthlens_user"
    POSTGRES_PASSWORD: str = "truthlens_password"
    POSTGRES_SERVER: str = "localhost" # Internal docker name or localhost for dev
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "truthlens"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        
    # Database Mode
    USE_SQLITE_FALLBACK: bool = True # SQLite enabled for development (Docker not found)
    SQLITE_URL: str = "sqlite:///./truthlens_local.db"

settings = Settings()
