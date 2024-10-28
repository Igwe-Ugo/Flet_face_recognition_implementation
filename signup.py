import re
import flet as ft

link_style = {
    "height": 50,
    "focused_border_color": "#F4CE14",
    "border_radius": 5,
    "cursor_height": 16,
    "cursor_color": "white",
    "content_padding": 10,
    "border_width": 1.5,
    "text_size": 14,
    "label_style": ft.TextStyle(
        color='#F4CE14'
    )
}

regexEmail = r"^[a-zA-Z0-9.a-zA-Z0-9.!#$%&'*+-/=?^_`{|}~]+@[a-zA-Z0-9]+\.[a-zA-Z]+"

class SignUpPage(ft.UserControl):
    def __init__(self, page) -> None:
        super().__init__()
        self.page = page

        self.fullname = ft.TextField(
            password=False,
            label='Enter fullname',
            **link_style,
        )

        self.email_address = ft.TextField(
            password=False,
            **link_style,
            label='Enter email address'
        )

        self.telephone = ft.TextField(
            password=False,
            **link_style,
            label='Enter phone number',
            #keyboard_type=
        )

        self.registerButton = ft.Container(
            border_radius=5,
            expand=True,
            bgcolor='#F4CE14',
            content=ft.Text(
                'Register',
                color='black',
                text_align=ft.TextAlign.CENTER,
                size=18,
            ),
            padding=ft.padding.only(left=25, right=25, top=10, bottom=10),
            on_click=self.check_signup_fields,
        )

        # using expanded and row to make the button span the full page width
        self.register_button_row = ft.Row(
            controls=[
               self.registerButton
            ],
            alignment='center',
            vertical_alignment='center'
        )

    def build(self):
        # Define the list of items to display
        return ft.Container(
            padding=ft.padding.only(left=25, right=25, top=10, bottom=10),
            content=ft.SafeArea(
                expand=True,
                content=ft.Column(
                    controls = [
                        ft.Text(
                            'Welcome to the Sign Up Page',
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            text_align='center'
                        ),
                        ft.Divider(
                            height=10,
                            color='transparent'
                        ),
                        ft.Column(
                            spacing=20,
                            controls=[
                                self.fullname,
                                self.email_address,
                                self.telephone,
                                ft.Divider(
                                    height=50,
                                    color='transparent'  
                                ),
                                self.register_button_row
                            ]
                        )
                    ]
                )
            )
        )

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

    def check_signup_fields(self, e):
        fullname = self.fullname.value
        email_address = self.email_address.value
        telephone = self.telephone.value

        if not (fullname and email_address and telephone):
            self.show_snackbar("All fields must be filled to proceed.")
        elif not re.match(regexEmail, email_address):
            self.show_snackbar("Invalid email address. Please enter a valid email.")
        else:
            # Store user credentials in client_storage
            self.page.client_storage.set("fullname", fullname)
            self.page.client_storage.set("email", email_address)
            self.page.client_storage.set("telephone", telephone)
            self.page.go('/register_face')
