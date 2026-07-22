import requests
import json
import sys
import os

# The endpoint we are testing
URL = "http://127.0.0.1:8000/api/analyze"

def test_analyze_endpoint(image_path):
    print(f"🚀 Starting Dry Run with image: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"❌ Error: Could not find image at '{image_path}'")
        print("Please place a photo named 'test_face.jpg' in this folder and try again.")
        sys.exit(1)

    print("📤 Sending image to FastAPI (which will trigger OpenCV -> YOLO -> Gemini -> RAG)...")
    
    # We must send the image as multipart/form-data
    with open(image_path, "rb") as f:
        files = {"file": (os.path.basename(image_path), f, "image/jpeg")}
        
        try:
            response = requests.post(URL, files=files)
            
            # Print the HTTP status code
            print(f"📡 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS! Here is the JSON output from Gemini:")
                # Pretty-print the JSON response
                parsed_json = response.json()
                print(json.dumps(parsed_json, indent=4))
            else:
                print("❌ FAILED. Error details:")
                print(response.text)
                
        except requests.exceptions.ConnectionError:
            print("❌ Error: Could not connect to the server.")
            print("Is your FastAPI backend running on port 8000?")

if __name__ == "__main__":
    # You can change this to the name of any photo you put in the backend folder
    test_image_name = "test_face.jpg"
    test_analyze_endpoint(test_image_name)
