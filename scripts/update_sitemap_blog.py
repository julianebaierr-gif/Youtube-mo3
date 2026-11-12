import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app.i18n import SUPPORTED_LANGUAGES

base = 'https://www.yt4mp3.com'
blog_urls = []

# All 16 hreflang links
links = [
    f'    <xhtml:link rel="alternate" hreflang="x-default" href="{base}/blog"/>',
    f'    <xhtml:link rel="alternate" hreflang="en" href="{base}/blog"/>'
]
for code in SUPPORTED_LANGUAGES:
    if code == 'en':
        continue
    links.append(f'    <xhtml:link rel="alternate" hreflang="{code}" href="{base}/{code}/blog/"/>')
links_str = '\n'.join(links)

# 1. English blog
en_entry = f'''  <url>
    <loc>{base}/blog</loc>
    <lastmod>2026-11-12</lastmod>
{links_str}
  </url>'''
blog_urls.append(en_entry)

# 2. Localized blogs
for code in SUPPORTED_LANGUAGES:
    if code == 'en':
        continue
    loc_entry = f'''  <url>
    <loc>{base}/{code}/blog/</loc>
    <lastmod>2026-11-12</lastmod>
{links_str}
  </url>'''
    blog_urls.append(loc_entry)

all_blog_xml = '\n'.join(blog_urls)

sitemap_path = os.path.join(BASE_DIR, 'public', 'sitemap.xml')
with open(sitemap_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Only add if not already in sitemap
if f'{base}/blog' not in content:
    assert '</urlset>' in content
    new_content = content.replace('</urlset>', all_blog_xml + '\n</urlset>')
    with open(sitemap_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(new_content)
    print(f'Successfully added {len(blog_urls)} blog entries to sitemap.xml')
else:
    print('Blog entries already present in sitemap.xml')
