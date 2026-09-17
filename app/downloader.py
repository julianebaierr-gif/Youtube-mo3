import os
import re
import uuid
import time
import threading
import tempfile
from typing import Dict, Any, Optional, List
import imageio_ffmpeg
import yt_dlp

FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

TEMP_DOWNLOAD_DIR = os.path.join(tempfile.gettempdir(), "media_converter_downloads")
os.makedirs(TEMP_DOWNLOAD_DIR, exist_ok=True)

# In-memory progress tracking
TASKS: Dict[str, Dict[str, Any]] = {}

COMMON_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-us,en;q=0.5',
    'Sec-Fetch-Mode': 'navigate',
}

YOUTUBE_EXTRACTOR_ARGS = {
    'youtube': {
        'player_client': ['mweb', 'web', 'android'],
        'player_skip': ['js', 'configs'],
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

def format_duration(seconds: Optional[int]) -> str:
    if not seconds:
        return "Unknown"
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

def extract_media_info(url: str) -> Dict[str, Any]:
    """Extract metadata and all available streams/formats up to 8K UHD"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'ffmpeg_location': FFMPEG_PATH,
        'skip_download': True,
        'noplaylist': True,
        'extractor_args': YOUTUBE_EXTRACTOR_ARGS,
        'http_headers': COMMON_HEADERS,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            platform_info = detect_platform(url)
            
            title = info.get('title', 'Unknown Title')
            duration = info.get('duration')
            thumbnail = info.get('thumbnail')
            uploader = info.get('uploader') or info.get('channel') or platform_info['name']
            views = info.get('view_count')
            
            raw_formats = info.get('formats', [])
            available_heights = set()
            height_to_size = {}

            # Calculate sizes from raw formats
            for f in raw_formats:
                h = f.get('height')
                if h and h >= 144:
                    available_heights.add(h)
                    size = f.get('filesize') or f.get('filesize_approx')
                    if size and (h not in height_to_size or size > height_to_size[h]):
                        height_to_size[h] = size

            resolution_tiers = [
                {"height": 4320, "label": "MP4 - 8K Ultra HD (4320p)", "badge": "8K Ultra HD", "tag": "8K UHD", "res_code": "4320p"},
                {"height": 2160, "label": "MP4 - 4K Ultra HD (2160p)", "badge": "4K Ultra HD", "tag": "4K UHD", "res_code": "2160p"},
                {"height": 1440, "label": "MP4 - 2K QHD (1440p)", "badge": "2K QHD", "tag": "2K QHD", "res_code": "1440p"},
                {"height": 1080, "label": "MP4 - 1080p Full HD", "badge": "1080p FHD", "tag": "Full HD", "res_code": "1080p"},
                {"height": 720, "label": "MP4 - 720p HD", "badge": "720p HD", "tag": "HD", "res_code": "720p"},
                {"height": 480, "label": "MP4 - 480p SD", "badge": "480p SD", "tag": "Medium", "res_code": "480p"},
                {"height": 360, "label": "MP4 - 360p Medium", "badge": "360p", "tag": "Data Saver", "res_code": "360p"},
                {"height": 240, "label": "MP4 - 240p Small", "badge": "240p", "tag": "Low", "res_code": "240p"},
                {"height": 144, "label": "MP4 - 144p Mobile", "badge": "144p", "tag": "Light", "res_code": "144p"},
            ]

            video_formats = []
            
            if available_heights:
                sorted_detected = sorted(list(available_heights), reverse=True)
                has_popular = False
                
                for tier in resolution_tiers:
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
                for tier in resolution_tiers:
                    if tier["height"] <= 2160:
                        video_formats.append({
                            "format": "mp4",
                            "quality": tier["res_code"],
                            "label": tier["label"],
                            "resolution": tier["res_code"],
                            "tag": tier["tag"],
                            "badge": tier["badge"],
                            "size": "",
                            "is_popular": tier["height"] == 1080
                        })

            # Full Audio Quality Range
            audio_formats = [
                {
                    "format": "mp3",
                    "quality": "320kbps",
                    "label": "MP3 - 320 kbps (Extreme Studio HQ)",
                    "bitrate": "320",
                    "tag": "Studio Master",
                    "badge": "320k HQ",
                    "is_popular": True
                },
                {
                    "format": "mp3",
                    "quality": "256kbps",
                    "label": "MP3 - 256 kbps (High Quality)",
                    "bitrate": "256",
                    "tag": "High Fidelity",
                    "badge": "256k",
                    "is_popular": False
                },
                {
                    "format": "mp3",
                    "quality": "192kbps",
                    "label": "MP3 - 192 kbps (Standard)",
                    "bitrate": "192",
                    "tag": "Standard",
                    "badge": "192k",
                    "is_popular": False
                },
                {
                    "format": "mp3",
                    "quality": "128kbps",
                    "label": "MP3 - 128 kbps (Fast Download)",
                    "bitrate": "128",
                    "tag": "Compact",
                    "badge": "128k",
                    "is_popular": False
                },
                {
                    "format": "m4a",
                    "quality": "Original",
                    "label": "M4A / AAC Audio (Original Bitrate)",
                    "bitrate": "original",
                    "tag": "Native Stream",
                    "badge": "M4A",
                    "is_popular": False
                },
                {
                    "format": "flac",
                    "quality": "Lossless",
                    "label": "FLAC Audio (Lossless Hi-Res)",
                    "bitrate": "flac",
                    "tag": "Audiophile",
                    "badge": "FLAC",
                    "is_popular": False
                },
                {
                    "format": "wav",
                    "quality": "Lossless",
                    "label": "WAV Audio (Uncompressed Studio)",
                    "bitrate": "wav",
                    "tag": "Studio WAV",
                    "badge": "WAV",
                    "is_popular": False
                }
            ]

            return {
                "success": True,
                "url": url,
                "title": title,
                "thumbnail": thumbnail,
                "duration": format_duration(duration),
                "duration_seconds": duration,
                "uploader": uploader,
                "views": format_number(views),
                "platform": platform_info,
                "audio_formats": audio_formats,
                "video_formats": video_formats,
                "id": info.get('id', 'media')
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def start_conversion_job(url: str, format_type: str, quality: str) -> str:
    """Starts background conversion job and returns task_id"""
    task_id = str(uuid.uuid4())
    TASKS[task_id] = {
        "status": "starting",
        "progress": 5,
        "message": "Initializing high-speed stream...",
        "speed": "",
        "eta": "",
        "file_path": None,
        "file_name": None,
        "size_mb": 0,
        "error": None
    }

    thread = threading.Thread(target=_run_conversion_worker, args=(task_id, url, format_type, quality), daemon=True)
    thread.start()
    return task_id

def _run_conversion_worker(task_id: str, url: str, format_type: str, quality: str):
    task = TASKS[task_id]
    output_template = os.path.join(TEMP_DOWNLOAD_DIR, f"%(title).50s-{task_id[:8]}.%(ext)s")

    def progress_hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                pct = min(95, int((downloaded / total) * 90) + 5)
            else:
                pct = 40
            
            speed_str = ""
            if d.get('speed'):
                spd = d['speed'] / (1024 * 1024)
                speed_str = f"{spd:.1f} MB/s"
            
            eta_str = ""
            if d.get('eta'):
                eta_str = f"{d['eta']}s"

            task["status"] = "downloading"
            task["progress"] = pct
            task["speed"] = speed_str
            task["eta"] = eta_str
            task["message"] = f"Downloading stream ({pct}% - {speed_str})"
            
        elif d['status'] == 'finished':
            task["status"] = "processing"
            task["progress"] = 96
            task["message"] = "Processing & converting media..."

    base_ydl_opts = {
        'ffmpeg_location': FFMPEG_PATH,
        'outtmpl': output_template,
        'progress_hooks': [progress_hook],
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'extractor_args': YOUTUBE_EXTRACTOR_ARGS,
        'http_headers': COMMON_HEADERS,
        'socket_timeout': 30,
        'retries': 10,
        'fragment_retries': 10,
    }

    if format_type == "mp3":
        bitrate = quality.replace("kbps", "") if "kbps" in quality else "320"
        ydl_opts = {
            **base_ydl_opts,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': bitrate,
            }],
        }
    elif format_type == "m4a":
        ydl_opts = {
            **base_ydl_opts,
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }],
        }
    elif format_type == "flac":
        ydl_opts = {
            **base_ydl_opts,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'flac',
            }],
        }
    elif format_type == "wav":
        ydl_opts = {
            **base_ydl_opts,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
        }
    else: # mp4 video
        res_height = quality.replace("p", "") if "p" in quality else "2160"
        ydl_opts = {
            **base_ydl_opts,
            'format': f'bestvideo[height<={res_height}]+bestaudio/best[height<={res_height}]/best',
            'merge_output_format': 'mp4',
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if format_type in ["mp3", "m4a", "flac", "wav"]:
                filename = os.path.splitext(filename)[0] + f".{format_type}"
            else:
                filename = os.path.splitext(filename)[0] + ".mp4"
                
            if not os.path.exists(filename):
                base = task_id[:8]
                for f in os.listdir(TEMP_DOWNLOAD_DIR):
                    if base in f:
                        filename = os.path.join(TEMP_DOWNLOAD_DIR, f)
                        break

            task["status"] = "completed"
            task["progress"] = 100
            task["message"] = "Ready for download!"
            task["file_path"] = filename
            task["file_name"] = os.path.basename(filename)
            task["size_mb"] = round(os.path.getsize(filename) / (1024 * 1024), 2) if os.path.exists(filename) else 0

    except Exception as e:
        task["status"] = "error"
        task["error"] = str(e)
        task["message"] = f"Conversion failed: {str(e)}"

def get_job_status(task_id: str) -> Optional[Dict[str, Any]]:
    return TASKS.get(task_id)
