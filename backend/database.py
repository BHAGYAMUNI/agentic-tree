from sqlalchemy import create_engine, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Use env var in Docker, fall back to local default for dev
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Postgres123@localhost:5432/agentic_tree_db",
)

# When running tests, use an in-memory SQLite database for isolation
if os.environ.get("RUNNING_TESTS") == "1":
    DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, json_serializer=None)
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()