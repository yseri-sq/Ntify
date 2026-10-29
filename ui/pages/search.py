import asyncio

import flet as ft

from service.youtube_catalog import search_youtube


def create_search_page(page: ft.Page, on_play=None):
    def on_search_focus(e):
        page.data = "search_focused"

    def on_search_blur(e):
        page.data = None

    search_field = ft.TextField(
        hint_text="Название песни или исполнитель",
        prefix_icon=ft.Icons.SEARCH,
        bgcolor="#282828",
        color="#FFFFFF",
        border_radius=12,
        border_color="#404040",
        focused_border_color="#1DB954",
        expand=True,
        on_focus=on_search_focus,
        on_blur=on_search_blur,
    )

    results_grid = ft.GridView(
        expand=True,
        max_extent=180,
        child_aspect_ratio=0.75,
        spacing=12,
        run_spacing=12,
        padding=8,
        controls=[],
    )

    status_text = ft.Text(
        "",
        size=13,
        color="#B3B3B3",
    )

    async def run_search(e=None):
        query = (search_field.value or "").strip()

        results_grid.controls.clear()
        status_text.value = ""

        if not query:
            status_text.value = "Введи название песни или исполнителя."
            page.update()
            return

        status_text.value = "Ищем музыку..."
        page.update()

        try:
            videos = await asyncio.to_thread(search_youtube, query, 20)

            if not videos:
                status_text.value = "Ничего не найдено."
                page.update()
                return

            for video in videos:
                title = video.get("title") or "Без названия"
                channel = video.get("channel") or "YouTube"
                video_id = video.get("id")

                thumbnail = video.get("thumbnail") or ""
                if video_id:
                    thumbnail = (
                        f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
                    )

                def play_video(e, item=video):
                    if on_play is not None:
                        asyncio.create_task(on_play(item))

                cover = ft.Container(
                    height=145,
                    width=float("inf"),
                    bgcolor="#383838",
                    border_radius=8,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    content=(
                        ft.Image(
                            src=thumbnail,
                            fit=ft.BoxFit.COVER,
                            width=float("inf"),
                            height=145,
                            error_content=ft.Icon(
                                ft.Icons.MUSIC_NOTE,
                                size=42,
                                color="#B3B3B3",
                            ),
                        )
                        if thumbnail
                        else ft.Icon(
                            ft.Icons.MUSIC_NOTE,
                            size=42,
                            color="#B3B3B3",
                        )
                    ),
                )

                card = ft.Container(
                    expand=True,
                    padding=10,
                    bgcolor="#181818",
                    border_radius=16,
                    shadow=ft.BoxShadow(blur_radius=12, color="#00000055"),
                    on_click=play_video,
                    ink=True,
                    content=ft.Column(
                        expand=True,
                        spacing=8,
                        controls=[
                            ft.Container(
                                height=110,
                                width=float("inf"),
                                bgcolor="#282828",
                                border_radius=8,
                                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                                content=(
                                    ft.Image(
                                        src=thumbnail,
                                        width=float("inf"),
                                        height=110,
                                        fit=ft.BoxFit.COVER,
                                    )
                                    if thumbnail
                                    else ft.Icon(
                                        ft.Icons.MUSIC_NOTE,
                                        size=42,
                                        color="#B3B3B3",
                                    )
                                ),
                            ),

                            ft.Container(
                                height=38,
                                alignment=ft.Alignment.TOP_LEFT,
                                content=ft.Text(
                                    title,
                                    size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color="#FFFFFF",
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ),

                            ft.Container(
                                height=18,
                                alignment=ft.Alignment.TOP_LEFT,
                                content=ft.Text(
                                    channel,
                                    size=11,
                                    color="#B3B3B3",
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ),

                            ft.Container(expand=True),
                        ],
                    ),
                )

                results_grid.controls.append(card)

            status_text.value = f"Найдено треков: {len(videos)}"
            page.update()

        except Exception as error:
            status_text.value = "Не удалось выполнить поиск."
            print(f"YouTube search error: {error}")
            page.update()

    async def submit_search(e):
        await run_search()

    search_field.on_submit = submit_search

    search_button = ft.IconButton(
        icon=ft.Icons.SEARCH,
        icon_color="#121212",
        bgcolor="#1DB954",
        tooltip="Найти музыку",
        on_click=submit_search,
    )

    return ft.Column(
        expand=True,
        spacing=18,
        controls=[
            ft.Text(
                "Поиск",
                size=28,
                weight=ft.FontWeight.BOLD,
                color="#FFFFFF",
            ),
            ft.Row(
                controls=[search_field, search_button],
                spacing=10,
            ),
            status_text,
            results_grid,
        ],
    )
