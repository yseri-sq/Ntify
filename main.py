import flet as ft

from ui.layout import create_layout
from ui.pages.home import create_home_page
from ui.pages.liked import create_liked_page
from ui.pages.podcasts import create_podcasts_page
from ui.pages.search import create_search_page
from ui.player_bar import create_player_bar
from ui.sidebar import create_sidebar


def main(page: ft.Page):
    page.title = "Ntify"
    page.window.width = 1520
    page.window.height = 870
    page.window.min_width = 1250
    page.window.min_height = 750
    page.bgcolor = "#121212"

    sidebar_width = 220
    sidebar_compact = False

    page_builders = {
        "Home": create_home_page,
        "Search": lambda: create_search_page(
            page=page,
            on_play=audio_service.play_youtube,
        ),
        "Like": lambda: create_liked_page(
            on_play=audio_service.play_youtube,
            page=page,
        ),
        "Podcasts": lambda: create_podcasts_page(
            on_play=audio_service.play_podcast_episode,
            page=page,
        ),
    }

    page_content = ft.Container(
        content=create_home_page(),
        expand=True,
        padding=24,
        border_radius=12,
        bgcolor="#181818",
        animate=200,
    )

    def navigate(page_name):
        builder = page_builders.get(page_name)

        if builder is not None:
            page_content.content = builder()
            page.update()

    sidebar = create_sidebar(
        width=sidebar_width,
        compact=sidebar_compact,
        on_navigate=navigate,
    )

    drag = {
        "start_width": sidebar_width,
        "start_compact": sidebar_compact,
        "x": 0,
    }

    def resize_start(e):
        drag["start_width"] = sidebar_width
        drag["start_compact"] = sidebar_compact
        drag["x"] = 0

    def resize_sidebar(e):
        nonlocal sidebar_width, sidebar_compact

        was_compact = sidebar_compact

        drag["x"] += e.local_delta.x
        x = drag["x"]

        if drag["start_compact"]:
            if x < 45:
                return

            sidebar_compact = False
            sidebar_width = max(180, min(360, 72 + x))
        else:
            new_width = drag["start_width"] + x

            if new_width < 150:
                sidebar_compact = True
                sidebar_width = 72
            else:
                sidebar_compact = False
                sidebar_width = max(180, min(360, new_width))

        if sidebar_compact != was_compact:
            updated_sidebar = create_sidebar(
                width=sidebar_width,
                compact=sidebar_compact,
                on_navigate=navigate,
            )
            sidebar.content = updated_sidebar.content

        sidebar.width = sidebar_width
        sidebar.padding = 8 if sidebar_compact else 16

        page.update()

    resize_handle = ft.GestureDetector(
        content=ft.Container(
            width=6,
            bgcolor="#333333",
            border_radius=3,
        ),
        on_pan_start=resize_start,
        on_pan_update=resize_sidebar,
    )

    player_bar, audio_service, lyrics_panel = create_player_bar(page)

    content = create_layout(
        sidebar,
        resize_handle,
        page_content,
        player_bar,
        lyrics_panel,
    )


    async def handle_keyboard(e: ft.KeyboardEvent):
        key = (e.key or "").strip().lower()

        if key not in ("space", "spacebar", ""):
            return

        if not (e.key or "").isspace() and key == "":
            return

        if getattr(page, "data", None) == "search_focused":
            return

        if audio_service.audio is None:
            return

        await audio_service.toggle_playback()


    page.on_keyboard_event = handle_keyboard


    page.add(content)


ft.run(main=main)
