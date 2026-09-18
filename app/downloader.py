import os
import re
import urllib.parse
from typing import Dict, Any, Optional, List
import requests
import yt_dlp

COMMON_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-us,en;q=0.5',
    'Sec-Fetch-Mode': 'navigate',
}

YOUTUBE_EXTRACTOR_ARGS = {
    'youtube': {
        'player_client': ['mweb', 'web', 'android', 'ios'],
        'player_skip': ['configs'],
    }
}

def detect_platform(url: str) -> Dict[str, str]:
    url_lower = url.lower()
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return {"name": "YouTube", "id": "youtube", "color": "from-red-500 to-rose-600", "badge": "YouTube"}
    elif "tiktok.com" in url_lower:
        return {"name": "TikTok", "id": "tiktok", "color": "from-pink-500 to-cyan-500", "badge": "TikTok"}
    elif "instagram.com" in url_lower:
        return {"name": "Instagram", "id": "instagram", "color": "from-purple-600 to-pink-500", "badge": "Instagram"}
    elif "facebook.com" in url_lower or "fb.watch" in url_lower:
        return {"name": "Facebook", "id": "facebook", "color": "from-blue-600 to-indigo-600", "badge": "Facebook"}
    elif "twitter.com" in url_lower or "x.com" in url_lower:
        return {"name": "Twitter / X", "id": "twitter", "color": "from-slate-800 to-zinc-900", "badge": "X (Twitter)"}
    elif "soundcloud.com" in url_lower:
        return {"name": "SoundCloud", "id": "soundcloud", "color": "from-orange-500 to-amber-600", "badge": "SoundCloud"}
    elif "pinterest.com" in url_lower:
        return {"name": "Pinterest", "id": "pinterest", "color": "from-red-600 to-rose-700", "badge": "Pinterest"}
    else:
        return {"name": "Universal Video/Audio", "id": "universal", "color": "from-indigo-600 to-violet-600", "badge": "Universal"}

def extract_youtube_id(url: str) -> Optional[str]:
    match = re.search(r'(?:v=|\/|youtu\.be\/|shorts\/)([0-9A-Za-z_-]{11})', url)
    return match.group(1) if match else None

def sanitize_filename(title: str) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|]', "", title)
    return cleaned.strip()[:60] or "media_download"

def format_duration(seconds: Optional[int]) -> str:
    if not seconds:
        return "HD Video"
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    if hours > 0:
        return f"{hours}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"

def format_number(num: Optional[int]) -> str:
    if not num:
        return ""
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    if num >= 1_000:
        return f"{num / 1_000:.1f}K"
    return str(num)

def format_size(bytes_val: Optional[int]) -> str:
    if not bytes_val or bytes_val <= 0:
        return ""
    mb = bytes_val / (1024 * 1024)
    if mb >= 1024:
        return f"{mb / 1024:.2f} GB"
    return f"{mb:.1f} MB"

def get_standard_formats():
    resolution_tiers = [
        {"format": "mp4", "quality": "4320p", "height": 4320, "label": "MP4 - 8K Ultra HD (4320p)", "badge": "8K Ultra HD", "tag": "8K UHD", "res_code": "4320p", "size": ""},
        {"format": "mp4", "quality": "2160p", "height": 2160, "label": "MP4 - 4K Ultra HD (2160p)", "badge": "4K Ultra HD", "tag": "4K UHD", "res_code": "2160p", "size": ""},
        {"format": "mp4", "quality": "1440p", "height": 1440, "label": "MP4 - 2K QHD (1440p)", "badge": "2K QHD", "tag": "2K QHD", "res_code": "1440p", "size": ""},
        {"format": "mp4", "quality": "1080p", "height": 1080, "label": "MP4 - 1080p Full HD", "badge": "1080p FHD", "tag": "Full HD", "res_code": "1080p", "size": "", "is_popular": True},
        {"format": "mp4", "quality": "720p", "height": 720, "label": "MP4 - 720p HD", "badge": "720p HD", "tag": "HD", "res_code": "720p", "size": ""},
        {"format": "mp4", "quality": "480p", "height": 480, "label": "MP4 - 480p SD", "badge": "480p SD", "tag": "Medium", "res_code": "480p", "size": ""},
        {"format": "mp4", "quality": "360p", "height": 360, "label": "MP4 - 360p Medium", "badge": "360p", "tag": "Data Saver", "res_code": "360p", "size": ""},
        {"format": "mp4", "quality": "240p", "height": 240, "label": "MP4 - 240p Small", "badge": "240p", "tag": "Low", "res_code": "240p", "size": ""},
        {"format": "mp4", "quality": "144p", "height": 144, "label": "MP4 - 144p Mobile", "badge": "144p", "tag": "Light", "res_code": "144p", "size": ""},
    ]

    audio_formats = [
        {"format": "mp3", "quality": "320kbps", "label": "MP3 - 320 kbps (High Quality)", "bitrate": "320", "tag": "320 kbps", "badge": "320k", "is_popular": True},
        {"format": "mp3", "quality": "256kbps", "label": "MP3 - 256 kbps (Standard HQ)", "bitrate": "256", "tag": "256 kbps", "badge": "256k", "is_popular": False},
        {"format": "mp3", "quality": "192kbps", "label": "MP3 - 192 kbps (Medium)", "bitrate": "192", "tag": "192 kbps", "badge": "192k", "is_popular": False},
        {"format": "mp3", "quality": "128kbps", "label": "MP3 - 128 kbps (Fast Download)", "bitrate": "128", "tag": "128 kbps", "badge": "128k", "is_popular": False}
    ]

    return resolution_tiers, audio_formats

FASTSAVER_API_KEY = os.environ.get("FASTSAVER_API_KEY", "fs_sk_8t8c1m9n1d9f5r6h3m4k9a7a8p1o")
# Set to True when you want to use FastSaver API credits, or False to preserve credits
ENABLE_FASTSAVER = os.environ.get("ENABLE_FASTSAVER", "true").lower() in ["true", "1", "yes"]

FASTSAVER_HEADERS = {
    "x-api-key": FASTSAVER_API_KEY,
    "Authorization": f"Bearer {FASTSAVER_API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def extract_media_info(url: str) -> Dict[str, Any]:
    """Extract metadata reliably across all platforms with optional FastSaver integration"""
    platform_info = detect_platform(url)
    std_video, std_audio = get_standard_formats()
    yt_id = extract_youtube_id(url)

    # 1. FastSaver Cloud Engine (Only active when ENABLE_FASTSAVER is True)
    if ENABLE_FASTSAVER and (yt_id or platform_info["id"] == "youtube"):
        try:
            r = requests.get(
                "https://api.fastsaver.io/v1/youtube/info",
                params={"url": url},
                headers=FASTSAVER_HEADERS,
                timeout=10
            )
            if r.status_code == 200:
                data = r.json()
                if data.get("ok"):
                    title = data.get("title", f"YouTube Video ({yt_id})")
                    duration = data.get("duration", 0)
                    thumbnail = (data.get("thumbnails", {}) or {}).get("max") or data.get("thumbnail") or f"https://i.ytimg.com/vi/{yt_id}/hqdefault.jpg"
                    uploader = data.get("author") or "YouTube Creator"
                    
                    fs_formats = data.get("formats", [])
                    available_resolutions = set()
                    for f in fs_formats:
                        fmt_str = f.get("format", "")
                        if fmt_str and "p" in fmt_str:
                            available_resolutions.add(fmt_str)

                    video_formats = []
                    has_popular = False
                    for tier in std_video:
                        if not available_resolutions or tier["res_code"] in available_resolutions or tier["res_code"] in ["1080p", "720p", "480p", "360p"]:
                            is_pop = False
                            if not has_popular and tier["res_code"] in ["1080p", "720p"]:
                                is_pop = True
                                has_popular = True

                            video_formats.append({
                                "format": "mp4",
                                "quality": tier["res_code"],
                                "label": tier["label"],
                                "resolution": tier["res_code"],
                                "tag": tier["tag"],
                                "badge": tier["badge"],
                                "size": tier.get("size", ""),
                                "is_popular": is_pop
                            })

                    return {
                        "success": True,
                        "url": url,
                        "title": title,
                        "thumbnail": thumbnail,
                        "duration": format_duration(duration),
                        "duration_seconds": duration,
                        "uploader": uploader,
                        "views": "",
                        "platform": platform_info,
                        "audio_formats": std_audio,
                        "video_formats": video_formats or std_video,
                        "id": yt_id or data.get("video_id", "media")
                    }
        except Exception:
            pass

    # 2. Universal yt-dlp Engine for TikTok, Instagram, Facebook, SoundCloud, etc.
    ydl_opts = {
        'extract_flat': False,
        'skip_download': True,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'http_headers': COMMON_HEADERS,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web', 'mweb'],
                'player_skip': ['configs'],
            }
        },
        'socket_timeout': 15,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Video Media')
            duration = info.get('duration')
            thumbnail = info.get('thumbnail')
            uploader = info.get('uploader') or info.get('channel') or platform_info['name']
            views = info.get('view_count')
            
            raw_formats = info.get('formats', [])
            available_heights = set()
            height_to_size = {}

            for f in raw_formats:
                h = f.get('height')
                if h and h >= 144:
                    available_heights.add(h)
                    size = f.get('filesize') or f.get('filesize_approx')
                    if size and (h not in height_to_size or size > height_to_size[h]):
                        height_to_size[h] = size

            video_formats = []
            if available_heights:
                sorted_detected = sorted(list(available_heights), reverse=True)
                has_popular = False
                
                for tier in std_video:
                    matching_h = None
                    for h in sorted_detected:
                        if abs(h - tier["height"]) <= 60 or (tier["height"] >= 1080 and h >= tier["height"] * 0.9):
                            matching_h = h
                            break
                    
                    if matching_h or tier["height"] in [1080, 720, 480, 360]:
                        is_pop = False
                        if not has_popular and (tier["height"] == 2160 or tier["height"] == 1080 or (tier["height"] == sorted_detected[0])):
                            is_pop = True
                            has_popular = True

                        size_str = format_size(height_to_size.get(tier["height"]) or height_to_size.get(matching_h))

                        video_formats.append({
                            "format": "mp4",
                            "quality": tier["res_code"],
                            "label": tier["label"],
                            "resolution": tier["res_code"],
                            "tag": tier["tag"],
                            "badge": tier["badge"],
                            "size": size_str,
                            "is_popular": is_pop
                        })
            else:
                video_formats = std_video

            return {
                "success": True,
                "url": url,
                "title": title,
                "thumbnail": thumbnail or (f"https://i.ytimg.com/vi/{yt_id}/hqdefault.jpg" if yt_id else None),
                "duration": format_duration(duration),
                "duration_seconds": duration,
                "uploader": uploader,
                "views": format_number(views),
                "platform": platform_info,
                "audio_formats": std_audio,
                "video_formats": video_formats,
                "id": info.get('id', yt_id or 'media')
            }
    except Exception as e:
        # Fallback to oEmbed for active YouTube videos
        if yt_id:
            try:
                oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={yt_id}&format=json"
                r = requests.get(oembed_url, timeout=5)
                if r.status_code == 200:
                    oembed_data = r.json()
                    return {
                        "success": True,
                        "url": url,
                        "title": oembed_data.get("title", f"YouTube Video ({yt_id})"),
                        "thumbnail": f"https://i.ytimg.com/vi/{yt_id}/hqdefault.jpg",
                        "duration": "HD Video",
                        "duration_seconds": 0,
                        "uploader": oembed_data.get("author_name", "YouTube Creator"),
                        "views": "",
                        "platform": platform_info,
                        "audio_formats": std_audio,
                        "video_formats": std_video,
                        "id": yt_id
                    }
                elif r.status_code == 404:
                    return {
                        "success": False,
                        "error": "This video is unavailable or private on YouTube. Please check the link."
                    }
            except Exception:
                pass

        return {
            "success": True,
            "url": url,
            "title": f"Media Stream ({platform_info['name']})",
            "thumbnail": f"https://i.ytimg.com/vi/{yt_id}/hqdefault.jpg" if yt_id else "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=600&q=80",
            "duration": "High Definition",
            "duration_seconds": 0,
            "uploader": platform_info['name'],
            "views": "",
            "platform": platform_info,
            "audio_formats": std_audio,
            "video_formats": std_video,
            "id": yt_id or "media"
        }

def resolve_stream_url(url: str, format_type: str, quality: str) -> Dict[str, Any]:
    """Extracts direct streaming stream URL using FastSaver API tunnel with yt-dlp fallback"""
    platform_info = detect_platform(url)
    yt_id = extract_youtube_id(url)

    # 1. FastSaver Cloud High Speed Tunnel (Only active when ENABLE_FASTSAVER is True)
    if ENABLE_FASTSAVER and (yt_id or platform_info["id"] == "youtube"):
        try:
            req_format = "audio" if format_type in ["mp3", "m4a", "wav", "flac"] else quality
            # Ensure quality is valid format tag like '720p', '1080p', or 'audio'
            if req_format not in ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p", "audio"]:
                req_format = "720p" if format_type == "mp4" else "audio"

            r = requests.post(
                "https://api.fastsaver.io/v1/youtube/download",
                json={"url": url, "format": req_format},
                headers=FASTSAVER_HEADERS,
                timeout=15
            )
            if r.status_code == 200:
                data = r.json()
                if data.get("ok") and data.get("download_url"):
                    return {
                        "success": True,
                        "stream_url": data["download_url"],
                        "file_name": data.get("filename") or f"media_{yt_id}.{format_type}",
                        "title": data.get("filename", "Media Download")
                    }
        except Exception:
            pass

    # 2. Universal Multi-platform Stream Resolver (TikTok, Instagram, Facebook, Twitter, SoundCloud)
    ydl_opts = {
        'extract_flat': False,
        'skip_download': True,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'http_headers': COMMON_HEADERS,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web', 'mweb'],
                'player_skip': ['configs'],
            }
        },
        'socket_timeout': 20,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title') or 'media_download'
            formats = info.get('formats', [])
            
            chosen_url = None
            ext = format_type

            if format_type in ["mp3", "m4a", "wav", "flac"]:
                audio_streams = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none' and f.get('url')]
                if audio_streams:
                    audio_streams.sort(key=lambda x: (x.get('abr') or 0), reverse=True)
                    chosen_url = audio_streams[0]['url']
                elif formats:
                    with_audio = [f for f in formats if f.get('acodec') != 'none' and f.get('url')]
                    if with_audio:
                        with_audio.sort(key=lambda x: (x.get('abr') or 0), reverse=True)
                        chosen_url = with_audio[0]['url']
                    else:
                        chosen_url = formats[0].get('url')
                ext = "mp3" if format_type == "mp3" else ("m4a" if format_type == "m4a" else "wav")
            else:
                req_h = int(quality.replace("p", "")) if "p" in quality else 720
                video_streams = [f for f in formats if f.get('url') and (f.get('vcodec') != 'none' or f.get('ext') == 'mp4')]
                
                prog_streams = [f for f in video_streams if f.get('acodec') != 'none' and f.get('vcodec') != 'none']
                if prog_streams:
                    prog_streams.sort(key=lambda x: abs((x.get('height') or 0) - req_h))
                    chosen_url = prog_streams[0]['url']
                elif video_streams:
                    video_streams.sort(key=lambda x: abs((x.get('height') or 0) - req_h))
                    chosen_url = video_streams[0]['url']
                elif formats:
                    chosen_url = formats[-1].get('url')
                ext = "mp4"

            if chosen_url:
                filename = f"{sanitize_filename(title)}.{ext}"
                return {
                    "success": True,
                    "stream_url": chosen_url,
                    "file_name": filename,
                    "title": title
                }

    except Exception:
        pass

    return {
        "success": False,
        "error": "Unable to extract direct download stream. Please check the link and try again."
    }
