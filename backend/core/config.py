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
        
    # Optional DB fall back for prototyping
    USE_SQLITE_FALLBACK: bool = True
    SQLITE_URL: str = "sqlite:///./truthlens_local_test.db"

settings = Settings()
