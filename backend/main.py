"""
main.py
--------
The ENTRY POINT of our FastAPI backend.

CONCEPT — FastAPI:
  FastAPI is a modern Python web framework for building APIs.
  It is:
  - FAST: One of the fastest Python frameworks (on par with Node.js, Go)
  - AUTO-DOCUMENTED: Visit http://localhost:8000/docs to see interactive API docs
  - TYPE-SAFE: Uses Pydantic for automatic data validation
  - ASYNC: Built on asyncio for handling many requests simultaneously

CONCEPT — CORS (Cross-Origin Resource Sharing):
  Our React frontend runs on http://localhost:5173
  Our FastAPI backend runs on http://localhost:8000
  
  By default, browsers BLOCK requests between different origins (security rule).
  CORS middleware tells the browser: 'It's okay, I allow requests from localhost:5173'
  
  In production, you'd replace localhost:5173 with your actual domain.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from database.db import engine, Base
from models import database_models  # noqa: F401 — Import to register models with SQLAlchemy
from routers import analysis, auth, history
from services.rag_service import initialize_rag


# ── Lifespan: runs code on startup and shutdown ──────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    CONCEPT — Lifespan events:
    Code before 'yield' runs when the server STARTS.
    Code after 'yield' runs when the server STOPS.
    
    We use this to:
    1. Create database tables (if they don't exist)
    2. Initialize the RAG pipeline (load documents into ChromaDB)
    """
    print("DermAI Server Starting...")
    
    # Create all database tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created")
    
    # Initialize the RAG pipeline (load knowledge base into ChromaDB)
    print("Initializing RAG knowledge base...")
    initialize_rag()
    
    # Create uploads directory
    os.makedirs("uploads", exist_ok=True)
    
    print("DermAI is ready! Visit http://localhost:8000/docs")
    
    yield  # Server runs here
    
    print("DermAI Server Shutting Down...")


# ── Create the FastAPI app ────────────────────────────────────────────────────
app = FastAPI(
    title="DermAI - Skin Analysis API",
    description="AI-powered skin analysis with personalized recommendations",
    version="1.0.0",
    lifespan=lifespan
)


# ── CORS Middleware ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow any origin (so Vercel can talk to Render)
    allow_credentials=True,
    allow_methods=["*"],          # Allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],          # Allow all headers
)


# ── Include Routers ──────────────────────────────────────────────────────────
# This registers all our routes with the main app
app.include_router(analysis.router)
app.include_router(auth.router)
app.include_router(history.router)


# ── Serve uploaded images as static files ─────────────────────────────────────
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# ── Root endpoint ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "message": "Welcome to DermAI API",
        "docs": "http://localhost:8000/docs",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Used by deployment platforms to check if server is running."""
    return {"status": "healthy", "service": "DermAI"}


# ── Run directly (for development) ───────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    # uvicorn is the ASGI server that actually runs FastAPI
    # reload=True means server auto-restarts when you save code changes
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
