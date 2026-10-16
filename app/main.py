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
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self' 'unsafe-inline' 'unsafe-eval' "
        "https://cdn.tailwindcss.com https://cdnjs.cloudflare.com https://fonts.googleapis.com https://fonts.gstatic.com https://images.unsplash.com https://*.ytimg.com https://*.googlevideo.com https://analytics.ahrefs.com https://pagead2.googlesyndication.com https://*.googlesyndication.com https://*.google.com https://*.doubleclick.net; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://analytics.ahrefs.com https://pagead2.googlesyndication.com https://*.googlesyndication.com https://www.googletagmanager.com https://*.google.com https://*.doubleclick.net; "
        "img-src 'self' data: https:; "
        "media-src 'self' blob: https:; "
        "connect-src 'self' https: https://noembed.com https://analytics.ahrefs.com https://pagead2.googlesyndication.com https://*.googlesyndication.com https://*.google.com https://*.doubleclick.net; "
        "frame-src 'self' https://loader.to https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com;"
    )
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

def render_converter_page(request: Request, page_key: str, lang: str = "en"):
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Language not found")
    
    seo_data = get_page_content(lang, page_key)
    ui_strings = get_ui_strings(lang)
    hreflangs = get_hreflang_links(page_key)
    switcher = get_language_switcher_links(page_key, lang)
    current_meta = SUPPORTED_LANGUAGES[lang]
    
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "seo": seo_data,
            "t": ui_strings,
            "lang": lang,
            "lang_dir": current_meta.get("dir", "ltr"),
            "hreflangs": hreflangs,
            "switcher": switcher,
            "current_lang": current_meta,
            "supported_languages": SUPPORTED_LANGUAGES
        }
    )

def render_legal_page(request: Request, page_key: str):
    ui_strings = get_ui_strings("en")
    switcher = get_language_switcher_links("home", "en")
    current_meta = SUPPORTED_LANGUAGES["en"]
    return templates.TemplateResponse(
        request=request,
        name="page.html",
        context={
            "seo": LEGAL_PAGES[page_key],
            "t": ui_strings,
            "lang": "en",
            "lang_dir": "ltr",
            "switcher": switcher,
            "current_lang": current_meta,
            "supported_languages": SUPPORTED_LANGUAGES
        }
    )

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
            return Response(content=f.read(), media_type="application/manifest+json; charset=utf-8")
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
        return Response(content=content, media_type="text/plain; charset=utf-8")
    content = "google.com, pub-2350272227833258, DIRECT, f08c47fec0942fa0\n"
    return Response(content=content, media_type="text/plain; charset=utf-8")

@app.api_route("/robots.txt", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def robots_txt():
    content = """User-agent: *
Allow: /
Disallow: /?s=
Disallow: /*?*s=
Disallow: /*?*q=
Disallow: /*?*ref=
Sitemap: https://www.yt4mp3.com/sitemap.xml
"""
    return Response(content=content, media_type="text/plain; charset=utf-8")

@app.api_route("/sitemap.xml", methods=["GET", "HEAD"])
async def sitemap_xml():
    sitemap_file = os.path.join(BASE_DIR, "public", "sitemap.xml")
    if os.path.exists(sitemap_file):
        with open(sitemap_file, "r", encoding="utf-8") as f:
            content = f.read()
        return Response(content=content, media_type="application/xml; charset=utf-8")
    raise HTTPException(status_code=404, detail="Sitemap not found")

@app.api_route("/llms.txt", methods=["GET", "HEAD"])
async def llms_txt():
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
- [Contact Us](https://www.yt4mp3.com/contact-us): Get in touch with our team for questions, feedback, or DMCA inquiries.
- [Terms of Service](https://www.yt4mp3.com/terms-of-service): Terms governing the personal and fair use of the converter tool.
- [Privacy Policy](https://www.yt4mp3.com/privacy-policy): Privacy practices and data handling information.
"""
    return Response(content=content, media_type="text/plain; charset=utf-8")

@app.get("/8f9b3e1c4a2d7e5f9a0b1c2d3e4f5a6b.txt")
async def indexnow_key():
    return Response(content="8f9b3e1c4a2d7e5f9a0b1c2d3e4f5a6b", media_type="text/plain; charset=utf-8")

@app.api_route("/api/indexnow", methods=["GET", "POST"])
async def trigger_indexnow():
    import urllib.request
    import json
    payload = {
        "host": "www.yt4mp3.com",
        "key": "8f9b3e1c4a2d7e5f9a0b1c2d3e4f5a6b",
        "keyLocation": "https://www.yt4mp3.com/8f9b3e1c4a2d7e5f9a0b1c2d3e4f5a6b.txt",
        "urlList": (
            [
                "https://www.yt4mp3.com/",
                "https://www.yt4mp3.com/youtube-to-mp3",
                "https://www.yt4mp3.com/youtube-to-mp4",
                "https://www.yt4mp3.com/contact-us",
                "https://www.yt4mp3.com/terms-of-service",
                "https://www.yt4mp3.com/privacy-policy"
            ] + [
                f"https://www.yt4mp3.com/{c}/" for c in SUPPORTED_LANGUAGES if c != "en"
            ] + [
                f"https://www.yt4mp3.com/{c}/youtube-to-mp3" for c in SUPPORTED_LANGUAGES if c != "en"
            ] + [
                f"https://www.yt4mp3.com/{c}/youtube-to-mp4" for c in SUPPORTED_LANGUAGES if c != "en"
            ]
        )
    }
    data = json.dumps(payload).encode("utf-8")
    results = {}
    for ep in ["https://api.indexnow.org/indexnow", "https://www.bing.com/indexnow"]:
        try:
            req = urllib.request.Request(ep, data=data, headers={"Content-Type": "application/json; charset=utf-8"})
            with urllib.request.urlopen(req, timeout=5) as res:
                results[ep] = {"status": res.status, "msg": "ok"}
        except Exception as e:
            results[ep] = {"status": 200, "detail": str(e)}
    return {"submitted": True, "results": results}

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
    elif clean_fmt in ["480", "360"]:
        fmt = clean_fmt
    elif clean_fmt in ["m4a", "flac", "wav", "aac", "webm", "opus", "ogg"]:
        fmt = clean_fmt
    else:
        fmt = "mp3"
    
    # 1. Primary Engine: savenow.to (unless engine is explicitly loader)
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
                    if dl and dl.startswith("http://"):
                        dl = dl.replace("http://", "https://")
                    return {"success": True, "id": data.get("id"), "engine": "savenow", "download_url": dl}
        except Exception:
            pass

    # 2. Secondary Engine: loader.to
    try:
        lto_url = f"https://loader.to/ajax/download.php?start=1&end=1&format={fmt}&url={encoded_url}"
        req = urllib.request.Request(lto_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://loader.to/"
        })
        with urllib.request.urlopen(req, timeout=9) as r:
            data = json.loads(r.read())
            if data and data.get("id"):
                dl = data.get("download_url")
                if dl and dl.startswith("http://"):
                    dl = dl.replace("http://", "https://")
                return {"success": True, "id": data.get("id"), "engine": "loader", "download_url": dl}
    except Exception:
        pass

    # 3. Tertiary Fallback: If loader direct was asked, try savenow as backup
    if engine == "loader":
        try:
            api_url = f"https://p.savenow.to/api/v2/download?format={fmt}&url={encoded_url}"
            req = urllib.request.Request(api_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Referer": "https://www.yt4mp3.com/"
            })
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read())
                if data and data.get("id"):
                    dl = data.get("download_url")
                    if dl and dl.startswith("http://"):
                        dl = dl.replace("http://", "https://")
                    return {"success": True, "id": data.get("id"), "engine": "savenow", "download_url": dl}
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
                        # Reject rogue ad redirect networks
                        if any(ad in dl.lower() for ad in ["ey43.com", "/ad/", "hoofsduke", "converttr.org"]):
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
        
        # Real-time Telegram Bot Notification (Configured via Vercel Environment Variables)
        tg_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        tg_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        if tg_token and tg_chat_id:
            try:
                alert_text = (
                    "🚨 *YT4MP3 Conversion Alert*\n\n"
                    f"🎬 *Video:* {video_title[:80]}\n"
                    f"🔗 *Link:* `{video_url}`\n"
                    f"🎛 *Format:* `{selected_format}`\n"
                    f"⚠️ *Error:* `{error_detail}`\n"
                    f"🌐 *User IP:* `{client_ip}`"
                )
                tg_url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
                payload = json.dumps({"chat_id": tg_chat_id, "text": alert_text, "parse_mode": "Markdown"}).encode("utf-8")
                tg_req = urllib.request.Request(tg_url, data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(tg_req, timeout=4):
                    pass
            except Exception as tg_err:
                print(f"Telegram notification dispatch error: {tg_err}")
                
        return {"success": True, "message": "Issue recorded. Thank you for reporting!"}
    except Exception as e:
        return {"success": False, "detail": str(e)}

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

