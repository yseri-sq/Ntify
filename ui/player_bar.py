import asyncio
import re

import flet as ft

from service.audio_service import AudioService
from service.lyrics_service import get_lyrics


def create_player_bar(page):
    cover_image = ft.Container(
        content=ft.Icon(
            ft.Icons.MUSIC_NOTE,
            size=30,
            color="#1DB954",
        ),
        width=58,
        height=58,
        bgcolor="#282828",
        border_radius=8,
        alignment=ft.Alignment.CENTER,
    )

    title_text = ft.Text(
        "Ничего не воспроизводится",
        color="#FFFFFF",
        weight=ft.FontWeight.BOLD,
        max_lines=1,
        overflow=ft.TextOverflow.ELLIPSIS,
    )

    artist_text = ft.Text(
        "Выбери музыку в поиске",
        color="#B3B3B3",
        size=12,
        max_lines=1,
        overflow=ft.TextOverflow.ELLIPSIS,
    )

    status_text = ft.Text(
        "",
        color="#B3B3B3",
        size=10,
    )

    # Управление воспроизведением
    play_button = ft.IconButton(
        icon=ft.Icons.PLAY_ARROW,
        icon_color="#FFFFFF",
        icon_size=30,
        tooltip="Воспроизведение / пауза",
    )

    previous_button = ft.IconButton(
        icon=ft.Icons.SKIP_PREVIOUS,
        icon_color="#B3B3B3",
        tooltip="Предыдущий трек",
        on_click=lambda e: None,
    )

    next_button = ft.IconButton(
        icon=ft.Icons.SKIP_NEXT,
        icon_color="#B3B3B3",
        tooltip="Следующий трек",
        on_click=lambda e: None,
    )

    current_time_text = ft.Text(
        "0:00",
        color="#B3B3B3",
        size=10,
    )

    duration_text = ft.Text(
        "0:00",
        color="#B3B3B3",
        size=10,
    )

    progress_slider = ft.Slider(
        min=0,
        max=1,
        value=0,
        active_color="#1DB954",
        inactive_color="#535353",
        thumb_color="#FFFFFF",
        expand=True,
    )

    volume_icon = ft.Icon(
        icon=ft.Icons.VOLUME_UP,
        color="#B3B3B3",
        size=20,
    )

    volume_slider = ft.Slider(
        min=0,
        max=1,
        value=0.8,
        divisions=20,
        active_color="#1DB954",
        inactive_color="#535353",
        thumb_color="#FFFFFF",
        width=170,
    )

    lyrics_button = ft.IconButton(
        icon=ft.Icons.LYRICS_SHARP,
        icon_color="#B3B3B3",
        tooltip="Показать текст песни",
    )

    lyrics_status = ft.Text(
        "Включи песню и нажми кнопку текста",
        color="#B3B3B3",
        size=14,
        text_align=ft.TextAlign.CENTER,
    )
    
    lyrics_column = ft.Column(
        controls=[lyrics_status],
        scroll=ft.ScrollMode.HIDDEN,
        auto_scroll=False,
        expand=True,
        spacing=12,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    like_button = ft.IconButton(
        icon=ft.Icons.FAVORITE_BORDER,
        icon_color="#B3B3B3",
        tooltip="Добавить в избранное",
        on_click=lambda e: None,
    )

    lyrics_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            "Lyrics",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color="#FFFFFF",
                            expand=True,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_color="#B3B3B3",
                            tooltip="Hiden lyrics",
                            on_click=lambda e: toggle_lyrics_panel(),
                        ),
                    ],
                ),
                lyrics_column,
            ],
            spacing=16,
            expand=True,
        ),
        bgcolor="#181818",
        padding=16,
        border_radius=12,
        width=320,
        expand=False,
        visible=False,
    )

    def toggle_lyrics_panel(e=None):
        lyrics_panel.visible = not lyrics_panel.visible
        page.update()


    lyrics_data = {
        "lines": [],
        "controls": [],
        "active_index": -1,
        "synced": False,
        "loaded_for": None,
    }

    def parse_lrc(text):
        parsed_lines = []

        for line in text.splitlines():
            timestamps = re.findall(
                r"\[(\d{2}):(\d{2}(?:\.\d{1,3})?)\]",
                line,
            )

            lyric_text = re.sub(
                r"\[\d{2}:\d{2}(?:\.\d{1,3})?\]",
                "",
                line,
            ).strip()

            for minute, second in timestamps:
                timestamp_ms = (
                    int(minute) * 60_000
                    + int(float(second) * 1000)
                )

                parsed_lines.append((timestamp_ms, lyric_text))

        return sorted(parsed_lines, key=lambda item: item[0])

    
    async def scroll_to_lyrics_line(index):
        offset = max(0, index * 44 - 100)

        await lyrics_column.scroll_to(
            offset=offset,
            duration=300,
        )


    def update_lyrics_position(position_ms):
        if not lyrics_data["synced"]:
            return

        lines = lyrics_data["lines"]
        controls = lyrics_data["controls"]

        if not lines or not controls:
            return

        active_index = -1

        for index, (timestamp, _) in enumerate(lines):
            if timestamp <= position_ms:
                active_index = index
            else:
                break

        
        if active_index >= 0 and lyrics_panel.visible:
            page.run_task(scroll_to_lyrics_line, active_index)

        if lyrics_panel.visible:
            page.update()


        lyrics_data["active_index"] = active_index

        for index, control in enumerate(controls):
            if index == active_index:
                control.color = "#1DB954"
                control.weight = ft.FontWeight.BOLD
                control.size = 21
            else:
                control.color = "#B3B3B3"
                control.weight = ft.FontWeight.NORMAL
                control.size = 18

        if lyrics_panel.visible:
            page.update()

    async def show_lyrics(e=None):
        if not lyrics_panel.visible:
            lyrics_panel.visible = True
            page.update()
        else:
            lyrics_panel.visible = False
            page.update()
            return

        current_track = (
            title_text.value,
            artist_text.value,
        )

        if current_track == lyrics_data["loaded_for"]:
            page.update()
            return

        lyrics_data["loaded_for"] = current_track
        lyrics_data["lines"] = []
        lyrics_data["controls"] = []
        lyrics_data["active_index"] = -1
        lyrics_data["synced"] = False

        lyrics_status.value = "Ищем текст песни в LRCLIB..."
        lyrics_column.controls = [lyrics_status]
        page.update()

        item = await asyncio.to_thread(
            get_lyrics,
            title_text.value,
            artist_text.value,
        )

        if current_track != (
            title_text.value,
            artist_text.value,
        ):
            lyrics_data["loaded_for"] = None
            return

        lyrics_column.controls.clear()

        if not item:
            lyrics_column.controls.append(
                ft.Text(
                    "Текст не найден.",
                    color="#B3B3B3",
                    size=16,
                    text_align=ft.TextAlign.CENTER,
                )
            )
            page.update()
            return

        synced_text = item.get("syncedLyrics") or ""
        plain_text = item.get("plainLyrics") or ""

        if synced_text:
            lyrics_data["lines"] = parse_lrc(synced_text)
            lyrics_data["synced"] = bool(lyrics_data["lines"])

        if not lyrics_data["lines"] and plain_text:
            lyrics_data["lines"] = [
                (0, line)
                for line in plain_text.splitlines()
            ]
            lyrics_data["synced"] = False

        if not lyrics_data["lines"]:
            lyrics_column.controls.append(
                ft.Text(
                    "У этой песни нет доступного текста.",
                    color="#B3B3B3",
                    size=16,
                )
            )
            page.update()
            return

        for _, lyric_line in lyrics_data["lines"]:
            lyric_control = ft.Text(
                lyric_line or "♪",
                color="#B3B3B3",
                size=18,
                text_align=ft.TextAlign.CENTER,
            )

            lyrics_data["controls"].append(lyric_control)
            lyrics_column.controls.append(lyric_control)

        if lyrics_data["synced"]:
            update_lyrics_position(audio_service.position_ms)

        page.update()

    lyrics_button.on_click = show_lyrics

    audio_service = AudioService(
        page=page,
        title_text=title_text,
        artist_text=artist_text,
        play_button=play_button,
        status_text=status_text,
        cover_image=cover_image,
        progress_slider=progress_slider,
        current_time_text=current_time_text,
        duration_text=duration_text,
        volume_slider=volume_slider,
        volume_icon=volume_icon,
    )

    audio_service.update_lyrics_position = update_lyrics_position

    play_button.on_click = audio_service.toggle_playback
    progress_slider.on_change_end = audio_service.seek
    volume_slider.on_change = audio_service.change_volume

    track_info = ft.Row(
        controls=[
            cover_image,
            ft.Column(
                controls=[
                    title_text,
                    artist_text,
                    # like_button,
                ],
                spacing=3,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
            ),
        ],
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Центральная часть: кнопки и прогресс
    playback_controls = ft.Row(
        controls=[
            previous_button,
            play_button,
            next_button,
        ],
        spacing=4,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    progress_row = ft.Row(
        controls=[
            current_time_text,
            progress_slider,
            duration_text,
        ],
        spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    center_controls = ft.Column(
        controls=[
            playback_controls,
            progress_row,
        ],
        spacing=0,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )

    volume_controls = ft.Row(
        controls=[
            lyrics_button,
            volume_icon,
            volume_slider,
        ],
        spacing=8,
        alignment=ft.MainAxisAlignment.END,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Панель текста находится над нижним плеером.
    
    
    player_bar = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=track_info,
                    width=250,
                    expand=False,
                ),
                ft.Container(
                    content=center_controls,
                    expand=True,
                ),
                ft.Container(
                    content=volume_controls,
                    width=250,
                    expand=False,
                ),
            ],
            spacing=8,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor="#181818",
        padding=10,
        border_radius=12,
        expand=False,
    )

    return player_bar, audio_service, lyrics_panel

