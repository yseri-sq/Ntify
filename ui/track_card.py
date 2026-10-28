import flet as ft


def create_track_card(track, on_play=None):
    title = getattr(track, "title", "Без названия")
    artist = getattr(track, "artist", "YouTube")
    cover_url = getattr(track, "cover_url", "")

    cover_content = (
        ft.Image(src=cover_url, fit=ft.BoxFit.COVER, width=160, height=132)
        if cover_url
        else ft.Icon(ft.Icons.ALBUM, size=56, color="#B3B3B3")
    )

    def play_track(e):
        if on_play is not None:
            on_play(track)

    return ft.Container(
        width=190,
        height=285,
        padding=12,
        bgcolor="#282828",
        border_radius=12,
        animate=200,
        content=ft.Column(
            controls=[
                ft.Container(
                    content=cover_content,
                    height=132,
                    width=float("inf"),
                    alignment=ft.Alignment.CENTER,
                    bgcolor="#333333",
                    border_radius=8,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                ),
                ft.Text(title, size=15, weight=ft.FontWeight.BOLD, color="#FFFFFF", max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(artist, size=12, color="#B3B3B3", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Container(expand=True),
                ft.FilledButton(
                    content="Play",
                    icon=ft.Icons.PLAY_ARROW,
                    on_click=play_track,
                    width=float("inf"),
                ),
            ],
            spacing=8,
            expand=True,
        ),
    )
