import os
import urllib.request
import urllib.parse
import json
import re
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
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
    "Cache-Control": "public, max-age=0, s-maxage=86400, stale-while-revalidate=604800",
    "CDN-Cache-Control": "public, s-maxage=86400, stale-while-revalidate=604800",
    "Vercel-CDN-Cache-Control": "public, s-maxage=86400, stale-while-revalidate=604800",
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

@app.api_route("/sitemap.xml", methods=["GET", "HEAD"])
async def sitemap_xml():
    sitemap_file = os.path.join(BASE_DIR, "public", "sitemap.xml")
    if os.path.exists(sitemap_file):
        with open(sitemap_file, "r", encoding="utf-8") as f:
            content = f.read()
        return Response(content=content, media_type="application/xml; charset=utf-8", headers=EDGE_HTML_HEADERS)
    raise HTTPException(status_code=404, detail="Sitemap not found")

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
    # All non-Google search engines supporting IndexNow protocol (Bing/Yahoo/DuckDuckGo/Ecosia, Yandex, Seznam, Naver, Yep)
    endpoints = [
        "https://api.indexnow.org/indexnow",
        "https://www.bing.com/indexnow",
        "https://yandex.com/indexnow",
        "https://search.seznam.cz/indexnow",
        "https://searchadvisor.naver.com/indexnow",
        "https://indexnow.yep.com/indexnow"
    ]
    results = {}
    for ep in endpoints:
        try:
            req = urllib.request.Request(
                ep,
                data=data,
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "User-Agent": "YT4MP3-AutoIndexer/2.0 (+https://www.yt4mp3.com)"
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
        "schedule": "every_12_hours",
        "excluded_engines": ["google"],
        "url_count": len(url_list),
        "results": results
    }

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
    
    # 1. Primary Engine: savenow.to (clean stream without button=1)
    if engine != "loader":
        try:
            api_url = f"https://p.savenow.to/api/v2/download?format={fmt}&url={encoded_url}"
            req = urllib.request.Request(api_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://www.yt4mp3.com/"
            })
            with urllib.request.urlopen(req, timeout=9) as r:
                data = json.loads(r.read())
                if data and data.get("id"):
                    dl = data.get("download_url")
                    if dl:
                        if "://p.savenow.to/" in dl or "://lto2.affadaffa.com/" in dl or any(ad in dl.lower() for ad in ["ey43.com", "/ad/", "hoofsduke", "converttr.org", "google.com"]):
                            dl = None
                        elif dl.startswith("http://"):
                            dl = dl.replace("http://", "https://")
                    return {"success": True, "id": data.get("id"), "engine": "savenow", "download_url": dl}
        except Exception:
            pass

    # 2. Secondary Engine: loader.to
    try:
        lto_url = f"https://loader.to/ajax/download.php?format={fmt}&url={encoded_url}"
        req = urllib.request.Request(lto_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://loader.to/"
        })
        with urllib.request.urlopen(req, timeout=9) as r:
            data = json.loads(r.read())
            if data and data.get("id"):
                dl = data.get("download_url")
                if dl:
                    if "://p.savenow.to/" in dl or "://lto2.affadaffa.com/" in dl or any(ad in dl.lower() for ad in ["ey43.com", "/ad/", "hoofsduke", "converttr.org", "google.com"]):
                        dl = None
                    elif dl.startswith("http://"):
                        dl = dl.replace("http://", "https://")
                return {"success": True, "id": data.get("id"), "engine": "loader", "download_url": dl}
    except Exception:
        pass

    raise HTTPException(status_code=502, detail="Unable to initiate media conversion")

@app.get("/api/progress")
async def proxy_progress(id: str):
    endpoints = [
        f"https://p.savenow.to/api/progress?id={id}",
        f"https://lto2.affadaffa.com/api/progress?id={id}"
    ]
    for ep in endpoints:
        try:
            req = urllib.request.Request(ep, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Referer": "https://www.yt4mp3.com/"
            })
            with urllib.request.urlopen(req, timeout=6) as r:
                data = json.loads(r.read())
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

@app.post("/api/report-issue")
async def report_issue(request: Request):
    try:
        body = await request.json()
        video_url = str(body.get("video_url", "Unknown"))
        video_title = str(body.get("video_title", "Unknown"))
        selected_format = str(body.get("format", "Unknown"))
        error_detail = str(body.get("error", "Stream conversion failed"))
        user_agent = request.headers.get("user-agent", "Unknown")
        client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "Unknown")
        
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

                alert_text = (
                    "🚨 <b>YT4MP3 Conversion Alert</b>\n\n"
                    f"🎬 <b>Video:</b> {safe_title}\n"
                    f"🔗 <b>Link:</b> {safe_url}\n"
                    f"🎛 <b>Format:</b> {safe_fmt}\n"
                    f"⚠️ <b>Error:</b> {safe_err}\n"
                    f"🌐 <b>User IP:</b> <code>{safe_ip}</code>"
                )
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
    i.strip() for i in (os.environ.get("COBALT_INSTANCES") or "https://api.cobalt.liubquanti.click/").split(",") if i.strip()
]

@app.get("/api/long-video")
async def long_video(url: str, mode: str = "audio", quality: str = "720"):
    if not re.search(r"(youtube\.com|youtu\.be)", url or ""):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    body = {"url": url, "filenameStyle": "basic"}
    if mode == "audio":
        body.update({"downloadMode": "audio", "audioFormat": "mp3", "audioBitrate": "320"})
    else:
        q = re.sub(r"[^0-9]", "", str(quality)) or "720"
        if q not in ["144", "240", "360", "480", "720", "1080", "1440", "2160"]:
            q = "720"
        codec = "vp9" if q in ("1440", "2160") else "h264"
        body.update({"downloadMode": "auto", "videoQuality": q, "youtubeVideoCodec": codec})

    last_err = "No long-video engine available"
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
            with urllib.request.urlopen(req, timeout=25) as res:
                data = json.loads(res.read().decode("utf-8"))
            if data.get("status") in ("tunnel", "redirect") and data.get("url"):
                return {"success": True, "download_url": data["url"], "filename": data.get("filename", ""), "engine": "cobalt"}
            last_err = str((data.get("error") or {}).get("code") or data.get("status") or "unknown")
        except urllib.error.HTTPError as e:
            try:
                err_body = json.loads(e.read().decode("utf-8", "ignore"))
                last_err = str((err_body.get("error") or {}).get("code") or f"HTTP {e.code}")
            except Exception:
                last_err = f"HTTP {e.code}"
        except Exception as e:
            last_err = str(e)
    return {"success": False, "error": last_err}


# ==============================================================================
# FASTSAVER ENGINE (4th fallback) — paid API with 4K support, no duration limit
# Uses api.fastsaver.io with API key. Costs credits per download.
# ==============================================================================
FASTSAVER_API_KEY = os.environ.get("FASTSAVER_API_KEY") or "fs_sk_9w9n0d9x3t0r0g2g0d3e0j3f6u7q"
FASTSAVER_LOW_CREDIT_THRESHOLD = 10000
_LAST_FS_BALANCE_CHECK_TS = 0.0
_LAST_FS_LOW_ALERT_TS = 0.0

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
async def fastsaver_video(url: str, mode: str = "audio", quality: str = "720"):
    if not re.search(r"(youtube\.com|youtu\.be)", url or ""):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    headers = {
        "X-Api-Key": FASTSAVER_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130 Safari/537.36",
    }
    # Determine format string for FastSaver
    if mode == "audio":
        fmt = "audio"
    else:
        q = re.sub(r"[^0-9]", "", str(quality)) or "720"
        fmt_map = {"2160": "2160p", "1440": "1440p", "1080": "1080p", "720": "720p", "480": "480p", "360": "360p", "240": "240p", "144": "144p"}
        fmt = fmt_map.get(q, "720p")
    body = json.dumps({"url": url, "format": fmt}).encode("utf-8")
    try:
        req = urllib.request.Request(
            "https://api.fastsaver.io/v1/youtube/download",
            data=body,
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=55) as res:
            data = json.loads(res.read().decode("utf-8"))
        # Check remaining credits after download and alert if <= 10,000
        _check_fastsaver_credits_and_alert(force_check=True)
        if data.get("ok") and data.get("download_url"):
            return {
                "success": True,
                "download_url": data["download_url"],
                "filename": data.get("filename", ""),
                "engine": "fastsaver",
            }
        return {"success": False, "error": data.get("detail", "fastsaver_unknown_error")}
    except urllib.error.HTTPError as e:
        try:
            err_body = json.loads(e.read().decode("utf-8", "ignore"))
            detail = err_body.get("detail", f"HTTP {e.code}")
        except Exception:
            detail = f"HTTP {e.code}"
        _check_fastsaver_credits_and_alert(force_check=False)
        return {"success": False, "error": str(detail)}
    except Exception as e:
        return {"success": False, "error": str(e)}


_VIDEO_RES_CACHE = {}

@app.get("/api/video-resolutions")
async def get_video_resolutions(id: str):
    vid = re.sub(r"[^a-zA-Z0-9_-]", "", id or "")
    if len(vid) != 11:
        return {"has_4k": False, "has_2k": False, "max_height": 1080, "duration_sec": 0}
    if vid in _VIDEO_RES_CACHE:
        return _VIDEO_RES_CACHE[vid]

    yt_url = f"https://www.youtube.com/watch?v={vid}"
    duration_sec = 0
    # 1. Fast, zero-credit check via YouTube watch page player response
    try:
        req = urllib.request.Request(
            yt_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        with urllib.request.urlopen(req, timeout=5) as res:
            html = res.read().decode("utf-8", "ignore")
        dur_match = re.search(r'"lengthSeconds":"(\d+)"', html)
        if dur_match:
            duration_sec = int(dur_match.group(1))
        heights = [int(h) for h in re.findall(r'"qualityLabel":"(\d+)p', html)]
        if heights:
            max_h = max(heights)
            result = {
                "has_4k": max_h >= 2160 or 2160 in heights,
                "has_2k": max_h >= 1440 or 1440 in heights,
                "max_height": max_h,
                "duration_sec": duration_sec,
                "source": "yt_watch",
            }
            _VIDEO_RES_CACHE[vid] = result
            return result
    except Exception:
        pass

    # 2. Fallback: FastSaver /v1/youtube/info (accurate format list when datacenter IP is blocked by YouTube)
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
        with urllib.request.urlopen(req, timeout=8) as res:
            data = json.loads(res.read().decode("utf-8"))
        _check_fastsaver_credits_and_alert(force_check=False)
        if data.get("ok"):
            raw_dur = data.get("duration") or data.get("lengthSeconds") or 0
            if isinstance(raw_dur, (int, float)):
                duration_sec = int(raw_dur)
            elif isinstance(raw_dur, str):
                if raw_dur.isdigit():
                    duration_sec = int(raw_dur)
                elif ":" in raw_dur:
                    parts = [int(p) for p in raw_dur.split(":") if p.isdigit()]
                    if len(parts) == 2:
                        duration_sec = parts[0] * 60 + parts[1]
                    elif len(parts) == 3:
                        duration_sec = parts[0] * 3600 + parts[1] * 60 + parts[2]
        if data.get("ok") and isinstance(data.get("formats"), list):
            fmt_names = [str(f.get("format", "")).lower() for f in data["formats"]]
            has_4k = any("2160" in f or "4k" in f for f in fmt_names)
            has_2k = any("1440" in f or "2k" in f for f in fmt_names)
            result = {
                "has_4k": has_4k,
                "has_2k": has_2k,
                "max_height": 2160 if has_4k else (1440 if has_2k else 1080),
                "duration_sec": duration_sec,
                "source": "fastsaver_info",
            }
            _VIDEO_RES_CACHE[vid] = result
            return result
    except Exception:
        pass

    return {"has_4k": False, "has_2k": False, "max_height": 1080, "duration_sec": duration_sec, "source": "default"}


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

