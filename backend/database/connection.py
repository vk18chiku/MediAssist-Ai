# backend/database/connection.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# .env file se variables load karna
load_dotenv()

# .env se DATABASE_URL nikalna (default SQLite)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mediassist.db")

# SQLite engine create karna
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Database session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class jisko inherit karke hum apne tables (models) banayenge
Base = declarative_base()

# DB session get karne ke liye dependency function
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()