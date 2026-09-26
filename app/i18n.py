# -*- coding: utf-8 -*-
"""
YT4MP3 Multilingual (i18n) Engine.
Google International SEO Compliant:
- 14 Global Languages (en, es, id, pt, fr, de, tr, it, ru, vi, ja, ko, ar, hi)
- Reciprocal hreflang tags with x-default
- Self-referencing canonical URLs
- Deep native keyword research (Primary + LSI/Semantics + Competitor Gaps)
- Localized UI & structured schema data
"""

from typing import Dict, List, Any
from app.seo_content import SEO_PAGES
from app.locales import (
    es, id, pt, fr, de, tr, it, ru, vi, ja, ko, ar, hi
)

SUPPORTED_LANGUAGES: Dict[str, Dict[str, str]] = {
    'en': {'code': 'en', 'dir': 'ltr', 'flag': '🇺🇸', 'name': 'English', 'native': 'English'},
    'es': {'code': 'es', 'dir': 'ltr', 'flag': '🇪🇸', 'name': 'Spanish', 'native': 'Español'},
    'id': {'code': 'id', 'dir': 'ltr', 'flag': '🇮🇩', 'name': 'Indonesian', 'native': 'Bahasa Indonesia'},
    'pt': {'code': 'pt', 'dir': 'ltr', 'flag': '🇧🇷', 'name': 'Portuguese', 'native': 'Português'},
    'fr': {'code': 'fr', 'dir': 'ltr', 'flag': '🇫🇷', 'name': 'French', 'native': 'Français'},
    'de': {'code': 'de', 'dir': 'ltr', 'flag': '🇩🇪', 'name': 'German', 'native': 'Deutsch'},
    'tr': {'code': 'tr', 'dir': 'ltr', 'flag': '🇹🇷', 'name': 'Turkish', 'native': 'Türkçe'},
    'it': {'code': 'it', 'dir': 'ltr', 'flag': '🇮🇹', 'name': 'Italian', 'native': 'Italiano'},
    'ru': {'code': 'ru', 'dir': 'ltr', 'flag': '🇷🇺', 'name': 'Russian', 'native': 'Русский'},
    'vi': {'code': 'vi', 'dir': 'ltr', 'flag': '🇻🇳', 'name': 'Vietnamese', 'native': 'Tiếng Việt'},
    'ja': {'code': 'ja', 'dir': 'ltr', 'flag': '🇯🇵', 'name': 'Japanese', 'native': '日本語'},
    'ko': {'code': 'ko', 'dir': 'ltr', 'flag': '🇰🇷', 'name': 'Korean', 'native': '한국어'},
    'ar': {'code': 'ar', 'dir': 'rtl', 'flag': '🇸🇦', 'name': 'Arabic', 'native': 'العربية'},
    'hi': {'code': 'hi', 'dir': 'ltr', 'flag': '🇮🇳', 'name': 'Hindi', 'native': 'हिन्दी'},
}

ENGLISH_UI: Dict[str, str] = {
    'all_formats_tab': 'All Formats',
    'all_rights_reserved': 'All rights reserved.',
    'back_to_converter': 'Back to Converter',
    'convert_btn': 'Convert',
    'download_now': 'Download Now',
    'download_ready': 'Your File is Ready',
    'faq_title': 'Frequently Asked Questions',
    'features_title': 'Why Choose YT4MP3',
    'free_badge': '100% Free',
    'how_it_works_title': 'How to Convert YouTube Videos',
    'languages_label': 'Languages',
    'legal_disclaimer': 'YT4MP3 is an independent educational media format converter tool designed for personal backup, offline research, and fair-use archiving. Users are responsible for complying with YouTube\'s Terms of Service and applicable local copyright laws.',
    'mp3_music_tab': 'MP3 Music',
    'mp4_video_tab': 'MP4 Video',
    'nav_home': 'Home',
    'nav_mp3': 'YouTube to MP3',
    'nav_mp4': 'YouTube to MP4',
    'paste_placeholder': 'Paste YouTube video, Shorts, or Music URL here...',
    'quick_convert': 'Quick Convert',
    'select_format': 'Select Format & Quality',
    'step1_desc': 'Find your favorite video on YouTube, click Share, and copy the video URL.',
    'step1_title': 'Copy Video Link',
    'step2_desc': 'Paste the link into the converter box above and choose MP3 audio (up to 320kbps) or MP4 video (up to 4K).',
    'step2_title': 'Paste & Select Format',
    'step3_desc': 'Click Convert, wait a few seconds for the cloud server to prepare the file, and download directly to your device.',
    'step3_title': 'Download File'
}

I18N_UI: Dict[str, Dict[str, str]] = {
    'en': ENGLISH_UI,
    'es': es.UI,
    'id': id.UI,
    'pt': pt.UI,
    'fr': fr.UI,
    'de': de.UI,
    'tr': tr.UI,
    'it': it.UI,
    'ru': ru.UI,
    'vi': vi.UI,
    'ja': ja.UI,
    'ko': ko.UI,
    'ar': ar.UI,
    'hi': hi.UI,
}

I18N_PAGES: Dict[str, Dict[str, Any]] = {
    'es': es.PAGES,
    'id': id.PAGES,
    'pt': pt.PAGES,
    'fr': fr.PAGES,
    'de': de.PAGES,
    'tr': tr.PAGES,
    'it': it.PAGES,
    'ru': ru.PAGES,
    'vi': vi.PAGES,
    'ja': ja.PAGES,
    'ko': ko.PAGES,
    'ar': ar.PAGES,
    'hi': hi.PAGES,
}

I18N_KEYWORDS: Dict[str, Dict[str, Any]] = {
    'es': es.KEYWORDS_RESEARCH,
    'id': id.KEYWORDS_RESEARCH,
    'pt': pt.KEYWORDS_RESEARCH,
    'fr': fr.KEYWORDS_RESEARCH,
    'de': de.KEYWORDS_RESEARCH,
    'tr': tr.KEYWORDS_RESEARCH,
    'it': it.KEYWORDS_RESEARCH,
    'ru': ru.KEYWORDS_RESEARCH,
    'vi': vi.KEYWORDS_RESEARCH,
    'ja': ja.KEYWORDS_RESEARCH,
    'ko': ko.KEYWORDS_RESEARCH,
    'ar': ar.KEYWORDS_RESEARCH,
    'hi': hi.KEYWORDS_RESEARCH,
}

def get_supported_languages() -> Dict[str, Dict[str, str]]:
    return SUPPORTED_LANGUAGES

def get_ui_strings(lang: str = "en") -> Dict[str, str]:
    return I18N_UI.get(lang, I18N_UI.get("en", ENGLISH_UI))

def get_page_content(lang: str, page_key: str) -> Dict[str, Any]:
    """
    Returns localized page dictionary.
    Falls back to authoritative English content in app.seo_content.SEO_PAGES.
    """
    if lang == "en":
        return SEO_PAGES.get(page_key, SEO_PAGES.get("home", {}))
    
    lang_pages = I18N_PAGES.get(lang)
    if lang_pages and page_key in lang_pages:
        return lang_pages[page_key]
    
    return SEO_PAGES.get(page_key, SEO_PAGES.get("home", {}))

def get_hreflang_links(page_key: str, base_url: str = "https://www.yt4mp3.com") -> List[Dict[str, str]]:
    """
    Generates reciprocal hreflang links for Google International SEO:
    - x-default pointing to English root/subpage
    - en pointing to English root/subpage
    - each localized version pointing to /{lang}/ or /{lang}/{page_key}
    """
    links = []
    
    # x-default & en URLs
    if page_key == "home":
        en_url = f"{base_url}/"
    else:
        en_url = f"{base_url}/{page_key}"
    
    links.append({"lang": "x-default", "url": en_url})
    links.append({"lang": "en", "url": en_url})
    
    for code in SUPPORTED_LANGUAGES:
        if code == "en":
            continue
        if page_key == "home":
            loc_url = f"{base_url}/{code}/"
        else:
            loc_url = f"{base_url}/{code}/{page_key}"
        links.append({"lang": code, "url": loc_url})
        
    return links

def get_language_switcher_links(page_key: str, current_lang: str = "en") -> List[Dict[str, Any]]:
    """
    Generates list of languages for the header/footer dropdown switcher,
    preserving the current page context.
    """
    switcher = []
    for code, meta in SUPPORTED_LANGUAGES.items():
        if code == "en":
            url = "/" if page_key == "home" else f"/{page_key}"
        else:
            url = f"/{code}/" if page_key == "home" else f"/{code}/{page_key}"
            
        switcher.append({
            "code": code,
            "name": meta["name"],
            "native": meta["native"],
            "dir": meta["dir"],
            "flag": meta["flag"],
            "url": url,
            "is_current": (code == current_lang)
        })
    return switcher
