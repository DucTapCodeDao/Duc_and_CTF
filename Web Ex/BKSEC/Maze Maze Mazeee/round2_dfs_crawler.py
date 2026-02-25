import re
import sys
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

START_URL = "http://103.77.175.40:8031/round2_qncdl1248dbsl/"
TIMEOUT_SEC = 20
DELAY_SEC = 0.0  # increase (e.g., 0.02) if you want to be gentler
MAX_PAGES = 200000  # safety cap

FLAG_RE = re.compile(r"BKSEC\{[^}]+\}")

SKIP_SCHEMES = ("javascript:", "mailto:", "tel:")
SKIP_HREFS = {"", "#", "./", "../", ".."}


def extract_links(html: str, base_url: str) -> list[str]:
    """
    Extract absolute URLs from <a href="..."> in HTML.
    Handles directory listings too.
    """
    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []

    for a in soup.select("a[href]"):
        href = (a.get("href") or "").strip()
        if not href or href in SKIP_HREFS:
            continue
        if href.lower().startswith(SKIP_SCHEMES):
            continue

        abs_url = urljoin(base_url, href)
        # Drop fragment
        abs_url = abs_url.split("#", 1)[0]
        links.append(abs_url)

    # De-duplicate while preserving order
    seen = set()
    uniq = []
    for u in links:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq


def in_scope(url: str, start_netloc: str) -> bool:
    p = urlparse(url)
    return p.scheme in ("http", "https") and p.netloc == start_netloc


def main() -> int:
    start_netloc = urlparse(START_URL).netloc
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (CTF DFS Crawler)",
            "Accept": "*/*",
            "Connection": "close",
        }
    )

    visited: set[str] = set()
    stack: list[str] = [START_URL]
    pages_fetched = 0

    while stack:
        url = stack.pop()  # DFS
        if url in visited:
            continue
        if not in_scope(url, start_netloc):
            continue
        visited.add(url)

        try:
            r = session.get(url, timeout=TIMEOUT_SEC, allow_redirects=True)
        except requests.RequestException:
            continue

        pages_fetched += 1
        if pages_fetched > MAX_PAGES:
            print("Not found flag")
            return 1

        text = r.text if isinstance(r.text, str) else ""
        m = FLAG_RE.search(text)
        if m:
            print(m.group(0))
            return 0

        # Only parse links if it looks like HTML
        ct = (r.headers.get("Content-Type") or "").lower()
        if ("text/html" in ct) or ("<html" in text.lower()):
            links = extract_links(text, r.url)

            # Push in reverse so the first link appears earlier in DFS traversal
            # (optional, just for deterministic-ish behavior)
            for nxt in reversed(links):
                if in_scope(nxt, start_netloc) and nxt not in visited:
                    stack.append(nxt)

        if DELAY_SEC:
            time.sleep(DELAY_SEC)

    print("Not found flag")
    return 1


if __name__ == "__main__":
    # pip install requests beautifulsoup4
    sys.exit(main())