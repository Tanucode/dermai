"""
routers/analysis.py
--------------------
This is the MAIN endpoint of our app — POST /api/analyze

CONCEPT — FastAPI Router:
  Instead of putting ALL endpoints in main.py (which gets messy),
  we split them into 'routers' by feature.
  - analysis.py → handles /api/analyze
  - auth.py     → handles /api/auth/*
  - history.py  → handles /api/history/*

  Then in main.py we just 'include' all routers.

CONCEPT — File Upload in FastAPI:
  When a user uploads an image from the browser,
  it comes as 'multipart/form-data' (not JSON).
  FastAPI handles this with UploadFile.
"""

import uuid
import json
import os
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from database.db import get_db
from models.database_models import AnalysisHistory, User
from services.gemini_service import analyze_skin_image, generate_skincare_recommendations
from services.rag_service import query_knowledge_base
from routers.auth import get_current_user

# Create a router — like a mini FastAPI app just for analysis routes
router = APIRouter(prefix="/api", tags=["Analysis"])

# Where to save uploaded images
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/analyze")
async def analyze_skin(
    file: UploadFile = File(...),      # The uploaded image file
    db: Session = Depends(get_db),     # DB session injected automatically
    current_user: User = Depends(get_current_user)  # Extract current user from JWT token
):
    """
    THE MAIN ENDPOINT — The entire app revolves around this.

    Flow:
    1. Receive image from React frontend
    2. Validate it's an image
    3. Send to Gemini Vision → get skin issues
    4. Query ChromaDB (RAG) → get relevant skincare knowledge
    5. Send issues + RAG context to Gemini → get recommendations
    6. Save result to database
    7. Return full analysis to frontend

    CONCEPT — async/await:
      This function is 'async' because it calls external APIs (Gemini).
      While waiting for Gemini to respond, FastAPI can handle other requests.
      This is why FastAPI can handle 1000s of users simultaneously.
    """

    # ── STEP 1: Validate file type ────────────────────────────────────────
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file.content_type}'. Please upload a JPEG, PNG, or WebP image."
        )

    # ── STEP 2: Read image bytes ──────────────────────────────────────────
    image_bytes = await file.read()  # 'await' because reading file is async

    # Sanity check — make sure file isn't too small (probably corrupt)
    if len(image_bytes) < 1000:
        raise HTTPException(status_code=400, detail="Image file is too small or corrupted.")

    try:
        masked_image_bytes, yolo_context, _ = process_and_detect(image_bytes)
    except ValueError as e:
        if str(e) == "NO_FACE_DETECTED":
            raise HTTPException(status_code=400, detail="No face detected. Please upload a clear picture of a human face.")
        raise HTTPException(status_code=400, detail=f"Image processing error: {e}")

    # Generate unique ID for this analysis
    analysis_id = str(uuid.uuid4())

    # Save the MASKED image to disk (not the raw image, for privacy)
    image_filename = f"{analysis_id}.jpg"
    image_path = os.path.join(UPLOAD_DIR, image_filename)
    with open(image_path, "wb") as f:
        f.write(masked_image_bytes)

    # ── STEP 4: Gemini Vision — analyze the skin ─────────────────────────
    print(f"\n[PIPELINE] Stage 3: Gemini Vision Analysis")
    print(f"[PIPELINE] Injecting YOLO Context: {yolo_context}")
    gemini_analysis = await analyze_skin_image(masked_image_bytes, yolo_context)

    # Check for prompt injection / invalid image (e.g. dog instead of face)
    if gemini_analysis.get("error") == "INVALID_IMAGE":
        # Delete the saved image since it's invalid
        if os.path.exists(image_path):
            os.remove(image_path)
        raise HTTPException(
            status_code=400,
            detail=gemini_analysis.get("message", "Invalid image. Please upload a clear human face.")
        )

    skin_type = gemini_analysis.get("skin_type", "combination")
    top_concerns = gemini_analysis.get("top_concerns", [])
    overall_score = gemini_analysis.get("overall_score", 5)

    # ── STEP 5: RAG — retrieve relevant skincare knowledge ────────────────
    print(f"\n[PIPELINE] Stage 4: RAG Knowledge Retrieval")
    rag_context = query_knowledge_base(top_concerns, skin_type)
    print(f"[PIPELINE] Retrieved Clinical Facts from ChromaDB:\n{rag_context}")

    # ── STEP 6: Gemini — generate personalized recommendations ────────────
    print(f"[Analysis] Generating recommendations...")
    recommendations = await generate_skincare_recommendations(
        skin_type=skin_type,
        top_concerns=top_concerns,
        rag_context=rag_context
    )

    # ── STEP 7: Build the final response ──────────────────────────────────
    full_result = {
        "analysis_id": analysis_id,
        "skin_type": skin_type,
        "overall_score": overall_score,
        "skin_age_estimate": gemini_analysis.get("skin_age_estimate", "N/A"),
        "issues": gemini_analysis.get("issues", []),
        "top_concerns": top_concerns,
        "ingredients": recommendations.get("ingredients", []),
        "morning_routine": recommendations.get("morning_routine", []),
        "night_routine": recommendations.get("night_routine", []),
        "diet_plan": recommendations.get("diet_plan", {}),
        "products": recommendations.get("products", []),
        "consultation_needed": recommendations.get("consultation_needed", False),
        "consultation_reason": recommendations.get("consultation_reason", None),
        "created_at": datetime.utcnow().isoformat()
    }

    # ── STEP 8: Save to database ──────────────────────────────────────────
    db_record = AnalysisHistory(
        analysis_id=analysis_id,
        user_id=current_user.id if current_user else None, # Link to logged-in user!
        image_path=image_path,
        result_json=json.dumps(full_result),
        skin_type=skin_type,
        overall_score=overall_score,
        top_concerns=", ".join(top_concerns)
    )
    db.add(db_record)
    db.commit()
    print(f"[Analysis] ✅ Saved to database: {analysis_id}")

    return full_result


@router.get("/analyze/{analysis_id}")
async def get_analysis(
    analysis_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch a previously saved analysis by its ID.
    Used when user wants to re-view their results.
    """
    # Ensure user can only fetch their own analysis, or allow guests to fetch unassigned ones
    query = db.query(AnalysisHistory).filter(AnalysisHistory.analysis_id == analysis_id)
    if current_user:
        query = query.filter(AnalysisHistory.user_id == current_user.id)
    else:
        query = query.filter(AnalysisHistory.user_id == None)
        
    record = query.first()

    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return json.loads(record.result_json)
