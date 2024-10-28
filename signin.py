import flet as ft
import cv2
import mediapipe as mp
import threading
import base64
import os, time
import json
import numpy as np
from face_utils import FaceDetector, get_face_encoding, compare_faces

mp_face_detection = mp.solutions.face_detection
cap = cv2.VideoCapture(0)

class SignInPage(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.face_detector = FaceDetector()
        self.running = True
        self.img = ft.Image(
            border_radius=ft.border_radius.all(20),
            width=299,
            height=299
        )
        self.signin_button =  ft.Row(
            controls=[
                ft.Container(
                    border_radius=5,
                    expand=True,
                    bgcolor=ft.colors.GREEN,
                    content=ft.Text('Capture face', text_align=ft.TextAlign.CENTER, size=18),
                    padding=ft.padding.only(left=25, right=25, top=10, bottom=10),
                    on_click=self.sign_in,
                )
            ],
            alignment='center',
            vertical_alignment='center'
        )

    def did_mount(self):
        self.update_frame()

    def will_unmount(self):
        self.running = False
        cap.release()

    def update_frame(self):
        def update():
            while self.running:
                ret, frame = cap.read()
                if ret:
                    frame = frame[120:120+299, 200:200+299, :]
                    _, im_arr = cv2.imencode('.png', frame)
                    im_b64 = base64.b64encode(im_arr)
                    self.img.src_base64 = im_b64.decode("utf-8")
                    self.update()

        threading.Thread(target=update, daemon=True).start()

    def build(self):
        return ft.Column(
            [
                ft.Divider(height=10, color='transparent'),
                ft.Text('Welcome to the SignIn Page', size=24, weight=ft.FontWeight.BOLD, text_align='center'),
                ft.Divider(height=20, color='transparent'),
                self.img,
                ft.Divider(height=50, color='transparent'),
                self.signin_button
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    
    def detect_face(self, image):
        with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
            results = face_detection.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            return bool(results.detections)
        
    def create_session(self, email):
        expiration_time = int(time.time()) + 24 * 60 * 60  # Current time + 24 hours
        session_data = {
            "email": email,
            "expiration_time": expiration_time
        }
        self.page.client_storage.set("session", session_data)

    def show_snackbar(self, message):
        """Display a snackbar with a message using the new Flet method."""
        snackbar = ft.SnackBar(
            bgcolor=ft.colors.GREY_900,
            content=ft.Text(message, color=ft.colors.WHITE)
        )
        # Append the snackbar to the page's overlay and make it visible
        self.page.overlay.append(snackbar)
        snackbar.open = True
        self.page.update()  # Refresh the page to show the snackbar

    def sign_in(self, e=None):
        ret, frame = cap.read()
        frame = frame[120:120 + 299, 200:200 + 299, :]
        if not ret:
            self.show_snackbar('Camera error. Please try again.')
            return

        # Detect face using MediaPipe
        face_location = self.face_detector.detect_face(frame)
        if not face_location:
            self.show_snackbar("No face detected. Please position your face properly.")
            return

        # Get face encoding using face_recognition
        unknown_encoding = get_face_encoding(frame)
        if unknown_encoding is None:
            self.show_snackbar("Unable to process face. Please try again.")
            return

        if os.path.exists('registered_faces.json'):
            with open('registered_faces.json', 'r') as f:
                user_data = json.load(f)

            best_match = None
            best_similarity = -1
            
            for user in user_data:
                registered_encoding = np.load(user['face_encoding'])
                similarity = compare_faces(registered_encoding, unknown_encoding)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = user

            threshold = 0.6  # Adjust this threshold as needed
            
            if best_similarity >= threshold:
                self.show_snackbar(f"Welcome back, {best_match['fullname']}!")
                self.create_session(best_match['email'])
                self.page.client_storage.set("recognized_user_data", best_match)
                self.page.go('/display_recognized_user')
            else:
                self.show_snackbar("Face not recognized. Please try again.")
        else:
            self.show_snackbar("No registered users found. Please sign up first.")
        