import os
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
from deepface import DeepFace

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Config for file uploads
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/analyze_deepface", methods=["POST"])
def analyze_deepface_api():
    """API endpoint to analyze an image for anti-spoofing using DeepFace."""
    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image uploaded"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"success": False, "error": "Empty filename"}), 400

    # Save the uploaded image
    image_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(image_path)

    try:
        start = time.time()
        result = DeepFace.extract_faces(
            img_path=image_path,
            detector_backend="opencv",
            anti_spoofing=True
        )

        if isinstance(result, list):
            result = result[0]

        processing_time = time.time() - start
        is_real = result.get("is_real", False)
        anti_info = result.get("anti_spoofing", {})
        spoof_score = anti_info.get("confidence", 0.0)

        if is_real:
            confidence = 1 - spoof_score
            spoof_type = "Real Face"
        else:
            confidence = spoof_score
            if spoof_score < 0.6:
                spoof_type = "Printed/2D Attack"
            elif spoof_score < 0.8:
                spoof_type = "Video Replay Attack"
            else:
                spoof_type = "Unknown Spoof"

        return jsonify({
            "success": True,
            "is_real": is_real,
            "confidence": confidence,
            "spoof_type": spoof_type,
            "processing_time": round(processing_time, 2)
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify API is running."""
    return jsonify({"status": "healthy", "message": "DeepFace Anti-Spoofing server is running"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4001, debug=True)