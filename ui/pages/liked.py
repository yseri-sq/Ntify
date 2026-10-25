import flet as ft


def create_liked_page():
    return ft.Column(
        controls=[
            ft.Icon(
                ft.Icons.FAVORITE,
                size=42,
                color="#1DB954",
            ),
            ft.Text(
                "Liked songs",
                size=28,
                weight=ft.FontWeight.BOLD,
                color="#FFFFFF",
            ),
            ft.Text(
                "Your favorite tracks will appear here.",
                size=14,
                color="#B3B3B3",
            ),
        ],
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
    )
