from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from app.core.config import settings
import time

# --- Simple Change Starts Here ---
engine_kwargs = {
    "pool_pre_ping": True,
    "pool_recycle": 1800,
    "future": True
}

# Only add pooling if NOT using SQLite
if not settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10
else:
    # Required for SQLite to work with FastAPI threads
    engine_kwargs["connect_args"] = {"check_same_thread": False}
# --- Simple Change Ends Here ---

RETRIES = 5
for attempt in range(RETRIES):
    try:
        engine = create_engine(
            settings.DATABASE_URL,
            **engine_kwargs  # Use the dynamic dictionary here
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