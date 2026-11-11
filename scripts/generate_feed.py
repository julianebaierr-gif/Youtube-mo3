import html
import os
import sys

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app.i18n import SUPPORTED_LANGUAGES, get_page_content

def build_feed_xml() -> str:
    pages = ["home", "youtube-to-mp3", "youtube-to-mp4", "youtube-shorts-downloader"]
    
    # Staggered publication dates across the last 3 months leading up to today (Nov 04, 2026)
    release_dates = {
        "youtube-to-mp3": "Tue, 18 Aug 2026 10:00:00 +0000",       # 3 months ago (August)
        "youtube-to-mp4": "Tue, 15 Sep 2026 10:00:00 +0000",       # 2 months ago (September)
        "youtube-shorts-downloader": "Thu, 15 Oct 2026 10:00:00 +0000", # 1 month ago (October)
        "home": "Wed, 04 Nov 2026 10:00:00 +0000",                 # Today (November 4, 2026)
    }
    
    urls = []
    for lang in SUPPORTED_LANGUAGES:
        for p in pages:
            data = get_page_content(lang, p)
            if lang == "en":
                link = "https://www.yt4mp3.com/" if p == "home" else f"https://www.yt4mp3.com/{p}"
            else:
                link = f"https://www.yt4mp3.com/{lang}/" if p == "home" else f"https://www.yt4mp3.com/{lang}/{p}"
            title = data.get("title") or "YT4MP3"
            desc = data.get("meta_desc") or "YouTube converter tool"
            desc = desc.replace("Cepat, cepat", "Cepat")
            pub_date = release_dates.get(p, "Wed, 04 Nov 2026 10:00:00 +0000")
            urls.append((link, title, desc, lang, pub_date))

    items_xml = "".join([
        f"""    <item>
      <title>{html.escape(title, quote=True)}</title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <description>{html.escape(desc, quote=True)}</description>
      <dc:language>{item_lang}</dc:language>
      <pubDate>{pub_date}</pubDate>
    </item>\n""" for link, title, desc, item_lang, pub_date in urls
    ])

    feed_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel>
    <title>YT4MP3 - YouTube Media Converter Tools &amp; Updates</title>
    <link>https://www.yt4mp3.com/</link>
    <description>Latest tools and multilingual updates for converting YouTube videos to MP3 and MP4.</description>
    <language>en-us</language>
    <lastBuildDate>Wed, 11 Nov 2026 13:00:00 +0000</lastBuildDate>
    <atom:link href="https://www.yt4mp3.com/feed.xml" rel="self" type="application/rss+xml" />
{items_xml}  </channel>
</rss>"""
    return feed_xml

if __name__ == "__main__":
    content = build_feed_xml()
    out_file = os.path.join(BASE_DIR, "public", "feed.xml")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {out_file} successfully.")
