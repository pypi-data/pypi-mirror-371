import requests
from pathlib import Path
import cv2
import numpy as np
import tensorflow as tf
from datetime import datetime
import subprocess
import sys
import time
import os

class DeepFaceAntiSpoofing:
    def __init__(self):
        self.models_dir = Path.cwd() / "models"
        self.data_dir = Path.cwd() / "data"
        self.age_gender_model_path = self.models_dir / "age_gender_model.h5"
        self.anti_spoofing_model_path = self.models_dir / "anti_spoofing_model.h5"
        self.cascade_path = self.data_dir / "haarcascade_frontalface_default.xml"
        self._ensure_resources()
        self.age_gender_model = self._load_age_gender_model()
        self.anti_spoofing_model = self._load_anti_spoofing_model()
        self.face_cascade = cv2.CascadeClassifier(str(self.cascade_path))
        if self.face_cascade.empty():
            raise Exception("Failed to load Haar Cascade classifier")
        self.api_running = self._start_api_server()

    def _start_api_server(self):
        """Start the deepface_api.py server if not already running."""
        api_url = "http://localhost:4001/health"  # Changed to port 4001
        try:
            # Check if API is already running
            response = requests.get(api_url, timeout=2)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass

        # Locate deepface_api.py in the deepface_antispoofing package directory
        package_dir = Path(__file__).parent
        api_path = package_dir / "deepface_api.py"
        if not api_path.exists():
            print(f"Error: deepface_api.py not found at {api_path}")
            return False

        print("Starting DeepFace Anti-Spoofing server...")
        try:
            # Start subprocess and capture output
            process = subprocess.Popen(
                [sys.executable, str(api_path)],
                cwd=package_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # Wait for the server to start
            for _ in range(15):  # Increased retries to 15 seconds
                try:
                    response = requests.get(api_url, timeout=2)
                    if response.status_code == 200:
                        print("DeepFace Anti-Spoofing started successfully")
                        return True
                except requests.RequestException:
                    time.sleep(1)
            # Capture subprocess output for debugging
            stdout, stderr = process.communicate(timeout=5)
            print(f"Subprocess stdout: {stdout}")
            print(f"Subprocess stderr: {stderr}")
            print("Failed to start DeepFace Anti-Spoofing server after retries")
            return False
        except Exception as e:
            print(f"Error starting DeepFace Anti-Spoofing server: {str(e)}")
            return False

    def _ensure_resources(self):
        """Ensure models and Haar Cascade file are available. Downloads them if they don't exist."""
        self.models_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)

        if not self.age_gender_model_path.exists():
            print("Downloading age_gender_model.h5...")
            response = requests.get("https://ipsoftechs.pythonanywhere.com/media/age_gender_model.h5")
            if response.status_code == 200:
                with open(self.age_gender_model_path, "wb") as f:
                    f.write(response.content)
                print("age_gender_model.h5 downloaded successfully.")
            else:
                raise Exception("Failed to download age_gender_model.h5")

        if not self.anti_spoofing_model_path.exists():
            print("Downloading anti_spoofing_model.h5...")
            response = requests.get("https://ipsoftechs.pythonanywhere.com/media/anti_spoofing_model.h5")
            if response.status_code == 200:
                with open(self.anti_spoofing_model_path, "wb") as f:
                    f.write(response.content)
                print("anti_spoofing_model.h5 downloaded successfully.")
            else:
                raise Exception("Failed to download anti_spoofing_model.h5")

        if not self.cascade_path.exists():
            print("Downloading haarcascade_frontalface_default.xml...")
            response = requests.get(
                "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
            )
            if response.status_code == 200:
                with open(self.cascade_path, "wb") as f:
                    f.write(response.content)
                print("haarcascade_frontalface_default.xml downloaded successfully.")
            else:
                raise Exception("Failed to download haarcascade_frontalface_default.xml")

    def _load_age_gender_model(self):
        """Load the age and gender model."""
        model = tf.keras.models.load_model(self.age_gender_model_path, compile=False)
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
            loss={
                'age': tf.keras.losses.CategoricalCrossentropy(),
                'gender': tf.keras.losses.CategoricalCrossentropy()
            },
            metrics={
                'age': 'accuracy',
                'gender': 'accuracy'
            }
        )
        return model

    def _load_anti_spoofing_model(self):
        """Load the anti-spoofing model."""
        model = tf.keras.models.load_model(self.anti_spoofing_model_path, compile=False)
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        return model

    def _convert_to_serializable(self, data):
        """Convert numpy types to JSON-serializable types."""
        if isinstance(data, dict):
            return {k: self._convert_to_serializable(v) for k, v in data.items()}
        elif isinstance(data, (np.float32, np.float64)):
            return float(data)
        elif isinstance(data, (np.int32, np.int64)):
            return int(data)
        return data

    def _detect_face(self, file_path: str) -> tuple[bool, str | tuple]:
        """Detect faces in the image using Haar Cascade."""
        try:
            img = cv2.imread(file_path)
            if img is None:
                return False, "Failed to load image"
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            if len(faces) == 1:
                return True, faces[0]
            elif len(faces) == 0:
                return False, "No face detected"
            else:
                return False, "Multiple faces detected"
        except Exception as e:
            return False, str(e)

    def analyze_image(self, file_path: str) -> dict:
        """Analyze an image for age, gender, and spoof detection."""
        face_detected, message_or_coords = self._detect_face(file_path)
        if not face_detected:
            return {"error": message_or_coords}

        try:
            img = cv2.imread(file_path)
            if img is None:
                raise ValueError("Failed to load image")

            img_age_gender = cv2.resize(img, (96, 96))
            img_age_gender = img_age_gender.astype(np.float32) / 255.0
            img_age_gender = np.expand_dims(img_age_gender, axis=0)

            img_anti_spoof = cv2.resize(img, (128, 128))
            img_anti_spoof = img_anti_spoof.astype(np.float32) / 255.0
            img_anti_spoof = np.expand_dims(img_anti_spoof, axis=0)

            age_pred, gender_pred = self.age_gender_model.predict(img_age_gender)
            age = int(np.argmax(age_pred[0]))
            gender_probs = gender_pred[0]
            gender_dict = {'Male': float(gender_probs[0]), 'Female': float(gender_probs[1])}
            dominant_gender = 'Male' if gender_probs[0] > gender_probs[1] else 'Female'

            spoof_pred = self.anti_spoofing_model.predict(img_anti_spoof)
            spoof_prob = float(spoof_pred[0][0])
            is_real = spoof_prob > 0.5
            spoof_dict = {'Fake': 1.0 - spoof_prob, 'Real': spoof_prob}
            dominant_spoof = 'Real' if is_real else 'Fake'

            analysis = {
                "age": age,
                "gender": gender_dict,
                "dominant_gender": dominant_gender,
                "spoof": spoof_dict,
                "dominant_spoof": dominant_spoof,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            return self._convert_to_serializable(analysis)
        except Exception as e:
            return {"error": str(e)}

    def analyze_deepface(self, image_path: str):
        """Analyze an image by calling the DeepFace API on localhost:4001."""
        if not self.api_running:
            return {"success": False, "error": "DeepFace API is not running"}
        try:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    with open(image_path, "rb") as image_file:
                        files = {"image": (os.path.basename(image_path), image_file, "image/jpeg")}
                        response = requests.post("http://localhost:4001/analyze_deepface", files=files, timeout=5)
                    if response.status_code == 200:
                        return response.json()
                    else:
                        return {"success": False, "error": f"API request failed with status {response.status_code}"}
                except requests.RequestException as e:
                    if attempt < max_retries - 1:
                        print(f"Retrying API call ({attempt + 1}/{max_retries})...")
                        time.sleep(2)
                        continue
                    return {"success": False, "error": f"Failed to connect to API after {max_retries} attempts: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    deepface = DeepFaceAntiSpoofing()
    result = deepface.analyze_image("path_to_image.jpg")
    print(result)