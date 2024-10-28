import flet as ft
import os, io, base64
from PIL import Image

class DisplayRecognizedUser(ft.UserControl):
    def __init__(self, page, user_data):
        super().__init__()
        self.page = page
        self.user_data = user_data
        self.no_user = ft.Icon(
            name=ft.icons.IMAGE_OUTLINED,
            scale=ft.Scale(5)
        )
        self.go_home_button =  ft.Row(
            controls=[
                ft.Container(
                    border_radius=5,
                    expand=True,
                    bgcolor='#F4CE14',
                    content=ft.Text('Sign out', text_align=ft.TextAlign.CENTER, size=18, color=ft.colors.BLACK),
                    padding=ft.padding.only(left=25, right=25, top=10, bottom=10),
                    on_click=self.go_home,
                )
            ],
            alignment='center',
            vertical_alignment='center'
        )

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
                    ft.Text('Face Recognized!', size=24, weight=ft.FontWeight.BOLD),
                    ft.Text('Below are the credentials of the user', size=18, weight=ft.FontWeight.W_800),
                    ft.Image(src_base64=img_data) if img_data else ft.Text('No Image available'),
                    ft.Text(f"Full Name: {self.user_data.get('fullname', 'N/A')}"),
                    ft.Text(f"Email: {self.user_data.get('email', 'N/A')}"),
                    ft.Text(f"Phone: {self.user_data.get('telephone', 'N/A')}"),
                    ft.Divider(height=20, color='transparent'),
                    self.go_home_button,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            alignment=ft.alignment.center,
            padding=20
        )
    
    def go_home(self, e):
        self.page.client_storage.remove("session")
        self.page.go('/')
    