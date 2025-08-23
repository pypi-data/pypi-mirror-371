from __future__ import annotations

import math
import asyncio
import os
import random
import re
import urllib.parse
from typing import Iterable, List, Optional, Tuple

import httpx
from bs4 import BeautifulSoup

from .exceptions import NotFound, ParseError, Rule34Error
from .models import Post, Tag
from .logger import logger
from .utils import (
    BASE_URL,
    USER_AGENT,
    build_list_url,
    build_tags_list_url,
    build_view_url,
    join_tags,
    parse_int,
    polite_sleep,
    polite_async_sleep,
)

DEFAULT_PER_PAGE = 42
MAX_PID = 200000
EXT_PRIORITIES = {
    "thumbnail": [".jpg", ".png", ".jpeg"],
    "sample":    [".jpg", ".png", ".jpeg"],
    "image":     [".png", ".jpg", ".jpeg", ".gif", ".webm", ".mp4"],
}

class _BaseClient:
    """Base client with common parsing logic."""
    def __init__(self, *, timeout: float = 20.0, headers: Optional[dict] = None):
        self._headers = {"User-Agent": USER_AGENT, **(headers or {})}
        self._timeout = timeout

    def _soup(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "html.parser")

    def _extract_posts_from_list(self, html: str) -> Tuple[List[Post], int, int]:
        """
        Parses the HTML of a post listing page for lightweight Post objects.
        This method is optimized to NOT call the expensive get_rest_of_urls function.
        Returns a tuple containing: (list of Post objects, max_pid found, total_posts_guess).
        """
        logger.debug("Starting _extract_posts_from_list")
        soup = self._soup(html)

        posts: List[Post] = []
        anchors = soup.select("a[href*='index.php?page=post'][href*='s=view'][href*='id=']")
        logger.debug(f"Found {len(anchors)} post anchors in HTML")

        for a in anchors:
            href = a.get("href", "")
            if "id=" in href:
                m = re.search(r"id=(\d+)", href)
                if not m:
                    continue
                
                post_id = int(m.group(1))
                page_url = urllib.parse.urljoin(BASE_URL + "/", href)
                
                img = a.find("img")
                thumbnail_url = urllib.parse.urljoin(BASE_URL + "/", img["src"]) if img and img.get("src") else ""
                
                posts.append(Post(
                    id=post_id, 
                    page_url=page_url, 
                    thumbnail_url=thumbnail_url,
                    sample_url=None,
                    image_url=None
                ))
                logger.debug(f"Extracted lightweight post id={post_id}")

        max_pid = 0
        pid_links = soup.select("a[href*='&pid=']")
        for link in pid_links:
            m = re.search(r"pid=(\d+)", link.get("href", ""))
            if m:
                max_pid = max(max_pid, int(m.group(1)))
        logger.debug(f"Estimated max_pid={max_pid} from pagination links")

        total_guess = 0
        count_text = soup.find(string=re.compile(r"Posts|post(s)? total", re.I))
        if count_text:
            m = re.search(r"(\d[\d,\.]*)", str(count_text))
            if m:
                total_guess = int(m.group(1).replace(",", "").replace(".", ""))
        logger.debug(f"Estimated total posts count={total_guess}")

        logger.debug(f"_extract_posts_from_list extracted {len(posts)} posts")
        return posts, max_pid, total_guess

    def _extract_post_view(self, html: str, post_url: str) -> Post:
        """Parses the HTML of a single post view page to extract all details."""
        soup = self._soup(html)

        m = re.search(r"id=(\d+)", post_url)
        if not m:
            raise ParseError("Cannot find post id in the URL")
        post_id = int(m.group(1))

        tags: List[str] = []
        for el in soup.select("#tag-list li a, .tag-type a, .tag a"):
            name = (el.get_text() or "").strip().replace(" ", "_")
            if name and name not in tags:
                tags.append(name)

        rating_el = soup.find(string=re.compile(r"Rating:", re.I))
        rating = re.search(r"Rating:\s*([A-Za-z]+)", rating_el.parent.get_text() if rating_el else "").group(1).lower() if rating_el else None

        image_url = None
        img_el = soup.select_one("#image, #img, .image img, #main_image")
        if img_el and img_el.get("src"):
            image_url = urllib.parse.urljoin(BASE_URL + "/", img_el["src"])

        width, height = None, None
        size_el = soup.find(string=re.compile(r"Size:|Resolution:", re.I))
        if size_el:
            size_match = re.search(r"(\d+)\s*[x×]\s*(\d+)", size_el.parent.get_text())
            if size_match:
                width, height = int(size_match.group(1)), int(size_match.group(2))

        file_ext = os.path.splitext(urllib.parse.urlparse(image_url or "").path)[1].lstrip('.') if image_url else None

        author_el = soup.find(string=re.compile(r"By:|Posted by", re.I))
        author = re.search(r"(?:By:|Posted by:?)\s*([A-Za-z0-9_\-]+)", author_el.parent.get_text() if author_el else "").group(1) if author_el else None

        source_el = soup.find(string=re.compile(r"Source:", re.I))
        source = re.search(r"Source:\s*(\S+)", source_el.parent.get_text() if source_el else "").group(1) if source_el else None
        
        urls = Rule34Client()._get_rest_of_urls(image_url or "")

        return Post(
            id=post_id,
            page_url=build_view_url(post_id),
            image_url=image_url,
            sample_url=urls.get("sample_url"),
            thumbnail_url=urls.get("thumbnail_url"),
            rating=rating,
            tags=tags,
            author=author,
            source=source,
            width=width,
            height=height,
            file_ext=file_ext,
        )

class Rule34Client(_BaseClient):
    """Synchronous client for Rule34."""
    def __init__(self, *, timeout: float = 20.0, headers: Optional[dict] = None, max_retries: int = 2):
        super().__init__(timeout=timeout, headers=headers)
        self._client = httpx.Client(timeout=timeout, headers=self._headers, follow_redirects=True)
        self._max_retries = max_retries

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _get(self, url: str) -> str:
        """Makes a GET request with retries and polite sleeping."""
        last_exc = None
        for attempt in range(self._max_retries + 1):
            try:
                logger.debug(f"GET {url} (attempt {attempt+1})")
                polite_sleep()
                r = self._client.get(url)
                r.raise_for_status()
                logger.debug(f"Response {r.status_code} from {url}")
                return r.text
            except Exception as e:
                logger.warning(f"Request failed for {url} on attempt {attempt+1}: {e}")
                last_exc = e
        raise Rule34Error(f"GET failed for {url}: {last_exc}")

    def _get_rest_of_urls(self, url: str) -> dict[str, str]:
        """
        Given any Rule34.xxx URL, return all three (thumbnail, sample, image) variants.
        """
        logger.debug(f"Resolving all URLs from source: {url}")
        
        def _check_url(base_url: str, orig_ext: str, kind: str) -> str:
            """Try original extension, then fall back to kind-specific priorities."""
            tried = []
            if orig_ext:
                tried.append(orig_ext)
                try:
                    check_url = base_url + orig_ext
                    logger.debug(f"HEAD request for {kind}: {check_url}")
                    r = self._client.head(check_url)
                    logger.debug(f" -> {r.status_code}")
                    if r.status_code == 200:
                        return check_url
                except Exception as e:
                    logger.warning(f"HEAD request failed for {check_url}: {e}")

            for ext in EXT_PRIORITIES.get(kind, []):
                if ext in tried:
                    continue
                tried.append(ext)
                try:
                    check_url = base_url + ext
                    logger.debug(f"HEAD request for {kind}: {check_url}")
                    r = self._client.head(check_url)
                    logger.debug(f" -> {r.status_code}")
                    if r.status_code == 200:
                        return check_url
                except Exception as e:
                    logger.warning(f"HEAD request failed for {check_url}: {e}")
            return ""

        urls = {"thumbnail_url": "", "sample_url": "", "image_url": ""}
        if "." not in url.rsplit("/", 1)[-1]: return urls
        
        base, _ext = url.rsplit(".", 1)
        orig_ext = "." + _ext.lower()

        if "thumbnails" in url:
            thumb_base = base
            sample_base = base.replace("thumbnails", "samples").replace("thumbnail_", "sample_")
            image_base  = base.replace("thumbnails", "images").replace("thumbnail_", "")
            urls["thumbnail_url"] = _check_url(thumb_base, orig_ext, "thumbnail")
            urls["sample_url"]    = _check_url(sample_base, orig_ext, "sample")
            urls["image_url"]     = _check_url(image_base, orig_ext, "image")
        elif "samples" in url:
            sample_base = base
            thumb_base  = base.replace("samples", "thumbnails").replace("sample_", "thumbnail_")
            image_base  = base.replace("samples", "images").replace("sample_", "")
            urls["sample_url"]    = _check_url(sample_base, orig_ext, "sample")
            urls["thumbnail_url"] = _check_url(thumb_base, orig_ext, "thumbnail")
            urls["image_url"]     = _check_url(image_base, orig_ext, "image")
        elif "images" in url:
            image_base  = base
            sample_base = base.replace("images", "samples", 1).rsplit("/", 1)[0] + "/sample_" + base.rsplit("/", 1)[1]
            thumb_base  = base.replace("images", "thumbnails", 1).rsplit("/", 1)[0] + "/thumbnail_" + base.rsplit("/", 1)[1]
            urls["image_url"]     = _check_url(image_base, orig_ext, "image")
            urls["sample_url"]    = _check_url(sample_base, orig_ext, "sample")
            urls["thumbnail_url"] = _check_url(thumb_base, orig_ext, "thumbnail")
        
        logger.debug(f"Resolved URLs: {urls}")
        return urls

    def search_posts(self, tags: Iterable[str], *, page: int = 0, per_page: int = DEFAULT_PER_PAGE) -> List[Post]:
        """Search for posts with given tags on a specific page."""
        pid = page * per_page
        if pid > MAX_PID:
            raise Rule34Error(f"Page offset too high (pid={pid}, max={MAX_PID})")
        url = build_list_url(tags, pid=pid)
        logger.debug(f"Searching posts: tags={tags}, page={page}, url={url}")
        html = self._get(url)
        posts, _, _ = self._extract_posts_from_list(html)
        
        for post in posts:
            if post.thumbnail_url:
                urls = self._get_rest_of_urls(post.thumbnail_url)
                post.sample_url = urls.get("sample_url")
                post.image_url = urls.get("image_url")

        logger.debug(f"Found and enriched {len(posts)} posts on page {page}")
        return posts

    def get_post(self, post_id: int) -> Post:
        """Get a single post by its ID."""
        url = build_view_url(post_id)
        logger.debug(f"Fetching post {post_id} from {url}")
        html = self._get(url)
        if re.search(r"Post not found|This post does not exist", html, re.I):
            raise NotFound(f"Post {post_id} not found")
        return self._extract_post_view(html, url)

    def random_post(self, tags: Iterable[str], *, only_urls: bool = False) -> Post:
        """Get a single random post for the given tags."""
        logger.debug(f"Picking random post with tags={tags}")
        url0 = build_list_url(tags)
        html0 = self._get(url0)
        posts0, max_pid, _ = self._extract_posts_from_list(html0)
        if not posts0:
            raise NotFound("No posts found for the given tags.")

        per_page = max(len(posts0), 1)
        max_page = min(max_pid // per_page if max_pid else 0, MAX_PID // per_page)

        rand_page = random.randint(0, max(0, max_page))
        pool = posts0
        if rand_page != 0:
            urlN = build_list_url(tags, pid=rand_page * per_page)
            htmlN = self._get(urlN)
            page_posts, _, _ = self._extract_posts_from_list(htmlN)
            if page_posts:
                pool = page_posts

        post = random.choice(pool)
        
        if post.thumbnail_url:
            urls = self._get_rest_of_urls(post.thumbnail_url)
            post.sample_url = urls.get("sample_url")
            post.image_url = urls.get("image_url")

        logger.debug(f"Random choice: post {post.id}")
        return post if only_urls else self.get_post(post.id)
    
    def random_posts(self, tags: Iterable[str], count: int = 5, *, only_urls: bool = False) -> List[Post]:
        """Return `count` random posts for given tags."""
        logger.debug(f"random_posts start tags={tags}, count={count}, only_urls={only_urls}")
        
        url0 = build_list_url(tags)
        html0 = self._get(url0)
        posts0, max_pid, total_posts = self._extract_posts_from_list(html0)
        
        if not posts0:
            raise NotFound("No posts found for the given tags.")

        per_page = max(len(posts0), 1)
        max_page = min(max_pid // per_page if max_pid else 0, MAX_PID // per_page)
        if total_posts > 0:
            max_page = (total_posts - 1) // per_page
        else:
            max_page = min(max_pid // per_page if max_pid else 0, MAX_PID // per_page)
        
        logger.debug(f"Total posts: ~{total_posts}, Posts per page: {per_page}, Max page: ~{max_page}")

        pages_to_fetch_count = min(math.ceil(count / per_page) + 2, max_page + 1)
        random_pages = random.sample(range(max_page + 1), k=pages_to_fetch_count)
        logger.debug(f"Will fetch {len(random_pages)} random pages: {random_pages}")

        pool = {post.id: post for post in posts0} if 0 in random_pages else {}
        for page_num in random_pages:
            if page_num == 0: continue
            url = build_list_url(tags, pid=page_num * per_page)
            html = self._get(url)
            new_posts, _, _ = self._extract_posts_from_list(html)
            for post in new_posts:
                pool[post.id] = post

        post_list = list(pool.values())
        if not post_list:
            raise NotFound("Could not gather any posts.")

        num_to_select = min(count, len(post_list))
        selected_posts = random.sample(post_list, k=num_to_select)
        logger.debug(f"Selected {len(selected_posts)} unique posts from a pool of {len(post_list)}")

        logger.debug(f"Enriching {len(selected_posts)} to include all image urls")
        for post in selected_posts:
            if post.thumbnail_url:
                urls = self._get_rest_of_urls(post.thumbnail_url)
                post.sample_url = urls.get("sample_url")
                post.image_url = urls.get("image_url") if urls.get("image_url") else (post.thumbnail_url.split("?")[0]+"?thumb")
        logger.debug(f"Returning {len(selected_posts)} posts. {only_urls=}")
        
        if only_urls:
            return selected_posts
        else:
            results = []
            for post in selected_posts:
                try:
                    results.append(self.get_post(post.id))
                except Exception as e:
                    logger.warning(f"Failed to fetch full details for post {post.id}: {e}")
            logger.debug(f"random_posts finished with {len(results)} full posts.")
            return results

    def autocomplete(self, prefix: str, *, limit: int = 10) -> List[Tag]:
        """Autocomplete tags using the site's JSON endpoint."""
        url = f"https://ac.rule34.xxx/autocomplete.php?q={urllib.parse.quote_plus(prefix)}"
        headers = {**self._headers, "Referer": "https://rule34.xxx/"}
        r = self._client.get(url, headers=headers)
        r.raise_for_status()
        data = r.json()
        results: List[Tag] = []
        for item in data[:limit]:
            name = item.get("value")
            count_match = re.search(r"\((\d+)\)", item.get("label", ""))
            count = int(count_match.group(1)) if count_match else 0
            if name:
                results.append(Tag(name=name, count=count))
        return results

    def download(self, post_id: int, out_dir: str = ".") -> str:
        """Download a post's image/video to a specified directory."""
        post = self.get_post(post_id)
        url = post.image_url or post.sample_url
        if not url:
            raise ParseError("No image URL found on post page to download.")
        
        fname = f"{post.id}.{post.file_ext or 'bin'}"
        path = os.path.join(out_dir, fname)
        os.makedirs(out_dir, exist_ok=True)
        
        polite_sleep()
        with self._client.stream("GET", url) as r:
            r.raise_for_status()
            with open(path, "wb") as f:
                for chunk in r.iter_bytes():
                    f.write(chunk)
        return path

    def close(self):
        """Closes the underlying HTTP client."""
        self._client.close()

class AsyncRule34Client(_BaseClient):
    """Asynchronous client for Rule34."""
    def __init__(self, *, timeout: float = 20.0, headers: Optional[dict] = None, max_retries: int = 2):
        super().__init__(timeout=timeout, headers=headers)
        self._client = httpx.AsyncClient(timeout=timeout, headers=self._headers, follow_redirects=True)
        self._max_retries = max_retries

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _get(self, url: str) -> str:
        """Makes an async GET request with retries and polite sleeping."""
        last_exc = None
        for attempt in range(self._max_retries + 1):
            try:
                logger.debug(f"GET {url} (attempt {attempt+1})")
                await polite_async_sleep()
                r = await self._client.get(url)
                r.raise_for_status()
                logger.debug(f"Response {r.status_code} from {url}")
                return r.text
            except Exception as e:
                logger.warning(f"Request failed for {url} on attempt {attempt+1}: {e}")
                last_exc = e
        raise Rule34Error(f"GET failed for {url}: {last_exc}")

    async def _get_rest_of_urls_async(self, url: str) -> dict[str, str]:
        """
        Asynchronously given any Rule34.xxx URL, return all three variants.
        """
        logger.debug(f"Resolving all URLs from source: {url}")
        
        async def _check_url(base_url: str, orig_ext: str, kind: str) -> str:
            """Try original extension, then fall back to kind-specific priorities."""
            tried = []
            if orig_ext:
                tried.append(orig_ext)
                try:
                    check_url = base_url + orig_ext
                    logger.debug(f"HEAD request for {kind}: {check_url}")
                    r = await self._client.head(check_url)
                    logger.debug(f" -> {r.status_code}")
                    if r.status_code == 200:
                        return check_url
                except Exception as e:
                    logger.warning(f"HEAD request failed for {check_url}: {e}")

            for ext in EXT_PRIORITIES.get(kind, []):
                if ext in tried:
                    continue
                tried.append(ext)
                try:
                    check_url = base_url + ext
                    logger.debug(f"HEAD request for {kind}: {check_url}")
                    r = await self._client.head(check_url)
                    logger.debug(f" -> {r.status_code}")
                    if r.status_code == 200:
                        return check_url
                except Exception as e:
                    logger.warning(f"HEAD request failed for {check_url}: {e}")
            return ""

        urls = {"thumbnail_url": "", "sample_url": "", "image_url": ""}
        if "." not in url.rsplit("/", 1)[-1]: return urls
        
        base, _ext = url.rsplit(".", 1)
        orig_ext = "." + _ext.lower()

        if "thumbnails" in url:
            thumb_base = base
            sample_base = base.replace("thumbnails", "samples").replace("thumbnail_", "sample_")
            image_base  = base.replace("thumbnails", "images").replace("thumbnail_", "")
            urls["thumbnail_url"] = await _check_url(thumb_base, orig_ext, "thumbnail")
            urls["sample_url"]    = await _check_url(sample_base, orig_ext, "sample")
            urls["image_url"]     = await _check_url(image_base, orig_ext, "image")
        elif "samples" in url:
            sample_base = base
            thumb_base  = base.replace("samples", "thumbnails").replace("sample_", "thumbnail_")
            image_base  = base.replace("samples", "images").replace("sample_", "")
            urls["sample_url"]    = await _check_url(sample_base, orig_ext, "sample")
            urls["thumbnail_url"] = await _check_url(thumb_base, orig_ext, "thumbnail")
            urls["image_url"]     = await _check_url(image_base, orig_ext, "image")
        elif "images" in url:
            image_base  = base
            sample_base = base.replace("images", "samples", 1).rsplit("/", 1)[0] + "/sample_" + base.rsplit("/", 1)[1]
            thumb_base  = base.replace("images", "thumbnails", 1).rsplit("/", 1)[0] + "/thumbnail_" + base.rsplit("/", 1)[1]
            urls["image_url"]     = await _check_url(image_base, orig_ext, "image")
            urls["sample_url"]    = await _check_url(sample_base, orig_ext, "sample")
            urls["thumbnail_url"] = await _check_url(thumb_base, orig_ext, "thumbnail")

        logger.debug(f"Resolved URLs: {urls}")
        return urls

    async def search_posts(self, tags: Iterable[str], *, page: int = 0, per_page: int = DEFAULT_PER_PAGE) -> List[Post]:
        """Asynchronously search for posts."""
        pid = page * per_page
        url = build_list_url(tags, pid=pid)
        html = await self._get(url)
        posts, _, _ = self._extract_posts_from_list(html)
        
        for post in posts:
            if post.thumbnail_url:
                urls = await self._get_rest_of_urls_async(post.thumbnail_url)
                post.sample_url = urls.get("sample_url")
                post.image_url = urls.get("image_url")
        return posts

    async def get_post(self, post_id: int) -> Post:
        """Asynchronously get a single post by its ID."""
        url = build_view_url(post_id)
        html = await self._get(url)
        if re.search(r"Post not found|This post does not exist", html, re.I):
            raise NotFound(f"Post {post_id} not found")
        return self._extract_post_view(html, url)
    
    async def autocomplete(self, prefix: str, *, limit: int = 10) -> List[Tag]:
        """Autocomplete tags using the site's JSON endpoint."""
        url = f"https://ac.rule34.xxx/autocomplete.php?q={urllib.parse.quote_plus(prefix)}"
        headers = {**self._headers, "Referer": "https://rule34.xxx/"}
        r = await self._client.get(url, headers=headers)
        r.raise_for_status()
        data = r.json()
        results: List[Tag] = []
        for item in data[:limit]:
            name = item.get("value")
            count_match = re.search(r"\((\d+)\)", item.get("label", ""))
            count = int(count_match.group(1)) if count_match else 0
            if name:
                results.append(Tag(name=name, count=count))
        return results

    async def random_post(self, tags: Iterable[str], *, only_urls: bool = False) -> Post:
        """Asynchronously get a single random post."""
        url0 = build_list_url(tags)
        html0 = await self._get(url0)
        posts0, max_pid, _ = self._extract_posts_from_list(html0)
        if not posts0:
            raise NotFound("No posts found for the given tags.")
        per_page = max(len(posts0), 1)
        max_page = min(max_pid // per_page if max_pid else 0, MAX_PID // per_page)

        rand_page = random.randint(0, max(0, max_page))
        pool = posts0
        if rand_page != 0:
            urlN = build_list_url(tags, pid=rand_page * per_page)
            htmlN = await self._get(urlN)
            page_posts, _, _ = self._extract_posts_from_list(htmlN)
            if page_posts:
                pool = page_posts
        
        post = random.choice(pool)
        
        if post.thumbnail_url:
            urls = await self._get_rest_of_urls_async(post.thumbnail_url)
            post.sample_url = urls.get("sample_url")
            post.image_url = urls.get("image_url")

        return post if only_urls else await self.get_post(post.id)
    
    async def random_posts(self, tags: Iterable[str], count: int = 5, *, only_urls: bool = False) -> List[Post]:
        """Asynchronously return `count` random posts for given tags."""
        logger.debug(f"async random_posts start tags={tags}, count={count}, only_urls={only_urls}")

        url0 = build_list_url(tags)
        html0 = await self._get(url0)
        posts0, max_pid, _ = self._extract_posts_from_list(html0)
        
        if not posts0:
            raise NotFound("No posts found for the given tags.")

        per_page = max(len(posts0), 1)
        max_page = min(max_pid // per_page if max_pid else 0, MAX_PID // per_page)
        logger.debug(f"per_page={per_page}, max_page={max_page}")

        pages_to_fetch_count = min(math.ceil(count / per_page) + 2, max_page + 1)
        random_pages = random.sample(range(max_page + 1), k=pages_to_fetch_count)

        async def fetch_page(page_num):
            url = build_list_url(tags, pid=page_num * per_page)
            html = await self._get(url)
            return self._extract_posts_from_list(html)[0]
        
        tasks = [fetch_page(p) for p in random_pages]
        pages_results = await asyncio.gather(*tasks)

        pool = {post.id: post for page_posts in pages_results for post in page_posts}

        post_list = list(pool.values())
        if not post_list:
            raise NotFound("Could not gather any posts.")

        num_to_select = min(count, len(post_list))
        selected_posts = random.sample(post_list, k=num_to_select)
        logger.debug(f"Selected {len(selected_posts)} unique posts from a pool of {len(post_list)}")

        async def enrich_post(post):
            if post.thumbnail_url:
                urls = await self._get_rest_of_urls_async(post.thumbnail_url)
                post.sample_url = urls.get("sample_url")
                post.image_url = urls.get("image_url") if urls.get("image_url") else (post.thumbnail_url.split("?")[0]+"?thumb")
            return post

        logger.debug(f"Enriching {len(selected_posts)} to include all image urls")
        enriched_posts = await asyncio.gather(*(enrich_post(p) for p in selected_posts))
        logger.debug(f"Returning {len(selected_posts)} posts. {only_urls=}")
        
        if only_urls:
            return enriched_posts
        else:
            return await asyncio.gather(*(self.get_post(p.id) for p in enriched_posts))

    async def close(self):
        """Closes the underlying async HTTP client."""
        await self._client.aclose()
