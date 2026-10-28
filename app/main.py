import os
import asyncio
import time
import urllib.request
import urllib.parse
import json
import re
import uuid
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app = FastAPI(
    title="YouTube to MP3 & MP4 Converter Pro - Studio Audio & 4K Video",
    description="Fast, free, and secure online YouTube to MP3 320kbps and YouTube to MP4 1080p/4K downloader.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def domain_redirect_middleware(request: Request, call_next):
    raw_host = request.headers.get("host", "").lower()
    host = raw_host.split(":")[0]
    if host in ["yt4mp3.com", "yt4mp3.cc", "www.yt4mp3.cc"]:
        new_url = f"https://www.yt4mp3.com{request.url.path}"
        if request.url.query:
            new_url += f"?{request.url.query}"
        return RedirectResponse(url=new_url, status_code=301)
    return await call_next(request)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    is_head = request.method == "HEAD"
    if is_head and not request.url.path.startswith("/api/"):
        request.scope["method"] = "GET"
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self' 'unsafe-inline' 'unsafe-eval' https: data: blob:; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https: data: blob:; "
        "img-src 'self' data: blob: https: http:; "
        "media-src 'self' blob: https: http:; "
        "connect-src 'self' https: wss:; "
        "frame-src 'self' https: data: blob:; "
        "worker-src 'self' blob: https:;"
    )
    if not request.url.path.startswith("/api/"):
        if "vary" in response.headers:
            del response.headers["vary"]
    if is_head:
        return Response(status_code=response.status_code, headers=dict(response.headers), media_type=response.media_type)
    return response

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)



from app.seo_content import SEO_PAGES
from app.legal_content import LEGAL_PAGES
from app.i18n import (
    SUPPORTED_LANGUAGES,
    get_ui_strings,
    get_page_content,
    get_hreflang_links,
    get_language_switcher_links
)

_CONVERTER_HTML_CACHE: dict[tuple[str, str], str] = {}
_LEGAL_HTML_CACHE: dict[str, str] = {}

EDGE_HTML_HEADERS = {
    "Cache-Control": "public, max-age=0, must-revalidate",
    "CDN-Cache-Control": "public, max-age=0, must-revalidate",
    "Vercel-CDN-Cache-Control": "public, max-age=0, must-revalidate",
}

def render_converter_page(request: Request, page_key: str, lang: str = "en"):
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Language not found")
    
    cache_key = (lang, page_key)
    html_str = _CONVERTER_HTML_CACHE.get(cache_key)
    if html_str is None:
        seo_data = get_page_content(lang, page_key)
        ui_strings = get_ui_strings(lang)
        hreflangs = get_hreflang_links(page_key)
        switcher = get_language_switcher_links(page_key, lang)
        current_meta = SUPPORTED_LANGUAGES[lang]
        tmpl = templates.env.get_template("index.html")
        html_str = tmpl.render(
            request=request,
            seo=seo_data,
            t=ui_strings,
            lang=lang,
            lang_dir=current_meta.get("dir", "ltr"),
            hreflangs=hreflangs,
            switcher=switcher,
            current_lang=current_meta,
            supported_languages=SUPPORTED_LANGUAGES
        )
        _CONVERTER_HTML_CACHE[cache_key] = html_str
    
    return HTMLResponse(content=html_str, headers=EDGE_HTML_HEADERS)

def render_legal_page(request: Request, page_key: str):
    html_str = _LEGAL_HTML_CACHE.get(page_key)
    if html_str is None:
        ui_strings = get_ui_strings("en")
        switcher = get_language_switcher_links("home", "en")
        current_meta = SUPPORTED_LANGUAGES["en"]
        tmpl = templates.env.get_template("page.html")
        html_str = tmpl.render(
            request=request,
            seo=LEGAL_PAGES[page_key],
            t=ui_strings,
            lang="en",
            lang_dir="ltr",
            switcher=switcher,
            current_lang=current_meta,
            supported_languages=SUPPORTED_LANGUAGES
        )
        _LEGAL_HTML_CACHE[page_key] = html_str
    return HTMLResponse(content=html_str, headers=EDGE_HTML_HEADERS)

# Root English Routes
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return render_converter_page(request, "home", "en")

@app.get("/youtube-to-mp3", response_class=HTMLResponse)
async def youtube_mp3_page(request: Request):
    return render_converter_page(request, "youtube-to-mp3", "en")

@app.get("/youtube-to-mp4", response_class=HTMLResponse)
async def youtube_mp4_page(request: Request):
    return render_converter_page(request, "youtube-to-mp4", "en")

@app.get("/youtube-shorts-downloader", response_class=HTMLResponse)
@app.get("/youtube-shorts-downloader/", response_class=HTMLResponse)
async def youtube_shorts_page(request: Request):
    return render_converter_page(request, "youtube-shorts-downloader", "en")

# Static Legal Pages (Universal English)
@app.get("/contact-us", response_class=HTMLResponse)
async def contact_us_page(request: Request):
    return render_legal_page(request, "contact-us")

@app.get("/terms-of-service", response_class=HTMLResponse)
async def terms_page(request: Request):
    return render_legal_page(request, "terms-of-service")

@app.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_page(request: Request):
    return render_legal_page(request, "privacy-policy")

# /dmca redirects to contact-us which contains the full DMCA section
@app.get("/dmca", response_class=HTMLResponse)
async def dmca_page(request: Request):
    return RedirectResponse(url="/contact-us#dmca", status_code=301)

# Viral URL Shortcut Routes (e.g. yt4mp3.com/watch?v=..., yt4mp3.com/shorts/..., yt4mp3.com/4youtube/...)
@app.get("/watch", response_class=HTMLResponse)
async def watch_shortcut_page(request: Request):
    return render_converter_page(request, "home", "en")

@app.get("/shorts/{short_id:path}", response_class=HTMLResponse)
async def shorts_shortcut_page(request: Request, short_id: str):
    return render_converter_page(request, "home", "en")

@app.get("/4youtube", response_class=HTMLResponse)
@app.get("/4youtube/{path:path}", response_class=HTMLResponse)
async def four_youtube_shortcut_page(request: Request, path: str = ""):
    return render_converter_page(request, "home", "en")

@app.get("/4/{path:path}", response_class=HTMLResponse)
async def four_shortcut_page(request: Request, path: str = ""):
    return render_converter_page(request, "home", "en")

# PWA Endpoints
@app.get("/manifest.json")
async def manifest_endpoint():
    manifest_file = os.path.join(BASE_DIR, "public", "manifest.json")
    if os.path.exists(manifest_file):
        with open(manifest_file, "r", encoding="utf-8") as f:
            return Response(content=f.read(), media_type="application/manifest+json; charset=utf-8", headers=EDGE_HTML_HEADERS)
    raise HTTPException(status_code=404, detail="Manifest not found")

@app.get("/sw.js")
async def service_worker_endpoint():
    sw_file = os.path.join(BASE_DIR, "public", "sw.js")
    if os.path.exists(sw_file):
        with open(sw_file, "r", encoding="utf-8") as f:
            return Response(content=f.read(), media_type="application/javascript; charset=utf-8")
    raise HTTPException(status_code=404, detail="Service worker not found")


# SEO, Discovery & System Endpoints
@app.api_route("/ads.txt", methods=["GET", "HEAD"])
async def ads_txt():
    ads_file = os.path.join(BASE_DIR, "public", "ads.txt")
    if os.path.exists(ads_file):
        with open(ads_file, "r", encoding="utf-8") as f:
            content = f.read()
        return Response(content=content, media_type="text/plain; charset=utf-8", headers=EDGE_HTML_HEADERS)
    content = "google.com, pub-2350272227833258, DIRECT, f08c47fec0942fa0\n"
    return Response(content=content, media_type="text/plain; charset=utf-8", headers=EDGE_HTML_HEADERS)

@app.api_route("/robots.txt", methods=["GET", "HEAD"])
async def robots_txt():
    robots_file = os.path.join(BASE_DIR, "public", "robots.txt")
    if os.path.exists(robots_file):
        with open(robots_file, "r", encoding="utf-8") as f:
            return Response(content=f.read(), media_type="text/plain; charset=utf-8", headers=EDGE_HTML_HEADERS)
    content = """User-agent: *
Allow: /
Disallow: /?s=
Disallow: /*?*s=
Disallow: /*?*q=
Disallow: /*?*ref=
Sitemap: https://www.yt4mp3.com/sitemap.xml
"""
    return Response(content=content, media_type="text/plain; charset=utf-8", headers=EDGE_HTML_HEADERS)

_SITEMAP_CACHE_XML = None

def get_authoritative_sitemap_xml() -> str:
    global _SITEMAP_CACHE_XML
    if _SITEMAP_CACHE_XML:
        return _SITEMAP_CACHE_XML
    sitemap_file = os.path.join(BASE_DIR, "public", "sitemap.xml")
    if os.path.exists(sitemap_file):
        try:
            with open(sitemap_file, "r", encoding="utf-8") as f:
                content = f.read()
                if content and "<urlset" in content:
                    _SITEMAP_CACHE_XML = content
                    return _SITEMAP_CACHE_XML
        except Exception:
            pass
    # Dynamic fallback: build sitemap from all 63 authoritative canonical URLs
    urls = get_all_sitemap_urls()
    items = []
    for u in urls:
        priority = "1.0" if u == "https://www.yt4mp3.com/" or u.endswith("/") else "0.8"
        items.append(f"""  <url>
    <loc>{u}</loc>
    <lastmod>2026-10-21</lastmod>
    <changefreq>daily</changefreq>
    <priority>{priority}</priority>
  </url>""")
    _SITEMAP_CACHE_XML = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(items) + "\n</urlset>"
    return _SITEMAP_CACHE_XML

@app.api_route("/sitemap.xml", methods=["GET", "HEAD"])
async def sitemap_xml():
    xml_content = get_authoritative_sitemap_xml()
    sitemap_headers = dict(EDGE_HTML_HEADERS)
    sitemap_headers["Content-Disposition"] = 'inline; filename="sitemap.xml"'
    return Response(content=xml_content, media_type="application/xml; charset=utf-8", headers=sitemap_headers)

# Redirect any alternate/legacy sitemap endpoints to the single authoritative sitemap
@app.api_route("/sitemap_index.xml", methods=["GET", "HEAD"])
@app.api_route("/sitemap-index.xml", methods=["GET", "HEAD"])
@app.api_route("/sitemaps.xml", methods=["GET", "HEAD"])
@app.api_route("/sitemap1.xml", methods=["GET", "HEAD"])
@app.api_route("/sitemap.xml.gz", methods=["GET", "HEAD"])
@app.api_route("/sitemap", methods=["GET", "HEAD"])
@app.api_route("/sitemap/", methods=["GET", "HEAD"])
async def redirect_duplicate_sitemaps():
    return RedirectResponse(url="https://www.yt4mp3.com/sitemap.xml", status_code=301)

@app.api_route("/llms.txt", methods=["GET", "HEAD"])
async def llms_txt():
    llms_file = os.path.join(BASE_DIR, "public", "llms.txt")
    if os.path.exists(llms_file):
        with open(llms_file, "r", encoding="utf-8") as f:
            return Response(content=f.read(), media_type="text/plain; charset=utf-8", headers=EDGE_HTML_HEADERS)
    content = """# YT4MP3
> Free Online YouTube to MP3 and MP4 Converter

YT4MP3 is a fast, free, web-based tool for converting and downloading YouTube videos into high-quality MP3 audio (up to 320kbps) and HD/4K MP4 video files.

## Core Features
- YouTube to MP3 converter with 320kbps, 256kbps, and 128kbps bitrate selection.
- YouTube to MP4 video downloader supporting 1080p, 720p, and 4K resolutions.
- Direct browser downloads with zero software installation and no user registration required.
- Fully compatible with desktop and mobile devices including Android, iOS, Windows, and macOS.

## Available Pages
- [Home](https://www.yt4mp3.com/): Free Online YouTube to MP3 and MP4 Converter.
- [YouTube to MP3 Converter](https://www.yt4mp3.com/youtube-to-mp3): Convert YouTube videos and music into high quality 320kbps MP3 audio files.
- [YouTube to MP4 Converter](https://www.yt4mp3.com/youtube-to-mp4): Download YouTube videos in 1080p, 720p, and 4K MP4 format.
- [YouTube Shorts Downloader](https://www.yt4mp3.com/youtube-shorts-downloader): Download YouTube Shorts videos in HD MP4 or convert Shorts to MP3.
- [Contact Us](https://www.yt4mp3.com/contact-us): Official support and DMCA contact (contact.yt4mp3@gmail.com).
- [Terms of Service](https://www.yt4mp3.com/terms-of-service): Terms governing the personal and fair use of the converter tool.
- [Privacy Policy](https://www.yt4mp3.com/privacy-policy): Privacy practices and data handling information.
"""
    return Response(content=content, media_type="text/plain; charset=utf-8", headers=EDGE_HTML_HEADERS)

@app.get("/8f9b3e1c4a2d7e5f9a0b1c2d3e4f5a6b.txt")
async def indexnow_key():
    return Response(content="8f9b3e1c4a2d7e5f9a0b1c2d3e4f5a6b", media_type="text/plain; charset=utf-8", headers=EDGE_HTML_HEADERS)

def get_all_sitemap_urls() -> list:
    sitemap_file = os.path.join(BASE_DIR, "public", "sitemap.xml")
    urls = []
    if os.path.exists(sitemap_file):
        try:
            with open(sitemap_file, "r", encoding="utf-8") as f:
                xml_content = f.read()
            found = re.findall(r"<loc>\s*(https?://[^<\s]+)\s*</loc>", xml_content, re.I)
            for u in found:
                if u not in urls:
                    urls.append(u)
        except Exception:
            pass
    if not urls:
        urls = (
            [
                "https://www.yt4mp3.com/",
                "https://www.yt4mp3.com/youtube-to-mp3",
                "https://www.yt4mp3.com/youtube-to-mp4",
                "https://www.yt4mp3.com/youtube-shorts-downloader",
                "https://www.yt4mp3.com/contact-us",
                "https://www.yt4mp3.com/terms-of-service",
                "https://www.yt4mp3.com/privacy-policy"
            ] + [
                f"https://www.yt4mp3.com/{c}/" for c in SUPPORTED_LANGUAGES if c != "en"
            ] + [
                f"https://www.yt4mp3.com/{c}/youtube-to-mp3" for c in SUPPORTED_LANGUAGES if c != "en"
            ] + [
                f"https://www.yt4mp3.com/{c}/youtube-to-mp4" for c in SUPPORTED_LANGUAGES if c != "en"
            ] + [
                f"https://www.yt4mp3.com/{c}/youtube-shorts-downloader" for c in SUPPORTED_LANGUAGES if c != "en"
            ]
        )
    return urls

@app.api_route("/api/indexnow", methods=["GET", "POST"])
async def trigger_indexnow():
    url_list = get_all_sitemap_urls()
    payload = {
        "host": "www.yt4mp3.com",
        "key": "8f9b3e1c4a2d7e5f9a0b1c2d3e4f5a6b",
        "keyLocation": "https://www.yt4mp3.com/8f9b3e1c4a2d7e5f9a0b1c2d3e4f5a6b.txt",
        "urlList": url_list
    }
    data = json.dumps(payload).encode("utf-8")
    # Official unified IndexNow endpoint (automatically shares with Bing, Yandex, Seznam, Naver, Yep without duplicate spam pings)
    endpoints = [
        "https://api.indexnow.org/indexnow",
        "https://www.bing.com/indexnow"
    ]
    results = {}
    for ep in endpoints:
        try:
            req = urllib.request.Request(
                ep,
                data=data,
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "User-Agent": "Mozilla/5.0 (compatible; YT4MP3-SitemapNotifier/1.0; +https://www.yt4mp3.com)"
                }
            )
            with urllib.request.urlopen(req, timeout=6) as res:
                results[ep] = {"status": res.status, "msg": "ok"}
        except urllib.error.HTTPError as he:
            results[ep] = {"status": he.code, "msg": "accepted" if he.code in [200, 202] else str(he)}
        except Exception as e:
            results[ep] = {"status": "error", "detail": str(e)}
    return {
        "submitted": True,
        "url_count": len(url_list),
        "results": results
    }

@app.on_event("startup")
async def start_auto_indexnow_scheduler():
    import asyncio
    async def _auto_index_loop():
        # Wait 90 seconds after server startup before initial run
        await asyncio.sleep(90)
        while True:
            try:
                await trigger_indexnow()
            except Exception as e:
                print(f"[AUTO_INDEXNOW_WARN] {e}")
            # Automatically push all URLs to Bing/IndexNow every 4 hours (14,400 seconds)
            await asyncio.sleep(14400)
    asyncio.create_task(_auto_index_loop())

# ==============================================================================
# UPSTREAM CONNECTION POOLS
# ==============================================================================
WEBSHARE_USER = os.environ.get("WEBSHARE_USER") or "jzoemevm"
WEBSHARE_PASS = os.environ.get("WEBSHARE_PASS") or "cxoms419j5eq"
WEBSHARE_POOLS = {
    "US": ["9.142.218.167:6831", "192.46.201.131:6645", "64.52.28.38:7725", "9.142.198.67:5734",
           "45.56.180.203:8437", "9.142.11.217:5373", "64.52.31.9:6196"],
    "GB": ["195.40.133.198:6418", "195.40.128.79:6799", "87.86.24.81:5732"],
    "FR": ["31.98.7.105:6283", "179.61.172.206:6757", "82.140.180.187:7147", "31.98.8.82:5760", "82.23.62.125:7878"],
    "JP": ["82.22.93.22:7729", "82.22.93.45:7752", "82.22.93.42:7749"],
    "CO": ["108.165.3.146:5277", "108.165.2.167:5798"],
}
WEBSHARE_POOL_PRIORITY = ["GB", "US", "FR", "JP", "CO"]

def fetch_converter_upstream(url: str, headers: dict = None, data: bytes = None, timeout: int = 9) -> bytes:
    """Robust upstream request helper: attempts direct connection, and automatically routes through
    Webshare ISP proxies if the direct datacenter IP receives HTTP 403 Forbidden or network block."""
    headers = headers or {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Referer": "https://loader.to/",
        "Origin": "https://loader.to",
    }
    # 1. Try direct connection first
    try:
        req = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        if e.code not in [403, 429]:
            err_body = e.read()
            if err_body:
                return err_body
            raise e
    except Exception:
        pass

    # 2. Transparent ISP Proxy Fallback (unlimited bandwidth static residential/ISP pool)
    import random
    us_ips = list(WEBSHARE_POOLS.get("US", [])) + list(WEBSHARE_POOLS.get("GB", []))
    random.shuffle(us_ips)
    last_ex = None
    for ip in us_ips[:4]:
        try:
            proxy_url = f"http://{WEBSHARE_USER}:{WEBSHARE_PASS}@{ip}"
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url}))
            req = urllib.request.Request(url, data=data, headers=headers)
            with opener.open(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as he:
            err_b = he.read()
            if err_b:
                return err_b
            last_ex = he
        except Exception as ex:
            last_ex = ex
            continue
    if last_ex:
        raise last_ex
    raise RuntimeError("All upstream converter routes failed")

_SAVENOW_TOKEN_CACHE = {"token": None, "expires_at": 0}

def get_savenow_pow_token() -> str:
    """Solves Savenow's SHA-256 Proof-of-Work challenge in ~15ms and mints an authenticated Bearer token.
    Eliminates all 403 Forbidden and malicious ad redirect gateway responses, unlocking direct worker links."""
    global _SAVENOW_TOKEN_CACHE
    import hashlib
    import time
    now = time.time()
    if _SAVENOW_TOKEN_CACHE.get("token") and now < (_SAVENOW_TOKEN_CACHE.get("expires_at", 0) - 30):
        return _SAVENOW_TOKEN_CACHE["token"]

    host = "https://p.savenow.to"
    try:
        # 1. Fetch challenge
        c_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Origin": "https://savenow.to",
            "Referer": "https://savenow.to/",
        }
        cr_bytes = fetch_converter_upstream(f"{host}/api/pow/challenge", headers=c_headers, timeout=6)
        ch = json.loads(cr_bytes.decode("utf-8"))

        salt = ch.get("salt")
        diff = int(ch.get("difficulty", 3))
        prefix = "0" * diff
        nonce = 0
        while True:
            h = hashlib.sha256(f"{salt}:{nonce}".encode("utf-8")).hexdigest()
            if h.startswith(prefix):
                break
            nonce += 1

        # 2. Verify challenge and obtain Bearer token
        v_payload = json.dumps({
            "salt": salt,
            "difficulty": diff,
            "expires_at": ch.get("expires_at"),
            "signature": ch.get("signature"),
            "nonce": nonce,
        }).encode("utf-8")
        v_headers = {
            "Content-Type": "application/json",
            "Origin": "https://savenow.to",
            "Referer": "https://savenow.to/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        vr_bytes = fetch_converter_upstream(f"{host}/api/pow/verify", headers=v_headers, data=v_payload, timeout=6)
        v_data = json.loads(vr_bytes.decode("utf-8"))
        token = v_data.get("token")
        exp = float(v_data.get("expires_at", now + 600))
        if token:
            _SAVENOW_TOKEN_CACHE = {"token": token, "expires_at": exp}
            return token
    except Exception as e:
        print(f"[SAVENOW_POW_ERROR] {e}")
    return _SAVENOW_TOKEN_CACHE.get("token") or ""

@app.get("/api/convert")
async def proxy_convert(url: str, format: str = "mp3", engine: str = "auto"):
    encoded_url = urllib.parse.quote(url)
    raw_fmt = format.lower().strip()
    
    # Robust format normalization to prevent 422 Unprocessable Entity
    clean_fmt = raw_fmt.replace("kbps", "").replace("p", "").strip()
    if clean_fmt in ["320", "256", "128", "64", "mp3", "audio"]:
        fmt = "mp3"
    elif clean_fmt in ["2160", "4k"]:
        fmt = "4k"
    elif clean_fmt in ["1440", "2k"]:
        fmt = "1440"
    elif clean_fmt in ["1080", "fhd"]:
        fmt = "1080"
    elif clean_fmt in ["720", "hd"]:
        fmt = "720"
    elif clean_fmt in ["480", "360", "240"]:
        fmt = clean_fmt
    elif clean_fmt in ["m4a", "flac", "wav", "aac", "webm", "opus", "ogg"]:
        fmt = clean_fmt
    else:
        fmt = "mp3"
    
    captured_err = None
    is_geo = False

    is_video_fmt = fmt in ["1080", "720", "480", "360", "1440", "4k"]
    # Prioritize official Loader cluster (p.lbserver.xyz) which mints genuine worker CDN download links (*.savenow.to)
    engine_order = ["loader", "savenow"]

    for eng in engine_order:
        if eng == "loader":
            try:
                lto_url = f"https://p.lbserver.xyz/api/v2/download?format={fmt}&url={encoded_url}&apikey=dfcb6d76f2f6a9894gjkege8a4ab232222"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                    "Referer": "https://loader.to/",
                    "Origin": "https://loader.to",
                }
                raw = fetch_converter_upstream(lto_url, headers=headers, timeout=9)
                data = json.loads(raw.decode("utf-8") if isinstance(raw, bytes) else str(raw))
                if data and data.get("id"):
                    dl = data.get("download_url")
                    if dl:
                        if "://p.savenow.to/" in dl or "://lto2.affadaffa.com/" in dl or any(ad in dl.lower() for ad in ["ey43.com", "/ad/", "hoofsduke", "converttr.org", "google.com"]):
                            dl = None
                        elif dl.startswith("http://"):
                            dl = dl.replace("http://", "https://")
                    return {"success": True, "id": data.get("id"), "engine": "loader", "download_url": dl}
                elif data and (data.get("text") or data.get("error") or data.get("message")):
                    captured_err = str(data.get("text") or data.get("error") or data.get("message"))
                    if re.search(r"country|region|unavailable|blocked|not available", captured_err, re.I):
                        is_geo = True
            except Exception as e:
                print(f"[LOADER_LBSERVER_WARN] {e}")

        elif eng == "savenow":
            try:
                token = get_savenow_pow_token()
                api_url = f"https://p.savenow.to/api/v2/download?format={fmt}&url={encoded_url}&apikey=dfcb6d76f2f6a9894gjkege8a4ab232222"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                    "Referer": "https://savenow.to/",
                    "Origin": "https://savenow.to",
                }
                if token:
                    headers["Authorization"] = f"Bearer {token}"
                raw = fetch_converter_upstream(api_url, headers=headers, timeout=9)
                data = json.loads(raw.decode("utf-8") if isinstance(raw, bytes) else str(raw))
                if data and data.get("id"):
                    dl = data.get("download_url")
                    if dl:
                        if "://p.savenow.to/" in dl or "://lto2.affadaffa.com/" in dl or any(ad in dl.lower() for ad in ["ey43.com", "/ad/", "hoofsduke", "converttr.org", "google.com"]):
                            dl = None
                        elif dl.startswith("http://"):
                            dl = dl.replace("http://", "https://")
                    return {"success": True, "id": data.get("id"), "engine": "savenow", "download_url": dl}
                elif data and (data.get("text") or data.get("error") or data.get("message")):
                    captured_err = str(data.get("text") or data.get("error") or data.get("message"))
                    if re.search(r"country|region|unavailable|blocked|not available", captured_err, re.I):
                        is_geo = True
            except Exception as e:
                print(f"[SAVENOW_CONVERT_WARN] {e}")

    if captured_err:
        return {"success": False, "error": captured_err, "is_geo_blocked": is_geo}

    raise HTTPException(status_code=502, detail="Unable to initiate media conversion")

@app.get("/api/progress")
async def proxy_progress(id: str):
    token = get_savenow_pow_token()
    endpoints = [
        f"https://p.lbserver.xyz/api/progress?id={id}",
        f"https://p.savenow.to/api/progress?id={id}",
        f"https://lto2.affadaffa.com/api/progress?id={id}"
    ]
    for ep in endpoints:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "Referer": "https://savenow.to/",
                "Origin": "https://savenow.to",
            }
            if token:
                headers["Authorization"] = f"Bearer {token}"
            raw = fetch_converter_upstream(ep, headers=headers, timeout=6)
            data = json.loads(raw.decode("utf-8") if isinstance(raw, bytes) else str(raw))
            if data:
                # Sanitize download_url if present
                if data.get("download_url"):
                    dl = str(data["download_url"]).strip()
                    # Reject ad gateway URLs (p.savenow.to and lto2.affadaffa.com are ad gateways; real files are on worker nodes like *.savenow.to)
                    if "://p.savenow.to/" in dl or "://lto2.affadaffa.com/" in dl or any(ad in dl.lower() for ad in ["ey43.com", "/ad/", "hoofsduke", "converttr.org", "google.com"]):
                        data["download_url"] = None
                    elif dl.startswith("http://"):
                        data["download_url"] = dl.replace("http://", "https://")
                return data
        except Exception:
            continue
    raise HTTPException(status_code=502, detail="Progress check failed")

@app.get("/api/report-issue")
@app.post("/api/report-issue")
async def report_issue(request: Request):
    try:
        if request.method == "POST":
            try:
                body = await request.json()
            except Exception:
                body = {}
        else:
            body = dict(request.query_params)

        video_url = str(body.get("video_url", "Unknown"))
        video_title = str(body.get("video_title", "Unknown"))
        selected_format = str(body.get("format", body.get("selected_format", "Unknown")))
        error_detail = str(body.get("error", body.get("error_detail", "Stream conversion failed")))
        user_agent = request.headers.get("user-agent", "Unknown")
        client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "Unknown")
        
        # Ignore malformed or fake URLs (e.g. "www.youtube", empty, or non-YouTube inputs)
        has_valid_id = bool(re.search(r"(?:v=|\/shorts\/|\/live\/|\/)([a-zA-Z0-9_-]{11})(?:[?&#/\s]|$)", video_url))
        if not has_valid_id or "www.youtube" in video_url.lower() and not re.search(r"v=[a-zA-Z0-9_-]{11}", video_url):
            return {"success": False, "ignored": True, "reason": "invalid_url_input"}

        # Log incident for analytics
        print(f"[CONVERSION_ISSUE_REPORT] URL: {video_url} | Title: {video_title} | Format: {selected_format} | Error: {error_detail} | IP: {client_ip}")
        
        # Real-time Telegram Bot Notification
        tg_token = os.environ.get("TELEGRAM_BOT_TOKEN") or "8717205816:AAGdAXIPjaUg986TTJU3n0UFe0wZxfIO3oo"
        tg_chat_id = os.environ.get("TELEGRAM_CHAT_ID") or "7396061312"
        if tg_token and tg_chat_id:
            try:
                import html as html_lib
                safe_title = html_lib.escape(video_title[:90])
                safe_url = html_lib.escape(video_url)
                safe_fmt = html_lib.escape(selected_format)
                safe_err = html_lib.escape(error_detail)
                safe_ip = html_lib.escape(client_ip)

                err_low = error_detail.lower()
                is_expected_restr = any(k in err_low for k in [
                    "broadcaster", "live stream", "private", "age-restricted", "age restricted", 
                    "video too long", "membership", "region", "droits", "copyright", "unavailable"
                ])
                header_badge = "ℹ️ <b>[Broadcaster DRM / Region Restricted]</b>" if is_expected_restr else "🚨 <b>YT4MP3 Conversion Alert</b>"

                alert_text = (
                    f"{header_badge}\n\n"
                    f"🎬 <b>Video:</b> {safe_title}\n"
                    f"🔗 <b>Link:</b> {safe_url}\n"
                    f"🎛 <b>Format:</b> {safe_fmt}\n"
                    f"⚠️ <b>Status:</b> {safe_err}\n"
                    f"🌐 <b>User IP:</b> <code>{safe_ip}</code>"
                )
                if is_expected_restr:
                    alert_text += "\n💡 <i>Handled gracefully by Broadcaster DRM Shield.</i>"
                tg_url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
                tg_payload = json.dumps({
                    "chat_id": tg_chat_id,
                    "text": alert_text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True
                }).encode("utf-8")
                tg_req = urllib.request.Request(
                    tg_url, 
                    data=tg_payload, 
                    headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(tg_req, timeout=6) as tg_res:
                    tg_resp_data = json.loads(tg_res.read().decode('utf-8'))
                    return {"success": True, "message": "Issue recorded and Telegram alert sent!", "telegram": tg_resp_data}
            except Exception as tg_err:
                print(f"Telegram notification dispatch error: {tg_err}")
                return {"success": True, "message": "Issue recorded", "telegram_error": str(tg_err)}
                
        return {"success": True, "message": "Issue recorded. Thank you for reporting!"}
    except Exception as e:
        return {"success": False, "detail": str(e)}


# ==============================================================================
# LONG VIDEO ENGINE (3+ hours) via public cobalt instances
# savenow.to / loader.to reject videos longer than 3 hours. Cobalt instances have
# no such limit and return a direct streaming "tunnel" URL. Cobalt does not send
# CORS headers, so the browser calls this proxy, then downloads the tunnel URL directly.
# ==============================================================================
COBALT_INSTANCES = [
    i.strip() for i in (os.environ.get("COBALT_INSTANCES") or "https://cobaltapi.cjs.nz/,https://rue-cobalt.xenon.zone/,https://api.cobalt.liubquanti.click/").split(",") if i.strip()
]

@app.get("/api/long-video")
@app.get("/api/free-convert")
async def long_video(url: str, mode: str = "audio", quality: str = "720", format: str = "mp3"):
    if not re.search(r"(youtube\.com|youtu\.be)", url or ""):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    clean_fmt = (format or "mp3").lower().strip()
    body = {"url": url, "filenameStyle": "basic"}
    if mode == "audio":
        audio_fmt = "mp3"
        if clean_fmt in ["wav", "opus"]:
            audio_fmt = clean_fmt
        elif clean_fmt in ["m4a", "aac"]:
            audio_fmt = "best"
        body.update({"downloadMode": "audio", "audioFormat": audio_fmt, "audioBitrate": "320"})
    else:
        q = re.sub(r"[^0-9]", "", str(quality)) or "720"
        if q not in ["144", "240", "360", "480", "720", "1080", "1440", "2160"]:
            q = "720"
        codec = "vp9" if q in ("1440", "2160") else "h264"
        body.update({"downloadMode": "auto", "videoQuality": q, "youtubeVideoCodec": codec})

    last_err = "No free conversion engine available"
    is_age = False
    is_unavail = False

    for inst in COBALT_INSTANCES:
        try:
            req = urllib.request.Request(
                inst,
                data=json.dumps(body).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130 Safari/537.36",
                },
            )
            with urllib.request.urlopen(req, timeout=12) as res:
                data = json.loads(res.read().decode("utf-8"))
            if data.get("status") in ("tunnel", "redirect") and data.get("url"):
                return {"success": True, "download_url": data["url"], "filename": data.get("filename", ""), "engine": "cobalt"}
            
            err_code = str((data.get("error") or {}).get("code") or data.get("status") or "")
            if "age" in err_code:
                is_age = True
                last_err = "This video is 18+ age-restricted on YouTube."
                break
            elif "unavailable" in err_code:
                is_unavail = True
                last_err = "This video is unavailable or private on YouTube."
                break
            last_err = err_code or "unknown"
        except urllib.error.HTTPError as e:
            try:
                err_body = json.loads(e.read().decode("utf-8", "ignore"))
                err_code = str((err_body.get("error") or {}).get("code") or "")
                if "age" in err_code:
                    is_age = True
                    last_err = "This video is 18+ age-restricted on YouTube."
                    break
                elif "unavailable" in err_code:
                    is_unavail = True
                    last_err = "This video is unavailable or private on YouTube."
                    break
                last_err = err_code or f"HTTP {e.code}"
            except Exception:
                last_err = f"HTTP {e.code}"
        except Exception as e:
            last_err = str(e)

    return {
        "success": False, 
        "error": last_err, 
        "is_age_restricted": is_age, 
        "is_unavailable": is_unavail, 
        "engine": "cobalt"
    }


# ==============================================================================
# FASTSAVER ENGINE — Paid Pro API with multi-tier caching & in-flight locking
# Prevents duplicate credit consumption on repeat clicks and concurrent requests
# ==============================================================================
FASTSAVER_API_KEY = os.environ.get("FASTSAVER_API_KEY") or "fs_sk_9w9n0d9x3t0r0g2g0d3e0j3f6u7q"
FASTSAVER_LOW_CREDIT_THRESHOLD = 10000
FASTSAVER_CACHE_FILE = "/tmp/fastsaver_cache.json"
_LAST_FS_BALANCE_CHECK_TS = 0.0
_LAST_FS_LOW_ALERT_TS = 0.0
_FASTSAVER_LINK_CACHE = {}
_FASTSAVER_IN_FLIGHT = {}
_FASTSAVER_LOCK = asyncio.Lock()

def _get_fastsaver_cache(key: str) -> dict:
    global _FASTSAVER_LINK_CACHE
    import time
    now = time.time()
    # 1. In-memory check
    if key in _FASTSAVER_LINK_CACHE:
        entry = _FASTSAVER_LINK_CACHE[key]
        if (now - entry.get("ts", 0)) < 250:  # 250s TTL (safe margin before FastSaver 5m expiry)
            return entry.get("data")
        else:
            _FASTSAVER_LINK_CACHE.pop(key, None)
    # 2. Local disk (/tmp) check across container warm starts
    if os.path.exists(FASTSAVER_CACHE_FILE):
        try:
            with open(FASTSAVER_CACHE_FILE, "r", encoding="utf-8") as f:
                disk = json.load(f)
                if key in disk:
                    d_entry = disk[key]
                    if (now - d_entry.get("ts", 0)) < 250:
                        _FASTSAVER_LINK_CACHE[key] = d_entry
                        return d_entry.get("data")
        except Exception:
            pass
    return None

def _set_fastsaver_cache(key: str, data: dict) -> None:
    global _FASTSAVER_LINK_CACHE
    import time
    now = time.time()
    _FASTSAVER_LINK_CACHE[key] = {"data": data, "ts": now}
    try:
        active = {k: v for k, v in _FASTSAVER_LINK_CACHE.items() if (now - v.get("ts", 0)) < 250}
        _FASTSAVER_LINK_CACHE = active
        with open(FASTSAVER_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(active, f)
    except Exception:
        pass

def _fetch_fastsaver_balance() -> dict:
    try:
        req = urllib.request.Request(
            "https://api.fastsaver.io/v1/balance",
            headers={
                "X-Api-Key": FASTSAVER_API_KEY,
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130 Safari/537.36",
            },
        )
        with urllib.request.urlopen(req, timeout=6) as res:
            data = json.loads(res.read().decode("utf-8"))
            if isinstance(data, dict) and data.get("ok"):
                return data
    except Exception:
        pass
    return {}

def _check_fastsaver_credits_and_alert(force_check: bool = False, test_alert: bool = False) -> dict:
    global _LAST_FS_BALANCE_CHECK_TS, _LAST_FS_LOW_ALERT_TS
    import time
    now = time.time()
    if not force_check and not test_alert and (now - _LAST_FS_BALANCE_CHECK_TS < 300):
        return {"checked": False}
    _LAST_FS_BALANCE_CHECK_TS = now

    bal = _fetch_fastsaver_balance()
    if not bal:
        return {"checked": True, "ok": False}

    credits = int(bal.get("credits", 0))
    plan_credits = int(bal.get("plan_credits", 100000))
    plan_name = str(bal.get("plan", "Pro"))
    expire_label = str(bal.get("expire_label", ""))

    should_alert = test_alert or (credits <= FASTSAVER_LOW_CREDIT_THRESHOLD)
    alert_sent = False

    if should_alert:
        stats = _load_analytics(force_cloud=False)
        last_alert_ts = max(float(_LAST_FS_LOW_ALERT_TS), float(stats.get("fs_al_ts", 0) or 0))
        # Send immediately on first drop <= 10k, then remind at most once every 6 hours
        if test_alert or (now - last_alert_ts >= 21600):
            tg_token = os.environ.get("TELEGRAM_BOT_TOKEN") or "8717205816:AAGdAXIPjaUg986TTJU3n0UFe0wZxfIO3oo"
            tg_chat_id = os.environ.get("TELEGRAM_CHAT_ID") or "7396061312"
            if tg_token and tg_chat_id:
                try:
                    header_tag = "🧪 <b>[TEST] FastSaver Low Credits Alert</b>" if test_alert else "⚠️ <b>FastSaver API Low Credits Alert!</b>"
                    msg = (
                        f"{header_tag}\n\n"
                        f"🔋 <b>Remaining Credits:</b> <code>{credits:,}</code> / <code>{plan_credits:,}</code>\n"
                        f"📉 <b>Alert Threshold:</b> <code>{FASTSAVER_LOW_CREDIT_THRESHOLD:,} credits</code>\n"
                        f"📦 <b>Current Plan:</b> {plan_name} ({expire_label})\n\n"
                        "⚡ <i>Aapke FastSaver API me 10,000 ya us se kam credits reh gaye hain. 4K aur long videos ka backup chalta rakhne ke liye credits top-up kar lein:</i>\n"
                        "🔗 https://api.fastsaver.io/pricing"
                    )
                    tg_payload = json.dumps({
                        "chat_id": tg_chat_id,
                        "text": msg,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": True,
                    }).encode("utf-8")
                    tg_req = urllib.request.Request(
                        f"https://api.telegram.org/bot{tg_token}/sendMessage",
                        data=tg_payload,
                        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
                    )
                    with urllib.request.urlopen(tg_req, timeout=6) as tg_res:
                        tg_data = json.loads(tg_res.read().decode("utf-8"))
                        alert_sent = bool(tg_data.get("ok"))
                    if alert_sent and not test_alert:
                        _LAST_FS_LOW_ALERT_TS = now
                        stats["fs_al_ts"] = int(now)
                        _save_analytics(stats, force_cloud=True)
                except Exception as e:
                    print(f"FastSaver low-credit Telegram alert error: {e}")

    return {
        "checked": True,
        "ok": True,
        "credits": credits,
        "plan_credits": plan_credits,
        "plan": plan_name,
        "threshold": FASTSAVER_LOW_CREDIT_THRESHOLD,
        "is_low": credits <= FASTSAVER_LOW_CREDIT_THRESHOLD,
        "alert_sent": alert_sent,
    }

@app.get("/api/fastsaver-balance-check")
async def fastsaver_balance_check(test_alert: int = 0):
    return _check_fastsaver_credits_and_alert(force_check=True, test_alert=(int(test_alert) == 1))

@app.get("/api/fastsaver-video")
async def fastsaver_video(url: str, mode: str = "audio", quality: str = "720", format: str = ""):
    if not re.search(r"(youtube\.com|youtu\.be)", url or ""):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    # Extract YouTube ID for smart caching
    vid = None
    m = re.search(r"(?:v=|\/embed\/|\/shorts\/|youtu\.be\/|\/v\/|watch\?v=|\&v=|^)([a-zA-Z0-9_-]{11})(?:[&?]|$)", url or "")
    if m:
        vid = m.group(1)

    req_fmt = (format or "").strip().lower()
    is_audio = (mode == "audio") or (req_fmt in ("audio", "mp3", "m4a", "flac", "wav", "aac", "ogg", "opus"))

    # Shared cache key: all audio formats for same video share 1 key (0 repeat credit consumption!)
    if is_audio:
        mode = "audio"
        fmt = "audio"
        cache_key = f"{vid}_audio"
    else:
        mode = "video"
        q = re.sub(r"[^0-9]", "", str(quality)) or "720"
        fmt_map = {"2160": "2160p", "1440": "1440p", "1080": "1080p", "720": "720p", "480": "480p", "360": "360p", "240": "240p", "144": "144p"}
        fmt = fmt_map.get(q, "720p")
        cache_key = f"{vid}_{fmt}"

    # Edge CDN caching headers: Vercel CDN caches at Edge nodes worldwide for 240s
    edge_headers = {
        "Cache-Control": "public, s-maxage=240, max-age=240, stale-while-revalidate=30",
        "Content-Type": "application/json; charset=utf-8"
    }

    # 1. Multi-tier Cache check (Memory + /tmp disk)
    if vid:
        cached_entry = _get_fastsaver_cache(cache_key)
        if cached_entry:
            return Response(content=json.dumps(cached_entry), media_type="application/json", headers=edge_headers)

    # 2. In-flight request deduplication lock (If 2 clicks happen simultaneously, request 2 waits for request 1)
    future_to_wait = None
    async with _FASTSAVER_LOCK:
        if cache_key in _FASTSAVER_IN_FLIGHT:
            future_to_wait = _FASTSAVER_IN_FLIGHT[cache_key]
        else:
            loop = asyncio.get_running_loop()
            _FASTSAVER_IN_FLIGHT[cache_key] = loop.create_future()

    if future_to_wait:
        try:
            in_flight_resp = await asyncio.wait_for(future_to_wait, timeout=45)
            if in_flight_resp and in_flight_resp.get("success"):
                return Response(content=json.dumps(in_flight_resp), media_type="application/json", headers=edge_headers)
        except Exception:
            pass

    # 3. Call FastSaver API directly
    headers = {
        "X-Api-Key": FASTSAVER_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130 Safari/537.36",
    }
    fmts_to_try = [fmt]
    if fmt == "2160p":
        fmts_to_try = ["2160p", "1440p", "1080p"]
    elif fmt == "1440p":
        fmts_to_try = ["1440p", "1080p"]

    resp_payload = None
    try:
        for try_fmt in fmts_to_try:
            body = json.dumps({"url": url, "format": try_fmt}).encode("utf-8")
            try:
                req = urllib.request.Request(
                    "https://api.fastsaver.io/v1/youtube/download",
                    data=body,
                    headers=headers,
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=55) as res:
                    data = json.loads(res.read().decode("utf-8"))
                _check_fastsaver_credits_and_alert(force_check=True)
                if data.get("ok") and data.get("download_url"):
                    resp_payload = {
                        "success": True,
                        "download_url": data["download_url"],
                        "filename": data.get("filename", ""),
                        "engine": "fastsaver",
                        "format_used": try_fmt,
                        "cached": False,
                    }
                    if vid:
                        _set_fastsaver_cache(cache_key, {**resp_payload, "cached": True})
                    break
                else:
                    resp_payload = {"success": False, "error": data.get("detail", "fastsaver_unknown_error")}
            except urllib.error.HTTPError as e:
                try:
                    err_body = json.loads(e.read().decode("utf-8", "ignore"))
                    detail = err_body.get("detail", f"HTTP {e.code}")
                except Exception:
                    detail = f"HTTP {e.code}"
                _check_fastsaver_credits_and_alert(force_check=False)
                is_age = any(k in str(detail).lower() for k in ("age_restrict", "age-restrict", "confirm your age", "sign in to confirm"))
                resp_payload = {"success": False, "error": str(detail), "is_age_restricted": is_age}
                if is_age:
                    break
            except Exception as e:
                resp_payload = {"success": False, "error": str(e)}
    finally:
        # Resolve all waiting in-flight coroutines
        async with _FASTSAVER_LOCK:
            fut = _FASTSAVER_IN_FLIGHT.pop(cache_key, None)
            if fut and not fut.done():
                fut.set_result(resp_payload or {"success": False, "error": "unknown"})

    if resp_payload and resp_payload.get("success"):
        return Response(content=json.dumps(resp_payload), media_type="application/json", headers=edge_headers)
    else:
        no_cache_headers = {"Cache-Control": "no-store, max-age=0", "Content-Type": "application/json; charset=utf-8"}
        return Response(content=json.dumps(resp_payload or {"success": False}), media_type="application/json", headers=no_cache_headers)


def build_proxy_candidates(allowed: list) -> list:
    """Ordered list of (label, proxy_url, country_lower) across all active multi-proxy pool IPs."""
    import random
    allowed_set = {str(c).upper() for c in (allowed or [])}
    candidates = []

    # 1. If specific allowed countries are identified, prioritize matching pool
    matched_ccs = [cc for cc in WEBSHARE_POOL_PRIORITY if cc in allowed_set]
    if matched_ccs:
        for cc in matched_ccs:
            ips = list(WEBSHARE_POOLS.get(cc, []))
            random.shuffle(ips)
            for i, ip in enumerate(ips):
                candidates.append((f"Webshare-{cc}-{i+1}", f"http://{WEBSHARE_USER}:{WEBSHARE_PASS}@{ip}", cc.lower()))
        for cc in WEBSHARE_POOL_PRIORITY:
            if cc not in matched_ccs:
                ips = list(WEBSHARE_POOLS.get(cc, []))
                random.shuffle(ips)
                for i, ip in enumerate(ips[:2]):
                    candidates.append((f"Webshare-{cc}-{i+1}", f"http://{WEBSHARE_USER}:{WEBSHARE_PASS}@{ip}", cc.lower()))
        return candidates

    # 2. If allowed countries are unknown (e.g. watch page scraping blocked by bot protection):
    # Interleave pools so that GB (UK), US (USA), FR (France), JP (Japan), CO are tested round-robin!
    pools_copy = {}
    for cc in ["GB", "US", "FR", "JP", "CO"]:
        ips = list(WEBSHARE_POOLS.get(cc, []))
        random.shuffle(ips)
        pools_copy[cc] = ips

    max_len = max((len(v) for v in pools_copy.values()), default=0)
    for idx in range(max_len):
        for cc in ["GB", "US", "FR", "JP", "CO"]:
            if idx < len(pools_copy[cc]):
                ip = pools_copy[cc][idx]
                candidates.append((f"Webshare-{cc}-{idx+1}", f"http://{WEBSHARE_USER}:{WEBSHARE_PASS}@{ip}", cc.lower()))

    return candidates

def detect_video_allowed_countries(vid: str) -> list:
    yt_url = f"https://www.youtube.com/watch?v={vid}"
    req = urllib.request.Request(
        yt_url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"}
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            html = r.read().decode("utf-8", "ignore")
        m = re.search(r'"availableCountries":\s*(\[[^\]]+\])', html)
        if m:
            return json.loads(m.group(1))
    except Exception as e:
        print("Country detection error:", e)
    return []

def get_yt_cookies_file():
    """Resolves YouTube cookies from environment variable YOUTUBE_COOKIES or local cookies.txt.
    Always copies or writes to a writable temporary directory so yt-dlp cookie writebacks
    never fail with [Errno 30] Read-only file system on Vercel/AWS Lambda."""
    import tempfile
    import shutil
    import base64

    writable_path = os.path.join(tempfile.gettempdir(), "yt4mp3_cookies.txt")

    raw_cookies = os.environ.get("YOUTUBE_COOKIES")
    if raw_cookies and len(raw_cookies.strip()) > 50:
        cleaned_cookies = raw_cookies.strip()
        if not cleaned_cookies.startswith("#") and "\t" not in cleaned_cookies:
            try:
                cleaned_cookies = base64.b64decode(cleaned_cookies).decode("utf-8", errors="ignore")
            except Exception:
                pass
        if "\\n" in cleaned_cookies and "\n" not in cleaned_cookies:
            cleaned_cookies = cleaned_cookies.replace("\\n", "\n")

        if "\t" in cleaned_cookies and ("youtube" in cleaned_cookies or "google" in cleaned_cookies):
            try:
                with open(writable_path, "w", encoding="utf-8") as cf:
                    cf.write(cleaned_cookies)
                return writable_path
            except Exception:
                pass

    candidates = [
        os.path.join(os.getcwd(), "cookies.txt"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cookies.txt"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt"),
        "/etc/secrets/cookies.txt",
        r"C:\Users\Admin\Downloads\cookies.txt",
    ]
    for c_path in candidates:
        if os.path.exists(c_path) and os.path.getsize(c_path) > 20:
            try:
                shutil.copy2(c_path, writable_path)
                return writable_path
            except Exception:
                return c_path
    return None

INVIDIOUS_PIPED_INSTANCES = [
    # Top Live Invidious & Piped Nodes
    {"type": "invidious", "url": "https://yt.chocolatemoo53.com"},
    {"type": "invidious", "url": "https://inv.nadeko.net"},
    {"type": "invidious", "url": "https://invidious.nerdvpn.de"},
    {"type": "invidious", "url": "https://invidious.tiekoetter.com"},
    {"type": "piped", "url": "https://pipedapi.adminforge.de"},
    {"type": "piped", "url": "https://pipedapi.reallyaweso.me"},
]

def _probe_single_instance(inst: dict, vid: str, is_audio: bool) -> str | None:
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    base = inst["url"]
    itype = inst["type"]
    try:
        if itype == "invidious":
            endpoint = f"{base}/api/v1/videos/{vid}"
            req = urllib.request.Request(endpoint, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=2.5, context=ctx) as r:
                data = json.loads(r.read().decode("utf-8"))
            if is_audio:
                for fmt in data.get("adaptiveFormats", []):
                    if (fmt.get("type") or "").startswith("audio/") and fmt.get("url"):
                        return fmt["url"]
            for fmt in data.get("formatStreams", []):
                if fmt.get("url"):
                    return fmt["url"]
        elif itype == "piped":
            endpoint = f"{base}/streams/{vid}"
            req = urllib.request.Request(endpoint, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=2.5, context=ctx) as r:
                data = json.loads(r.read().decode("utf-8"))
            if is_audio:
                streams = data.get("audioStreams", [])
                if streams and streams[0].get("url"):
                    return streams[0]["url"]
            streams = [s for s in data.get("videoStreams", []) if not s.get("videoOnly")]
            if streams and streams[0].get("url"):
                return streams[0]["url"]
    except Exception:
        pass
    return None

def fetch_invidious_piped_stream(vid: str, is_audio: bool = False) -> str | None:
    """Fast concurrent fallback across top Invidious and Piped public instances."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    try:
        with ThreadPoolExecutor(max_workers=len(INVIDIOUS_PIPED_INSTANCES)) as executor:
            futs = {executor.submit(_probe_single_instance, inst, vid, is_audio): inst for inst in INVIDIOUS_PIPED_INSTANCES}
            for future in as_completed(futs, timeout=3.0):
                try:
                    res = future.result()
                    if res:
                        return res
                except Exception:
                    pass
    except Exception:
        pass
    return None

@app.get("/api/geo-stream-check")
async def geo_stream_check(url: str = "", format: str = "mp3"):
    clean_url = (url or "").strip()
    vid = None
    m = re.search(r"(?:v=|\/embed\/|\/shorts\/|youtu\.be\/|\/v\/|watch\?v=|\&v=|^)([a-zA-Z0-9_-]{11})(?:[&?]|$)", clean_url)
    if m:
        vid = m.group(1)
    elif len(clean_url) == 11 and re.match(r"^[a-zA-Z0-9_-]{11}$", clean_url):
        vid = clean_url

    if not vid or len(vid) != 11:
        return {"success": False, "error": "invalid_url"}

    fmt_clean = (format or "mp3").lower().strip()
    is_audio = fmt_clean in ["mp3", "m4a", "flac", "wav", "aac", "ogg", "opus", "audio", "320", "256", "128", "64"]

    # Check cache first
    import tempfile
    cache_type = "audio" if is_audio else "video"
    cache_path = os.path.join(tempfile.gettempdir(), f"yt4mp3_geo_{vid}_{cache_type}.dat")
    if os.path.exists(cache_path) and os.path.getsize(cache_path) > 10000:
        return {"success": True, "download_url": f"/api/geo-stream?url={urllib.parse.quote(clean_url)}&format={fmt_clean}", "cached": True}

    cookie_file = get_yt_cookies_file()
    allowed = detect_video_allowed_countries(vid)
    proxy_candidates = build_proxy_candidates(allowed)
    fmt_selector = "140/ba[protocol^=http]/18/b[protocol^=http]/best[protocol^=http]" if is_audio else "18/22/b[protocol^=http]/bv[protocol^=http][ext=mp4]/best[protocol^=http]"

    import yt_dlp
    stream_url = None
    last_err = None
    target_country = proxy_candidates[0][2] if proxy_candidates else "gb"

    attempts = [(c, None) for c in proxy_candidates[:2]]
    # Innertube embedded clients for bypass of soft age-gates / embedding allowed
    if proxy_candidates:
        attempts.append(((proxy_candidates[0][0], proxy_candidates[0][1], proxy_candidates[0][2]), ["tv_embedded"]))
    attempts.append((("Direct-Server", None, "us"), None))
    for attempt, ((proxy_label, proxy_url, cand_country), client) in enumerate(attempts):
        ydl_opts = {
            "proxy": proxy_url,
            "quiet": True,
            "no_warnings": True,
            "format": fmt_selector if client is None else ("140/ba[protocol^=http]/18/b[protocol^=http]/best[protocol^=http]" if is_audio else "18/22/b[protocol^=http]/bv[protocol^=http][ext=mp4]/best[protocol^=http]"),
            "noplaylist": True,
            "socket_timeout": 8,
            "js_runtimes": {"node": {}, "deno": {}},
        }
        if client:
            ydl_opts["extractor_args"] = {"youtube": {"player_client": client}}
            if client in (["tv_embedded"], ["web_embedded"]):
                ydl_opts["http_headers"] = {
                    "Referer": f"https://www.youtube.com/embed/{vid}",
                    "Origin": "https://www.youtube.com",
                }
        if not proxy_url and cookie_file:
            ydl_opts["cookiefile"] = cookie_file
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={vid}", download=False)
            if info:
                cand_url = info.get("url")
                if not cand_url and info.get("requested_formats"):
                    if is_audio:
                        audio_fmts = [f for f in info["requested_formats"] if f.get("vcodec") == "none"]
                        cand_url = audio_fmts[-1].get("url") if audio_fmts else info["requested_formats"][-1].get("url")
                    else:
                        cand_url = info["requested_formats"][0].get("url")
                if cand_url:
                    stream_url = cand_url
                    target_country = cand_country
                    break
        except Exception as e:
            last_err = e
            continue

    # Fallback to public Invidious / Piped cluster if yt-dlp was blocked by age-gate
    if not stream_url:
        try:
            inv_stream = fetch_invidious_piped_stream(vid, is_audio)
            if inv_stream:
                stream_url = inv_stream
        except Exception:
            pass

    if stream_url:
        country_param = f"&country={target_country}" if target_country else ""
        return {
            "success": True,
            "download_url": f"/api/geo-stream?url={urllib.parse.quote(clean_url)}&format={fmt_clean}{country_param}",
            "country": target_country
        }
    is_age = any(k in str(last_err).lower() for k in ("age", "sign in to confirm", "confirm your age", "inappropriate"))
    return {
        "success": False,
        "error": "all_proxies_exhausted",
        "is_age_restricted": is_age,
        "detail": str(last_err),
        "country": target_country
    }


@app.get("/api/geo-stream")
async def geo_stream(url: str = "", format: str = "mp3", country: str = ""):
    clean_url = (url or "").strip()
    vid = None
    m = re.search(r"(?:v=|\/embed\/|\/shorts\/|youtu\.be\/|\/v\/|watch\?v=|\&v=|^)([a-zA-Z0-9_-]{11})(?:[&?]|$)", clean_url)
    if m:
        vid = m.group(1)
    elif len(clean_url) == 11 and re.match(r"^[a-zA-Z0-9_-]{11}$", clean_url):
        vid = clean_url

    if not vid or len(vid) != 11:
        return HTMLResponse(content="""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Invalid Link | YT4MP3</title>
<style>body{font-family:sans-serif;background:#f8fafc;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;}
.card{background:#fff;padding:32px;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.08);max-width:440px;text-align:center;border:1px solid #e2e8f0;}
h2{color:#e11d48;margin-top:0;}p{color:#475569;font-size:14px;line-height:1.5;}a{display:inline-block;margin-top:16px;background:#2563eb;color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:600;font-size:14px;}
</style></head>
<body><div class="card"><h2>⚠️ Invalid YouTube Link</h2><p>Please enter a valid YouTube video URL.</p><a href="/">Return to YT4MP3</a></div></body></html>""", status_code=400)

    # Detect allowed country
    target_country = (country or "").strip().lower()
    allowed = [target_country.upper()] if target_country else detect_video_allowed_countries(vid)
    if not target_country and allowed:
        priority_fast_countries = ["GB", "US", "DE", "IN", "JP", "SG", "FR", "CA", "AU", "NL", "KR", "BR"]
        for pc in priority_fast_countries:
            if pc in allowed:
                target_country = pc.lower()
                break
        if not target_country:
            target_country = str(allowed[0]).lower()
        if not target_country:
            target_country = str(allowed[0]).lower()

    fmt_clean = (format or "mp3").lower().strip()
    is_audio = fmt_clean in ["mp3", "m4a", "flac", "wav", "aac", "ogg", "opus", "audio", "320", "256", "128", "64"]
    default_ext = "m4a" if fmt_clean in ["m4a", "aac"] else ("mp3" if is_audio else "mp4")

    # 1. Zero-Bandwidth Cache Check: If file was already streamed, serve from /tmp with 0 MB proxy usage!
    import tempfile
    cache_type = "audio" if is_audio else "video"
    cache_path = os.path.join(tempfile.gettempdir(), f"yt4mp3_geo_{vid}_{cache_type}.dat")
    meta_path = os.path.join(tempfile.gettempdir(), f"yt4mp3_geo_{vid}_{cache_type}.meta")

    if os.path.exists(cache_path) and os.path.getsize(cache_path) > 10000:
        saved_title = f"YT4MP3_{vid}"
        saved_ext = default_ext
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as mf:
                    meta_lines = mf.read().splitlines()
                    if meta_lines:
                        saved_title = meta_lines[0].strip()
                    if len(meta_lines) > 1 and meta_lines[1].strip():
                        saved_ext = meta_lines[1].strip()
            except Exception:
                pass
        safe_title = re.sub(r'[\\/*?:"<>|]', "", saved_title).strip()
        safe_title = re.sub(r"[^\x20-\x7E]", "_", safe_title)[:80].strip() or f"YT4MP3_{vid}"
        filename = f"{safe_title}.{saved_ext}"
        file_size = os.path.getsize(cache_path)
        content_type = "audio/mp4" if saved_ext == "m4a" else ("audio/mpeg" if saved_ext == "mp3" else "video/mp4")

        def iter_cached_file():
            with open(cache_path, "rb") as cf:
                while True:
                    chunk = cf.read(128 * 1024)
                    if not chunk:
                        break
                    yield chunk

        resp_headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "public, max-age=3600",
            "Content-Length": str(file_size),
            "Accept-Ranges": "bytes",
            "X-Proxy-Cached": "1",
        }
        return StreamingResponse(iter_cached_file(), media_type=content_type, headers=resp_headers)

    # Audio format selector: prefer lightweight pure AAC audio (140/ba, ~20MB) to conserve proxy bandwidth;
    # Video format selector: progressive video stream (18/22/b, ~360p-720p).
    fmt_selector = "140/ba[protocol^=http]/18/b[protocol^=http]/best[protocol^=http]" if is_audio else "18/22/b[protocol^=http]/bv[protocol^=http][ext=mp4]/best[protocol^=http]"

    try:
        import yt_dlp

        cookie_file = get_yt_cookies_file()
        info = None
        stream_url = None
        raw_title = f"YT4MP3_{vid}"
        actual_ext = default_ext
        last_extract_err = None

        # Smart rotation: Webshare country proxies first
        proxy_candidates = build_proxy_candidates(allowed)
        attempts = [(c, None) for c in proxy_candidates[:2]]
        # Innertube embedded clients for bypass of soft age-gates / embedding allowed
        if proxy_candidates:
            attempts.append(((proxy_candidates[0][0], proxy_candidates[0][1], proxy_candidates[0][2]), ["tv_embedded"]))
        attempts.append((("Direct-Server", None, "us"), None))
        for attempt, ((proxy_label, proxy_url, cand_country), client) in enumerate(attempts):
            target_country = cand_country

            ydl_opts = {
                "proxy": proxy_url,
                "quiet": True,
                "no_warnings": True,
                "format": fmt_selector if client is None else ("140/ba[protocol^=http]/18/b[protocol^=http]/best[protocol^=http]" if is_audio else "18/22/b[protocol^=http]/bv[protocol^=http][ext=mp4]/best[protocol^=http]"),
                "noplaylist": True,
                "extract_flat": False,
                "socket_timeout": 15,
                # Let yt-dlp solve YouTube JS challenges with whichever runtime exists (deno default, node if installed)
                "js_runtimes": {"deno": {}, "node": {}},
            }
            if client:
                ydl_opts["extractor_args"] = {"youtube": {"player_client": client}}
                if client in (["tv_embedded"], ["web_embedded"]):
                    ydl_opts["http_headers"] = {
                        "Referer": f"https://www.youtube.com/embed/{vid}",
                        "Origin": "https://www.youtube.com",
                    }
            if not proxy_url and cookie_file:
                ydl_opts["cookiefile"] = cookie_file

            # PO Token (Proof of Origin) & Visitor Data support to bypass bot challenges on datacenter IPs
            po_token = os.environ.get("YOUTUBE_PO_TOKEN")
            visitor_data = os.environ.get("YOUTUBE_VISITOR_DATA")
            if po_token or visitor_data:
                yt_args = ydl_opts.setdefault("extractor_args", {}).setdefault("youtube", {})
                if po_token:
                    yt_args["po_token"] = [
                        f"web.gvs+{po_token}",
                        f"web.player+{po_token}",
                        f"mweb.gvs+{po_token}",
                        f"mweb.player+{po_token}",
                    ]
                if visitor_data:
                    yt_args["visitor_data"] = [visitor_data]

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(f"https://www.youtube.com/watch?v={vid}", download=False)

                cand_url = None
                if info:
                    cand_url = info.get("url")
                    if not cand_url and info.get("requested_formats"):
                        if is_audio:
                            audio_fmts = [f for f in info["requested_formats"] if f.get("vcodec") == "none"]
                            cand_url = audio_fmts[-1].get("url") if audio_fmts else info["requested_formats"][-1].get("url")
                        else:
                            cand_url = info["requested_formats"][0].get("url")

                if cand_url:
                    upstream_headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                        "Accept": "*/*",
                        "Connection": "keep-alive",
                    }
                    # Use the exact headers yt-dlp resolved for this player client
                    if isinstance(info.get("http_headers"), dict):
                        upstream_headers.update({k: v for k, v in info["http_headers"].items() if k.lower() != "accept-encoding"})
                    if proxy_url:
                        opener = urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url}))
                    else:
                        opener = urllib.request.build_opener()
                    # Open the stream inside the attempt: an unsolved/blocked URL (403) falls through to the next client/proxy
                    upstream_res = opener.open(urllib.request.Request(cand_url, headers=upstream_headers), timeout=30)
                    stream_url = cand_url
                    raw_title = info.get("title") or raw_title
                    extracted_ext = info.get("ext") or ""
                    if is_audio:
                        actual_ext = extracted_ext if extracted_ext in ["m4a", "mp3", "aac"] else ("m4a" if extracted_ext == "mp4" else default_ext)
                    else:
                        actual_ext = extracted_ext or "mp4"
                    break
            except Exception as e:
                last_extract_err = e
                continue

        # Fallback to public Invidious / Piped cluster if yt-dlp failed
        if not stream_url:
            try:
                inv_stream = fetch_invidious_piped_stream(vid, is_audio)
                if inv_stream:
                    inv_headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                        "Accept": "*/*",
                        "Connection": "keep-alive",
                    }
                    upstream_res = urllib.request.urlopen(urllib.request.Request(inv_stream, headers=inv_headers), timeout=30)
                    stream_url = inv_stream
            except Exception:
                pass

        if not stream_url:
            # Telegram notification of DRM / proxy exhaust failure
            try:
                tg_token = os.environ.get("TELEGRAM_BOT_TOKEN") or "8717205816:AAGdAXIPjaUg986TTJU3n0UFe0wZxfIO3oo"
                tg_chat_id = os.environ.get("TELEGRAM_CHAT_ID") or "7396061312"
                if tg_token and tg_chat_id:
                    alert_text = (
                        f"🔒 <b>Geo Stream Blocked:</b>\n"
                        f"🎬 Video: <code>{vid}</code>\n"
                        f"🔗 Link: https://www.youtube.com/watch?v={vid}\n"
                        f"🎛 Format: {fmt_clean.upper()}\n"
                        f"⚠️ All proxies exhausted ({str(last_extract_err)[:70]})"
                    )
                    payload = json.dumps({
                        "chat_id": tg_chat_id,
                        "text": alert_text,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": True,
                    }).encode("utf-8")
                    tg_req = urllib.request.Request(
                        f"https://api.telegram.org/bot{tg_token}/sendMessage",
                        data=payload,
                        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
                    )
                    urllib.request.urlopen(tg_req, timeout=3).read()
            except Exception:
                pass

            return HTMLResponse(content=f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Playback Restricted | YT4MP3</title>
<style>body{{font-family:sans-serif;background:#f8fafc;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;}}
.card{{background:#fff;padding:32px;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.08);max-width:440px;text-align:center;border:1px solid #e2e8f0;}}
h2{{color:#e11d48;margin-top:0;}}p{{color:#475569;font-size:14px;line-height:1.5;}}a{{display:inline-block;margin-top:16px;background:#2563eb;color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:600;font-size:14px;}}
</style></head>
<body><div class="card"><h2>🔒 Regional DRM Protection</h2><p>This video is protected by regional broadcaster DRM and cannot be converted directly.</p><a href="/">Return to YT4MP3</a></div></body></html>""", status_code=403)

        safe_title = re.sub(r'[\\/*?:"<>|]', "", raw_title).strip()
        safe_title = re.sub(r"[^\x20-\x7E]", "_", safe_title)[:80].strip() or f"YT4MP3_{vid}"
        filename = f"{safe_title}.{actual_ext}"
        content_type = "audio/mp4" if actual_ext == "m4a" else ("audio/mpeg" if actual_ext == "mp3" else "video/mp4")

        content_len = upstream_res.headers.get("Content-Length")

        # Telegram notification of successful unlock
        try:
            tg_token = os.environ.get("TELEGRAM_BOT_TOKEN") or "8717205816:AAGdAXIPjaUg986TTJU3n0UFe0wZxfIO3oo"
            tg_chat_id = os.environ.get("TELEGRAM_CHAT_ID") or "-1003463852033"
            if tg_token and tg_chat_id:
                alert_text = (
                    f"🌍 <b>Geo Proxy Stream:</b>\n"
                    f"Unlocked <code>{vid}</code> via {proxy_label} ({fmt_clean.upper()})\n"
                    f"Title: {safe_title}"
                )
                payload = json.dumps({
                    "chat_id": tg_chat_id,
                    "text": alert_text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                }).encode("utf-8")
                tg_req = urllib.request.Request(
                    f"https://api.telegram.org/bot{tg_token}/sendMessage",
                    data=payload,
                    headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
                )
                urllib.request.urlopen(tg_req, timeout=3).read()
        except Exception:
            pass

        cache_part = f"{cache_path}.part"
        def stream_chunks():
            f_cache = None
            fully_downloaded = False
            try:
                f_cache = open(cache_part, "wb")
            except Exception:
                f_cache = None

            try:
                while True:
                    chunk = upstream_res.read(128 * 1024)
                    if not chunk:
                        fully_downloaded = True
                        break
                    if f_cache:
                        try:
                            f_cache.write(chunk)
                        except Exception:
                            pass
                    yield chunk
            finally:
                if f_cache:
                    try:
                        f_cache.close()
                    except Exception:
                        pass
                    if fully_downloaded:
                        try:
                            if os.path.exists(cache_path):
                                os.remove(cache_path)
                            os.rename(cache_part, cache_path)
                            with open(meta_path, "w", encoding="utf-8") as mf:
                                mf.write(f"{raw_title}\n{actual_ext}")
                        except Exception:
                            pass
                    else:
                        try:
                            if os.path.exists(cache_part):
                                os.remove(cache_part)
                        except Exception:
                            pass
                try:
                    upstream_res.close()
                except Exception:
                    pass

        resp_headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Accept-Ranges": "bytes",
        }
        if content_len:
            resp_headers["Content-Length"] = str(content_len)

        return StreamingResponse(stream_chunks(), media_type=content_type, headers=resp_headers)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Geo-proxy stream error: {str(e)}")


_VIDEO_RES_CACHE = {}

@app.get("/api/video-resolutions")
async def get_video_resolutions(id: str):
    vid = re.sub(r"[^a-zA-Z0-9_-]", "", id or "")
    if len(vid) != 11:
        return Response(content=json.dumps({"has_4k": False, "has_2k": False, "max_height": 1080, "duration_sec": 0}), media_type="application/json")
    if vid in _VIDEO_RES_CACHE:
        return Response(content=json.dumps(_VIDEO_RES_CACHE[vid]), media_type="application/json", headers={"Cache-Control": "public, s-maxage=86400, max-age=86400"})

    yt_url = f"https://www.youtube.com/watch?v={vid}"
    duration_sec = 0
    # 1. Fast check via YouTube watch page (zero credits)
    try:
        req = urllib.request.Request(
            yt_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        with urllib.request.urlopen(req, timeout=3) as res:
            html = res.read().decode("utf-8", "ignore")
        dur_match = re.search(r'"lengthSeconds":"(\d+)"', html)
        if dur_match:
            duration_sec = int(dur_match.group(1))

        # Detect regional country restrictions
        m_c = re.search(r'"availableCountries":\s*(\[[^\]]+\])', html)
        allowed_countries = json.loads(m_c.group(1)) if m_c else []
        is_geo_blocked = bool(
            (len(allowed_countries) > 0 and len(allowed_countries) < 150) or
            (re.search(r'"status":\s*"UNPLAYABLE"', html) and not re.search(r'Private|deleted|removed|terminated', html, re.I))
        )

        heights = [int(h) for h in re.findall(r'qualityLabel[^\d]+(\d+)p', html)]
        if heights and duration_sec > 0:
            max_h = max(heights)
            result = {
                "has_4k": max_h >= 2160 or 2160 in heights,
                "has_2k": max_h >= 1440 or 1440 in heights,
                "max_height": max_h,
                "duration_sec": duration_sec,
                "is_geo_blocked": is_geo_blocked,
                "source": "yt_watch",
            }
            _VIDEO_RES_CACHE[vid] = result
            return Response(content=json.dumps(result), media_type="application/json", headers={"Cache-Control": "public, s-maxage=86400, max-age=86400"})
    except Exception:
        pass

    # 2. FastSaver /v1/youtube/info (0.4s fast, 100% accurate 4K/2K detection when YouTube blocks datacenter IP)
    try:
        info_url = f"https://api.fastsaver.io/v1/youtube/info?url={urllib.parse.quote(yt_url)}"
        req = urllib.request.Request(
            info_url,
            headers={
                "X-Api-Key": FASTSAVER_API_KEY,
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130 Safari/537.36",
            },
        )
        with urllib.request.urlopen(req, timeout=4) as res:
            data = json.loads(res.read().decode("utf-8"))
        if data.get("ok"):
            raw_dur = data.get("duration") or data.get("lengthSeconds") or 0
            if isinstance(raw_dur, (int, float)):
                duration_sec = int(raw_dur)
            elif isinstance(raw_dur, str) and raw_dur.isdigit():
                duration_sec = int(raw_dur)

            fmt_names = [str(f.get("format", "")).lower() for f in (data.get("formats") or [])]
            has_4k = any("2160" in f or "4k" in f for f in fmt_names)
            has_2k = any("1440" in f or "2k" in f for f in fmt_names)
            result = {
                "has_4k": has_4k,
                "has_2k": has_2k,
                "max_height": 2160 if has_4k else (1440 if has_2k else 1080),
                "duration_sec": duration_sec,
                "is_geo_blocked": False,
                "source": "fastsaver_info",
            }
            _VIDEO_RES_CACHE[vid] = result
            return Response(content=json.dumps(result), media_type="application/json", headers={"Cache-Control": "public, s-maxage=86400, max-age=86400"})
    except Exception:
        pass

    default_result = {"has_4k": False, "has_2k": False, "max_height": 1080, "duration_sec": duration_sec, "source": "default"}
    return Response(content=json.dumps(default_result), media_type="application/json")


@app.get("/api/download-thumbnail")
async def download_thumbnail(id: str = ""):
    vid = (id or "").strip()
    if not re.match(r"^[a-zA-Z0-9_-]{11}$", vid):
        raise HTTPException(status_code=400, detail="Invalid YouTube video ID")
    for tier in ("maxresdefault", "sddefault", "hqdefault"):
        thumb_url = f"https://i.ytimg.com/vi/{vid}/{tier}.jpg"
        try:
            req = urllib.request.Request(
                thumb_url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130 Safari/537.36"},
            )
            with urllib.request.urlopen(req, timeout=6) as res:
                if res.status == 200:
                    img_bytes = res.read()
                    if len(img_bytes) > 1500:
                        return Response(
                            content=img_bytes,
                            media_type="image/jpeg",
                            headers={
                                "Content-Disposition": f'attachment; filename="YT4MP3-Thumbnail-{vid}-HD.jpg"',
                                "Cache-Control": "public, max-age=86400",
                            },
                        )
        except Exception:
            continue
    return RedirectResponse(url=f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg")


# ==============================================================================
# REAL-TIME VISITOR, DWELL-TIME & 12-HOUR PKT TELEGRAM ANALYTICS SYSTEM
# ==============================================================================
ANALYTICS_TMP_FILE = "/tmp/yt4mp3_analytics.json"
_LAST_CLOUD_SYNC_TS = 0.0

def _default_analytics() -> dict:
    import time
    return {
        "ts": int(time.time()),
        "all_u": 0,
        "all_dl": 0,
        "u": 0,
        "pv": 0,
        "dur_s": 0,
        "dur_n": 0,
        "max_s": 0,
        "dl": 0,
        "mp3": 0,
        "mp4": 0,
        "mob": 0,
        "dsk": 0,
        "c": {}
    }

def _fetch_cloud_analytics() -> dict:
    tg_token = os.environ.get("TELEGRAM_BOT_TOKEN") or "8717205816:AAGdAXIPjaUg986TTJU3n0UFe0wZxfIO3oo"
    if not tg_token:
        return {}
    try:
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{tg_token}/getMyDescription",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=4) as res:
            data = json.loads(res.read().decode("utf-8"))
            desc = (data.get("result") or {}).get("description", "")
            if desc and desc.startswith("YT4MP3_STATS:"):
                raw_json = desc[len("YT4MP3_STATS:"):]
                parsed = json.loads(raw_json)
                if isinstance(parsed, dict):
                    return parsed
    except Exception as e:
        print(f"Cloud analytics fetch notice: {e}")
    return {}

def _merge_analytics(base: dict, incoming: dict) -> dict:
    if not incoming:
        return base
    merged = _default_analytics()
    # If incoming has a newer period reset timestamp, prefer the newer period counters
    base_ts = int(base.get("ts") or 0)
    inc_ts = int(incoming.get("ts") or 0)
    merged["all_u"] = max(int(base.get("all_u") or 0), int(incoming.get("all_u") or 0))
    merged["all_dl"] = max(int(base.get("all_dl") or 0), int(incoming.get("all_dl") or 0))

    if abs(base_ts - inc_ts) <= 60 or base_ts == 0 or inc_ts == 0:
        merged["ts"] = max(base_ts, inc_ts) or merged["ts"]
        for k in ["u", "pv", "dur_s", "dur_n", "max_s", "dl", "mp3", "mp4", "mob", "dsk"]:
            merged[k] = max(int(base.get(k) or 0), int(incoming.get(k) or 0))
        c_merged = {}
        for src in [base.get("c") or {}, incoming.get("c") or {}]:
            if isinstance(src, dict):
                for ck, cv in src.items():
                    c_merged[ck] = max(int(c_merged.get(ck) or 0), int(cv or 0))
        merged["c"] = dict(sorted(c_merged.items(), key=lambda x: x[1], reverse=True)[:6])
    else:
        newer = incoming if inc_ts > base_ts else base
        merged["ts"] = int(newer.get("ts") or merged["ts"])
        for k in ["u", "pv", "dur_s", "dur_n", "max_s", "dl", "mp3", "mp4", "mob", "dsk"]:
            merged[k] = int(newer.get(k) or 0)
        c_new = newer.get("c") if isinstance(newer.get("c"), dict) else {}
        merged["c"] = dict(sorted(c_new.items(), key=lambda x: x[1], reverse=True)[:6])
    return merged

def _load_analytics(force_cloud: bool = False) -> dict:
    local_data = {}
    if os.path.exists(ANALYTICS_TMP_FILE):
        try:
            with open(ANALYTICS_TMP_FILE, "r", encoding="utf-8") as f:
                local_data = json.load(f)
        except Exception:
            local_data = {}

    if not local_data or force_cloud:
        cloud_data = _fetch_cloud_analytics()
        merged = _merge_analytics(local_data or _default_analytics(), cloud_data)
        try:
            with open(ANALYTICS_TMP_FILE, "w", encoding="utf-8") as f:
                json.dump(merged, f, separators=(",", ":"))
        except Exception:
            pass
        return merged

    base = _default_analytics()
    base.update(local_data)
    return base

def _save_analytics(stats: dict, force_cloud: bool = False) -> None:
    global _LAST_CLOUD_SYNC_TS
    import time
    # Keep top 6 countries so compact JSON stays well under 512 chars
    if isinstance(stats.get("c"), dict):
        stats["c"] = dict(sorted(stats["c"].items(), key=lambda x: x[1], reverse=True)[:6])
    else:
        stats["c"] = {}

    try:
        with open(ANALYTICS_TMP_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, separators=(",", ":"))
    except Exception:
        pass

    now = time.time()
    if force_cloud or (now - _LAST_CLOUD_SYNC_TS >= 12.0):
        _LAST_CLOUD_SYNC_TS = now
        tg_token = os.environ.get("TELEGRAM_BOT_TOKEN") or "8717205816:AAGdAXIPjaUg986TTJU3n0UFe0wZxfIO3oo"
        if tg_token:
            try:
                compact = "YT4MP3_STATS:" + json.dumps(stats, separators=(",", ":"))
                if len(compact) <= 512:
                    payload = json.dumps({"description": compact}).encode("utf-8")
                    req = urllib.request.Request(
                        f"https://api.telegram.org/bot{tg_token}/setMyDescription",
                        data=payload,
                        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
                    )
                    urllib.request.urlopen(req, timeout=3).read()
            except Exception as e:
                print(f"Cloud analytics sync notice: {e}")

def _format_duration_human(seconds: float) -> str:
    sec = max(0, int(round(seconds)))
    if sec < 60:
        return f"{sec} sec"
    mins, rem_sec = divmod(sec, 60)
    if mins < 60:
        return f"{mins}m {rem_sec}s"
    hrs, rem_mins = divmod(mins, 60)
    return f"{hrs}h {rem_mins}m {rem_sec}s"

@app.post("/api/analytics-ping")
async def analytics_ping(request: Request):
    try:
        raw_body = await request.body()
        body = json.loads(raw_body.decode("utf-8")) if raw_body else {}
    except Exception:
        body = {}

    event_type = str(body.get("event", "visit")).lower()
    stats = _load_analytics(force_cloud=False)
    ua = request.headers.get("user-agent", "").lower()
    country = (
        request.headers.get("x-vercel-ip-country")
        or request.headers.get("cf-ipcountry")
        or str(body.get("country", ""))
        or "GLB"
    ).upper()[:4]

    force_sync = False
    if event_type == "visit":
        is_new_session = bool(body.get("new_session", True))
        stats["pv"] = int(stats.get("pv", 0)) + 1
        if is_new_session:
            stats["u"] = int(stats.get("u", 0)) + 1
            stats["all_u"] = int(stats.get("all_u", 0)) + 1
            is_mobile = any(m in ua for m in ["mobile", "android", "iphone", "ipad", "ipod"])
            if is_mobile:
                stats["mob"] = int(stats.get("mob", 0)) + 1
            else:
                stats["dsk"] = int(stats.get("dsk", 0)) + 1
            c_map = stats.get("c") if isinstance(stats.get("c"), dict) else {}
            c_map[country] = int(c_map.get(country, 0)) + 1
            stats["c"] = c_map
            force_sync = True

    elif event_type == "duration":
        delta_sec = max(0, min(600, int(body.get("delta_sec", 0) or 0)))
        total_sec = max(0, min(14400, int(body.get("total_sec", 0) or 0)))
        first_ping = bool(body.get("first_ping", False))
        if delta_sec > 0:
            stats["dur_s"] = int(stats.get("dur_s", 0)) + delta_sec
        if first_ping:
            stats["dur_n"] = int(stats.get("dur_n", 0)) + 1
        if total_sec > int(stats.get("max_s", 0)):
            stats["max_s"] = total_sec

    elif event_type == "download":
        fmt = str(body.get("format", "mp3")).lower()
        stats["dl"] = int(stats.get("dl", 0)) + 1
        stats["all_dl"] = int(stats.get("all_dl", 0)) + 1
        if fmt in ["mp3", "m4a", "flac", "wav", "ogg", "opus", "aac"]:
            stats["mp3"] = int(stats.get("mp3", 0)) + 1
        else:
            stats["mp4"] = int(stats.get("mp4", 0)) + 1
        force_sync = True

    _save_analytics(stats, force_cloud=force_sync)
    return {"ok": True}

@app.get("/api/telegram-stats-report")
@app.post("/api/telegram-stats-report")
async def telegram_stats_report(reset: int = 0):
    # 12-hour traffic report disabled per user request; only check FastSaver <= 10k credits alert
    stats = _load_analytics(force_cloud=True)
    fs_status = _check_fastsaver_credits_and_alert(force_check=True, test_alert=False)
    return {
        "success": True,
        "report_disabled": True,
        "stats_snapshot": stats,
        "fastsaver_check": fs_status
    }

FAVICON_SVG_CONTENT = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a" />
      <stop offset="100%" stop-color="#020617" />
    </linearGradient>
    <linearGradient id="roseGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fb7185" />
      <stop offset="50%" stop-color="#f43f5e" />
      <stop offset="100%" stop-color="#e11d48" />
    </linearGradient>
    <linearGradient id="blueGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8" />
      <stop offset="100%" stop-color="#2563eb" />
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#f43f5e" flood-opacity="0.35" />
    </filter>
  </defs>

  <!-- Dark tactile badge background -->
  <rect width="512" height="512" rx="128" fill="url(#bgGrad)" />
  <rect x="8" y="8" width="496" height="496" rx="120" fill="none" stroke="#334155" stroke-width="4" opacity="0.6" />

  <!-- Stylized Fast Play Arrow + Audio Wave combination -->
  <!-- Triangle Play Body with rounded corners -->
  <path d="M168 136 C168 118 188 108 204 118 L386 238 C400 248 400 264 386 274 L204 394 C188 404 168 394 168 376 Z" 
        fill="url(#roseGrad)" filter="url(#glow)" />

  <!-- Modern Inset Dynamic Sound Wavebars inside the play icon -->
  <rect x="220" y="216" width="14" height="80" rx="7" fill="#ffffff" opacity="0.95" />
  <rect x="246" y="186" width="14" height="140" rx="7" fill="#ffffff" opacity="0.95" />
  <rect x="272" y="226" width="14" height="60" rx="7" fill="#ffffff" opacity="0.95" />

  <!-- Subtle Cyan Sound Accent Arc on right -->
  <circle cx="396" cy="180" r="14" fill="url(#blueGrad)" />
  <circle cx="420" cy="220" r="10" fill="url(#blueGrad)" opacity="0.8" />
</svg>"""

@app.get("/favicon.ico")
@app.get("/favicon.svg")
@app.get("/static/favicon.svg")
async def favicon():
    return HTMLResponse(content=FAVICON_SVG_CONTENT, media_type="image/svg+xml")

@app.get("/youtube-to-mp3-320kbps")
async def youtube_320k_redirect():
    return RedirectResponse(url="/youtube-to-mp3", status_code=301)

@app.get("/tiktok-downloader")
@app.get("/instagram-downloader")
@app.get("/facebook-downloader")
async def legacy_redirect():
    return RedirectResponse(url="/", status_code=301)

# Localized Routes (13 international languages)
@app.get("/{lang}", response_class=HTMLResponse)
@app.get("/{lang}/", response_class=HTMLResponse)
async def localized_home_page(request: Request, lang: str):
    if lang == "en":
        return RedirectResponse(url="/", status_code=301)
    if lang not in SUPPORTED_LANGUAGES:
        clean_id = lang.strip("/")
        if len(clean_id) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', clean_id):
            return render_converter_page(request, "home", "en")
        if clean_id.startswith("4youtube") or clean_id.startswith("watch"):
            return render_converter_page(request, "home", "en")
        raise HTTPException(status_code=404, detail="Page not found")
    return render_converter_page(request, "home", lang)

@app.get("/{lang}/youtube-to-mp3", response_class=HTMLResponse)
@app.get("/{lang}/youtube-to-mp3/", response_class=HTMLResponse)
async def localized_youtube_mp3_page(request: Request, lang: str):
    if lang == "en":
        return RedirectResponse(url="/youtube-to-mp3", status_code=301)
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Page not found")
    return render_converter_page(request, "youtube-to-mp3", lang)

@app.get("/{lang}/youtube-to-mp4", response_class=HTMLResponse)
@app.get("/{lang}/youtube-to-mp4/", response_class=HTMLResponse)
async def localized_youtube_mp4_page(request: Request, lang: str):
    if lang == "en":
        return RedirectResponse(url="/youtube-to-mp4", status_code=301)
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Page not found")
    return render_converter_page(request, "youtube-to-mp4", lang)

@app.get("/{lang}/youtube-shorts-downloader", response_class=HTMLResponse)
@app.get("/{lang}/youtube-shorts-downloader/", response_class=HTMLResponse)
async def localized_youtube_shorts_page(request: Request, lang: str):
    if lang == "en":
        return RedirectResponse(url="/youtube-shorts-downloader", status_code=301)
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Page not found")
    return render_converter_page(request, "youtube-shorts-downloader", lang)

