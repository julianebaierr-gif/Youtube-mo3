import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app.i18n import SUPPORTED_LANGUAGES

base = "https://www.yt4mp3.com"
slug = "youtube-to-mp4-converter-free-guide"
article_urls = []

# Build the 16 reciprocal hreflangs
links = [
    f'    <xhtml:link rel="alternate" hreflang="x-default" href="{base}/blog/{slug}"/>',
    f'    <xhtml:link rel="alternate" hreflang="en" href="{base}/blog/{slug}"/>'
]
for code in SUPPORTED_LANGUAGES:
    if code == "en":
        continue
    links.append(f'    <xhtml:link rel="alternate" hreflang="{code}" href="{base}/{code}/blog/{slug}"/>')
links_str = "\n".join(links)

# 1. English article
en_entry = f'''  <url>
    <loc>{base}/blog/{slug}</loc>
    <lastmod>2026-11-12</lastmod>
{links_str}
  </url>'''
article_urls.append(en_entry)

# 2. Localized articles
for code in SUPPORTED_LANGUAGES:
    if code == "en":
        continue
    loc_entry = f'''  <url>
    <loc>{base}/{code}/blog/{slug}</loc>
    <lastmod>2026-11-12</lastmod>
{links_str}
  </url>'''
    article_urls.append(loc_entry)

all_article_xml = "\n".join(article_urls)

sitemap_path = os.path.join(BASE_DIR, "public", "sitemap.xml")
with open(sitemap_path, "r", encoding="utf-8") as f:
    content = f.read()

if f"{base}/blog/{slug}" not in content:
    assert "</urlset>" in content
    new_content = content.replace("</urlset>", all_article_xml + "\n</urlset>")
    with open(sitemap_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_content)
    print(f"Successfully added {len(article_urls)} Article 2 entries to sitemap.xml")
else:
    print("Article 2 entries already present in sitemap.xml")
