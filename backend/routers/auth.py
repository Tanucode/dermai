"""
routers/auth.py
----------------
Handles user registration and login.

CONCEPT — JWT (JSON Web Tokens):
  When a user logs in, we don't store a 'session' on the server.
  Instead, we give them a TOKEN (a signed string) they store in their browser.
  Every future request includes this token → server verifies it's valid.
  
  Token looks like: eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxfQ.abc123
  It has 3 parts separated by dots: header.payload.signature
  
  This is STATELESS auth — no server memory needed.
  Used by: Google, Twitter, Netflix, every modern API.

CONCEPT — Password Hashing:
  NEVER store plain passwords. Ever.
  We use bcrypt to hash: "password123" → "$2b$12$randomsaltXXXXXXXXXXXX"
  Even if someone steals the database, they can't reverse the hash.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

from database.db import get_db
from models.database_models import User
from models.schemas import UserCreate, UserLogin, Token, UserOut

load_dotenv()

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# bcrypt context for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme for reading Bearer tokens from request headers
security = HTTPBearer(auto_error=False)

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30


def hash_password(password: str) -> str:
    """Convert plain password to bcrypt hash."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Check if plain password matches the stored hash."""
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    """
    Create a JWT token.
    data = {"user_id": 1, "email": "user@example.com"}
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    Dependency that extracts the current user from JWT token.
    Used in protected endpoints like: user = Depends(get_current_user)
    """
    if not credentials:
        return None
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            return None
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except JWTError:
        return None


@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account."""
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"user_id": new_user.id, "email": new_user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password."""
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"user_id": user.id, "email": user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current logged-in user info."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return current_user
