"""
database/db.py
--------------
This file sets up our database connection using SQLAlchemy.

CONCEPT: SQLAlchemy is an ORM (Object Relational Mapper).
- Instead of writing raw SQL like: SELECT * FROM users
- You write Python like: db.query(User).all()
- SQLAlchemy converts your Python code to SQL automatically.

We are using SQLite for now (a simple file-based database).
In production, you would swap this for PostgreSQL just by changing DATABASE_URL.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# The database URL tells SQLAlchemy WHERE the database is
# sqlite:///./dermai.db → creates a file called dermai.db in the current folder
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dermai.db")

# Render often provides PostgreSQL URLs starting with postgres:// instead of postgresql://
# SQLAlchemy > 1.4 requires postgresql:// and will crash otherwise.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create the database "engine" - this is the connection to the database
# connect_args is needed only for SQLite (for thread safety)
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

# SessionLocal is a factory for creating database sessions
# Each API request gets its own session (like a temporary connection)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class for all our database models (tables)
Base = declarative_base()


def get_db():
    """
    This is a FastAPI 'dependency'.
    It creates a database session for each request, 
    and automatically closes it when the request is done.
    
    The 'yield' keyword makes this a generator - FastAPI handles cleanup automatically.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
