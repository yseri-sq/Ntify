import re

import requests


def get_lyrics(title, artist):
    try:
        clean_title = re.sub(r"\s*[\(\[].*?[\)\]]", "", title)
        clean_title = re.sub(r"\s*-\s*Official.*$", "", clean_title, flags=re.IGNORECASE)
        clean_title = re.sub(r"\s*-\s*Music Video.*$", "", clean_title, flags=re.IGNORECASE)
        clean_title = re.sub(r"\s*-\s*Lyrics.*$", "", clean_title, flags=re.IGNORECASE)
        clean_title = re.sub(r"\s*-\s*Audio.*$", "", clean_title, flags=re.IGNORECASE)
        clean_title = clean_title.strip()

        headers = {
            "User-Agent": "Ntify/1.0",
            "Accept": "application/json",
        }

        response = requests.get(
            "https://lrclib.net/api/search",
            params={
                "track_name": clean_title,
                "artist_name": artist,
            },
            headers=headers,
            timeout=15,
        )

        if response.status_code >= 400:
            response = requests.get(
                "https://lrclib.net/api/search",
                params={
                    "q": f"{clean_title} {artist}",
                },
                headers=headers,
                timeout=15,
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