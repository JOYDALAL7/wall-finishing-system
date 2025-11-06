# backend/app/database.py

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.pool import QueuePool

# ============================================================
# 1️⃣ Database Path Configuration
# ============================================================
# If DATABASE_URL exists (e.g. PostgreSQL on Render), use it
# Otherwise, default to SQLite stored safely in /app/trajectory.db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SQLITE_PATH = os.path.join("/app", "trajectory.db")

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE_PATH}")

# ============================================================
# 2️⃣ SQLite Connection Settings + Pool Configuration
# ============================================================
connect_args = {"check_same_thread": False, "timeout": 30} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_pre_ping=True,
    echo=False,
    future=True
)

# ============================================================
# 3️⃣ Ensure Database Directory and WAL Mode for SQLite
# ============================================================
if DATABASE_URL.startswith("sqlite"):
    db_dir = os.path.dirname(DEFAULT_SQLITE_PATH)
    os.makedirs(db_dir, exist_ok=True)  # Ensure /app exists

    # ✅ Create database file if missing
    if not os.path.exists(DEFAULT_SQLITE_PATH):
        open(DEFAULT_SQLITE_PATH, "a").close()

    # ✅ Apply SQLite optimizations
    with engine.begin() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL;"))
        conn.execute(text("PRAGMA synchronous=NORMAL;"))
        conn.execute(text("PRAGMA busy_timeout=30000;"))  # Wait 30s before "database locked"

# ============================================================
# 4️⃣ Session Factory Setup
# ============================================================
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

# ============================================================
# 5️⃣ Base Model for SQLAlchemy ORM
# ============================================================
Base = declarative_base()

# ============================================================
# 6️⃣ Dependency for FastAPI Routes
# ============================================================
def get_db() -> Session:
    """
    Provides a database session per request.
    Rolls back on error and closes after use.
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
