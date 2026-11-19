import os, sys, pprint
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from app.seo_content import SEO_PAGES

REPL = [
 ("Step-by-Step Guide to Saving YouTube Shorts Without Watermarks", "Step-by-Step Guide to Saving Your YouTube Shorts for Offline Viewing"),
 ("Saving YouTube Shorts Without Watermarks", "Saving YouTube Shorts for Offline Viewing"),
 ("without dealing with intrusive watermarks or forced app store downloads", "without installing extra apps"),
 ("Unlimited (up to 12+ hours)", "Long-form (up to several hours, where supported)"),
 ("Our service guarantees zero added watermarks: no promotional logos, no third-party branding, and no visual overlays are ever stamped onto your saved video.", "Files are saved as the source provides them: our service does not add logos, branding, or visual overlays to your video."),
 ("you completely bypass the risks of untrusted mobile apps", "you avoid many of the risks of untrusted mobile apps"),
 ("No watermark 9:16 vertical MP4 &amp; viral audio", "Clean 9:16 vertical MP4 &amp; audio"),
 ("YT4MP3 delivers pure source video files without added watermarks, author stamps, or website branding.", "YT4MP3 delivers the source video file as provided, without adding logos, stamps, or website branding."),
 ("Do downloaded YouTube Shorts have watermarks?", "Does YT4MP3 add logos or branding to saved Shorts?"),
 ("YT4MP3 provides unlimited free downloads for everyday personal and educational archiving.", "YT4MP3 is free to use for everyday personal and educational archiving of content you are allowed to save."),
 ("Download original, clean YouTube Shorts without third-party watermarks, channel stamps, or annoying promotional overlays.", "Save YouTube Shorts as clean MP4 files with no extra overlays added by our service."),
 ("No Watermarks or Logos", "Clean Files, No Added Branding"),
 ("Fast, free vertical video downloader with zero watermarks.", "Fast, free vertical video converter for Shorts you own or are allowed to save."),
 ("or convert to 320kbps MP3 audio with zero watermarks.", "or convert to 320kbps MP3 audio."),
 ("Free online YouTube audio downloader with unlimited conversions.", "Free online YouTube to MP3 converter for personal use."),
 ("No, YT4MP3 allows unlimited video conversions and downloads for everyday personal and educational use.", "YT4MP3 is free for everyday personal and educational use of content you are permitted to save."),
 ("No, our system never overlays watermarks, branding stamps, or promotional banners on your downloaded video files.", "No. Our service does not add overlays, branding stamps, or banners to the files you save."),
 ("Are there any hidden watermarks on downloaded videos?", "Does the service add anything to downloaded videos?"),
 ("zero pop-ups, watermarks, or third-party installers", "no installers or software downloads"),
 ("Standard low-tier video rippers often drop", "Low-quality converters often drop"),
 ("to convert and download music files", "to convert audio files"),
 ("Apple Music, Spotify Local Files, Windows Media Player, VLC Media Player, or Winamp", "Apple Music, Windows Media Player, VLC Media Player, or Winamp"),
 ("Samsung Music, VLC, Google Files, or Spotify Local Files", "Samsung Music, VLC, or Google Files"),
 ("educational lifehacks", "educational tips"),
 ("Download YouTube videos and Shorts in 1080p Full HD, 2K, and 4K MP4 with YT4MP3.", "Convert YouTube links to MP4 in up to 1080p Full HD, 2K, or 4K when the source offers it, with YT4MP3."),
 ("Download YouTube videos and Shorts in 1080p Full HD, 2K, and 4K resolutions with smooth 60fps frame rates.", "Save videos in 1080p Full HD, 2K, or 4K when the source offers it, with smooth 60fps where available."),
]

def fix(o):
    if isinstance(o, dict):
        return {k: fix(v) for k, v in o.items()}
    if isinstance(o, list):
        return [fix(v) for v in o]
    if isinstance(o, str):
        for a, b in REPL:
            o = o.replace(a, b)
        # keep toc ids consistent
        o = o.replace("without-watermarks", "for-offline-viewing")
        return o
    return o

new = fix(SEO_PAGES)
out = "# -*- coding: utf-8 -*-\n\nSEO_PAGES = " + pprint.pformat(new, width=120) + "\n"
with open(os.path.join(ROOT, "app", "seo_content.py"), "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
print("rewritten")
