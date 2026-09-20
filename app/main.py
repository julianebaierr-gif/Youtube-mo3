import os
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
    host = request.headers.get("host", "").lower()
    # If request comes from the old domain yt4mp3.cc, 301 redirect to www.yt4mp3.com
    if "yt4mp3.cc" in host:
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
        "https://cdn.tailwindcss.com https://cdnjs.cloudflare.com https://fonts.googleapis.com https://fonts.gstatic.com https://images.unsplash.com https://*.ytimg.com https://*.googlevideo.com https://analytics.ahrefs.com; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://analytics.ahrefs.com; "
        "img-src 'self' data: https:; "
        "media-src 'self' blob: https:; "
        "connect-src 'self' https: https://analytics.ahrefs.com;"
    )
    return response

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)



from app.seo_content import SEO_PAGES
from app.legal_content import LEGAL_PAGES

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"seo": SEO_PAGES["home"]})

@app.get("/youtube-to-mp3", response_class=HTMLResponse)
async def youtube_mp3_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"seo": SEO_PAGES["youtube-to-mp3"]})

@app.get("/youtube-to-mp4", response_class=HTMLResponse)
async def youtube_mp4_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"seo": SEO_PAGES["youtube-to-mp4"]})

@app.get("/contact-us", response_class=HTMLResponse)
async def contact_us_page(request: Request):
    return templates.TemplateResponse(request=request, name="page.html", context={"seo": LEGAL_PAGES["contact-us"]})

@app.get("/terms-of-service", response_class=HTMLResponse)
async def terms_page(request: Request):
    return templates.TemplateResponse(request=request, name="page.html", context={"seo": LEGAL_PAGES["terms-of-service"]})

@app.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_page(request: Request):
    return templates.TemplateResponse(request=request, name="page.html", context={"seo": LEGAL_PAGES["privacy-policy"]})

@app.api_route("/robots.txt", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def robots_txt():
    content = """User-agent: *
Allow: /
Sitemap: https://www.yt4mp3.com/sitemap.xml
"""
    return Response(content=content, media_type="text/plain; charset=utf-8")

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

