from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from app.core.config import settings
import time

RETRIES = 5
for attempt in range(RETRIES):
    try:
        engine = create_engine(
            settings.DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=1800,
            future=True
        )
        # Test connection properly
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database connected!")
        break
    except OperationalError:
        if attempt < RETRIES - 1:
            print("Database not ready, retrying in 3s...")
            time.sleep(3)
        else:
            raise

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()
