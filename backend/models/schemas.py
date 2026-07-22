"""
models/schemas.py
-----------------
Pydantic schemas define the SHAPE of data going in and out of our API.

CONCEPT: Pydantic is a data validation library.
- When a user sends data to our API, Pydantic checks it automatically.
- If data is wrong (e.g. missing field), FastAPI returns an error automatically.
- Pydantic also auto-generates the API documentation (Swagger UI).

Think of schemas like contracts: "I promise this data will look exactly like this."
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ─────────────────────────────────────────────
#  SKIN ISSUE — represents one detected problem
# ─────────────────────────────────────────────
class SkinIssue(BaseModel):
    name: str                    # e.g. "Dark Circles"
    severity: int                # 0-10 scale (10 = most severe)
    description: str             # Human-readable explanation
    icon: Optional[str] = "⚠️"  # Emoji for UI display


# ─────────────────────────────────────────────
#  INGREDIENT — a recommended skincare ingredient
# ─────────────────────────────────────────────
class Ingredient(BaseModel):
    name: str           # e.g. "Niacinamide"
    benefit: str        # e.g. "Reduces dark spots and pores"
    how_to_use: str     # e.g. "Apply 2-3 drops after toner, morning and night"
    concentration: str  # e.g. "5-10%"


# ─────────────────────────────────────────────
#  ROUTINE STEP — one step in a skincare routine
# ─────────────────────────────────────────────
class RoutineStep(BaseModel):
    step_number: int
    product_type: str   # e.g. "Cleanser", "Toner", "Moisturizer"
    description: str    # What to do
    timing: str         # "Morning" / "Night" / "Both"


# ─────────────────────────────────────────────
#  DIET PLAN — food recommendations for skin
# ─────────────────────────────────────────────
class DietPlan(BaseModel):
    foods_to_eat: List[str]     # e.g. ["Blueberries", "Green tea", "Salmon"]
    foods_to_avoid: List[str]   # e.g. ["Sugar", "Dairy", "Processed foods"]
    supplements: List[str]      # e.g. ["Vitamin C", "Omega-3", "Zinc"]
    hydration_tip: str          # e.g. "Drink 8 glasses of water daily"


# ─────────────────────────────────────────────
#  PRODUCT RECOMMENDATION
# ─────────────────────────────────────────────
class ProductRecommendation(BaseModel):
    name: str           # Product name
    brand: str          # Brand name
    category: str       # e.g. "Serum", "Moisturizer"
    price_range: str    # e.g. "₹500 - ₹1000"
    buy_link: str       # Amazon / Nykaa URL
    why_recommended: str


# ─────────────────────────────────────────────
#  FULL SKIN ANALYSIS RESULT (the main response)
# ─────────────────────────────────────────────
class SkinAnalysisResult(BaseModel):
    analysis_id: str
    skin_type: str                              # oily / dry / combination / normal / sensitive
    overall_score: int                          # 0-10 (10 = perfect skin)
    skin_age_estimate: str                      # e.g. "24-28"
    issues: List[SkinIssue]                     # All detected skin problems
    top_concerns: List[str]                     # Top 3 most urgent issues
    ingredients: List[Ingredient]               # Recommended ingredients
    morning_routine: List[RoutineStep]          # Step-by-step morning routine
    night_routine: List[RoutineStep]            # Step-by-step night routine
    diet_plan: DietPlan                         # Food recommendations
    products: List[ProductRecommendation]       # Product recommendations
    consultation_needed: bool                   # Should they see a dermatologist?
    consultation_reason: Optional[str] = None   # Why consultation is needed
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ─────────────────────────────────────────────
#  GEMINI RAW RESPONSE (internal use only)
# ─────────────────────────────────────────────
class GeminiSkinAnalysis(BaseModel):
    """
    This represents the raw JSON that Gemini Vision returns.
    We parse this first, then enrich it with RAG data.
    """
    skin_type: str
    overall_score: int
    skin_age_estimate: str
    issues: List[dict]
    top_concerns: List[str]


# ─────────────────────────────────────────────
#  USER AUTH SCHEMAS
# ─────────────────────────────────────────────
class UserCreate(BaseModel):
    email: str
    password: str
    name: str


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    name: str

    class Config:
        from_attributes = True  # Allows converting SQLAlchemy models to Pydantic
