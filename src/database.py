from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from src.config import POSTGRESQL_DATABASE_URL

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
