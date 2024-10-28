import os
import io
import json
import base64
import flet as ft
from PIL import Image

class User(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.no_user = ft.Icon(
            name=ft.icons.IMAGE_OUTLINED,
            scale=ft.Scale(5)
        )

        self.user_data = self.get_latest_user()
        self.go_home_button =  ft.Row(
            controls=[
                ft.Container(
                    border_radius=5,
                    expand=True,
                    bgcolor='#F4CE14',
                    content=ft.Text('Back to Home', text_align=ft.TextAlign.CENTER, size=18, color=ft.colors.BLACK),
                    padding=ft.padding.only(left=25, right=25, top=10, bottom=10),
                    on_click=self.go_home,
                )
            ],
            alignment='center',
            vertical_alignment='center'
        )

    def get_latest_user(self):
        if os.path.exists('registered_faces.json'):
            with open('registered_faces.json', 'r') as f:
                all_users = json.load(f)
                if all_users:
                    return all_users[-1] # return the last registered user
        return None
    
    def load_image(self, path):
        if os.path.exists(path):
            with Image.open(path) as img:
                img = img.resize((299, 299)) # resize image for display
                buffered = io.BytesIO()
                img.save(buffered, format='PNG')
                return base64.b64encode(buffered.getvalue()).decode()
        return None
    
    def build(self):
        if not self.user_data:
            return ft.Column(
                [
                    ft.Divider(height=120, color='transparent'),
                    self.no_user,
                    ft.Divider(height=70, color='transparent'),
                    ft.Text('No user data found', size=18, weight=ft.FontWeight.W_800),
                ],
                horizontal_alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            )
        
        img_data = self.load_image(self.user_data.get('face_image', ''))
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text('Registration Successful!', size=24, weight=ft.FontWeight.BOLD),
                    ft.Text('Below are the credentials of the user', size=18, weight=ft.FontWeight.W_800),
                    ft.Divider(height=30, color='transparent'),
                    ft.Image(src_base64=img_data) if img_data else ft.Text('No Image available'),
                    ft.Divider(height=15, color='transparent'),
                    ft.Text(f"Full Name: {self.user_data.get('fullname', 'N/A')}"),
                    ft.Text(f"Email: {self.user_data.get('email', 'N/A')}"),
                    ft.Text(f"Phone Number: {self.user_data.get('telephone', 'N/A')}"),
                    ft.Divider(height=50, color='transparent'),
                    self.go_home_button,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            alignment=ft.alignment.center,
            padding=20,
        )
    
    def go_home(self, e):
        self.page.go('/')
