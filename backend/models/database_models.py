"""
models/database_models.py
--------------------------
SQLAlchemy Models = Database Tables

CONCEPT: Each class here becomes a TABLE in our database.
- class User → creates a 'users' table
- class AnalysisHistory → creates an 'analysis_history' table
- Each attribute = a column in the table

This is the ORM (Object Relational Mapper) in action!
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db import Base


class User(Base):
    """
    Represents the 'users' table.
    Stores user account information.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  # Auto-increment ID
    email = Column(String, unique=True, index=True)     # Must be unique
    name = Column(String)
    hashed_password = Column(String)                    # NEVER store plain passwords!
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationship: one user → many analyses
    # This lets you do: user.analyses to get all their analyses
    analyses = relationship("AnalysisHistory", back_populates="user")


class AnalysisHistory(Base):
    """
    Represents the 'analysis_history' table.
    Stores each skin analysis result for a user.
    """
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String, unique=True, index=True)   # UUID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # nullable for guests
    image_path = Column(String)                             # Where we saved the image
    result_json = Column(Text)                              # Full JSON result stored as text
    skin_type = Column(String)
    overall_score = Column(Integer)
    top_concerns = Column(String)                           # Stored as comma-separated string
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship: each analysis belongs to one user
    user = relationship("User", back_populates="analyses")
