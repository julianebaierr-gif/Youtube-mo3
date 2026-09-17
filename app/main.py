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
        "title": "YouTube to MP3 Converter & Multi-Platform Video Downloader - 320kbps & 4K HD",
        "h1": "YouTube to MP3 & MP4 Video Downloader",
        "subtitle": "Convert YouTube, TikTok, Instagram, and Facebook videos to studio-grade 320kbps MP3 audio or crystal-clear 1080p, 4K, and 8K MP4 files with instant 1-click PC & Mobile downloading.",
        "badge": "✨ Next-Gen Media Engine 2026",
        "active_tab": "all",
        "placeholder": "Paste YouTube, TikTok, Instagram, or Facebook link here...",
        "meta_desc": "Convert YouTube to MP3 320kbps and download 4K/1080p MP4 videos from YouTube, TikTok without watermark, Instagram, and Facebook. Free, unlimited, and fast.",
        "article_h2": "The Ultimate All-in-One Online Media Converter & Downloader",
        "article_p1": "MediaConvert Pro is designed from the ground up for content creators, music lovers, educators, and everyday users who need an ultra-fast, dependable, and 100% ad-free online media converter. Our platform processes public media streams instantly, giving you direct access to high-fidelity MP3 music tracks, pristine lossless audio, and ultra-high-definition 4K and 1080p video downloads across all your devices.",
        "article_p2": "Whether you are looking to save an entire lecture as an audio podcast, extract background music from a viral TikTok clip without watermarks, or keep high-resolution Instagram Reels for offline viewing, our cloud-accelerated engine delivers instant direct stream resolution with zero waiting queues, zero annoying popups, and zero software installation.",
        "features": [
            {"title": "Multi-Platform Streaming", "desc": "Seamless support for YouTube, YouTube Shorts, TikTok without watermark, Instagram Reels, Facebook Watch, and Twitter / X.", "icon": "fa-solid fa-globe"},
            {"title": "True 320kbps Studio Audio", "desc": "Extract audio with authentic dynamic range preservation at 320kbps, 256kbps, 192kbps, 128kbps, and lossless WAV/FLAC formats.", "icon": "fa-solid fa-music"},
            {"title": "8K & 4K Ultra HD MP4", "desc": "Download videos in high resolutions including 8K (4320p), 4K UHD (2160p), 2K (1440p), and 1080p Full HD with crisp visual clarity.", "icon": "fa-solid fa-film"},
            {"title": "Instant Direct PC Download", "desc": "Files are streamed directly with native download attachment headers, ensuring single-click saving straight to your computer or phone.", "icon": "fa-solid fa-bolt"},
            {"title": "100% Free & No Sign-up", "desc": "No registration, no subscriptions, no daily conversion caps, and no software or browser extensions required.", "icon": "fa-solid fa-circle-check"},
            {"title": "Zero Ad-Intrusions & Secure", "desc": "Clean user interface without deceptive download buttons, malware redirects, or tracking cookies. All traffic is SSL encrypted.", "icon": "fa-solid fa-shield-halved"}
        ],
        "faq": [
            {"q": "How does MediaConvert Pro convert YouTube videos to MP3?", "a": "When you paste a video link, our engine extracts the raw high-bitrate audio stream and formats it into an MP3 container up to 320kbps. The file is streamed directly to your browser for immediate 1-click saving."},
            {"q": "Can I use this tool on my iPhone, iPad, Android, or Mac?", "a": "Yes! MediaConvert Pro runs entirely within your web browser (Safari, Chrome, Edge, Firefox). Simply paste your link and hit Convert on any device without installing apps."},
            {"q": "Is there any limit on how many files I can download daily?", "a": "No. You can convert and download as many videos and songs as you like with completely unlimited access 24/7."}
        ]
    },
    "youtube-to-mp3": {
        "title": "YouTube to MP3 Converter - Free Online 320kbps Audio Downloader",
        "h1": "YouTube to MP3 Converter",
        "subtitle": "Extract authentic studio-grade 320kbps, 256kbps, and 128kbps MP3 audio from any YouTube video or Shorts clip in seconds.",
        "badge": "🎵 YouTube MP3 Studio 320k",
        "active_tab": "yt-mp3",
        "placeholder": "Paste YouTube video or Shorts link (e.g. youtube.com/watch?v=...)",
        "meta_desc": "Free YouTube to MP3 converter. Convert YouTube videos and Shorts into 320kbps, 256kbps, and 128kbps MP3 audio files with high speed and zero ads.",
        "article_h2": "Convert YouTube Videos to High Quality MP3 Audio Online",
        "article_p1": "Converting YouTube videos to MP3 is the most convenient way to enjoy your favorite music tracks, DJ mixes, podcasts, speeches, audiobooks, and motivational speeches offline. Our dedicated YouTube to MP3 converter isolates the master audio stream directly from the source video, preserving the original stereo balance, acoustic richness, and frequency spectrum.",
        "article_p2": "Unlike inferior online tools that encode low-grade 64kbps or 128kbps audio and disguise it as high quality, MediaConvert Pro provides genuine high-bitrate MP3 conversions up to 320kbps. If you need uncompressed audio for professional editing or audiophile playback, you can also select M4A (AAC), WAV, or FLAC lossless audio formats.",
        "features": [
            {"title": "Extreme 320kbps Bitrate", "desc": "Get the highest possible MP3 bitrate with crisp trebles, balanced midtones, and punchy deep bass notes.", "icon": "fa-solid fa-compact-disc"},
            {"title": "YouTube Shorts to MP3", "desc": "Easily convert viral YouTube Shorts audio, trending background sounds, and voiceovers into downloadable MP3s.", "icon": "fa-solid fa-mobile-screen"},
            {"title": "Multi-Format Audio Support", "desc": "Choose between MP3 (320k/256k/192k/128k), M4A AAC, Studio WAV, and Hi-Res Lossless FLAC audio formats.", "icon": "fa-solid fa-sliders"},
            {"title": "Cloud Acceleration", "desc": "Process long YouTube audio streams and playlist clips in seconds with our optimized cloud pipeline.", "icon": "fa-solid fa-cloud-bolt"},
            {"title": "Universal Device Compatibility", "desc": "Downloaded MP3 files work flawlessly across iOS Music, Android media players, Windows Media Player, iTunes, and car stereo systems.", "icon": "fa-solid fa-headphones"},
            {"title": "Strict Privacy Protection", "desc": "We do not store your download logs, user IP history, or converted media files on permanent disks.", "icon": "fa-solid fa-user-shield"}
        ],
        "faq": [
            {"q": "Why is 320kbps MP3 better than standard 128kbps?", "a": "320kbps is the maximum MP3 encoding bitrate. It captures over twice as much audio data per second as 128kbps, ensuring zero compression artifacts, wider stereo depth, and crystal-clear instrument separation."},
            {"q": "Can I convert YouTube music videos on an iPhone or iPad?", "a": "Yes. Open Safari on iOS, paste the YouTube link into our converter, choose MP3 320kbps, and tap Download. The audio will save directly to your Files app and can be played offline in Apple Music or any media player."},
            {"q": "Does this converter work with live streams or long videos?", "a": "Yes, standard live recordings, podcast episodes, and audiobooks up to several hours long can be converted without timeouts."}
        ]
    },
    "youtube-to-mp4": {
        "title": "YouTube to MP4 Converter - Download 8K, 4K, 1080p Full HD Videos",
        "h1": "YouTube to MP4 Video Downloader",
        "subtitle": "Download YouTube videos, Shorts, and documentaries in 8K (4320p), 4K (2160p), 2K (1440p), 1080p Full HD, and 720p HD MP4 format.",
        "badge": "🎬 YouTube MP4 4K / 8K",
        "active_tab": "yt-mp4",
        "placeholder": "Paste YouTube video link to download MP4 (e.g. youtube.com/watch?v=...)",
        "meta_desc": "Download YouTube videos to MP4 in 8K, 4K, 2K, 1080p Full HD and 720p with audio. Fast, free, unlimited, and compatible with PC, Mac, iPhone, and Android.",
        "article_h2": "Download YouTube Videos in High Definition MP4 (8K / 4K / 1080p)",
        "article_p1": "Experience YouTube videos in their full cinematic glory with our free YouTube to MP4 video downloader. From fast-paced gaming clips and 60fps tech reviews to 4K travel vlogs and 8K nature documentaries, our converter enables you to download videos in their highest available resolutions without sacrificing picture or sound quality.",
        "article_p2": "Standard video downloaders often strip audio when downloading 1080p or 4K videos due to YouTube's separate video/audio stream delivery. MediaConvert Pro automatically resolves and pairs high-resolution video streams with crisp audio tracks into a universally compatible MP4 container, ready for offline playback on smart TVs, laptops, tablets, and smartphones.",
        "features": [
            {"title": "8K & 4K Ultra HD", "desc": "Full support for ultra-high-definition 4320p (8K) and 2160p (4K UHD) high-bitrate video streams.", "icon": "fa-solid fa-tv"},
            {"title": "1080p & 720p 60FPS", "desc": "Smooth 60 frames per second playback for high-speed action videos, sports highlights, and gaming footage.", "icon": "fa-solid fa-gauge-high"},
            {"title": "Universal MP4 Format", "desc": "MP4 is natively supported across Windows, macOS, Android, iOS, VLC, QuickTime, and smart TVs.", "icon": "fa-solid fa-circle-play"},
            {"title": "High-Speed CDN Streams", "desc": "Direct CDN stream extraction ensures maximum download bandwidth without server-side throttling.", "icon": "fa-solid fa-download"},
            {"title": "YouTube Shorts Downloader", "desc": "Save trending YouTube Shorts videos in vertical HD MP4 format with clean audio and zero watermarks.", "icon": "fa-solid fa-film"},
            {"title": "Safe & Clean Downloading", "desc": "Zero adware, zero browser popups, and zero third-party software bundles. Just pure, clean video downloads.", "icon": "fa-solid fa-shield-heart"}
        ],
        "faq": [
            {"q": "How do I download a 1080p or 4K YouTube video with audio included?", "a": "Paste the YouTube video link above, click Convert Now, switch to the Video tab, and select 1080p FHD or 4K UHD. Our engine automatically packages both high-definition video and full-quality stereo audio into your download."},
            {"q": "Why is MP4 the best format for video downloads?", "a": "MP4 (H.264 / AAC) is the worldwide standard for digital video. It offers exceptional compression efficiency, preserving vibrant picture detail while keeping file sizes reasonable and playing smoothly on every device."},
            {"q": "Can I download YouTube Shorts as MP4 videos?", "a": "Yes! Copy the link of any YouTube Shorts video and paste it into the converter to download the complete vertical MP4 video file instantly."}
        ]
    },
    "tiktok-downloader": {
        "title": "TikTok Downloader - Download TikTok Video Without Watermark HD & MP3",
        "h1": "TikTok Video & MP3 Downloader",
        "subtitle": "Save TikTok videos without watermark in high definition MP4 or extract original background sounds into 320kbps MP3 audio.",
        "badge": "⚡ TikTok HD No Watermark",
        "active_tab": "tiktok",
        "placeholder": "Paste TikTok video link (e.g. tiktok.com/@user/video/...)",
        "meta_desc": "Free TikTok downloader without watermark. Save TikTok videos in Full HD MP4 or extract trending TikTok music and sounds to MP3 on PC, iPhone, and Android.",
        "article_h2": "Download TikTok Videos Without Watermark in Full HD",
        "article_p1": "TikTok is the epicenter of viral trends, creative edits, funny sketches, and catchy music. However, saving videos directly from the TikTok app leaves a bouncing watermark and username logo across the footage. MediaConvert Pro allows you to download clean TikTok videos without watermark in original HD MP4 quality.",
        "article_p2": "In addition to video downloads, our tool allows you to strip and extract original TikTok audio tracks, viral songs, sound effects, and voice clips directly into high-bitrate MP3 files. It works on all devices without requiring you to install TikTok mods, shady third-party apps, or browser extensions.",
        "features": [
            {"title": "100% No Watermark", "desc": "Removes the bouncing TikTok logo and creator username overlay for a clean, professional video file.", "icon": "fa-solid fa-wand-magic-sparkles"},
            {"title": "Original Full HD Quality", "desc": "Downloads videos in their original uploaded resolution and framerate with zero re-encoding blur.", "icon": "fa-solid fa-image"},
            {"title": "TikTok Sound to MP3", "desc": "Extract trending background sounds, songs, and dialogue clips into standalone 320kbps MP3 files.", "icon": "fa-solid fa-music"},
            {"title": "Works with Short & Full Links", "desc": "Supports both standard desktop URLs and short mobile share links (vt.tiktok.com and vm.tiktok.com).", "icon": "fa-solid fa-link"},
            {"title": "iPhone & Android Ready", "desc": "Save TikTok videos directly to your camera roll or gallery in Mobile Safari and Mobile Chrome.", "icon": "fa-solid fa-mobile"},
            {"title": "Unlimited Free Saves", "desc": "Download as many viral TikTok videos and sound clips as you want with unlimited high-speed bandwidth.", "icon": "fa-solid fa-infinity"}
        ],
        "faq": [
            {"q": "How do I get the link of a TikTok video to download?", "a": "Open the TikTok app, go to the video you want to save, tap the Share button (arrow icon), and select 'Copy Link'. Paste this link into our converter above."},
            {"q": "Where are downloaded TikTok videos saved on my phone?", "a": "On Android, files are saved in your Downloads folder and automatically appear in your Gallery. On iPhone (iOS), files download to the Safari Downloads section and can be saved to your Photos app with one tap."},
            {"q": "Do I need to log into my TikTok account?", "a": "No. You never need to log in or share your account credentials. The downloader works anonymously for all public TikTok videos."}
        ]
    },
    "instagram-downloader": {
        "title": "Instagram Reels & Video Downloader - Save IG Posts, Reels & Audio",
        "h1": "Instagram Reels & Video Downloader",
        "subtitle": "Download Instagram Reels, Video Posts, and IGTV clips in 1080p Full HD MP4 or extract audio tracks into MP3.",
        "badge": "📸 Instagram Reels HD",
        "active_tab": "instagram",
        "placeholder": "Paste Instagram Reel or Video URL (e.g. instagram.com/reel/...)",
        "meta_desc": "Free Instagram video downloader. Save Instagram Reels, video posts, and IGTV in 1080p Full HD MP4 and MP3 audio on iPhone, Android, Mac, and Windows.",
        "article_h2": "Download Instagram Reels and Videos in High Definition",
        "article_p1": "Instagram Reels and video posts showcase incredible travel content, workout routines, delicious recipes, cinematic edits, and artistic inspiration. With MediaConvert Pro, you can easily save any public Instagram Reel or video post directly to your device in crystal-clear 1080p Full HD MP4 format.",
        "article_p2": "Our downloader bypasses Instagram's app restrictions, giving you offline access to high-resolution video streams and background audio. Whether you want to archive inspirational content, edit video compilations, or save viral audio tracks as MP3s, our tool delivers fast, secure, and hassle-free downloads.",
        "features": [
            {"title": "Instagram Reels in 1080p", "desc": "Download viral Instagram Reels in high-definition 1080x1920 vertical format with rich colors.", "icon": "fa-brands fa-instagram"},
            {"title": "Extract Reel Audio to MP3", "desc": "Save original trending Instagram audio tracks and music mixes directly as 320kbps MP3 files.", "icon": "fa-solid fa-music"},
            {"title": "IGTV & Feed Video Posts", "desc": "Full support for standard square and landscape feed video posts as well as long-form IGTV clips.", "icon": "fa-solid fa-film"},
            {"title": "No Instagram Login Required", "desc": "Download public reels and videos anonymously without entering your Instagram username or password.", "icon": "fa-solid fa-lock"},
            {"title": "Direct Mobile Camera Roll Save", "desc": "Easily transfer and save downloaded videos straight into your iPhone Photos or Android Gallery.", "icon": "fa-solid fa-folder-open"},
            {"title": "Superfast Cloud Processing", "desc": "Extract and download Instagram video streams in under 2 seconds with high-speed CDN routing.", "icon": "fa-solid fa-bolt"}
        ],
        "faq": [
            {"q": "How can I copy an Instagram Reel link to download?", "a": "Open the Instagram app, tap the three dots (...) or the Paper Airplane share button on the Reel, and tap 'Copy Link'. Paste that link into MediaConvert Pro."},
            {"q": "Can I download videos from private Instagram accounts?", "a": "Our downloader respects user privacy and only downloads media from public Instagram accounts and publicly shareable reels."},
            {"q": "Does this tool reduce the video quality of the Reel?", "a": "No. We fetch the original source video file provided by Instagram's servers, ensuring zero compression loss and maximum resolution."}
        ]
    },
    "facebook-downloader": {
        "title": "Facebook Video Downloader - Save FB Watch & Reels in 1080p HD",
        "h1": "Facebook Video Downloader",
        "subtitle": "Convert and save Facebook videos, public reels, and FB Watch clips in 1080p Full HD MP4 and high-quality MP3.",
        "badge": "👥 Facebook HD Saver",
        "active_tab": "facebook",
        "placeholder": "Paste Facebook video link (e.g. facebook.com/watch/?v=...)",
        "meta_desc": "Free Facebook video downloader. Download Facebook Watch videos, public reels, and video posts in 1080p Full HD MP4 and MP3 audio online.",
        "article_h2": "Download Facebook Videos and Reels in Full HD Quality",
        "article_p1": "Facebook is home to millions of engaging community videos, news broadcasts, gaming streams, cooking tutorials, and viral Facebook Reels. MediaConvert Pro allows you to easily download and convert any public Facebook video into high-definition 1080p or 720p MP4 files for offline playback.",
        "article_p2": "Our intelligent URL parser supports all Facebook link variations, including standard desktop watch URLs, mobile fb.watch links, and Facebook Reel links. You can also extract audio from Facebook speeches, podcast clips, and live recordings into standalone MP3 format in 1 click.",
        "features": [
            {"title": "1080p Full HD FB Videos", "desc": "Capture Facebook videos in maximum available definition (1080p FHD / 720p HD) with stereo audio.", "icon": "fa-brands fa-facebook"},
            {"title": "Facebook Reels Downloader", "desc": "Download short vertical Facebook Reels with crisp video clarity and no quality degradation.", "icon": "fa-solid fa-mobile-screen"},
            {"title": "Facebook Video to MP3", "desc": "Extract audio commentaries, speech recordings, and music performances into 320kbps MP3 files.", "icon": "fa-solid fa-file-audio"},
            {"title": "Supports All FB Link Types", "desc": "Works with facebook.com/watch, fb.watch short links, and mobile Facebook video shares seamlessly.", "icon": "fa-solid fa-link"},
            {"title": "100% Free & No Account Needed", "desc": "No need to connect your personal Facebook profile or install questionable browser extensions.", "icon": "fa-solid fa-unlock"},
            {"title": "Lightning Fast Downloads", "desc": "Direct CDN stream extraction delivers high download speeds directly to your PC, Mac, or phone.", "icon": "fa-solid fa-gauge-high"}
        ],
        "faq": [
            {"q": "How do I download a video from Facebook?", "a": "Click the 'Share' button beneath the Facebook video or Reel, select 'Copy link', paste it into our search bar, and click 'Convert Now' to choose your quality."},
            {"q": "Can I convert Facebook videos to MP3 audio files?", "a": "Yes! Simply select the MP3 audio format after pasting your Facebook link to download the audio track alone."},
            {"q": "Is it safe to download Facebook videos with MediaConvert Pro?", "a": "Absolutely. Our platform is completely secure, does not require your Facebook credentials, and operates over encrypted HTTPS connections."}
        ]
    },
    "youtube-320kbps": {
        "title": "YouTube to MP3 320kbps Converter - Studio HQ Audio Master Free",
        "h1": "YouTube to MP3 320kbps (Studio Quality)",
        "subtitle": "Convert YouTube music videos and audio tracks into authentic maximum-bitrate 320kbps MP3 audio with full dynamic fidelity.",
        "badge": "🔥 320kbps Studio Master",
        "active_tab": "yt-mp3",
        "placeholder": "Paste YouTube music link for 320kbps MP3 (youtube.com/watch?v=...)",
        "meta_desc": "Convert YouTube to MP3 320kbps extreme quality online for free. Enjoy maximum bitrate audio conversion with studio richness, punchy bass, and crystal-clear sound.",
        "article_h2": "Experience Studio-Grade YouTube to MP3 320kbps Audio Conversion",
        "article_p1": "For true audiophiles, music enthusiasts, DJs, and sound engineers, standard 128kbps audio simply does not cut it. Compression artifacts, washed-out high frequencies, and muffled bass can ruin the listening experience. Our dedicated YouTube to MP3 320kbps converter is engineered specifically to extract and encode audio at the highest possible bitrate.",
        "article_p2": "By utilizing optimal acoustic quantization algorithms, MediaConvert Pro preserves the fullest dynamic range, crispest stereo separation, and most articulate vocal clarity possible from source streams. Enjoy your favorite songs, concert recordings, electronic mixes, and ambient soundscapes in true 320kbps master quality on your headphones, sound systems, and studio monitors.",
        "features": [
            {"title": "True Maximum 320kbps Bitrate", "desc": "Encodes at the upper ceiling of the MP3 standard for unmatched clarity, punch, and depth.", "icon": "fa-solid fa-music"},
            {"title": "Full Stereo Panning & Dynamics", "desc": "Preserves precise stereo imaging, wide soundstages, and intricate acoustic instrument details.", "icon": "fa-solid fa-sliders"},
            {"title": "Lossless FLAC & WAV Option", "desc": "Need bit-perfect uncompressed audio? We also offer direct WAV and FLAC lossless format options.", "icon": "fa-solid fa-compact-disc"},
            {"title": "Ideal for DJs & Audio Editors", "desc": "Download studio-quality tracks ready for use in DAWs, DJ mixing software, and playlist libraries.", "icon": "fa-solid fa-headphones-simple"},
            {"title": "High-Speed Direct Download", "desc": "Converts and delivers 320kbps audio files in seconds straight to your PC, Mac, iPhone, or Android.", "icon": "fa-solid fa-bolt"},
            {"title": "100% Free & Unlimited", "desc": "Convert your entire favorite music playlist track-by-track with zero subscription fees or caps.", "icon": "fa-solid fa-infinity"}
        ],
        "faq": [
            {"q": "What makes 320kbps the best MP3 bitrate?", "a": "320kbps (kilobits per second) represents the highest audio resolution supported by the MP3 codec. It retains virtually all frequencies up to 20kHz that human ears can perceive, eliminating the 'tinny' compression distortion common in low-bitrate rips."},
            {"q": "Will 320kbps MP3 files work on all devices?", "a": "Yes! MP3 is the most universally compatible audio format in the world. 320kbps MP3 files play seamlessly on iOS, Android, macOS, Windows, car audio systems, smart speakers, and standalone MP3 players."},
            {"q": "How fast is the 320kbps MP3 conversion process?", "a": "Our cloud audio stream processing extracts and packages your 320kbps MP3 file in approximately 1 to 3 seconds, ready for instant direct download."}
        ]
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
