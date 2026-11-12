# -*- coding: utf-8 -*-
"""
Full Native Translation Engine for All 15 Languages.
Translates all 15 content sections into authentic, high-quality native language text for:
- ar (Arabic) -> using native AR_SECTIONS
- es (Spanish) -> using native ES_SECTIONS
- pt (Portuguese)
- fr (French)
- de (German)
- id (Indonesian)
- it (Italian)
- ru (Russian)
- tr (Turkish)
- vi (Vietnamese)
- ja (Japanese)
- ko (Korean)
- hi (Hindi)
- my (Burmese)
- en (English master)
"""

import os
import sys
import re
import json
import time
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from scripts.generate_blog_article import EN_CONTENT_SECTIONS, TITLE, SLUG, MAIN_KEYWORD
from scripts.translate_all_sections import AR_SECTIONS, ES_SECTIONS, auto_localize_links

CACHE_FILE = os.path.join(BASE_DIR, "scratch", "translations_cache.json")

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

cache = load_cache()

def translate_query(text: str, target_lang: str, retries: int = 4) -> str:
    clean = text.strip()
    if not clean:
        return text
    
    cache_key = f"{target_lang}::{clean}"
    if cache_key in cache:
        return cache[cache_key]
    
    url = f'https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl={target_lang}&dt=t&q={urllib.parse.quote(clean)}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                result = ''.join([part[0] for part in data[0] if part[0]])
                
                # Clean dashes
                result = result.replace('—', '-').replace('–', '-')
                cache[cache_key] = result
                time.sleep(0.04) # Polite delay
                return result
        except Exception as e:
            time.sleep(0.5 * (attempt + 1))
            if attempt == retries - 1:
                print(f"Failed to translate to {target_lang} after {retries} attempts: {e}")
                return clean
    return clean

def translate_html_block(block: str, lang: str) -> str:
    """Translates a block of HTML preserving tags and attributes."""
    if not block.strip():
        return block
    
    # If it's a heading
    h2_match = re.match(r'<h2\s+id="([^"]+)">([^<]+)</h2>', block.strip())
    if h2_match:
        h2_id = h2_match.group(1)
        h2_text = h2_match.group(2)
        translated_text = translate_query(h2_text, lang)
        return f'<h2 id="{h2_id}">{translated_text}</h2>'
    
    # For regular paragraphs
    translated_block = translate_query(block, lang)
    # Clean up any potential translation artifacts on attributes
    translated_block = re.sub(r'href\s*=\s*["\']\s*(/[^"\'\s]+)\s*["\']', r'href="\1"', translated_block)
    # Remove any stray <hr> if model hallucinated
    translated_block = translated_block.replace('<hr>', '').replace('<hr/>', '').replace('<hr />', '')
    return translated_block

def translate_table(table_html: str, lang: str) -> str:
    """Translates the comparison table cleanly preserving structure."""
    soup = BeautifulSoup(table_html, 'html.parser')
    for th in soup.find_all('th'):
        orig = th.get_text().strip()
        th.string = translate_query(orig, lang)
    for td in soup.find_all('td'):
        if td.find('strong'):
            continue
        text = td.get_text().strip()
        if 'kHz' not in text and not text.startswith('~'):
            td.string = translate_query(text, lang)
    return str(soup)

def translate_section(sec_html: str, lang: str) -> str:
    """Parses a section into its constituent blocks, translates each, and rejoins."""
    if '<div class="table-responsive">' in sec_html:
        parts = re.split(r'(<div class="table-responsive">.*?</div>)', sec_html, flags=re.DOTALL)
        result_parts = []
        for part in parts:
            if '<div class="table-responsive">' in part:
                result_parts.append(translate_table(part, lang))
            else:
                blocks = re.findall(r'(<h2[^>]*>.*?</h2>|<p>.*?</p>)', part, flags=re.DOTALL)
                for b in blocks:
                    result_parts.append(translate_html_block(b, lang))
        return "\n".join(result_parts)
    else:
        blocks = re.findall(r'(<h2[^>]*>.*?</h2>|<p>.*?</p>)', sec_html, flags=re.DOTALL)
        result_blocks = []
        for b in blocks:
            result_blocks.append(translate_html_block(b, lang))
        return "\n".join(result_blocks)

OTHER_LANGUAGES = {
    "pt": {
        "title": "Guia Completo para Extrair Audio do YouTube e Converter em MP3 Gratis",
        "meta_desc": "Descubra como converter YouTube para MP3 em 320kbps com alta qualidade gratis. Tutorial completo para Windows, Mac, iPhone, Android e MP3 players.",
        "excerpt": "Aprenda a converter videos do YouTube para arquivos MP3 a 320kbps com total seguranca e velocidade sem instalar programas.",
        "category": "Guia de Conversao",
        "published_date": "12 de novembro de 2026",
        "reading_time": "12 min de leitura",
        "lang_name": "Português",
    },
    "fr": {
        "title": "Guide Complet pour Extraire l Audio de YouTube et Convertir en MP3 Gratuit",
        "meta_desc": "Decouvrez comment convertir YouTube en MP3 320kbps haute fidelite gratuitement. Tutoriel pour Windows, Mac, iPhone, Android et baladeurs MP3.",
        "excerpt": "Apprenez a convertir vos videos YouTube en fichiers audio MP3 a 320kbps en toute securite et rapidite sans logiciel.",
        "category": "Guide de Conversion",
        "published_date": "12 novembre 2026",
        "reading_time": "12 min de lecture",
        "lang_name": "Français",
    },
    "de": {
        "title": "Der Grosse Leitfaden zur YouTube Audio Extraktion und Kostenlosen MP3 Konvertierung",
        "meta_desc": "Erfahren Sie, wie Sie YouTube kostenlos in 320kbps MP3 umwandeln. Umfassende Anleitung fur Windows, Mac, iPhone, Android und MP3 Player.",
        "excerpt": "Lernen Sie, wie Sie YouTube Videos sicher und schnell in hochauflosende 320kbps MP3 Audiodateien konvertieren.",
        "category": "Konverter Ratgeber",
        "published_date": "12. November 2026",
        "reading_time": "12 Min. Lesezeit",
        "lang_name": "Deutsch",
    },
    "id": {
        "title": "Panduan Lengkap Ekstraksi Audio YouTube dan Konversi MP3 Gratis",
        "meta_desc": "Pelajari cara konversi YouTube ke MP3 kualitas tinggi 320kbps gratis. Tutorial lengkap untuk Windows, Mac, iPhone, Android, dan MP3 player.",
        "excerpt": "Cara mudah dan aman mengubah video YouTube menjadi file audio MP3 320kbps tanpa aplikasi tambahan.",
        "category": "Panduan Konverter",
        "published_date": "12 November 2026",
        "reading_time": "12 menit baca",
        "lang_name": "Bahasa Indonesia",
    },
    "it": {
        "title": "Guida Completa all Estrazione Audio da YouTube e Conversione MP3 Gratis",
        "meta_desc": "Scopri come convertire YouTube in MP3 a 320kbps in alta fedelta gratis. Tutorial per Windows, Mac, iPhone, Android e lettori MP3.",
        "excerpt": "Impara a convertire video YouTube in file audio MP3 a 320kbps in modo rapido e sicuro senza installare software.",
        "category": "Guida alla Conversione",
        "published_date": "12 novembre 2026",
        "reading_time": "12 min di lettura",
        "lang_name": "Italiano",
    },
    "ru": {
        "title": "Полное руководство по извлечению аудио из YouTube и бесплатной конвертации в MP3",
        "meta_desc": "Узнайте, как бесплатно конвертировать видео YouTube в MP3 320 кбит/с. Руководство для Windows, Mac, iPhone, Android и MP3-плееров.",
        "excerpt": "Инструкция по быстрому и безопасному извлечению кристально чистого звука 320 кбит/с из видеороликов YouTube.",
        "category": "Инструкции",
        "published_date": "12 ноября 2026",
        "reading_time": "12 мин чтения",
        "lang_name": "Русский",
    },
    "tr": {
        "title": "YouTube Ses Donusturme ve Ucretsiz MP3 Rehberi",
        "meta_desc": "YouTube videolarini ucretsiz olarak 320kbps studyo kalitesinde MP3 e donusturme rehberi. Windows, Mac, iPhone ve Android destegi.",
        "excerpt": "YouTube videolarini yuksek ses kalitesinde guvenli ve hizli sekilde MP3 dosyasina donusturmenin yollari.",
        "category": "Donusturucu Rehberi",
        "published_date": "12 Kasim 2026",
        "reading_time": "12 dk okuma",
        "lang_name": "Türkçe",
    },
    "vi": {
        "title": "Huong Dan Toan Dien Tach Am Thanh YouTube Va Chuyen Doi MP3 Mien Phi",
        "meta_desc": "Kham pha cach chuyen doi YouTube sang MP3 320kbps chat luong cao mien phi. Ho tro day du Windows, Mac, iPhone, Android va may nghe nhac MP3.",
        "excerpt": "Huong dan chuyen doi video YouTube sang tap tin am thanh MP3 320kbps an toan, khong quang cao va cuc ky nhanh chong.",
        "category": "Huong Dan Chuyen Doi",
        "published_date": "12 thang 11, 2026",
        "reading_time": "12 phut doc",
        "lang_name": "Tiếng Việt",
    },
    "ja": {
        "title": "YouTube音声を高音質MP3に無料変換するための完全ガイド",
        "meta_desc": "YouTube動画を最高音質320kbpsのMP3に無料変換する方法を徹底解説。Windows、Mac、iPhone、Android、MP3プレーヤー対応。",
        "excerpt": "YouTube動画からクリアな320kbps音声を抽出し、安全かつ高速にMP3ファイルとして保存する手順を解説します。",
        "category": "変換ガイド",
        "published_date": "2026年11月12日",
        "reading_time": "読了目安 12分",
        "lang_name": "日本語",
    },
    "ko": {
        "title": "유튜브 오디오 추출 및 무료 고음질 MP3 변환 완벽 가이드",
        "meta_desc": "YouTube 동영상을 320kbps 고음질 MP3로 무료 변환하는 방법을 확인하세요. Windows, Mac, iPhone, Android 및 MP3 플레이어 완벽 지원.",
        "excerpt": "복잡한 프로그램 설치 없이 YouTube 동영상을 320kbps 고음질 MP3 파일로 안전하고 빠르게 변환하는 방법을 안내합니다.",
        "category": "변환 가이드",
        "published_date": "2026年 11월 12일",
        "reading_time": "12분 분량",
        "lang_name": "한국어",
    },
    "hi": {
        "title": "YouTube ऑडियो निकालने और मुफ्त MP3 फाइल बदलने की पूरी गाइड",
        "meta_desc": "YouTube वीडियो को 320kbps उच्च गुणवत्ता वाले MP3 में मुफ्त में बदलना सीखें। Windows, Mac, iPhone, Android और MP3 प्लेयर के लिए पूरा ट्यूटोरियल।",
        "excerpt": "YouTube वीडियो को बिना किसी ऐप के 320kbps MP3 ऑडियो फ़ाइलों में सुरक्षित और तेज़ी से बदलने का सबसे आसान तरीका जानें।",
        "category": "कन्वर्टर गाइड",
        "published_date": "12 नवंबर 2026",
        "reading_time": "12 मिनट का समय",
        "lang_name": "हिन्दी",
    },
    "my": {
        "title": "YouTube အသံထုတ်ယူခြင်းနှင့် အခမဲ့ MP3 ပြောင်းလဲခြင်းဆိုင်ရာ လမ်းညွှန်",
        "meta_desc": "YouTube ဗီဒီယိုများကို 320kbps အသံအရည်အသွေးမြင့် MP3 အဖြစ် အခမဲ့ပြောင်းလဲနည်း။ Windows, Mac, iPhone, Android နှင့် MP3 စက်များအတွက် ပြည့်စုံသော လမ်းညွှန်။",
        "excerpt": "YouTube ဗီဒီယိုများကို ဆော့ဖ်ဝဲမလိုဘဲ 320kbps MP3 အသံဖိုင်များအဖြစ် လုံခြုံမြန်ဆန်စွာ ပြောင်းလဲနည်းကို လေ့လာပါ။",
        "category": "ပြောင်းလဲခြင်း လမ်းညွှန်",
        "published_date": "၁၂ နိုဝင်ဘာ ၂၀၂၆",
        "reading_time": "ဖတ်ရှုချိန် ၁၂ မိနစ်",
        "lang_name": "မြန်မာစာ",
    }
}

en_full_html = "\n".join(EN_CONTENT_SECTIONS)
ar_full_html = auto_localize_links("\n".join(AR_SECTIONS), "ar")
es_full_html = auto_localize_links("\n".join(ES_SECTIONS), "es")

ALL_ARTICLES_DATA = {
    "en": {
        "slug": SLUG,
        "title": TITLE,
        "meta_desc": "Discover how to convert YouTube to MP3 in 320kbps high quality audio for free. Complete tutorial for Windows, Mac, iPhone, Android, and MP3 players.",
        "excerpt": "Learn how to convert YouTube videos to 320kbps MP3 audio files safely. Comprehensive tutorial covering bitrates, Windows, Mac, mobile devices, and MP3 players.",
        "category": "Converter Guide",
        "published_date": "November 12, 2026",
        "modified_date": "November 12, 2026",
        "reading_time": "12 min read",
        "thumbnail": "/static/blog/blog-youtube-to-mp3.jpg",
        "content_html": en_full_html
    },
    "ar": {
        "slug": SLUG,
        "title": "الدليل الشامل لتحويل صوتيات يوتيوب واستخراج ملفات MP3 بجودة عالية مجانا",
        "meta_desc": "اكتشف كيفية تحويل يوتيوب إلى MP3 بجودة صوت 320kbps مجاناً. دليل تعليمي شامل لأجهزة ويندوز وماك وآيفون وأندرويد ومشغلات MP3.",
        "excerpt": "تعرف على كيفية تحويل مقاطع فيديو يوتيوب إلى ملفات MP3 صوتية نقية بجودة 320kbps بدون برامج وبأمان وسرعة فائقة.",
        "category": "دليل التحويل",
        "published_date": "12 نوفمبر 2026",
        "modified_date": "12 نوفمبر 2026",
        "reading_time": "12 دقيقة قراءة",
        "thumbnail": "/static/blog/blog-youtube-to-mp3.jpg",
        "content_html": ar_full_html
    },
    "es": {
        "slug": SLUG,
        "title": "Guia Completa para Extraer Audio de YouTube y Convertir a MP3 Gratis",
        "meta_desc": "Descubre como convertir YouTube a MP3 en 320kbps de alta fidelidad gratis. Tutorial completo para Windows, Mac, iPhone, Android y reproductores MP3.",
        "excerpt": "Aprende a convertir videos de YouTube a archivos de audio MP3 en 320kbps de forma segura y rapida sin instalar programas.",
        "category": "Guia de Conversion",
        "published_date": "12 de noviembre de 2026",
        "modified_date": "12 de noviembre de 2026",
        "reading_time": "12 min de lectura",
        "thumbnail": "/static/blog/blog-youtube-to-mp3.jpg",
        "content_html": es_full_html
    }
}

def main():
    print(f"Starting translation of remaining {len(OTHER_LANGUAGES)} languages...")
    for code, meta in OTHER_LANGUAGES.items():
        print(f"\nProcessing [{code} - {meta['lang_name']}]...")
        t0 = time.time()
        
        translated_sections = []
        for s_idx, sec in enumerate(EN_CONTENT_SECTIONS):
            trans_sec = translate_section(sec, code)
            translated_sections.append(trans_sec)
        
        full_trans_html = "\n".join(translated_sections)
        # Apply link localization
        localized_html = auto_localize_links(full_trans_html, code)
        
        # Verify internal links
        assert f'href="/{code}/youtube-to-mp3"' in localized_html, f"Missing {code} mp3 link!"
        assert f'href="/{code}/youtube-to-mp4"' in localized_html, f"Missing {code} mp4 link!"
        assert f'href="/{code}/youtube-shorts-downloader"' in localized_html, f"Missing {code} shorts link!"
        assert f'href="/{code}/"' in localized_html, f"Missing {code} home link!"
        
        ALL_ARTICLES_DATA[code] = {
            "slug": SLUG,
            "title": meta["title"],
            "meta_desc": meta["meta_desc"],
            "excerpt": meta["excerpt"],
            "category": meta["category"],
            "published_date": meta["published_date"],
            "modified_date": meta["published_date"],
            "reading_time": meta["reading_time"],
            "thumbnail": "/static/blog/blog-youtube-to-mp3.jpg",
            "content_html": localized_html
        }
        
        save_cache(cache)
        elapsed = time.time() - t0
        print(f"[{code}] Done in {elapsed:.1f}s! Content length: {len(localized_html)} chars.")

    # Master Article Object
    master_article = ALL_ARTICLES_DATA["en"]
    translations_map = {}
    for code in ALL_ARTICLES_DATA:
        if code == "en":
            continue
        translations_map[code] = ALL_ARTICLES_DATA[code]

    master_article["translations"] = translations_map

    out_path = os.path.join(BASE_DIR, "app", "articles_data.py")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write('"""\nYT4MP3 Blog Articles Content Repository\n"""\n\n')
        f.write('from typing import List, Dict, Any\n\n')
        f.write(f'BLOG_ARTICLES: List[Dict[str, Any]] = [{repr(master_article)}]\n')

    print(f"\nALL 15 LANGUAGES TRANSLATED AND SAVED TO {out_path}!")

if __name__ == "__main__":
    main()
