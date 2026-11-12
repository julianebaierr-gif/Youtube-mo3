# -*- coding: utf-8 -*-
"""
Article 2 Translation & Master Deployment Engine.
Builds full native translations for Article 2 across all 15 languages,
localizes internal links, updates app/articles_data.py, updates sitemap and feed.
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

from scripts.generate_blog_article_2 import EN_CONTENT_SECTIONS, TITLE, SLUG, MAIN_KEYWORD
from scripts.translate_all_sections import auto_localize_links

CACHE_FILE = os.path.join(BASE_DIR, "scratch", "translations_cache_art2.json")

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
    
    h2_match = re.match(r'<h2\s+id="([^"]+)">([^<]+)</h2>', block.strip())
    if h2_match:
        h2_id = h2_match.group(1)
        h2_text = h2_match.group(2)
        translated_text = translate_query(h2_text, lang)
        return f'<h2 id="{h2_id}">{translated_text}</h2>'
    
    translated_block = translate_query(block, lang)
    translated_block = re.sub(r'href\s*=\s*["\']\s*(/[^"\'\s]+)\s*["\']', r'href="\1"', translated_block)
    translated_block = translated_block.replace('<hr>', '').replace('<hr/>', '').replace('<hr />', '')
    return translated_block

def translate_table(table_html: str, lang: str) -> str:
    soup = BeautifulSoup(table_html, 'html.parser')
    for th in soup.find_all('th'):
        orig = th.get_text().strip()
        th.string = translate_query(orig, lang)
    for td in soup.find_all('td'):
        if td.find('strong'):
            continue
        text = td.get_text().strip()
        if not text.startswith('~') and 'x' not in text and '16:9' not in text:
            td.string = translate_query(text, lang)
    return str(soup)

def translate_section(sec_html: str, lang: str) -> str:
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

ARTICLE_METADATA = {
    "en": {
        "slug": SLUG,
        "title": TITLE,
        "meta_desc": "Discover how to convert YouTube to MP4 in 1080p Full HD and 4K quality for free. Complete tutorial for Windows, Mac, iPhone, Android, and mobile devices.",
        "excerpt": "Learn how to convert YouTube videos to high definition 1080p and 4K MP4 files safely with synchronized audio and zero software installation.",
        "category": "Video Guide",
        "published_date": "November 12, 2026",
        "modified_date": "November 12, 2026",
        "reading_time": "12 min read",
        "thumbnail": "/static/og-image.png",
    },
    "ar": {
        "slug": SLUG,
        "title": "الدليل الشامل لتحويل مقاطع يوتيوب إلى MP4 وتنزيل فيديو عالي الدقة 1080p مجانا",
        "meta_desc": "اكتشف كيفية تحويل يوتيوب إلى MP4 بدقة 1080p Full HD و 4K مجاناً. دليل تعليمي شامل لأجهزة ويندوز وماك وآيفون وأندرويد.",
        "excerpt": "تعلم كيفية تحويل مقاطع فيديو يوتيوب إلى ملفات MP4 عالية الدقة 1080p و 4K بأمان وسرعة وبصوت متزامن بدون برامج.",
        "category": "دليل الفيديو",
        "published_date": "12 نوفمبر 2026",
        "modified_date": "12 نوفمبر 2026",
        "reading_time": "12 دقيقة قراءة",
        "thumbnail": "/static/og-image.png",
    },
    "es": {
        "slug": SLUG,
        "title": "Guia Completa para Convertir Videos de YouTube a MP4 y Descargas en 1080p Gratis",
        "meta_desc": "Descubre como convertir YouTube a MP4 en 1080p Full HD y calidad 4K gratis. Tutorial completo para Windows, Mac, iPhone y Android.",
        "excerpt": "Aprende a convertir videos de YouTube a archivos MP4 en alta definicion 1080p y 4K con audio sincronizado de forma segura y rapida.",
        "category": "Guia de Video",
        "published_date": "12 de noviembre de 2026",
        "modified_date": "12 de noviembre de 2026",
        "reading_time": "12 min de lectura",
        "thumbnail": "/static/og-image.png",
    },
    "de": {
        "slug": SLUG,
        "title": "Der Grosse Leitfaden zur YouTube MP4 Video Konvertierung und 1080p Downloads",
        "meta_desc": "Erfahren Sie, wie Sie YouTube kostenlos in 1080p Full HD und 4K MP4 umwandeln. Umfassende Anleitung fur Windows, Mac, iPhone und Android.",
        "excerpt": "Lernen Sie, wie Sie YouTube Videos sicher und schnell in hochauflosende 1080p und 4K MP4 Dateien mit synchronem Ton konvertieren.",
        "category": "Video Ratgeber",
        "published_date": "12. November 2026",
        "modified_date": "12. November 2026",
        "reading_time": "12 Min. Lesezeit",
        "thumbnail": "/static/og-image.png",
    },
    "fr": {
        "slug": SLUG,
        "title": "Guide Complet pour Convertir des Videos YouTube en MP4 et Telecharger en 1080p Gratuit",
        "meta_desc": "Decouvrez comment convertir YouTube en MP4 1080p Full HD et 4K gratuitement. Tutoriel complet pour Windows, Mac, iPhone et Android.",
        "excerpt": "Apprenez a convertir des videos YouTube en fichiers MP4 haute definition 1080p et 4K en toute securite avec un son parfaitement synchronise.",
        "category": "Guide Video",
        "published_date": "12 novembre 2026",
        "modified_date": "12 novembre 2026",
        "reading_time": "12 min de lecture",
        "thumbnail": "/static/og-image.png",
    },
    "pt": {
        "slug": SLUG,
        "title": "Guia Completo para Converter Videos do YouTube em MP4 e Baixar em 1080p Gratis",
        "meta_desc": "Descubra como converter YouTube para MP4 em 1080p Full HD e 4K gratis. Tutorial completo para Windows, Mac, iPhone e Android.",
        "excerpt": "Aprenda a converter videos do YouTube para arquivos MP4 em alta definicao 1080p e 4K com audio sincronizado e total seguranca.",
        "category": "Guia de Video",
        "published_date": "12 de novembro de 2026",
        "modified_date": "12 de novembro de 2026",
        "reading_time": "12 min de leitura",
        "thumbnail": "/static/og-image.png",
    },
    "it": {
        "slug": SLUG,
        "title": "Guida Completa alla Conversione Video YouTube in MP4 e Download in 1080p Gratis",
        "meta_desc": "Scopri come convertire YouTube in MP4 a 1080p Full HD e 4K gratis. Tutorial completo per Windows, Mac, iPhone e Android.",
        "excerpt": "Impara a convertire video YouTube in file MP4 in alta definizione 1080p e 4K con audio sincronizzato in modo rapido e sicuro.",
        "category": "Guida Video",
        "published_date": "12 novembre 2026",
        "modified_date": "12 novembre 2026",
        "reading_time": "12 min di lettura",
        "thumbnail": "/static/og-image.png",
    },
    "id": {
        "slug": SLUG,
        "title": "Panduan Lengkap Konversi Video YouTube ke MP4 dan Unduhan 1080p Gratis",
        "meta_desc": "Pelajari cara konversi YouTube ke MP4 kualitas 1080p Full HD dan 4K gratis. Tutorial lengkap untuk Windows, Mac, iPhone, dan Android.",
        "excerpt": "Cara mudah dan aman mengubah video YouTube menjadi file MP4 resolusi tinggi 1080p dan 4K dengan audio sinkron tanpa aplikasi.",
        "category": "Panduan Video",
        "published_date": "12 November 2026",
        "modified_date": "12 November 2026",
        "reading_time": "12 menit baca",
        "thumbnail": "/static/og-image.png",
    },
    "ru": {
        "slug": SLUG,
        "title": "Полное руководство по конвертации видео YouTube в MP4 и загрузке в 1080p бесплатно",
        "meta_desc": "Узнайте, как бесплатно конвертировать видео YouTube в MP4 1080p Full HD и 4K. Руководство для Windows, Mac, iPhone и Android.",
        "excerpt": "Инструкция по безопасному извлечению и сохранению видеороликов YouTube в формате высокой четкости 1080p и 4K со синхронным звуком.",
        "category": "Видео инструкции",
        "published_date": "12 ноября 2026",
        "modified_date": "12 ноября 2026",
        "reading_time": "12 мин чтения",
        "thumbnail": "/static/og-image.png",
    },
    "tr": {
        "slug": SLUG,
        "title": "YouTube Video MP4 Donusturme ve 1080p Ucretsiz Indirme Rehberi",
        "meta_desc": "YouTube videolarini ucretsiz olarak 1080p Full HD ve 4K kalitesinde MP4 e donusturme rehberi. Windows, Mac, iPhone ve Android destegi.",
        "excerpt": "YouTube videolarini yuksek cozunurlukte 1080p ve 4K MP4 formatina guvenli ve senkronize sesle donusturmenin en kolay yolu.",
        "category": "Video Rehberi",
        "published_date": "12 Kasim 2026",
        "modified_date": "12 Kasim 2026",
        "reading_time": "12 dk okuma",
        "thumbnail": "/static/og-image.png",
    },
    "vi": {
        "slug": SLUG,
        "title": "Huong Dan Toan Dien Chuyen Doi Video YouTube Sang MP4 Va Tai 1080p Mien Phi",
        "meta_desc": "Kham pha cach chuyen doi YouTube sang MP4 1080p Full HD va 4K mien phi. Ho tro day du Windows, Mac, iPhone va Android.",
        "excerpt": "Huong dan chuyen doi video YouTube sang tap tin MP4 do phan giai cao 1080p va 4K an toan, dong bo am thanh va cuc ky nhanh chong.",
        "category": "Huong Dan Video",
        "published_date": "12 thang 11, 2026",
        "modified_date": "12 thang 11, 2026",
        "reading_time": "12 phut doc",
        "thumbnail": "/static/og-image.png",
    },
    "ja": {
        "slug": SLUG,
        "title": "YouTube動画を最高画質1080pのMP4に無料変換するための完全ガイド",
        "meta_desc": "YouTube動画を1080p Full HDや4K画質のMP4に無料変換する方法を徹底解説。Windows、Mac、iPhone、Android対応。",
        "excerpt": "YouTube動画を高画質1080p・4KのMP4ファイルとして安全かつ音声同期を保って高速保存する手順を解説します。",
        "category": "動画変換ガイド",
        "published_date": "2026年11月12日",
        "modified_date": "2026年11月12日",
        "reading_time": "読了目安 12分",
        "thumbnail": "/static/og-image.png",
    },
    "ko": {
        "slug": SLUG,
        "title": "유튜브 동영상 무료 MP4 변환 및 1080p 초고화질 다운로드 완벽 가이드",
        "meta_desc": "YouTube 동영상을 1080p Full HD 및 4K 고화질 MP4로 무료 변환하는 방법을 확인하세요. Windows, Mac, iPhone, Android 완벽 지원.",
        "excerpt": "프로그램 설치 없이 YouTube 동영상을 1080p 및 4K 고화질 MP4 파일로 오디오 싱크 밀림 없이 안전하게 변환하는 방법을 안내합니다.",
        "category": "동영상 가이드",
        "published_date": "2026년 11월 12일",
        "modified_date": "2026년 11월 12일",
        "reading_time": "12분 분량",
        "thumbnail": "/static/og-image.png",
    },
    "hi": {
        "slug": SLUG,
        "title": "YouTube वीडियो को MP4 में बदलने और 1080p डाउनलोड करने की पूरी गाइड",
        "meta_desc": "YouTube वीडियो को 1080p Full HD और 4K MP4 में मुफ्त में बदलना सीखें। Windows, Mac, iPhone और Android के लिए पूरा ट्यूटोरियल।",
        "excerpt": "बिना किसी ऐप के YouTube वीडियो को 1080p और 4K MP4 फाइलों में सिंक ऑडियो के साथ सुरक्षित और तेज़ी से डाउनलोड करने का तरीका जानें।",
        "category": "वीडियो गाइड",
        "published_date": "12 नवंबर 2026",
        "modified_date": "12 नवंबर 2026",
        "reading_time": "12 मिनट का समय",
        "thumbnail": "/static/og-image.png",
    },
    "my": {
        "slug": SLUG,
        "title": "YouTube ဗီဒီယိုများကို MP4 အဖြစ် ပြောင်းလဲခြင်းနှင့် 1080p အခမဲ့ဒေါင်းလုဒ် လမ်းညွှန်",
        "meta_desc": "YouTube ဗီဒီယိုများကို 1080p Full HD နှင့် 4K MP4 အဖြစ် အခမဲ့ပြောင်းလဲနည်း။ Windows, Mac, iPhone နှင့် Android အတွက် ပြည့်စုံသော လမ်းညွှန်။",
        "excerpt": "YouTube ဗီဒီယိုများကို ဆော့ဖ်ဝဲမလိုဘဲ 1080p နှင့် 4K MP4 ဖိုင်များအဖြစ် အသံနှင့်ရုပ်ထွက်ကိုက်ညီစွာ လုံခြုံမြန်ဆန်စွာ ဒေါင်းလုဒ်လုပ်နည်း။",
        "category": "ဗီဒီယို လမ်းညွှန်",
        "published_date": "၁၂ နိုဝင်ဘာ ၂၀၂၆",
        "modified_date": "၁၂ နိုဝင်ဘာ ၂၀၂၆",
        "reading_time": "ဖတ်ရှုချိန် ၁၂ မိနစ်",
        "thumbnail": "/static/og-image.png",
    }
}

en_full_html = "\n".join(EN_CONTENT_SECTIONS)

ALL_ART2_DATA = {
    "en": {
        **ARTICLE_METADATA["en"],
        "content_html": en_full_html
    }
}

def main():
    print(f"Building Article 2 across all 15 languages...")
    other_codes = [c for c in ARTICLE_METADATA if c != "en"]
    
    for code in other_codes:
        meta = ARTICLE_METADATA[code]
        print(f"\nProcessing [{code}]...")
        t0 = time.time()
        
        translated_sections = []
        for sec in EN_CONTENT_SECTIONS:
            translated_sections.append(translate_section(sec, code))
            
        full_html = "\n".join(translated_sections)
        localized_html = auto_localize_links(full_html, code)
        
        # Verify internal links
        assert f'href="/{code}/youtube-to-mp4"' in localized_html, f"Missing {code} mp4 link!"
        assert f'href="/{code}/youtube-to-mp3"' in localized_html, f"Missing {code} mp3 link!"
        assert f'href="/{code}/youtube-shorts-downloader"' in localized_html, f"Missing {code} shorts link!"
        assert f'href="/{code}/"' in localized_html, f"Missing {code} home link!"
        
        ALL_ART2_DATA[code] = {
            **meta,
            "content_html": localized_html
        }
        
        save_cache(cache)
        elapsed = time.time() - t0
        print(f"[{code}] Done in {elapsed:.1f}s! Length: {len(localized_html)} chars.")

    # Master Article 2 Object
    master_art2 = ALL_ART2_DATA["en"]
    trans_map = {}
    for code in ALL_ART2_DATA:
        if code != "en":
            trans_map[code] = ALL_ART2_DATA[code]
    master_art2["translations"] = trans_map

    # Load existing articles from app/articles_data.py
    from app.articles_data import BLOG_ARTICLES
    existing_articles = [art for art in BLOG_ARTICLES if art.get("slug") != SLUG]
    existing_articles.append(master_art2)

    out_path = os.path.join(BASE_DIR, "app", "articles_data.py")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write('"""\nYT4MP3 Blog Articles Content Repository\n"""\n\n')
        f.write('from typing import List, Dict, Any\n\n')
        f.write(f'BLOG_ARTICLES: List[Dict[str, Any]] = {repr(existing_articles)}\n')

    print(f"\nSaved {len(existing_articles)} articles to {out_path}!")

if __name__ == "__main__":
    main()
