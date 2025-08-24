# DeepFace Anti-Spoofing

The **DeepFace Anti-Spoofing** package enables users to perform advanced face recognition, anti-spoofing, and deepfake detection on images. It provides predictions for age, gender, and determines whether an image contains a real face, a printed photo, a replay attack, a presentation attack, or an AI-generated deepfake. This package is designed for secure authentication, identity verification, and seamless integration into Python applications, ensuring reliable and efficient image analysis.

## Features

- **Face Analysis**: Predict age and gender from uploaded images using the `analyze_image` method.
- **Anti-Spoofing Detection**: Determine whether a face is real or part of a spoofing attack (e.g., printed photo, replay, or presentation attack) using the `analyze_deepface` method.
- **Deepfake Detection**: Detect AI-generated faces or deepfakes with high accuracy via the `analyze_image` method.
- **Simple Integration**: Easily integrate into Python applications for robust image analysis.

## Documentation

Comprehensive documentation, guidance, and code examples, including a web interface for testing, are provided at the [DeepFace Anti-Spoofing Documentation](https://ipsoftechsolutions.pythonanywhere.com/deepface-antispoofing-documentation/).

## Installation

To use the DeepFace Anti-Spoofing and Deepfake Analysis package in your Python application, install the required package:

```bash
pip install deepface-antispoofing
```

## Usage Examples

### Example 1: Face Analysis with Age, Gender, and Deepfake Detection
The `analyze_image` method predicts age, gender, and whether the image contains a real or AI-generated face.

```python
from deepface_antispoofing import DeepFaceAntiSpoofing

file_path = "path_to_image.jpg"

deepface = DeepFaceAntiSpoofing()

response = deepface.analyze_image(file_path)

print(response)
```

**Sample Response**:
```json
{
  "id": 1,
  "age": 30,
  "gender": {
    "Male": 0.85,
    "Female": 0.15
  },
  "dominant_gender": "Male",
  "spoof": {
    "Fake": 0.02,
    "Real": 0.98
  },
  "dominant_spoof": "Real",
  "timestamp": "2025-04-18 12:34:56"
}
```

### Example 2: Anti-Spoofing Detection for Printed, Replay, or Presentation Attacks
The `analyze_deepface` method determines whether the face is real or part of a spoofing attack, such as a printed photo, replay attack, or presentation attack.

```python
from deepface_antispoofing import DeepFaceAntiSpoofing

file_path = "path_to_image.jpg"

deepface = DeepFaceAntiSpoofing()

response = deepface.analyze_deepface(file_path)

print(response)
```

**Sample Response**:
```json
{
  "confidence": 1.0,
  "is_real": "True",
  "processing_time": 1.03,
  "spoof_type": "Real Face",
  "success": "True"
}
```

## Key Points

- Ensure the uploaded image contains a clear face for accurate analysis.
- Use `analyze_image` for age, gender, and deepfake detection.
- Use `analyze_deepface` for detecting spoofing attacks like printed photos, replay attacks, or presentation attacks.
- Refer to the [official documentation](https://ipsoftechsolutions.pythonanywhere.com/deepface-antispoofing-documentation/) for detailed endpoint specifications, advanced features, and web interface usage.

## Support

For any issues or questions, please contact [ipsoftechsolutions@gmail.com](mailto:ipsoftechsolutions@gmail.com).

---

Thank you for choosing DeepFace Anti-Spoofing for your face recognition, anti-spoofing, and deepfake detection needs!