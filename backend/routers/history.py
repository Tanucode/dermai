"""
routers/history.py
-------------------
Handles analysis history — lets users view past skin analyses.
"""

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db
from models.database_models import AnalysisHistory, User
from routers.auth import get_current_user

router = APIRouter(prefix="/api/history", tags=["History"])


@router.get("/")
def get_history(
    limit: int = 10, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the most recent analyses for the logged-in user.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="You must be logged in to view history.")

    records = (
        db.query(AnalysisHistory)
        .filter(AnalysisHistory.user_id == current_user.id)
        .order_by(AnalysisHistory.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "analysis_id": r.analysis_id,
            "skin_type": r.skin_type,
            "overall_score": r.overall_score,
            "top_concerns": r.top_concerns,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]


@router.get("/{analysis_id}")
def get_single_history(
    analysis_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get one full analysis result by ID."""
    if not current_user:
        raise HTTPException(status_code=401, detail="You must be logged in to view this analysis.")

    record = db.query(AnalysisHistory).filter(
        AnalysisHistory.analysis_id == analysis_id,
        AnalysisHistory.user_id == current_user.id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return json.loads(record.result_json)


@router.delete("/{analysis_id}")
def delete_analysis(
    analysis_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a specific analysis belonging to the user."""
    if not current_user:
        raise HTTPException(status_code=401, detail="You must be logged in to delete an analysis.")

    record = db.query(AnalysisHistory).filter(
        AnalysisHistory.analysis_id == analysis_id,
        AnalysisHistory.user_id == current_user.id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    db.delete(record)
    db.commit()
    return {"message": "Deleted successfully"}
