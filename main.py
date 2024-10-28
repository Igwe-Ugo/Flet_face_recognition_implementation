import time
import flet as ft
from signup import SignUpPage
from signin import SignInPage
from landingpage import LandingPage
from register_face import RegisterFace
from user import User
from display_recognized_user import DisplayRecognizedUser

def main(page: ft.Page):
    page.title = "Flet Face Recognition Application"
    page.theme_mode = ft.ThemeMode.DARK

    landing_page_instance = LandingPage(page)
    signin_page_instance = SignInPage(page)
    signup_page_instance = SignUpPage(page)
    register_face_instance = RegisterFace(page)
    user_instance = User(page)

    def show_snackbar(message):
        """Display a snackbar with a message using the new Flet method."""
        snackbar = ft.SnackBar(
            bgcolor=ft.colors.GREY_900,
            content=ft.Text(message, color=ft.colors.WHITE)
        )
        # Append the snackbar to the page's overlay and make it visible
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()  # Refresh the page to show the snackbar

    def check_session():
        session = page.client_storage.get("session")
        if session:
            current_time = int(time.time())
            if current_time < session["expiration_time"]:
                #show_snackbar('Session is still active')
                return True
            else:
                # Session expired, clear it
                #show_snackbar('Session has expired, no longer active')
                page.client_storage.remove("session")
        return False

    def route_change(route):
        page.views.clear()
        # Check client_storage for protected routes
        is_session_valid = check_session()

        if page.route == '/':
            if is_session_valid:
                page.go("/display_recognized_user")
            else:
                page.views.append(landing_page_instance)
        elif page.route == "/signin":
            """ if is_session_valid:
                page.go("/display_recognized_user")
            else: """
            page.views.append(
                ft.View(
                    route="/signin",
                    controls=[
                        ft.AppBar(
                            leading=ft.IconButton(
                                icon=ft.icons.ARROW_BACK_IOS,
                                icon_size=20,
                                tooltip='Back to Landing Page',
                                on_click=lambda _: page.go("/")
                            ),
                            title=ft.Text("Sign In"),
                            bgcolor=ft.colors.SURFACE_VARIANT
                        ),
                        signin_page_instance
                    ]
                )
            )
        elif page.route == "/signup":
            page.views.append(
                ft.View(
                    route="/signup",
                    controls=[
                        ft.AppBar(
                            leading=ft.IconButton(
                                icon=ft.icons.ARROW_BACK_IOS,
                                icon_size=20,
                                tooltip='Back to Landing Page',
                                on_click=lambda _: page.go("/")
                            ),
                            title=ft.Text("Sign Up"),
                            bgcolor=ft.colors.SURFACE_VARIANT
                        ),
                        signup_page_instance
                    ]
                )
            )
        elif page.route == "/register_face":
            if is_session_valid:
                page.go("/display_recognized_user")
            else:
                page.views.append(
                    ft.View(
                        route="/register_face",
                        controls=[
                            ft.AppBar(
                                leading=ft.IconButton(
                                    icon=ft.icons.ARROW_BACK_IOS,
                                    icon_size=20,
                                    tooltip='Back to Sign Up Page',
                                    on_click=lambda _: page.go("/signup")
                                ),
                                title=ft.Text("Register face"),
                                bgcolor=ft.colors.SURFACE_VARIANT
                            ),
                            register_face_instance,
                        ]
                    )
                )
        elif page.route == "/user":
            page.views.append(
                ft.View(
                    route="/user",
                    controls=[
                        ft.AppBar(
                            leading=ft.IconButton(
                                icon=ft.icons.ARROW_BACK_IOS,
                                icon_size=20,
                                tooltip='Back',
                                on_click=lambda _: page.go("/register_face")
                            ),
                            title=ft.Text("Registered User"),
                            bgcolor=ft.colors.SURFACE_VARIANT
                        ),
                        user_instance,
                    ]
                )
            )
        elif page.route.startswith("/display_recognized_user"):
            # Extract user data from the route
            user_data = page.client_storage.get("recognized_user_data")
            if user_data:
                display_recognized_user_instance = DisplayRecognizedUser(page, user_data)
                page.views.append(
                    ft.View(
                        route="/display_recognized_user",
                        controls=[
                            ft.AppBar(
                                leading=ft.IconButton(
                                    icon=ft.icons.ARROW_BACK_IOS,
                                    icon_size=20,
                                    tooltip='Back to Sign In',
                                    on_click=lambda _: page.go("/signin")
                                ),
                                title=ft.Text("Recognized User"),
                                bgcolor=ft.colors.SURFACE_VARIANT
                            ),
                            display_recognized_user_instance,
                        ]
                    )
                )
            else:
                show_snackbar('No User found with this face, please signup')
                # If no user data is found, redirect to sign up page
                page.go("/signup")
        else:
            page.views.append(landing_page_instance)

        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

if __name__ == '__main__':
    ft.app(target=main, assets_dir='assets')
