import requests


def get_lyrics(title, artist):
    try:
        response = requests.get(
            "https://lrclib.net/api/search",
            params={
                "track_name": title,
                "artist_name": artist,
            },
            headers={
                "User-Agent": "Ntify/1.0"
            },
            timeout=10,
        )

        response.raise_for_status()
        results = response.json()

        if not results:
            return None

        for item in results:
            if item.get("syncedLyrics"):
                return item

        for item in results:
            if item.get("plainLyrics"):
                return item

        return None

    except Exception as error:
        print(f"LRCLIB error: {error}")
        return None
