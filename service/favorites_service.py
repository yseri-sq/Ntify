import json
from pathlib import Path


FAVORITES_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "favorites.json"
)


def get_favorites():
    FAVORITES_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not FAVORITES_FILE.exists():
        return []

    try:
        with FAVORITES_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except (json.JSONDecodeError, OSError):
        return []


def toggle_favorite(track_id):
    favorites = get_favorites()

    if track_id in favorites:
        favorites.remove(track_id)
    else:
        favorites.append(track_id)

    FAVORITES_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with FAVORITES_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            favorites,
            file,
            ensure_ascii=False,
            indent=4,
        )

    return favorites
