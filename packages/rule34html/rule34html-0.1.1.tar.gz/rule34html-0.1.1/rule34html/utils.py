from __future__ import annotations
import re, time, random, urllib.parse, httpx, asyncio
from typing import Iterable, List

USER_AGENT = "rule34html/0.1"
HEADERS = {"User-Agent": USER_AGENT}

BASE_URL = "https://rule34.xxx"
EXT_PRIORITIES = {
    "thumbnail": [".jpg", ".png", ".jpeg"],
    "sample":    [".jpg", ".png", ".jpeg"],
    "image":     [".png", ".jpg", ".jpeg", ".gif", ".webm", ".mp4"],
}

def join_tags(tags: Iterable[str]) -> str:
    safe = []
    for t in tags:
        t = t.strip().replace(" ", "_")
        if t:
            safe.append(t)
    return "+".join(urllib.parse.quote_plus(t) for t in safe)

def build_list_url(tags: Iterable[str], pid: int | None = None) -> str:
    q = join_tags(tags)
    if pid is not None:
        return f"{BASE_URL}/index.php?page=post&s=list&tags={q}&pid={pid}"
    return f"{BASE_URL}/index.php?page=post&s=list&tags={q}"

def build_view_url(post_id: int) -> str:
    return f"{BASE_URL}/index.php?page=post&s=view&id={post_id}"

def build_tags_list_url(prefix: str, page: int = 0) -> str:
    # Use wildcard on tags listing page, e.g., tags=list&tags=pre*
    # This is HTML, not the JSON autocomplete endpoint.
    star = urllib.parse.quote_plus(prefix.strip().replace(" ", "_") + "*")
    return f"{BASE_URL}/index.php?page=tags&s=list&tags={star}&pid={page*70}"

def polite_sleep(min_ms: int = 250, max_ms: int = 800):
    time.sleep(random.uniform(min_ms/1000, max_ms/1000))

async def polite_async_sleep(min_ms: int = 250, max_ms: int = 800):
    await asyncio.sleep(random.uniform(min_ms/1000, max_ms/1000))

def parse_int(value: str) -> int | None:
    m = re.search(r"\d+", value or "")
    return int(m.group()) if m else None