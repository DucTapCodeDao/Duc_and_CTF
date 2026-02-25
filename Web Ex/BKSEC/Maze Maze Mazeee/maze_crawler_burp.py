import re                                       # dùng regex để tìm flag hoặc tìm pattern của URL kế tiếp.
import time                                     # dùng sleep() để delay giữa các request (tránh spam server).
import argparse                                 # đọc tham số dòng lệnh (--start, --proxy, …) khi chạy script.
from urllib.parse import urljoin, urlparse      # urljoin: ghép URL tuyệt đối từ URL hiện tại + href tương đối (giống cách browser xử lý link).
                                                # urlparse: tách URL để lấy netloc (domain:port) nhằm kiểm tra “out of scope”.
import requests                                 # gửi HTTP request như một “mini browser”.
from bs4 import BeautifulSoup                   # parse HTML để trích href từ các thẻ <a>.

FLAG_PATTERNS = [
    re.compile(r"BKSEC\{[^}]+\}", re.I)
    # [^}]+ = “mọi ký tự bất kỳ, miễn không phải }”, lặp 1+ lần.
    # re.I = case-insensitive (không phân biệt hoa thường), dù với BKSEC{} thường không cần lắm.
]

NEXT_PAGE_REGEX = re.compile(r"page-\d+[-_A-Za-z0-9]*\.html?$", re.I)
# page- literal
# \d+ = số trang
# [-_A-Za-z0-9]* = phần tên sau số (tùy bài)
# \.html? = .htm hoặc .html (vì l là tùy chọn)
# $ = kết thúc chuỗi (đảm bảo link kết thúc bằng .htm/.html)

def find_flag(text: str) -> str | None:
    for rx in FLAG_PATTERNS:
        m = rx.search(text)
        if m:
            return m.group(0)
    return None
# Nhận vào text (thường là HTML body).
# Lặp qua từng regex trong FLAG_PATTERNS.
# rx.search(text) tìm match đầu tiên ở bất kỳ vị trí nào.
# Nếu match, trả về m.group(0) = toàn bộ chuỗi khớp (ví dụ BKSEC{...}).
# Nếu không tìm thấy gì, trả None.

def extract_next_url(html: str, current_url: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    hrefs = []
    for a in soup.select("a[href]"):
        href = (a.get("href") or "").strip()
        if not href or href == "#":
            continue
        hrefs.append(href)

    if not hrefs:
        return None

    # ưu tiên chain kiểu page-x
    for h in hrefs:
        if NEXT_PAGE_REGEX.search(h):
            return urljoin(current_url, h)

    # fallback: lấy cái đầu
    return urljoin(current_url, hrefs[0])


def main():
    ap = argparse.ArgumentParser(description="CTF Maze crawler (via Burp proxy).")
    ap.add_argument("--base", default="http://103.77.175.40:8031", help="Base URL")
    ap.add_argument("--start", default="/pages/page-1-Tombstone.html", help="Start path or full URL")
    ap.add_argument("--max", type=int, default=500, help="Max pages")
    ap.add_argument("--delay", type=float, default=0.05, help="Delay between requests (seconds)")
    ap.add_argument("--proxy", default="http://127.0.0.1:8080", help="Burp proxy URL")
    ap.add_argument("--insecure", action="store_true", help="Disable TLS verification (useful if HTTPS through Burp)")
    args = ap.parse_args()

    # Burp proxy
    proxies = {"http": args.proxy, "https": args.proxy}

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (CTF Maze Crawler via Burp)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "close",
    })

    # Start URL: nếu user đưa full URL thì dùng luôn, không thì join với base
    if args.start.startswith("http://") or args.start.startswith("https://"):
        url = args.start
    else:
        url = urljoin(args.base, args.start)

    visited = set()

    for step in range(1, args.max + 1):
        if url in visited:
            print(f"[!] Loop detected: {url}")
            return
        visited.add(url)

        r = session.get(
            url,
            timeout=20,
            allow_redirects=True,
            proxies=proxies,
            verify=(not args.insecure),
        )

        print(f"[{step:03}] {r.status_code} {url}")

        # scan flag in body
        flag = find_flag(r.text)
        if flag:
            print(f"\n[+] FLAG FOUND: {flag}")
            print(f"[+] URL: {url}")
            return

        # keyword hint (không phụ thuộc find_flag)
        if re.search(r"\bflag\b", r.text, re.I):
            print("\n[!] Found keyword 'flag' in body. Inspect this page.")
            print(f"[!] URL: {url}")
            return

        next_url = extract_next_url(r.text, url)
        if not next_url:
            print("[!] No next <a href> found. Stop.")
            print(f"[!] Last URL: {url}")
            return

        # stay in-scope
        if urlparse(next_url).netloc != urlparse(args.base).netloc:
            print(f"[!] Out of scope next URL: {next_url}")
            return

        url = next_url
        time.sleep(args.delay)

    print("[-] Reached max steps without finding flag.")


if __name__ == "__main__":
    main()