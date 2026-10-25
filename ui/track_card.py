import flet as ft

from service.favorites_service import (
    get_favorites,
    toggle_favorite,
)


def create_track_card(track, on_play=None):
    favorites = get_favorites()
    is_favorite = track.id in favorites

    title = track.title
    artist = track.artist

    favorite_button = ft.IconButton(
        icon=(
            ft.Icons.FAVORITE
            if is_favorite
            else ft.Icons.FAVORITE_BORDER
        ),
        icon_color="#1DB954" if is_favorite else "#B3B3B3",
        tooltip="Remove from liked songs" if is_favorite else "Add to liked songs",
    )

    def change_favorite(e):
        nonlocal is_favorite

        toggle_favorite(track.id)
        is_favorite = not is_favorite

        favorite_button.icon = (
            ft.Icons.FAVORITE
            if is_favorite
            else ft.Icons.FAVORITE_BORDER
        )
        favorite_button.icon_color = (
            "#1DB954" if is_favorite else "#B3B3B3"
        )
        favorite_button.tooltip = (
            "Remove from liked songs"
            if is_favorite
            else "Add to liked songs"
        )

        favorite_button.update()

    favorite_button.on_click = change_favorite

    def play_track(e):
        if on_play is not None:
            on_play(track)

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.ALBUM,
                        size=56,
                        color="#B3B3B3",
                    ),
                    height=130,
                    alignment=ft.Alignment.CENTER,
                    bgcolor="#333333",
                    border_radius=8,
                ),
                ft.Text(
                    title,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color="#FFFFFF",
                    max_lines=1,
                ),
                ft.Text(
                    artist,
                    size=13,
                    color="#B3B3B3",
                    max_lines=1,
                ),
                ft.Row(
                    controls=[
                        ft.FilledButton(
                            content="Play",
                            icon=ft.Icons.PLAY_ARROW,
                            on_click=play_track,
                        ),
                        favorite_button,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=8,
        ),
        width=190,
        padding=12,
        bgcolor="#282828",
        border_radius=12,
        animate=200,
    )
