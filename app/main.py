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

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"seo": SEO_PAGES["home"]})

@app.get("/youtube-to-mp3", response_class=HTMLResponse)
async def youtube_mp3_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"seo": SEO_PAGES["youtube-to-mp3"]})

@app.get("/youtube-to-mp4", response_class=HTMLResponse)
async def youtube_mp4_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"seo": SEO_PAGES["youtube-to-mp4"]})

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
    return {"status": "ok", "service": "MediaConvert Pro Engine"}
