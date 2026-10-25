
import json
import os
import re
import xml.etree.ElementTree as ET

from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import urlencode

import requests


CATALOG_URL = "https://itunes.apple.com/search"
LOOKUP_URL = "https://itunes.apple.com/lookup"

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
)
RSS_FILE = os.path.join(DATA_DIR, "podcast_feeds.json")

HEADERS = {
    "User-Agent": "Ntify/1.0 podcast reader",
}


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def search_podcasts(query):
    """Ищет подкасты в публичном каталоге Apple Podcasts."""
    query = query.strip()

    if not query:
        return []

    response = requests.get(
        CATALOG_URL,
        params={
            "term": query,
            "entity": "podcast",
            "limit": 25,
            "media": "podcast",
        },
        headers=HEADERS,
        timeout=15,
    )
    response.raise_for_status()

    results = []

    for item in response.json().get("results", []):
        results.append({
            "id": str(item.get("collectionId", "")),
            "title": item.get("collectionName", "Без названия"),
            "author": item.get("artistName", "Неизвестный автор"),
            "image": item.get("artworkUrl600")
            or item.get("artworkUrl100")
            or "",
            "feed_url": item.get("feedUrl", ""),
            "description": "",
        })

    return results


def _local_name(tag):
    """Убирает XML namespace из имени тега."""
    return tag.rsplit("}", 1)[-1].lower()


def _child_text(element, name):
    for child in element:
        if _local_name(child.tag) == name.lower():
            return (child.text or "").strip()

    return ""


def _child_attribute(element, name, attribute):
    for child in element:
        if _local_name(child.tag) == name.lower():
            return child.attrib.get(attribute, "")

    return ""


def _format_date(value):
    if not value:
        return ""

    try:
        parsed = parsedate_to_datetime(value)
        return parsed.strftime("%d.%m.%Y")
    except (TypeError, ValueError, OverflowError):
        return value


def _format_duration(value):
    if not value:
        return ""

    value = str(value).strip()

    # RSS может указывать длительность в секундах.
    if value.isdigit():
        total_seconds = int(value)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"

        return f"{minutes}:{seconds:02d}"

    return value


def parse_rss_feed(feed_url):
    """Загружает сведения о подкасте и его выпусках из RSS."""
    response = requests.get(
        feed_url,
        headers=HEADERS,
        timeout=20,
    )
    response.raise_for_status()

    if len(response.content) > 15 * 1024 * 1024:
        raise ValueError("RSS-файл слишком большой.")

    root = ET.fromstring(response.content)

    channel = root

    if _local_name(root.tag) != "channel":
        for element in root.iter():
            if _local_name(element.tag) == "channel":
                channel = element
                break

    title = _child_text(channel, "title") or "Подкаст"
    author = (
        _child_text(channel, "author")
        or _child_text(channel, "creator")
        or "Неизвестный автор"
    )
    description = _child_text(channel, "description")
    image = _child_attribute(channel, "image", "href")

    # В классическом RSS обложка обычно находится внутри <image><url>.
    if not image:
        for element in channel.iter():
            if _local_name(element.tag) == "image":
                image = _child_text(element, "url")
                if image:
                    break

    episodes = []

    for item in channel:
        if _local_name(item.tag) not in ("item", "entry"):
            continue

        episode_title = (
            _child_text(item, "title") or "Выпуск без названия"
        )

        audio_url = _child_attribute(item, "enclosure", "url")

        # Некоторые RSS-ленты используют media:content.
        if not audio_url:
            audio_url = _child_attribute(item, "content", "url")

        if not audio_url:
            continue

        duration = (
            _child_text(item, "duration")
            or _child_text(item, "itunes:duration")
        )

        pub_date = (
            _child_text(item, "pubdate")
            or _child_text(item, "published")
            or _child_text(item, "updated")
        )

        episode_image = (
            _child_attribute(item, "image", "href")
            or image
        )

        episodes.append({
            "title": episode_title,
            "author": author,
            "description": (
                _child_text(item, "description")
                or _child_text(item, "summary")
            ),
            "url": audio_url,
            "date": _format_date(pub_date),
            "duration": _format_duration(duration),
            "image": episode_image,
        })

    return {
        "title": title,
        "author": author,
        "description": description,
        "image": image,
        "feed_url": feed_url,
        "episodes": episodes,
    }


def get_saved_feeds():
    _ensure_data_dir()

    if not os.path.exists(RSS_FILE):
        return []

    try:
        with open(RSS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

    except (OSError, json.JSONDecodeError):
        pass

    return []


def save_feed(feed_url):
    feed_url = feed_url.strip()

    if not feed_url.lower().startswith(("http://", "https://")):
        raise ValueError("Введи корректную HTTP или HTTPS RSS-ссылку.")

    # Проверяем, что это действительно читаемая RSS-лента.
    podcast = parse_rss_feed(feed_url)

    feeds = get_saved_feeds()

    if not any(item.get("feed_url") == feed_url for item in feeds):
        feeds.append({
            "feed_url": feed_url,
            "title": podcast["title"],
            "author": podcast["author"],
            "image": podcast["image"],
        })

        _ensure_data_dir()

        with open(RSS_FILE, "w", encoding="utf-8") as file:
            json.dump(
                feeds,
                file,
                ensure_ascii=False,
                indent=2,
            )

    return podcast


def remove_feed(feed_url):
    feeds = [
        item for item in get_saved_feeds()
        if item.get("feed_url") != feed_url
    ]

    _ensure_data_dir()

    with open(RSS_FILE, "w", encoding="utf-8") as file:
        json.dump(feeds, file, ensure_ascii=False, indent=2)


def get_podcast_feed_url(podcast_id):
    """Получает RSS-ссылку из каталога Apple Podcasts."""
    response = requests.get(
        LOOKUP_URL,
        params={"id": podcast_id},
        headers=HEADERS,
        timeout=15,
    )
    response.raise_for_status()

    results = response.json().get("results", [])

    if not results:
        return ""

    return results[0].get("feedUrl", "")
