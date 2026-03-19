import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Libro de Temas Digital"
    
    # Database
    DB_DIALECT = os.getenv("DB_DIALECT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    
    @property
    def DATABASE_URL(self):
        # Validate that all required db variables are present
        required_vars = [self.DB_DIALECT, self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_PORT, self.DB_NAME]
        if any(v is None for v in required_vars):
            # If any variable is missing, fallback to a safe or informative value for debugging
            # though in production you'd want a clear configuration error
            return "sqlite:///./missing_config.db"
        return f"{self.DB_DIALECT}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 480))

settings = Settings()
