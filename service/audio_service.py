import asyncio

import flet as ft
import flet_audio as fta
import yt_dlp


class AudioService:
    def __init__(
        self,
        page,
        title_text,
        artist_text,
        play_button,
        status_text,
        cover_image,
        progress_slider,
        current_time_text,
        duration_text,
        volume_slider,
        volume_icon,
    ):
        self.page = page

        self.title_text = title_text
        self.artist_text = artist_text
        self.play_button = play_button
        self.status_text = status_text

        self.cover_image = cover_image
        self.progress_slider = progress_slider
        self.current_time_text = current_time_text
        self.duration_text = duration_text
        self.volume_slider = volume_slider
        self.volume_icon = volume_icon

        self.audio = None
        self.current_video = None

        self.is_playing = False
        self.duration_ms = 0
        self.position_ms = 0
        self.volume = 0.8
        self.seeking = False
        self.update_lyrics_position = None
        self.on_track_change = None

        self.queue = []
        self.queue_index = -1

    @staticmethod
    def get_audio_url(video_url):
        options = {
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(video_url, download=False)

        return info["url"]

    @staticmethod
    def format_time(milliseconds):
        total_seconds = max(0, int(milliseconds / 1000))
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"

    def update_play_button(self):
        self.play_button.icon = (
            ft.Icons.PAUSE
            if self.is_playing
            else ft.Icons.PLAY_ARROW
        )

    
    async def play_youtube(self, video):
        self.current_video = dict(video)

        for i, v in enumerate(self.queue):
            if v.get("url") == video.get("url"):
                self.queue_index = i
                break
        else:
            if not self.queue:
                self.queue = [dict(video)]
                self.queue_index = 0

        self.position_ms = 0
        self.duration_ms = 0
        self.progress_slider.max = 1
        self.progress_slider.value = 0
        self.current_time_text.value = "0:00"
        self.duration_text.value = "0:00"
        self.title_text.value = video.get("title", "Без названия")
        self.artist_text.value = video.get("channel", "YouTube")
        if self.on_track_change is not None:
            self.on_track_change(self.current_video)
        self.status_text.value = "Загрузка аудио..."
        self.page.update()

        try:
            audio_url = await asyncio.to_thread(
                self.get_audio_url,
                video["url"],
            )

            if self.audio is not None:
                old_audio = self.audio
                self.audio = None

                try:
                    await old_audio.pause()
                except Exception:
                    pass

                try:
                    await old_audio.release()
                except Exception:
                    pass

                try:
                    self.page.services.remove(old_audio)
                except (ValueError, AttributeError):
                    pass

            self.audio = fta.Audio(
                src=audio_url,
                autoplay=True,
                volume=self.volume,
                on_position_change=self.on_position_change,
                on_duration_change=self.on_duration_change,
                on_state_change=self.on_state_change,
            )

            self.page.services.append(self.audio)

            await self.audio.play()

            self.is_playing = True
            self.status_text.value = "Воспроизведение"
            self.update_play_button()

        except Exception as error:
            self.is_playing = False
            self.status_text.value = "Ошибка запуска аудио"
            self.update_play_button()
            print(f"Audio playback error: {error}")

        self.page.update()


    
    def set_queue(self, videos):
        self.queue = [dict(v) for v in videos]
        self.queue_index = -1

    async def next_track(self):
        if not self.queue or self.queue_index + 1 >= len(self.queue):
            return
        await self.play_youtube(self.queue[self.queue_index + 1])

    async def previous_track(self):
        if not self.queue or self.queue_index - 1 < 0:
            return
        await self.play_youtube(self.queue[self.queue_index - 1])

    async def toggle_playback(self):
        if self.audio is None:
            return

        try:
            if self.is_playing:
                await self.audio.pause()
                self.is_playing = False
                self.status_text.value = "Пауза"
            else:
                await self.audio.resume()
                self.is_playing = True
                self.status_text.value = "Воспроизведение"

            self.update_play_button()
            self.page.update()

        except Exception as error:
            print(f"Toggle playback error: {error}")

    
    async def on_position_change(self, e):
        position = int(e.position)

        if self.duration_ms > 0:
            position = min(position, self.duration_ms)

        self.position_ms = max(0, position)

        if not self.seeking:
            slider_max = max(1, int(self.progress_slider.max or 1))
            self.progress_slider.value = min(
                self.position_ms,
                slider_max,
            )

        self.current_time_text.value = self.format_time(
            self.position_ms
        )

        if self.update_lyrics_position is not None:
            self.update_lyrics_position(self.position_ms)

        self.page.update()


    async def on_duration_change(self, e):
        duration = getattr(e, "duration", None)

        if duration is not None:
            self.duration_ms = max(
                0,
                int(duration.in_milliseconds),
            )

        self.progress_slider.max = max(1, self.duration_ms)

        self.position_ms = min(
            self.position_ms,
            self.duration_ms,
        )
        self.progress_slider.value = min(
            max(0, self.position_ms),
            self.progress_slider.max,
        )

        self.duration_text.value = self.format_time(
            self.duration_ms
        )

        self.page.update()

    async def on_state_change(self, e):
        state = str(getattr(e, "state", "")).lower()

        if "playing" in state:
            self.is_playing = True
        elif "paused" in state or "stopped" in state:
            self.is_playing = False

        self.update_play_button()
        self.page.update()

    
    async def seek(self, e):
        if self.audio is None or self.duration_ms <= 0:
            return

        position = int(e.control.value)

        try:
            await self.audio.seek(
                ft.Duration(milliseconds=position)
            )
            self.position_ms = position
            self.current_time_text.value = self.format_time(position)
            self.page.update()
        except Exception as error:
            print(f"Seek error: {error}")


    def change_volume(self, e):
        self.volume = float(e.control.value)

        if self.audio is not None:
            self.audio.volume = self.volume
            self.audio.update()

        if self.volume == 0:
            self.volume_icon.icon = ft.Icons.VOLUME_OFF
        elif self.volume < 0.5:
            self.volume_icon.icon = ft.Icons.VOLUME_DOWN
        else:
            self.volume_icon.icon = ft.Icons.VOLUME_UP

        self.page.update()

    
    async def play_podcast_episode(self, episode):
        self.current_video = {
            "title": episode.get("title", "Подкаст"),
            "channel": episode.get("author", "Подкасты"),
            "url": episode["url"],
        }
        self.title_text.value = episode.get("title", "Подкаст")
        self.artist_text.value = episode.get("author", "Подкасты")
        if self.on_track_change is not None:
            self.on_track_change(self.current_video)
        self.status_text.value = "Загрузка выпуска..."
        self.position_ms = 0
        self.duration_ms = 0
        self.progress_slider.max = 1
        self.progress_slider.value = 0
        self.current_time_text.value = "0:00"
        self.duration_text.value = "0:00"
        self.page.update()

        try:
            if self.audio is not None:
                old_audio = self.audio
                self.audio = None

                try:
                    await old_audio.pause()
                except Exception:
                    pass

                try:
                    await old_audio.release()
                except Exception:
                    pass

                try:
                    self.page.services.remove(old_audio)
                except (ValueError, AttributeError):
                    pass

            self.audio = fta.Audio(
                src=episode["url"],
                autoplay=True,
                volume=self.volume,
                on_position_change=self.on_position_change,
                on_duration_change=self.on_duration_change,
                on_state_change=self.on_state_change,
            )

            self.page.services.append(self.audio)
            await self.audio.play()

            self.is_playing = True
            self.status_text.value = "Воспроизведение подкаста"
            self.update_play_button()

        except Exception as error:
            self.is_playing = False
            self.status_text.value = "Ошибка запуска выпуска"
            self.update_play_button()
            print(f"Podcast playback error: {error}")

        self.page.update()