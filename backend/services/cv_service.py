import io
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image
from ultralytics import YOLO
from huggingface_hub import hf_hub_download
import os

# ── 1. Initialize MediaPipe Face Mesh (High Accuracy Masking) ──
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5
)

# MediaPipe Face Oval Landmark Indices
FACE_OVAL_INDICES = [
    10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 
    397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 
    172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109
]

# ── 2. Download YOLO Model from Hugging Face ──
# In production, replace repo_id with a dermatology-specific repo 
# e.g., repo_id="your-org/yolov8-acne-detector"
try:
    print("[YOLO] Downloading weights from Hugging Face...")
    os.environ['YOLO_VERBOSE'] = 'False'
    
    # Downloading a standard YOLOv8 weights file from Hugging Face hub as a demonstration
    # of the HF integration architecture.
    model_path = hf_hub_download(
        repo_id="merve/yolov8n", 
        filename="yolov8n.pt",
        cache_dir="models"
    )
    yolo_model = YOLO(model_path)
    print("[YOLO] Hugging Face model loaded successfully!")
except Exception as e:
    print(f"[YOLO] Error loading model from Hugging Face: {e}")
    yolo_model = None

def process_and_detect(image_bytes: bytes) -> tuple[bytes, str, dict]:
    """
    STAGE 1 & 2 OF THE HIGH-ACCURACY PIPELINE
    
    1. MediaPipe Face Masking: Detects face and cuts out background.
    2. YOLO Object Detection: Scans masked face using HF weights.
    
    Returns:
        (masked_image_bytes, yolo_text_context, face_regions_dict)
    Raises:
        ValueError if no face is detected.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Invalid image file format.")
        
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w, _ = img.shape

    # ── STEP 1: MediaPipe Face Masking (Geometry) ──
    results = face_mesh.process(img_rgb)
    
    if not results.multi_face_landmarks:
        # FAIL-FAST: No face detected, reject instantly!
        raise ValueError("NO_FACE_DETECTED")
        
    landmarks = results.multi_face_landmarks[0]
    
    face_points = []
    for idx in FACE_OVAL_INDICES:
        point = landmarks.landmark[idx]
        x = int(point.x * w)
        y = int(point.y * h)
        face_points.append([x, y])
        
    face_points = np.array(face_points, dtype=np.int32)
    
    # Create mask and apply it
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(mask, [face_points], 255)
    masked_img = cv2.bitwise_and(img_rgb, img_rgb, mask=mask)
    
    # ── STEP 2: YOLO Object Detection (Disabled for Dynamic VLM) ──
    # We leave this section empty so the VLM (Gemini) can analyze the skin 
    # dynamically using its own vision capabilities, rather than anchoring 
    # to a hardcoded mock YOLO string.
    yolo_text_context = ""

    # Convert masked image to bytes
    pil_img = Image.fromarray(masked_img)
    img_byte_arr = io.BytesIO()
    pil_img.save(img_byte_arr, format='JPEG', quality=95)
    masked_image_bytes = img_byte_arr.getvalue()

    # ── STEP 3: Calculate Semantic Face Regions for AI HUD ──
    # We use MediaPipe's precise facial landmarks to define zones,
    # so we can draw HUD markers without relying on a VLM's flaky spatial grounding.
    def get_bbox(indices):
        xs = [int(landmarks.landmark[i].x * w) for i in indices]
        ys = [int(landmarks.landmark[i].y * h) for i in indices]
        return [min(ys), min(xs), max(ys), max(xs)] # ymin, xmin, ymax, xmax
    
    face_regions = {
        "eyes": get_bbox([33, 133, 362, 263, 145, 374, 159, 386]), 
        "forehead": get_bbox([10, 338, 297, 332, 284, 109, 67, 103]),
        "cheeks": get_bbox([50, 205, 187, 116, 280, 425, 411, 345, 323, 137]),
        "nose": get_bbox([1, 2, 98, 327]),
        "jaw": get_bbox([152, 148, 176, 149, 150, 136, 172, 377, 400, 378, 379, 365, 397])
    }

    return masked_image_bytes, yolo_text_context, face_regions
