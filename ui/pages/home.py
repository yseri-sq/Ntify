import flet as ft

from ui.track_card import create_track_card


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
            # ft.Row(
            #     controls=cards,
            #     wrap=True,
            #     spacing=16,
            #     run_spacing=16,
            # ),
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
