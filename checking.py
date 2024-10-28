import cv2
import os
import mediapipe as mp
from face_utils import get_face_encoding

mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)
cap = cv2.VideoCapture(0)

def detect_face(image):
    """Detect face using MediaPipe and return face location"""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_detection.process(image_rgb)
    
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

while True:
    ret, frame = cap.read()
    cv2.imshow('Face Recognition', frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        filename = 'checking.jpg'
        cv2.imwrite(filename, frame)
        break

# Load the saved image
file_path = cv2.imread(filename)
# Pass the image to detect_face function
detect_file = detect_face(file_path)
print(detect_file)

if detect_file:
    x, y, width, height = detect_file
    # Crop the face from the original image
    face_image = file_path[y:y + height, x:x + width]
    cv2.imwrite('cropped_face.jpg', face_image)
    face_encoding = get_face_encoding(face_image)
    print(face_encoding)

cap.release()
cv2.destroyAllWindows()
