from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from config import (
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_HOST,
    POSTGRES_DB_PORT,
    POSTGRES_DB
)

POSTGRESQL_DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_DB_PORT}/{POSTGRES_DB}"
)

postgresql_engine = create_engine(POSTGRESQL_DATABASE_URL)
PostgresqlSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=postgresql_engine
)

Base = declarative_base()


def get_postgresql_db() -> Session:
    db = PostgresqlSessionLocal()
    try:
        yield db
    finally:
        db.close()
