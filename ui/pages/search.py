import asyncio

import flet as ft

from service.youtube_catalog import search_youtube


def create_search_page(on_play=None):
    search_field = ft.TextField(
        hint_text="Название песни или исполнитель",
        prefix_icon=ft.Icons.SEARCH,
        border=ft.OutlineInputBorder(side=ft.BorderSide(color="#1DB954", width=2)),
        bgcolor="#282828",
        border_color="#282828",
        color="#FFFFFF",
        expand=True,
    )

    results_grid = ft.GridView(
        expand=True,
        max_extent=230,
        child_aspect_ratio=0.95,
        spacing=12,
        run_spacing=12,
        controls=[],
    )

    async def run_search(e=None):
        query = (search_field.value or "").strip()
        results_grid.controls.clear()
        results_grid.update()

        if not query:
            return

        try:
            videos = await asyncio.to_thread(search_youtube, query, 20)

            for video in videos:
                title = video.get("title") or "Без названия"
                channel = video.get("channel") or "YouTube"
                video_id = video.get("id")

                thumbnail = video.get("thumbnail") or ""
                if video_id:
                    thumbnail = (
                        f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg"
                    )

                cover = ft.Image(
                    src=thumbnail,
                    width=190,
                    height=115,
                    fit=ft.BoxFit.COVER,
                    border_radius=8,
                )

                def play_video(e, item=video):
                    if on_play is not None:
                        asyncio.create_task(on_play(item))

                card = ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                content=cover,
                                width=190,
                                height=115,
                                bgcolor="#383838",
                                border_radius=8,
                                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                            ),
                            ft.Text(
                                title,
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color="#FFFFFF",
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        channel,
                                        size=11,
                                        color="#B3B3B3",
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                        expand=True,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.PLAY_CIRCLE_FILLED,
                                        icon_color="#1DB954",
                                        icon_size=32,
                                        tooltip="Воспроизвести",
                                        on_click=play_video,
                                    ),
                                ],
                                spacing=4,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ],
                        spacing=5,
                        tight=True,
                    ),
                    padding=10,
                    bgcolor="#282828",
                    border_radius=12,
                )

                results_grid.controls.append(card)

            results_grid.update()

        except Exception as error:
            print(f"YouTube search error: {error}")

    search_field.on_submit = lambda e: asyncio.create_task(run_search())

    search_button = ft.IconButton(
        icon=ft.Icons.SEARCH,
        icon_color="#121212",
        bgcolor="#1DB954",
        tooltip="Найти музыку",
        on_click=lambda e: asyncio.create_task(run_search()),
    )

    return ft.Column(
        controls=[
            ft.Text(
                "Search",
                size=28,
                weight=ft.FontWeight.BOLD,
                color="#FFFFFF",
            ),
            ft.Row(
                controls=[search_field, search_button],
                spacing=10,
            ),
            results_grid,
        ],
        spacing=16,
        expand=True,
    )
