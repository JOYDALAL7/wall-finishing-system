# backend/app/database.py

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.pool import QueuePool

# -------------------------------------------------------------
# 🔹 1. Database URL (default: SQLite file)
# -------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trajectory.db")

# -------------------------------------------------------------
# 🔹 2. SQLite connection args + pooling setup
# -------------------------------------------------------------
connect_args = {"check_same_thread": False, "timeout": 30} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    poolclass=QueuePool,     # Recommended for concurrent FastAPI requests
    pool_size=10,            # Max number of connections kept open
    max_overflow=20,         # Allow temporary extra connections
    pool_timeout=30,         # Wait before throwing "database is locked"
    pool_pre_ping=True,      # Detect stale connections
    echo=False,
    future=True
)

# -------------------------------------------------------------
# 🔹 3. Enable WAL (Write-Ahead Logging) for SQLite concurrency
# -------------------------------------------------------------
if DATABASE_URL.startswith("sqlite"):
    with engine.begin() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL;"))
        conn.execute(text("PRAGMA synchronous=NORMAL;"))
        conn.execute(text("PRAGMA busy_timeout=30000;"))  # 30s wait before "locked"

# -------------------------------------------------------------
# 🔹 4. Session factory configuration
# -------------------------------------------------------------
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,  # Keeps objects valid after commit
)

# -------------------------------------------------------------
# 🔹 5. Declarative Base for ORM Models
# -------------------------------------------------------------
Base = declarative_base()

# -------------------------------------------------------------
# 🔹 6. Dependency for FastAPI routes
# -------------------------------------------------------------
def get_db() -> Session:
    """
    Yields a database session per request.
    Ensures rollback on failure and closes session after use.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
