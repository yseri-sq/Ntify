import asyncio

import flet as ft

from service.podcast_service import (get_podcast_feed_url, get_saved_feeds,
                                     parse_rss_feed, remove_feed, save_feed,
                                     search_podcasts)

GREEN = "#1DB954"
BG = "#181818"
CARD = "#242424"
MUTED = "#B3B3B3"


def create_podcasts_page(on_play, page=None):
    page_ref = {"value": page}
    search_field = ft.TextField(
            hint_text="Название песни или исполнитель",
            prefix_icon=ft.Icons.SEARCH,
            bgcolor="#282828",
            color="#FFFFFF",
            border_radius=12,
            border_color="#404040",
            focused_border_color="#1DB954",
            expand=True,
        )

    rss_field = ft.TextField(
        hint_text="https://example.com/podcast.rss",
        prefix_icon=ft.Icons.LINK,
        border=ft.OutlineInputBorder(side=ft.BorderSide(color=GREEN, width=2)),
        bgcolor=CARD,
        border_color="transparent",
        expand=True,
    )

    message = ft.Text("", color=MUTED, size=13)

    catalog_grid = ft.ResponsiveRow(
        columns=12,
        spacing=12,
        run_spacing=12,
    )

    episode_column = ft.Column(
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    saved_column = ft.Column(
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
    )

    selected_podcast = {"value": None}
    page_ref = {"value": page}

    def show_message(text, color=MUTED):
        message.value = text
        message.color = color

        if page_ref["value"] is not None:
            page_ref["value"].update()

    def podcast_card(podcast):
        image_url = podcast.get("image", "")
        title = podcast.get("title", "Без названия")
        author = podcast.get("author", "Неизвестный автор")

        cover = ft.Container(
            height=160,
            bgcolor="#303030",
            border_radius=10,
            alignment=ft.Alignment.CENTER,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            content=(
                ft.Image(
                    src=image_url,
                    fit=ft.BoxFit.COVER,
                    expand=True,
                )
                if image_url
                else ft.Icon(ft.Icons.PODCASTS, size=48, color=GREEN)
            ),
        )

        return ft.Container(
            col={"sm": 6, "md": 4, "lg": 3, "xl": 3},
            content=ft.Container(
                on_click=lambda e, item=podcast: page_ref["value"].run_task(
                                                open_podcast, item
                                            ),
                ink=True,
                height=285,
                content=ft.Column(
                    controls=[
                        cover,
                        ft.Text(
                            title,
                            color="#FFFFFF",
                            weight=ft.FontWeight.BOLD,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Text(
                            author,
                            color=MUTED,
                            size=12,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Container(expand=True),
                    ],
                    spacing=8,
                    expand=True,
                ),
                bgcolor=CARD,
                padding=12,
                border_radius=12,
            ),
        )

    def episode_row(episode):
        title = episode.get("title", "Выпуск без названия")
        author = episode.get("author", "")
        date = episode.get("date", "")
        duration = episode.get("duration", "")

        details = " · ".join(
            value for value in [author, date, duration] if value
        )

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.HEADPHONES,
                        color=GREEN,
                        size=28,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                title,
                                color="#FFFFFF",
                                weight=ft.FontWeight.BOLD,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                details or "Подкаст",
                                color=MUTED,
                                size=12,
                            ),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.PLAY_CIRCLE_FILLED,
                        icon_color=GREEN,
                        icon_size=34,
                        tooltip="Воспроизвести выпуск",
                        on_click=lambda e, item=episode: play_episode(item),
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=CARD,
            padding=12,
            border_radius=10,
        )

    def play_episode(episode):
        try:
            page_ref["value"].run_task(
                on_play,
                episode,
            )
            show_message(
                f"Воспроизведение: {episode.get('title', 'Без названия')}",
                GREEN,
            )
        except Exception as error:
            show_message(
                f"Ошибка воспроизведения: {error}",
                "#FF5555",
            )

    async def open_podcast(podcast):
        feed_url = podcast.get("feed_url", "")

        if not feed_url and podcast.get("id"):
            show_message("Получаем RSS-ссылку из каталога...")
            try:
                feed_url = await asyncio.to_thread(
                    get_podcast_feed_url,
                    podcast["id"],
                )
            except Exception as error:
                show_message(f"Ошибка каталога: {error}", "#FF7777")
                return

        if not feed_url:
            show_message(
                "У этой передачи нет доступной RSS-ссылки.",
                "#FF7777",
            )
            return

        await load_feed(feed_url)

    async def load_feed(feed_url):
        show_message("Загружаем выпуски...")
        episode_column.controls.clear()
        if page_ref["value"] is not None:
            page_ref["value"].update()

        try:
            podcast = await asyncio.to_thread(
                parse_rss_feed,
                feed_url,
            )
        except Exception as error:
            show_message(f"Не удалось загрузить RSS: {error}", "#FF7777")
            return

        selected_podcast["value"] = podcast

        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_color=GREEN,
                        tooltip="Назад к каталогу",
                        on_click=lambda e: show_catalog(),
                    ),
                    ft.Text(
                        "Выпуски",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color="#FFFFFF",
                    ),
                ],
            ),
        )

        episode_column.controls.extend([
            header,
            ft.Text(
                podcast["title"],
                size=24,
                weight=ft.FontWeight.BOLD,
                color="#FFFFFF",
            ),
            ft.Text(
                podcast.get("description", ""),
                color=MUTED,
                size=13,
            ),
            ft.Divider(color="#333333"),
        ])

        if not podcast["episodes"]:
            episode_column.controls.append(
                ft.Text(
                    "В этой RSS-ленте не найдено аудиовыпусков.",
                    color=MUTED,
                )
            )
        else:
            for episode in podcast["episodes"]:
                episode_column.controls.append(episode_row(episode))

        show_message(
            f"Загружено выпусков: {len(podcast['episodes'])}",
            GREEN,
        )
        show_catalog(show_episodes=True)

    def show_catalog(show_episodes=False):
        content_column.controls.clear()

        if show_episodes:
            content_column.controls.append(episode_column)
        else:
            content_column.controls.extend([
                ft.Text(
                    "Подкасты",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color="#FFFFFF",
                ),
                ft.Text(
                    "Найди передачу или добавь свою RSS-ленту.",
                    color=MUTED,
                ),
                ft.Row(
                    controls=[
                        search_field,
                        ft.IconButton(
                            icon=ft.Icons.SEARCH,
                            icon_color=GREEN,
                            tooltip="Искать",
                            on_click=lambda e: page_ref["value"].run_task(
                                search_catalog, e
                            ),
                        ),
                    ],
                ),
                ft.Row(
                    controls=[
                        rss_field,
                        ft.Button(
                            "Добавить RSS",
                            icon=ft.Icons.ADD,
                            on_click=lambda e: page_ref["value"].run_task(
                                add_rss, e
                            ),
                            style=ft.ButtonStyle(
                                bgcolor=GREEN,
                                color="#000000",
                            ),
                        ),
                    ],
                ),
                message,
                ft.Text(
                    "Каталог",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="#FFFFFF",
                ),
                catalog_grid,
                ft.Divider(color="#333333"),
                ft.Text(
                    "Мои RSS-подкасты",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="#FFFFFF",
                ),
                saved_column,
            ])
            refresh_saved_feeds()

        if page_ref["value"] is not None:
            page_ref["value"].update()

    async def search_catalog(e=None):
        query = (search_field.value or "").strip()

        if not query:
            show_message("Введи название подкаста.")
            return

        catalog_grid.controls.clear()
        show_message("Ищем подкасты...")
        if page_ref["value"] is not None:
            page_ref["value"].update()

        try:
            results = await asyncio.to_thread(search_podcasts, query)
        except Exception as error:
            show_message(f"Ошибка поиска: {error}", "#FF7777")
            return

        for podcast in results:
            catalog_grid.controls.append(podcast_card(podcast))

        show_message(f"Найдено подкастов: {len(results)}", GREEN)
        if page_ref["value"] is not None:
            page_ref["value"].update()

    async def add_rss(e=None):
        feed_url = (rss_field.value or "").strip()

        if not feed_url:
            show_message("Вставь RSS-ссылку.")
            return

        show_message("Проверяем RSS-ленту...")
        if page_ref["value"] is not None:
            page_ref["value"].update()

        try:
            podcast = await asyncio.to_thread(save_feed, feed_url)
        except Exception as error:
            show_message(f"Не удалось добавить RSS: {error}", "#FF7777")
            return

        rss_field.value = ""
        refresh_saved_feeds()

        show_message(f"Добавлен подкаст: {podcast['title']}", GREEN)
        await load_feed(feed_url)

    def refresh_saved_feeds():
        saved_column.controls.clear()
        feeds = get_saved_feeds()

        if not feeds:
            saved_column.controls.append(
                ft.Text(
                    "Пока нет сохранённых RSS-подкастов.",
                    color=MUTED,
                )
            )
            return

        for feed in feeds:
            saved_column.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.PODCASTS,
                                color=GREEN,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        feed.get("title", "Подкаст"),
                                        color="#FFFFFF",
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        feed.get("author", ""),
                                        color=MUTED,
                                        size=12,
                                    ),
                                ],
                                expand=True,
                                spacing=3,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.PLAY_ARROW,
                                icon_color=GREEN,
                                tooltip="Открыть выпуски",
                                on_click=lambda e, item=feed: page_ref["value"].run_task(
                                    load_feed,
                                    item["feed_url"],
                                ),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=MUTED,
                                tooltip="Удалить RSS",
                                on_click=lambda e, item=feed: page_ref["value"].run_task(
                                    delete_rss, item
                                ),
                            ),
                        ],
                    ),
                    bgcolor=CARD,
                    padding=10,
                    border_radius=10,
                )
            )

    async def delete_rss(feed):
        try:
            await asyncio.to_thread(remove_feed, feed["feed_url"])
            refresh_saved_feeds()
            show_message("RSS-подкаст удалён.", GREEN)
        except Exception as error:
            show_message(f"Ошибка удаления: {error}", "#FF7777")

    content_column = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=16,
    )

    page = ft.Container(
        content=content_column,
        expand=True,
    )

    show_catalog()

    return page