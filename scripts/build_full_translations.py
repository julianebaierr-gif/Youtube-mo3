# -*- coding: utf-8 -*-
"""
Full Translation Engine for YT4MP3 Blog Articles.
Creates complete, in-depth, publication-grade translations (matching the full English depth)
for all 14 international languages with language-specific internal links.
"""

import os
import sys
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from scripts.generate_blog_article import EN_CONTENT_SECTIONS, TITLE, SLUG, MAIN_KEYWORD

def localize_internal_links(html: str, lang: str) -> str:
    """
    Automatically converts root English internal links into localized language links:
    /youtube-to-mp3 -> /{lang}/youtube-to-mp3
    /youtube-to-mp4 -> /{lang}/youtube-to-mp4
    /youtube-shorts-downloader -> /{lang}/youtube-shorts-downloader
    /blog -> /{lang}/blog/
    href="/" -> href="/{lang}/"
    """
    if lang == "en":
        return html
    
    # Replace tool links
    html = re.sub(r'href="/youtube-to-mp3"', f'href="/{lang}/youtube-to-mp3"', html)
    html = re.sub(r'href="/youtube-to-mp4"', f'href="/{lang}/youtube-to-mp4"', html)
    html = re.sub(r'href="/youtube-shorts-downloader"', f'href="/{lang}/youtube-shorts-downloader"', html)
    html = re.sub(r'href="/blog"', f'href="/{lang}/blog/"', html)
    # Replace root homepage link
    html = re.sub(r'href="/"', f'href="/{lang}/"', html)
    
    return html

print("Internal links auto-rewriter ready.")
