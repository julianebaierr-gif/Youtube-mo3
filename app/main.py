import os
import urllib.parse
import requests
from fastapi import FastAPI, Query, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, StreamingResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.downloader import extract_media_info, resolve_stream_url, sanitize_filename

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
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self' 'unsafe-inline' 'unsafe-eval' "
        "https://cdn.tailwindcss.com https://cdnjs.cloudflare.com https://fonts.googleapis.com https://fonts.gstatic.com https://images.unsplash.com https://*.ytimg.com https://*.googlevideo.com; "
        "img-src 'self' data: https:; "
        "media-src 'self' blob: https:; "
        "connect-src 'self' https:;"
    )
    return response

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

class ExtractRequest(BaseModel):
    url: str

class ConvertRequest(BaseModel):
    url: str
    format: str = "mp3"
    quality: str = "320kbps"

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

@app.get("/robots.txt", response_class=HTMLResponse)
async def robots_txt():
    content = """User-agent: *
Allow: /
Disallow: /api/
Sitemap: https://www.yt4mp3.cc/sitemap.xml
"""
    return HTMLResponse(content=content, media_type="text/plain")

@app.get("/llms.txt", response_class=HTMLResponse)
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
- [Home](https://www.yt4mp3.cc/): Free Online YouTube to MP3 and MP4 Converter.
- [YouTube to MP3 Converter](https://www.yt4mp3.cc/youtube-to-mp3): Convert YouTube videos and music into high quality 320kbps MP3 audio files.
- [YouTube to MP4 Converter](https://www.yt4mp3.cc/youtube-to-mp4): Download YouTube videos in 1080p, 720p, and 4K MP4 format.
- [Contact Us](https://www.yt4mp3.cc/contact-us): Get in touch with our team for questions, feedback, or DMCA inquiries.
- [Terms of Service](https://www.yt4mp3.cc/terms-of-service): Terms governing the personal and fair use of the converter tool.
- [Privacy Policy](https://www.yt4mp3.cc/privacy-policy): Privacy practices and data handling information.
"""
    return HTMLResponse(content=content, media_type="text/plain; charset=utf-8")

@app.get("/sitemap.xml", response_class=HTMLResponse)
async def sitemap_xml():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.yt4mp3.cc/</loc>
    <lastmod>2026-09-18</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://www.yt4mp3.cc/youtube-to-mp3</loc>
    <lastmod>2026-09-18</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://www.yt4mp3.cc/youtube-to-mp4</loc>
    <lastmod>2026-09-18</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://www.yt4mp3.cc/contact-us</loc>
    <lastmod>2026-09-18</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
  <url>
    <loc>https://www.yt4mp3.cc/terms-of-service</loc>
    <lastmod>2026-09-18</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
  <url>
    <loc>https://www.yt4mp3.cc/privacy-policy</loc>
    <lastmod>2026-09-18</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
</urlset>"""
    return Response(content=xml, media_type="text/xml; charset=utf-8")

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

@app.post("/api/extract")
async def api_extract(payload: ExtractRequest):
    url = payload.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")
    
    data = extract_media_info(url)
    if not data.get("success"):
        return JSONResponse(status_code=400, content=data)
    return JSONResponse(content=data)

@app.post("/api/convert")
async def api_start_conversion(payload: ConvertRequest):
    try:
        url = payload.url.strip()
        if not url:
            return JSONResponse(status_code=400, content={"success": False, "error": "URL cannot be empty"})
        
        res = resolve_stream_url(url, payload.format, payload.quality)
        if not res.get("success") or not res.get("stream_url"):
            return JSONResponse(status_code=400, content={
                "success": False,
                "error": res.get("error") or "Unable to extract direct stream. Please try another format or link."
            })

        stream_url = res["stream_url"]
        file_name = res.get("file_name", "media_download")

        # Proxy stream URL with Content-Disposition
        proxy_download_url = f"/api/stream-download?stream_url={urllib.parse.quote(stream_url)}&filename={urllib.parse.quote(file_name)}&format={payload.format}"

        return JSONResponse(content={
            "success": True,
            "download_url": proxy_download_url,
            "direct_stream_url": stream_url,
            "file_name": file_name,
            "title": res.get("title", "Media")
        })
    except Exception as e:
        return JSONResponse(status_code=400, content={
            "success": False,
            "error": f"Conversion error: {str(e)}"
        })

@app.get("/api/stream-download")
async def api_stream_download(stream_url: str = Query(...), filename: str = Query("download"), format: str = Query("mp3")):
    decoded_url = urllib.parse.unquote(stream_url)
    
    # Ensure filename has extension
    ext = format.lower()
    clean_name = filename if filename.endswith(f".{ext}") else f"{filename}.{ext}"
    safe_filename = urllib.parse.quote(clean_name)

    mime_map = {
        "mp3": "audio/mpeg",
        "m4a": "audio/mp4",
        "wav": "audio/wav",
        "flac": "audio/flac",
        "mp4": "video/mp4"
    }
    mime_type = mime_map.get(ext, "application/octet-stream")

    headers = {
        "Content-Disposition": f'attachment; filename="{clean_name}"; filename*=UTF-8\'\'{safe_filename}',
        "Content-Type": mime_type,
        "Cache-Control": "no-cache"
    }

    try:
        # Stream chunks directly to client browser
        req = requests.get(decoded_url, stream=True, headers=COMMON_HEADERS, timeout=45)
        if req.status_code in [200, 206]:
            def iterfile():
                for chunk in req.iter_content(chunk_size=1024 * 64):
                    if chunk:
                        yield chunk

            return StreamingResponse(iterfile(), headers=headers, media_type=mime_type)
        else:
            return RedirectResponse(url=decoded_url)
    except Exception as e:
        return RedirectResponse(url=decoded_url)

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "YT4MP3 Engine"}
