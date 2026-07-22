"""
services/gemini_service.py
---------------------------
This is where we talk to Google's Gemini Vision AI.

CONCEPT: Multimodal AI
- Normal AI (like ChatGPT text) only understands text.
- Multimodal AI understands BOTH text AND images at the same time.
- We send: [face photo + text prompt] → Gemini returns skin analysis JSON.

FLOW:
  1. User uploads image → we read it as bytes
  2. We send image + structured prompt to Gemini Vision
  3. Gemini returns JSON with detected skin problems
  4. We parse + validate that JSON using Pydantic
"""

import json
import re
import os
import traceback
from dotenv import load_dotenv
from PIL import Image
import io

from google import genai
from google.genai import types

load_dotenv()

# ── Configure Gemini with your API key ──────────────────────────────────────
# Using the NEW google-genai SDK
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Disable safety filters that incorrectly flag facial skin analysis as dangerous medical content
SAFETY_CONFIG = types.GenerateContentConfig(
    safety_settings=[
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=types.HarmBlockThreshold.BLOCK_NONE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=types.HarmBlockThreshold.BLOCK_NONE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=types.HarmBlockThreshold.BLOCK_NONE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=types.HarmBlockThreshold.BLOCK_NONE,
        ),
    ]
)


# ── The Master Skin Analysis Prompt ─────────────────────────────────────────
# This is PROMPT ENGINEERING — carefully crafting instructions so the AI
# returns exactly the format we want (valid JSON, specific fields).
SKIN_ANALYSIS_PROMPT = """
You are an expert dermatology AI assistant. Carefully analyze the provided image.

CRITICAL SECURITY STEP: First, verify that the image clearly shows a human face (it may be cropped or masked to only show the skin/features). 
If the image is NOT a human face (e.g., a dog, a car, a document, random noise), 
you MUST reject it and return exactly this JSON:
{"error": "INVALID_IMAGE", "message": "Please upload a clear picture of a human face."}

If it IS a human face or facial skin, proceed with the cosmetic analysis.
Note: This is a cosmetic skin assessment, NOT a medical diagnosis.

{yolo_context}

Your job is to detect skin conditions and return a detailed analysis.

Analyze and score the following issues on a scale of 0-10 (0 = not present, 10 = very severe):
- Dark circles (under eyes)
- Dark spots / Hyperpigmentation  
- Acne / Pimples / Breakouts
- Oiliness / Excess shine
- Dryness / Flakiness / Dehydration
- Wrinkles / Fine lines
- Redness / Rosacea / Irritation
- Uneven skin tone / Dullness
- Open pores / Blackheads / Whiteheads
- Eye bags / Puffiness

IMPORTANT RULES:
1. Only include issues with severity > 2 in the issues list
2. Be honest but sensitive — avoid harsh language
3. overall_score is for skin health (10 = perfect, 0 = very problematic)
4. Return ONLY valid JSON — no extra text, no markdown, no code blocks

Return this EXACT JSON structure:
{
  "skin_type": "oily",
  "overall_score": 6,
  "skin_age_estimate": "22-26",
  "issues": [
    {
      "name": "Dark Circles",
      "severity": 7,
      "description": "Moderate dark circles detected under both eyes, likely due to fatigue or genetics",
      "icon": "👁️"
    },
    {
      "name": "Acne",
      "severity": 5,
      "description": "Mild to moderate acne present on forehead and cheeks",
      "icon": "🔴"
    }
  ],
  "top_concerns": ["Dark Circles", "Acne", "Oiliness"]
}
"""


async def analyze_skin_image(image_bytes: bytes, yolo_context: str = "") -> dict:
    """
    Sends the masked face image + YOLO text to Gemini Vision.

    Args:
        image_bytes: The masked image bytes from MediaPipe/OpenCV
        yolo_context: The text string from YOLO object detection
    
    Returns:
        A dict with skin_type, overall_score, issues, top_concerns, etc.

    CONCEPT — async/await:
        'async def' means this function runs without blocking other requests.
        FastAPI is built on async Python — it can handle many users at once
        because while waiting for Gemini to respond, it handles other requests.
    """
    try:
        # Convert bytes to a PIL Image object
        # PIL = Python Imaging Library — used for image processing
        image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB if needed (some images are RGBA with transparency)
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Inject YOLO context into the prompt
        # We MUST use .replace instead of .format because the prompt contains JSON curly braces {}
        formatted_prompt = SKIN_ANALYSIS_PROMPT.replace("{yolo_context}", yolo_context)

        # Send to Gemini: [image, text_prompt] (Using new SDK)
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=[image, formatted_prompt],
            config=SAFETY_CONFIG
        )

        # Extract the text response
        response_text = response.text.strip()

        # Robust JSON extraction: Find the first { and last }
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            response_text = response_text[start_idx:end_idx+1]

        # Parse the JSON string into a Python dict
        analysis_data = json.loads(response_text)

        return analysis_data

    except json.JSONDecodeError as e:
        # If Gemini didn't return valid JSON, we return a safe fallback
        print(f"[Gemini] JSON parse error: {e}")
        print(f"[Gemini] Raw response: {response.text}")
        return _get_fallback_analysis()

    except Exception as e:
        print(f"[Gemini] Error: {e}")
        traceback.print_exc()
        return _get_fallback_analysis()

async def generate_skincare_recommendations(
    skin_type: str,
    top_concerns: list[str],
    rag_context: str
) -> dict:
    """
    Second Gemini call — generates personalized recommendations.

    We use the RAG context (retrieved from ChromaDB) to ground
    the AI's recommendations in real skincare knowledge.

    CONCEPT — RAG (Retrieval Augmented Generation):
        Instead of asking AI to make up recommendations,
        we FIRST retrieve relevant facts from our knowledge base,
        THEN feed those facts to Gemini as context.
        This makes the AI more accurate and less likely to hallucinate.
    """
    recommendation_prompt = f"""
You are a professional skincare consultant. Based on the skin analysis below,
provide personalized skincare recommendations.

PATIENT SKIN PROFILE:
- Skin Type: {skin_type}
- Top Concerns: {", ".join(top_concerns)}

RELEVANT SKINCARE KNOWLEDGE (use this as reference):
{rag_context}

Provide recommendations in this EXACT JSON format (return ONLY valid JSON):
{{
  "ingredients": [
    {{
      "name": "Niacinamide",
      "benefit": "Reduces dark spots, minimizes pores, controls oil",
      "how_to_use": "Apply 2-3 drops after toner, morning and night",
      "concentration": "5-10%"
    }}
  ],
  "morning_routine": [
    {{
      "step_number": 1,
      "product_type": "Gentle Cleanser",
      "description": "Use a gentle, pH-balanced cleanser to remove overnight buildup",
      "timing": "Morning"
    }}
  ],
  "night_routine": [
    {{
      "step_number": 1,
      "product_type": "Oil Cleanser / Micellar Water",
      "description": "First cleanse to remove sunscreen and makeup",
      "timing": "Night"
    }}
  ],
  "diet_plan": {{
    "foods_to_eat": ["Blueberries", "Green tea", "Fatty fish", "Avocado", "Sweet potatoes"],
    "foods_to_avoid": ["Refined sugar", "Dairy milk", "Processed snacks", "Alcohol"],
    "supplements": ["Vitamin C 500mg", "Omega-3 1000mg", "Zinc 25mg"],
    "hydration_tip": "Drink at least 8 glasses of water daily. Add lemon for Vitamin C."
  }},
  "consultation_needed": false,
  "consultation_reason": null,
  "products": [
    {{
      "name": "Minimalist 10% Niacinamide Serum",
      "brand": "Minimalist",
      "category": "Serum",
      "price_range": "₹399 - ₹599",
      "buy_link": "https://www.amazon.in/s?k=minimalist+niacinamide+serum",
      "why_recommended": "Directly targets dark spots and oiliness"
    }}
  ]
}}
"""

    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=recommendation_prompt,
            config=SAFETY_CONFIG
        )
        response_text = response.text.strip()

        # Robust JSON extraction
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            response_text = response_text[start_idx:end_idx+1]

        return json.loads(response_text)

    except Exception as e:
        print(f"[Gemini Recommendations] Error: {e}")
        return _get_fallback_recommendations()


def _get_fallback_analysis() -> dict:
    """Returns safe fallback data if Gemini fails."""
    return {
        "skin_type": "combination",
        "overall_score": 5,
        "skin_age_estimate": "N/A",
        "issues": [
            {
                "name": "Analysis Unavailable",
                "severity": 0,
                "description": "Could not analyze the image. Please try with a clearer face photo.",
                "icon": "⚠️"
            }
        ],
        "top_concerns": ["Please retry with better lighting"]
    }


def _get_fallback_recommendations() -> dict:
    """Returns safe fallback recommendations if second Gemini call fails."""
    return {
        "ingredients": [
            {
                "name": "Niacinamide",
                "benefit": "Multi-tasking ingredient that reduces dark spots, controls oil, and minimizes pores",
                "how_to_use": "Apply 2-3 drops after toner, morning and night",
                "concentration": "5-10%"
            },
            {
                "name": "Hyaluronic Acid",
                "benefit": "Deep hydration that plumps skin and reduces fine lines",
                "how_to_use": "Apply on damp skin, pat gently. Follow with moisturizer",
                "concentration": "1-2%"
            }
        ],
        "morning_routine": [
            {"step_number": 1, "product_type": "Gentle Cleanser", "description": "Cleanse to remove overnight oil buildup", "timing": "Morning"},
            {"step_number": 2, "product_type": "Toner", "description": "Balance skin pH and prep for actives", "timing": "Morning"},
            {"step_number": 3, "product_type": "Serum", "description": "Apply niacinamide or Vitamin C serum", "timing": "Morning"},
            {"step_number": 4, "product_type": "Moisturizer", "description": "Lock in hydration", "timing": "Morning"},
            {"step_number": 5, "product_type": "SPF 50+ Sunscreen", "description": "Most important step — protects from UV damage", "timing": "Morning"}
        ],
        "night_routine": [
            {"step_number": 1, "product_type": "Oil Cleanser", "description": "Remove sunscreen and impurities", "timing": "Night"},
            {"step_number": 2, "product_type": "Face Wash", "description": "Deep cleanse with a gentle cleanser", "timing": "Night"},
            {"step_number": 3, "product_type": "Treatment Serum", "description": "Apply retinol or AHA/BHA serum", "timing": "Night"},
            {"step_number": 4, "product_type": "Night Cream", "description": "Rich moisturizer to repair overnight", "timing": "Night"}
        ],
        "diet_plan": {
            "foods_to_eat": ["Blueberries", "Green tea", "Fatty fish (salmon)", "Avocado", "Sweet potatoes", "Spinach", "Walnuts"],
            "foods_to_avoid": ["Refined sugar", "Dairy milk", "Processed snacks", "Alcohol", "Fried foods"],
            "supplements": ["Vitamin C 500mg", "Omega-3 1000mg", "Zinc 25mg", "Biotin"],
            "hydration_tip": "Drink at least 8 glasses of water daily. Start your morning with warm lemon water."
        },
        "consultation_needed": False,
        "consultation_reason": None,
        "products": [
            {
                "name": "Minimalist 10% Niacinamide Serum",
                "brand": "Minimalist",
                "category": "Serum",
                "price_range": "₹399 - ₹599",
                "buy_link": "https://www.amazon.in/s?k=minimalist+niacinamide+serum",
                "why_recommended": "Targets dark spots and oiliness"
            },
            {
                "name": "Simple Kind to Skin Moisturiser",
                "brand": "Simple",
                "category": "Moisturizer",
                "price_range": "₹299 - ₹499",
                "buy_link": "https://www.amazon.in/s?k=simple+moisturiser",
                "why_recommended": "Gentle, fragrance-free hydration"
            }
        ]
    }
