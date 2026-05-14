import os
from dotenv import load_dotenv

load_dotenv(override=True)

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "database", "optistock.db"))

JWT_SECRET = os.getenv("JWT_SECRET", "optistock-super-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7

CORS_ORIGINS = ["*"]

