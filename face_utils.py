# face_utils.py
import cv2
import numpy as np
import mediapipe as mp
import face_recognition

class FaceDetector:
    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(min_detection_confidence=0.5)
        
    def detect_face(self, image):
        """Detect face using MediaPipe and return face location"""
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(image_rgb)
        
        if results.detections:
            detection = results.detections[0]  # Get the first detected face
            bbox = detection.location_data.relative_bounding_box
            
            h, w, _ = image.shape
            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)
            width = int(bbox.width * w)
            height = int(bbox.height * h)
            
            # Add padding to ensure the whole face is captured
            padding = 20
            x = max(0, x - padding)
            y = max(0, y - padding)
            width = min(w - x, width + 2*padding)
            height = min(h - y, height + 2*padding)
            
            return (x, y, width, height)
        return None
    
# Function to align face using MediaPipe
def align_face(image, landmarks):
    left_eye = landmarks.landmark[33]
    right_eye = landmarks.landmark[263]
    nose = landmarks.landmark[1]

    # Calculate angle for rotation
    dY = right_eye.y - left_eye.y
    dX = right_eye.x - left_eye.x
    angle = np.degrees(np.arctan2(dY, dX)) - 180

    # Get image center and calculate rotation matrix
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    # Rotate the image
    aligned = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC)

    # Crop to face
    x, y = int(nose.x * w), int(nose.y * h)
    crop_size = min(w, h) // 2
    cropped = aligned[max(0, y-crop_size):y+crop_size, max(0, x-crop_size):x+crop_size]

    # Resize to 224x224 (VGGFace input size)
    resized = cv2.resize(cropped, (224, 224))

    return resized

def get_face_encoding(image):
    """Get face encoding using face_recognition library"""
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_image, model="hog")
    
    if face_locations:
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        if face_encodings:
            return face_encodings[0]
    return None

def compare_faces(known_encoding, unknown_encoding, tolerance=0.6):
    """Compare two face encodings and return similarity score"""
    if known_encoding is None or unknown_encoding is None:
        return 0.0
        
    # Calculate face distance
    face_distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]
    # Convert distance to similarity score (0 to 1)
    similarity = 1 - face_distance
    return similarity
