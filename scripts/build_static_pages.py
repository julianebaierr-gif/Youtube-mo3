import os
import sys
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from fastapi.testclient import TestClient
import app.main as main_mod
from app.main import app, SUPPORTED_LANGUAGES, FAVICON_SVG_CONTENT

PUBLIC_DIR = os.path.join(BASE_DIR, "public")
STATIC_DIR = os.path.join(BASE_DIR, "static")

def build_static():
    client = TestClient(app, base_url="https://www.yt4mp3.com")

    # 1. Copy static/ directory into public/static/ so @vercel/static serves it directly
    pub_static = os.path.join(PUBLIC_DIR, "static")
    if os.path.exists(STATIC_DIR):
        os.makedirs(pub_static, exist_ok=True)
        for root, dirs, files in os.walk(STATIC_DIR):
            rel = os.path.relpath(root, STATIC_DIR)
            target_dir = os.path.join(pub_static, rel) if rel != "." else pub_static
            os.makedirs(target_dir, exist_ok=True)
            for f in files:
                shutil.copy2(os.path.join(root, f), os.path.join(target_dir, f))

    # 2. Write favicon.svg and favicon.ico into public/
    with open(os.path.join(PUBLIC_DIR, "favicon.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(FAVICON_SVG_CONTENT)

    # 2b. Regenerate public/feed.xml so titles/descriptions match latest SEO content
    feed_path = os.path.join(PUBLIC_DIR, "feed.xml")
    if os.path.exists(feed_path):
        os.remove(feed_path)
    main_mod._FEED_CACHE_XML = None
    fresh_feed = main_mod.get_authoritative_feed_xml()
    with open(feed_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(fresh_feed)

    # 3. Pre-render all 63 canonical HTML pages into public/pages/
    pages_dir = os.path.join(PUBLIC_DIR, "pages")
    os.makedirs(pages_dir, exist_ok=True)

    # Root English pages
    en_routes = {
        "/": os.path.join(pages_dir, "en", "index.html"),
        "/youtube-to-mp3": os.path.join(pages_dir, "en", "youtube-to-mp3.html"),
        "/youtube-to-mp4": os.path.join(pages_dir, "en", "youtube-to-mp4.html"),
        "/youtube-shorts-downloader": os.path.join(pages_dir, "en", "youtube-shorts-downloader.html"),
        "/blog": os.path.join(pages_dir, "en", "blog.html"),
        "/contact-us": os.path.join(pages_dir, "legal", "contact-us.html"),
        "/terms-of-service": os.path.join(pages_dir, "legal", "terms-of-service.html"),
        "/privacy-policy": os.path.join(pages_dir, "legal", "privacy-policy.html"),
    }

    count = 0
    for route, out_path in en_routes.items():
        resp = client.get(route)
        assert resp.status_code == 200, f"Failed to render {route}: {resp.status_code}"
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(resp.text)
        count += 1

    # 14 International Languages x 4 pages = 56 pages
    for lang in SUPPORTED_LANGUAGES:
        if lang == "en":
            continue
        lang_routes = {
            f"/{lang}/": os.path.join(pages_dir, lang, "index.html"),
            f"/{lang}/youtube-to-mp3": os.path.join(pages_dir, lang, "youtube-to-mp3.html"),
            f"/{lang}/youtube-to-mp4": os.path.join(pages_dir, lang, "youtube-to-mp4.html"),
            f"/{lang}/youtube-shorts-downloader": os.path.join(pages_dir, lang, "youtube-shorts-downloader.html"),
            f"/{lang}/blog/": os.path.join(pages_dir, lang, "blog.html"),
        }
        for route, out_path in lang_routes.items():
            resp = client.get(route)
            assert resp.status_code == 200, f"Failed to render {route}: {resp.status_code}"
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(resp.text)
            count += 1

    print(f"Successfully pre-rendered {count} static HTML pages into public/pages/")

if __name__ == "__main__":
    build_static()
