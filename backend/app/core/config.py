import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Personal Finance Tracker"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./finance.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "supersecretkey")
    JWT_ALGORITHM: str = "HS256"

settings = Settings()