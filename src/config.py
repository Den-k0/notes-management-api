import os

from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER", "test_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "test_password")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "test_host")
POSTGRES_DB_PORT = int(os.getenv("POSTGRES_DB_PORT", 5432))
POSTGRES_DB = os.getenv("POSTGRES_DB", "test_db")
