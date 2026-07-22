# 🧬 DermAI: System Architecture & Design Document

This document serves as a comprehensive log of the DermAI architecture, the concepts we learned, the design choices we made, and how the entire pipeline functions from end to end.

---

## 🏗️ The Tech Stack

*   **Frontend**: React + Vite + Vanilla CSS (Dynamic, Glassmorphism UI)
*   **Backend**: Python + FastAPI
*   **Database**: SQLite (SQLAlchemy ORM) + ChromaDB (Vector Database)
*   **AI Models**:
    *   **Computer Vision**: OpenCV + MediaPipe (Face Detection)
    *   **Object Detection**: Hugging Face YOLO (`yolov8n`)
    *   **Embeddings**: Hugging Face `sentence-transformers` (`all-MiniLM-L6-v2`)
    *   **Vision Language Model (VLM)**: Google Gemini (`gemini-3.5-flash`) via `google-genai` SDK

---

## 🧠 The AI Pipeline (End-to-End)

When a user uploads a photo, the backend processes it through a strict, multi-stage pipeline. We call this the **Detector-Augmented VLM Pipeline**.

### Stage 1: Face Validation & Geometric Masking (MediaPipe + OpenCV)
Before we spend money/quota on API calls, we validate the image locally.
*   **Concept**: Fail-fast validation. 
*   **Design Choice**: If a user uploads a dog or a car, MediaPipe instantly rejects it. If it is a face, OpenCV mathematically calculates the facial contours and cuts out the background (creating a black mask). This forces the downstream AI to focus *only* on the skin pixels and prevents it from getting distracted by clothes or backgrounds.

### Stage 2: Feature Detection (Hugging Face YOLO)
*   **Concept**: Bounding-box object detection.
*   **Design Choice**: While VLMs (like Gemini) are great at general reasoning, they sometimes miss tiny details. YOLO models are specifically trained to draw boxes around objects. In a production medical setting, this would be a custom YOLO weights file trained purely on acne and melanoma to inject quantitative data into the pipeline.

### Stage 3: Vision Language Analysis (Gemini 3.5 Flash)
*   **Concept**: Multimodal Vision-Language processing.
*   **Design Choice**: We send the perfectly masked image + the text output from YOLO directly to Google's Gemini 3.5 Flash engine. We use a strict system prompt instructing Gemini to output *only* valid JSON.
*   **The SDK Evolution (API Rot)**: We originally started with `gemini-1.5-flash` using the legacy `google.generativeai` SDK. We discovered that Google had completely retired the 1.5 models for this developer account and was throwing 404 API errors. We upgraded our entire codebase to the modern `google-genai` SDK and pivoted to the cutting-edge `gemini-3.5-flash` model.

### Stage 4: Knowledge Retrieval (RAG via Hugging Face)
*   **Concept**: Retrieval-Augmented Generation (RAG).
*   **Design Choice**: LLMs hallucinate medical facts. To prevent this, we built a local RAG database (`skincare_dataset.json`). 
*   **The Embedding Swap**: Initially, we used Google's API to generate embeddings. When Google deprecated their embedding endpoints, we pivoted to an offline Hugging Face model (`all-MiniLM-L6-v2`). This was a massive architectural win: it made our database searches 100% free, mathematically faster, and completely immune to internet API failures. 
*   **How it works**: We take the "Top Concerns" (e.g., Acne, Dark Circles) identified by Gemini in Stage 3, convert them into numbers (vectors), and search ChromaDB for the closest matching clinical treatments.

### Stage 5: Final Recommendations (Gemini Text)
*   **Concept**: Context-grounded generation.
*   **Design Choice**: We pass the clinical facts retrieved from RAG *back* into Gemini. We instruct it: *"You are a dermatologist. Recommend a routine for this user, but you MUST base your recommendations on these specific facts."* This generates the final, medically grounded JSON response that is sent to the frontend.

---

## 🔒 Security & Safety Design

1.  **Safety Filters**: Medical/Cosmetic imagery is often incorrectly flagged by generic AI safety filters (e.g., analyzing bare skin is sometimes flagged as sexually explicit). We had to explicitly override Google's `HarmBlockThreshold` settings to allow the AI to function as a medical assistant.
2.  **Stateless Auth (Upcoming)**: We opted to use JSON Web Tokens (JWT) instead of server-side sessions. This allows our FastAPI backend to remain stateless, making it infinitely scalable.

---

## 📈 Future Scalability

Because we separated the pipeline into distinct stages, we can swap out any piece without breaking the others:
*   If we want a better Face Detector, we can replace MediaPipe with Dlib.
*   If OpenAI releases a better vision model, we simply swap out the Stage 3 Gemini API call with GPT-4o.
*   If we need more medical knowledge, we just add more text to `skincare_dataset.json` and ChromaDB automatically indexes it.
