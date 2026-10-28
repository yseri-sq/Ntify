import flet as ft

#https://www.youtube.com/watch?v=glEiPXAYE-U&list=RDCLAK5uy_kP2172rQNb3KFXz880xp6M98R_ME5CIKA&index=2

def create_home_page(on_play=None):

    return ft.Column(
        controls=[
            ft.Text(
                "Good evening",
                size=28,
                weight=ft.FontWeight.BOLD,
                color="#FFFFFF",
            ),
            ft.Text(
                "Popular tracks",
                size=20,
                weight=ft.FontWeight.BOLD,
                color="#FFFFFF",
            ),
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
