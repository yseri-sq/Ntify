import asyncio
import flet as ft

from service.favorites_service import get_favorites, toggle_favorite

GREEN = "#1DB954"
MUTED = "#B3B3B3"


def create_liked_page(on_play=None, page=None):
    tracks_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    page_ref = {"value": page}

    def refresh():
        tracks_column.controls.clear()
        favorites = get_favorites()
        if not favorites:
            tracks_column.controls.append(ft.Text("Пока нет избранных песен. Нажми ♥ у трека в плеере или поиске.", color=MUTED, size=14))
            return
        for track in favorites:
            tracks_column.controls.append(track_row(track))

    def track_row(track):
        image_url = track.get("thumbnail", "")
        cover = ft.Container(
            width=56, height=56, bgcolor="#303030", border_radius=6,
            alignment=ft.Alignment.CENTER,
            content=ft.Image(src=image_url, width=56, height=56, fit=ft.BoxFit.COVER, border_radius=6) if image_url else ft.Icon(ft.Icons.MUSIC_NOTE, color=GREEN, size=28),
        )
        def play(e):
            if on_play:
                if page_ref["value"]:
                    page_ref["value"].run_task(on_play, track)
                else:
                    asyncio.create_task(on_play(track))
        def remove(e):
            toggle_favorite(track)
            refresh()
            if page_ref["value"]:
                page_ref["value"].update()
        return ft.Container(
            content=ft.Row([
                cover,
                ft.Column([
                    ft.Text(track.get("title", "Без названия"), color="#FFFFFF", weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(track.get("channel", "YouTube"), color=MUTED, size=12, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ], spacing=4, expand=True),
                ft.IconButton(icon=ft.Icons.PLAY_ARROW, icon_color=GREEN, tooltip="Воспроизвести", on_click=play),
                ft.IconButton(icon=ft.Icons.FAVORITE, icon_color=GREEN, tooltip="Убрать из избранного", on_click=remove),
            ], spacing=12),
            padding=10, bgcolor="#282828", border_radius=8,
        )

    refresh()
    return ft.Column(
        controls=[
            ft.Row([ft.Icon(ft.Icons.FAVORITE, size=36, color=GREEN), ft.Text("Liked songs", size=28, weight=ft.FontWeight.BOLD, color="#FFFFFF")], spacing=12),
            tracks_column,
        ],
        spacing=16, expand=True,
    )
