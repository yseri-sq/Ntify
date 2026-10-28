import asyncio
import datetime

import flet as ft

from service.youtube_catalog import get_playlist

PLAYLISTS = [
    ("https://www.youtube.com/playlist?list=RDCLAK5uy_kP2172rQNb3KFXz880xp6M98R_ME5CIKA", "Плейлист 1", "https://i.ytimg.com/vi/glEiPXAYE-U/hqdefault.jpg"),
    ("https://www.youtube.com/playlist?list=RDCLAK5uy_kWiJXUNLZM9EyS3GBGznl1ku8_cOos97U", "Плейлист 2", "https://i.ytimg.com/vi/BX0lKSa_PTk/hqdefault.jpg"),
    ("https://www.youtube.com/playlist?list=RDCLAK5uy_nVT2-bFfxplES7OQSLcnwlJqpsQ9gn0yY", "Плейлист 3", "https://i.ytimg.com/vi/mTduyC2zPXg/hqdefault.jpg"),
]


def create_home_page(on_play=None, page=None):
    hour = datetime.datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    header = ft.Text(greeting, size=28, weight=ft.FontWeight.BOLD, color="#FFFFFF")
    playlists_title = ft.Text("Playlists", size=22, weight=ft.FontWeight.BOLD, color="#FFFFFF")

    cards_row = ft.Row(spacing=16, wrap=True, controls=[])

    back_button = ft.TextButton(
        "Back",
        style=ft.ButtonStyle(color="#FFFFFF"),
        visible=False,
    )

    current_playlist_title = ft.Text(
        "",
        size=26,
        weight=ft.FontWeight.BOLD,
        color="#FFFFFF",
        visible=False,
    )

    tracks_list = ft.Column(
        spacing=2,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        visible=False,
    )

    header_row = ft.Row(
        [back_button, current_playlist_title],
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    playlist_header = ft.Container(
        content=header_row,
        visible=False,
        padding=ft.Padding.only(bottom=8),
    )

    content = ft.Column(
        controls=[
            header,
            playlists_title,
            cards_row,
            playlist_header,
            tracks_list,
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    def show_home(e=None):
        cards_row.visible = True
        playlists_title.visible = True
        back_button.visible = False
        current_playlist_title.visible = False
        playlist_header.visible = False
        tracks_list.visible = False
        tracks_list.controls.clear()
        if page is not None:
            page.update()

    async def open_playlist(url, title):
        cards_row.visible = False
        playlists_title.visible = False
        back_button.visible = True
        current_playlist_title.value = title
        current_playlist_title.visible = True
        playlist_header.visible = True
        tracks_list.controls.clear()
        tracks_list.visible = True
        if page is not None:
            page.update()

        videos = await asyncio.to_thread(get_playlist, url)
        if on_play is not None and hasattr(on_play, "__self__"):
            on_play.__self__.set_queue(videos)

        for index, video in enumerate(videos):
            def make_handler(v=video):
                async def handler(e):
                    if on_play is not None:
                        await on_play(v)
                return handler

            tracks_list.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(
                                    str(index + 1),
                                    color="#B3B3B3",
                                    size=14,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                width=40,
                                alignment=ft.Alignment.CENTER,
                            ),
                            ft.Image(
                                src=video["thumbnail"],
                                width=52,
                                height=52,
                                fit=ft.BoxFit.COVER,
                                border_radius=6,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        video["title"],
                                        color="#FFFFFF",
                                        size=14,
                                        weight=ft.FontWeight.W_500,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    ft.Text(
                                        video["channel"],
                                        color="#B3B3B3",
                                        size=12,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                    border_radius=8,
                    bgcolor="#181818",
                    on_click=make_handler(),
                    ink=True,
                    on_hover=lambda e: setattr(e.control, "bgcolor", "#282828" if e.data == "true" else "#181818") or page.update() if page else None,
                )
            )

        if page is not None:
            page.update()

    back_button.on_click = show_home

    for url, title, thumb in PLAYLISTS:
        def make_card(u=url, t=title, th=thumb):
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Image(
                            src=th,
                            width=180,
                            height=110,
                            fit=ft.BoxFit.COVER,
                            border_radius=10,
                        ),
                            ft.Text(
                                t,
                                color="#FFFFFF",
                                weight=ft.FontWeight.BOLD,
                                size=14,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                    ],
                    spacing=8,
                ),
                bgcolor="#232323",
                padding=12,
                border_radius=12,
                width=204,
                on_click=lambda e, u=u, t=t: page.run_task(open_playlist, u, t) if page is not None else None,
                ink=True,
            )

        cards_row.controls.append(make_card())

    return content
