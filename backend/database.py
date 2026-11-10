import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Use DATABASE_URL from environment if provided (e.g., Postgres on cloud)
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    # Vercel serverless filesystem is read-only outside /tmp
    if os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"):
        DATA_DIR = "/tmp/hospital_data"
    else:
        DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    os.makedirs(DATA_DIR, exist_ok=True)
    DB_PATH = os.path.join(DATA_DIR, "hospital.db")
    DATABASE_URL = f"sqlite:///{DB_PATH}"

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
