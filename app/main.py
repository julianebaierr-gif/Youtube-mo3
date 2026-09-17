import os
import urllib.parse
import requests
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, StreamingResponse, RedirectResponse
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
    title="MediaConvert Pro - Free High Speed Video & MP3 Converter",
    description="Convert and Download YouTube, TikTok, Instagram, Facebook Videos to MP3 320kbps & MP4 HD.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

class ExtractRequest(BaseModel):
    url: str

class ConvertRequest(BaseModel):
    url: str
    format: str = "mp3"
    quality: str = "320kbps"

SEO_PAGES = {
    "home": {
        "title": "YouTube to MP3 Converter & Video Downloader - Fast, Free & HD",
        "h1": "YouTube to MP3 & MP4 Converter",
        "subtitle": "Convert and download videos from YouTube, TikTok, Instagram, Facebook & Twitter into Ultra HQ 320kbps MP3 audio or up to 8K/4K/1080p MP4.",
        "badge": "✨ Next-Gen Converter 2026",
        "active_tab": "all",
        "meta_desc": "Best free online YouTube to MP3 converter and multi-platform video downloader. High quality 320kbps audio, 8K/4K/1080p MP4, unlimited speed, no ads."
    },
    "youtube-to-mp3": {
        "title": "YouTube to MP3 Converter - Free Online 320kbps Audio Downloader",
        "h1": "YouTube to MP3 Converter",
        "subtitle": "Extract studio quality 320kbps, 256kbps and 128kbps MP3 audio from any YouTube video in seconds with zero ads.",
        "badge": "🎵 YouTube to MP3 320kbps",
        "active_tab": "yt-mp3",
        "meta_desc": "Convert YouTube to MP3 high quality 320kbps audio online for free. Works seamlessly on iPhone, Android, Mac & Windows PC."
    },
    "youtube-to-mp4": {
        "title": "YouTube to MP4 Converter - Download 8K, 4K, 1080p Full HD Videos",
        "h1": "YouTube to MP4 Video Downloader",
        "subtitle": "Download YouTube videos and Shorts in 8K, 4K UHD, 1080p Full HD, 720p HD, and 480p MP4 format with crystal clear sound.",
        "badge": "🎬 YouTube to MP4 4K / 8K",
        "active_tab": "yt-mp4",
        "meta_desc": "Free YouTube to MP4 converter to download HD YouTube videos, shorts and clips in 8K, 4K, 1080p, 720p, 480p and 360p."
    },
    "tiktok-downloader": {
        "title": "TikTok Downloader - Download TikTok Video Without Watermark HD",
        "h1": "TikTok Video & MP3 Downloader",
        "subtitle": "Save TikTok videos without watermark in high definition MP4 or extract background sounds into MP3.",
        "badge": "⚡ No Watermark HD",
        "active_tab": "tiktok",
        "meta_desc": "Download TikTok videos without watermark for free in Full HD. Extract TikTok sounds and songs to MP3 320kbps."
    },
    "instagram-downloader": {
        "title": "Instagram Video & Reels Downloader - Save IG Posts & Audio",
        "h1": "Instagram Reels & Video Downloader",
        "subtitle": "Download Instagram Reels, Stories, IGTV and Posts directly to MP4 video or MP3 audio in original quality.",
        "badge": "📸 Instagram Reels HD",
        "active_tab": "instagram",
        "meta_desc": "Free Instagram Reels and video downloader. Save IG stories and video posts in high quality MP4 & MP3."
    },
    "facebook-downloader": {
        "title": "Facebook Video Downloader - Save FB Watch & Reels 1080p",
        "h1": "Facebook Video Downloader",
        "subtitle": "Convert and save Facebook videos, public reels, and FB watch clips in 1080p HD MP4 and MP3.",
        "badge": "👥 Facebook HD Saver",
        "active_tab": "facebook",
        "meta_desc": "Fast Facebook video downloader online. Save FB watch videos and reels to MP4 and MP3 in high definition."
    },
    "youtube-320kbps": {
        "title": "YouTube to MP3 320kbps Converter - Studio HQ Audio Free",
        "h1": "YouTube to MP3 320kbps (Extreme Quality)",
        "subtitle": "Enjoy maximum bitrate 320kbps audio conversion with original acoustic richness and enhanced clarity.",
        "badge": "🔥 320kbps Studio Quality",
        "active_tab": "yt-mp3",
        "meta_desc": "Convert YouTube videos to authentic 320kbps MP3 audio files with high bitrates and superior clarity."
    }
}

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"seo": SEO_PAGES["home"]})

@app.get("/youtube-to-mp3", response_class=HTMLResponse)
async def youtube_mp3_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"seo": SEO_PAGES["youtube-to-mp3"]})

@app.get("/youtube-to-mp4", response_class=HTMLResponse)
async def youtube_mp4_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"seo": SEO_PAGES["youtube-to-mp4"]})

@app.get("/tiktok-downloader", response_class=HTMLResponse)
async def tiktok_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"seo": SEO_PAGES["tiktok-downloader"]})

@app.get("/instagram-downloader", response_class=HTMLResponse)
async def instagram_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"seo": SEO_PAGES["instagram-downloader"]})

@app.get("/facebook-downloader", response_class=HTMLResponse)
async def facebook_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"seo": SEO_PAGES["facebook-downloader"]})

@app.get("/youtube-to-mp3-320kbps", response_class=HTMLResponse)
async def youtube_320k_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"seo": SEO_PAGES["youtube-320kbps"]})

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
    url = payload.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")
    
    res = resolve_stream_url(url, payload.format, payload.quality)
    stream_url = res.get("stream_url")
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

@app.get("/api/stream-download")
async def api_stream_download(stream_url: str = Query(...), filename: str = Query("download"), format: str = Query("mp3")):
    decoded_url = urllib.parse.unquote(stream_url)
    safe_filename = urllib.parse.quote(filename)

    mime_type = "audio/mpeg" if format == "mp3" else ("video/mp4" if format == "mp4" else "application/octet-stream")
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{safe_filename}",
        "Content-Type": mime_type
    }

    try:
        # Stream chunks directly from CDN to browser without storing on serverless disk
        req = requests.get(decoded_url, stream=True, headers=COMMON_HEADERS, timeout=30)
        if req.status_code in [200, 206]:
            def iterfile():
                for chunk in req.iter_content(chunk_size=1024 * 64):
                    if chunk:
                        yield chunk

            return StreamingResponse(iterfile(), headers=headers, media_type=mime_type)
        else:
            return RedirectResponse(url=decoded_url)
    except Exception:
        return RedirectResponse(url=decoded_url)

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "MediaConvert Pro Engine"}
