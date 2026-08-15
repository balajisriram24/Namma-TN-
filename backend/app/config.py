import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB = os.getenv("MONGO_DB", "namma_tn")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXP_SECONDS = int(os.getenv("JWT_EXP_SECONDS", str(60 * 60 * 24)))
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@namma.tn")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
