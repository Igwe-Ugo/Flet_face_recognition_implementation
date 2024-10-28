# register_face.py
import os
import json
import base64
import cv2
import time
import threading
import flet as ft
import numpy as np
from datetime import datetime
from face_utils import FaceDetector, get_face_encoding

class RegisterFace(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.running = True
        self.face_detector = FaceDetector()
        self.camera = None
        self.init_camera()
        
        self.img = ft.Image(
            border_radius=ft.border_radius.all(20),
            width=299,
            height=299
        )
        self.capture_face_button = ft.Row(
            controls=[
                ft.Container(
                    border_radius=5,
                    expand=True,
                    bgcolor=ft.colors.GREEN,
                    content=ft.Text('Register face', text_align=ft.TextAlign.CENTER, size=18),
                    padding=ft.padding.only(left=25, right=25, top=10, bottom=10),
                    on_click=self.capture_image,
                )
            ],
            alignment='center',
            vertical_alignment='center'
        )
        
    def init_camera(self):
        """Initialize the camera with error handling"""
        if self.camera is not None and self.camera.isOpened():
            self.camera.release()
        
        # Try different camera indices
        for index in range(2):  # Try camera 0 and 1
            self.camera = cv2.VideoCapture(index)
            if self.camera.isOpened():
                # Set camera resolution
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                break
        
        if not self.camera.isOpened():
            print("Error: Could not open camera")
            self.show_snackbar("Error: Could not access camera")

    def did_mount(self):
        self.update_cam_timer()

    def will_unmount(self):
        self.running = False
        if self.camera is not None:
            self.camera.release()

    def update_cam_timer(self):
        def update():
            while self.running:
                if self.camera is None or not self.camera.isOpened():
                    self.init_camera()
                    time.sleep(1)
                    continue

                ret, frame = self.camera.read()
                if not ret or frame is None:
                    print("Error: Failed to grab frame")
                    time.sleep(0.1)
                    continue

                try:
                    # Get center crop coordinates
                    height, width = frame.shape[:2]
                    start_y = max(0, (height - 299) // 2)
                    start_x = max(0, (width - 299) // 2)
                    
                    # Crop frame to center
                    cropped_frame = frame[start_y:start_y+299, start_x:start_x+299]
                    
                    # Check if crop was successful
                    if cropped_frame.shape[:2] != (299, 299):
                        cropped_frame = cv2.resize(frame, (299, 299))
                    
                    # Convert to base64
                    _, im_arr = cv2.imencode('.png', cropped_frame)
                    im_b64 = base64.b64encode(im_arr)
                    
                    # Update image in UI
                    self.img.src_base64 = im_b64.decode("utf-8")
                    self.update()
                    
                except Exception as e:
                    print(f"Error processing frame: {e}")
                
                time.sleep(0.033)  # Cap at ~30 FPS

        threading.Thread(target=update, daemon=True).start()

    def build(self):
        return ft.Column(
            [
                ft.Divider(height=10, color='transparent'),
                ft.Text('Position face for capturing', size=24, weight=ft.FontWeight.BOLD, text_align='center'),
                ft.Divider(height=20, color='transparent'),
                self.img,
                ft.Divider(height=50, color='transparent'),
                self.capture_face_button
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    def show_snackbar(self, message):
        snackbar = ft.SnackBar(
            bgcolor=ft.colors.GREY_900,
            content=ft.Text(message, color=ft.colors.WHITE)
        )
        self.page.overlay.append(snackbar)
        snackbar.open = True
        self.page.update()

    def create_session(self, email):
        expiration_time = int(time.time()) + 24 * 60 * 60  # Current time + 24 hours
        session_data = {
            "email": email,
            "expiration_time": expiration_time
        }
        self.page.session.set("session", session_data)

    def capture_image(self, e=None):
        if self.camera is None or not self.camera.isOpened():
            self.show_snackbar("Camera not available. Please check your camera connection.")
            return

        ret, frame = self.camera.read()
        if not ret or frame is None:
            self.show_snackbar("Failed to capture image. Please try again.")
            return

        try:
            # Get center crop
            height, width = frame.shape[:2]
            start_y = max(0, (height - 299) // 2)
            start_x = max(0, (width - 299) // 2)
            frame = frame[start_y:start_y+299, start_x:start_x+299]
            
            # Ensure correct size
            if frame.shape[:2] != (299, 299):
                frame = cv2.resize(frame, (299, 299))

            # Detect face using MediaPipe
            face_location = self.face_detector.detect_face(frame)
            if not face_location:
                self.show_snackbar("No face detected. Please position your face properly.")
                return

            # Get face encoding
            face_encoding = get_face_encoding(frame)
            if face_encoding is None:
                self.show_snackbar("Unable to process face. Please try again.")
                return

            # Get user data
            fullname = self.page.client_storage.get("fullname")
            email = self.page.client_storage.get("email")
            telephone = self.page.client_storage.get("telephone")

            if not all([fullname, email, telephone]):
                self.show_snackbar("User data not found. Please sign up again.")
                self.page.go('/signup')
                return

            # Save face image
            save_dir = os.path.join('application_data', "user_faces")
            os.makedirs(save_dir, exist_ok=True)
            image_path = os.path.join(save_dir, f'{email}.jpg')
            cv2.imwrite(image_path, frame)

            # Save face encoding
            save_encoding = os.path.join('application_data', 'user_faces_encoding')
            os.makedirs(save_encoding, exist_ok=True)
            encoding_path = os.path.join(save_encoding, f'{email}_encoding.npy')
            np.save(encoding_path, face_encoding)
            
            # Prepare user data
            user_data = {
                "fullname": fullname,
                "email": email,
                "telephone": telephone,
                "face_image": image_path,
                "face_encoding": encoding_path,
                "date_registered": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            }
            
            # Load existing data or create new file
            if os.path.exists('registered_faces.json'):
                with open('registered_faces.json', 'r') as f:
                    all_users = json.load(f)
            else:
                all_users = []

            # Add new user data
            all_users.append(user_data)

            # Save updated data
            with open('registered_faces.json', 'w') as f:
                json.dump(all_users, f, indent=4)
            
            self.show_snackbar('Face registered successfully!')
            
            # Clear client_storage and create session
            #self.page.client_storage.clear()
            self.create_session(email)
            self.page.go('/user')

        except Exception as e:
            print(f"Error during capture: {e}")
            self.show_snackbar("An error occurred while processing the image. Please try again.")
