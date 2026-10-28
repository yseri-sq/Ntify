import json
from pathlib import Path

FAVORITES_FILE = Path(__file__).resolve().parent.parent / "data" / "favorites.json"


def get_favorites():
    FAVORITES_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not FAVORITES_FILE.exists():
        return []
    try:
        with FAVORITES_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            return []
        return [item for item in data if isinstance(item, dict) and item.get("id")]
    except (json.JSONDecodeError, OSError):
        return []


def is_favorite(track_id):
    return any(str(item.get("id")) == str(track_id) for item in get_favorites())


def toggle_favorite(track):
    if isinstance(track, dict):
        track_data = {
            "id": str(track.get("id") or track.get("url") or ""),
            "title": track.get("title") or "Без названия",
            "channel": track.get("channel") or track.get("artist") or "YouTube",
            "url": track.get("url") or "",
            "thumbnail": track.get("thumbnail") or "",
        }
    else:
        track_data = {"id": str(track), "title": "Без названия", "channel": "YouTube", "url": "", "thumbnail": ""}

    if not track_data["id"]:
        return False, get_favorites()

    favorites = get_favorites()
    existing = next((item for item in favorites if str(item.get("id")) == track_data["id"]), None)
    if existing:
        favorites = [item for item in favorites if str(item.get("id")) != track_data["id"]]
        is_liked = False
    else:
        favorites.append(track_data)
        is_liked = True

    FAVORITES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with FAVORITES_FILE.open("w", encoding="utf-8") as file:
        json.dump(favorites, file, ensure_ascii=False, indent=4)
    return is_liked, favorites
