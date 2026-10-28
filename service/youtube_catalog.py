import yt_dlp


def get_playlist(playlist_url, limit=50):
    options = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True,
        "playlistend": limit,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        result = ydl.extract_info(playlist_url, download=False)

    videos = []
    for item in result.get("entries", []):
        if not item:
            continue
        video_id = item.get("id")
        if not video_id:
            continue
        videos.append({
            "id": video_id,
            "title": item.get("title") or "Unknown title",
            "channel": item.get("channel") or item.get("uploader") or "Unknown channel",
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "thumbnail": item.get("thumbnail") or f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
        })
    return videos


def search_youtube(query, limit=20):
    query = query.strip()

    if not query:
        return []

    options = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True,
        "noplaylist": True,
        "playlistend": limit,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        result = ydl.extract_info(
            f"ytsearch{limit}:{query}",
            download=False,
        )

    videos = []

    for item in result.get("entries", []):
        if not item:
            continue

        video_id = item.get("id")
        if not video_id:
            continue

        videos.append({
            "id": video_id,
            "title": item.get("title") or "Unknown title",
            "channel": (
                item.get("channel")
                or item.get("uploader")
                or "Unknown channel"
            ),
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "thumbnail": (
                item.get("thumbnail")
                or f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
            ),
        })

    return videos
