import os
import urllib.request
import urllib.parse
import json
import re
import uuid
import base64
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app = FastAPI(
    title="YouTube to MP3 & MP4 Converter Pro - Studio Audio & 4K Video",
    description="Fast, free, and secure online YouTube to MP3 320kbps and YouTube to MP4 1080p/4K downloader.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def domain_redirect_middleware(request: Request, call_next):
    raw_host = request.headers.get("host", "").lower()
    host = raw_host.split(":")[0]
    if host in ["yt4mp3.com", "yt4mp3.cc", "www.yt4mp3.cc"]:
        new_url = f"https://www.yt4mp3.com{request.url.path}"
        if request.url.query:
            new_url += f"?{request.url.query}"
        return RedirectResponse(url=new_url, status_code=301)
    return await call_next(request)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    is_head = request.method == "HEAD"
    if is_head and not request.url.path.startswith("/api/"):
        request.scope["method"] = "GET"
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self' 'unsafe-inline' 'unsafe-eval' https: data: blob:; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https: data: blob:; "
        "img-src 'self' data: blob: https: http:; "
        "media-src 'self' blob: https: http:; "
        "connect-src 'self' https: wss:; "
        "frame-src 'self' https: data: blob:; "
        "worker-src 'self' blob: https:;"
    )
    if not request.url.path.startswith("/api/"):
        if "vary" in response.headers:
            del response.headers["vary"]
    if is_head:
        return Response(status_code=response.status_code, headers=dict(response.headers), media_type=response.media_type)
    return response

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)



from app.seo_content import SEO_PAGES
from app.legal_content import LEGAL_PAGES
from app.i18n import (
    SUPPORTED_LANGUAGES,
    get_ui_strings,
    get_page_content,
    get_hreflang_links,
    get_language_switcher_links
)
from app.blog_data import (
    BLOG_I18N_PAGES,
    get_blog_content,
    get_blog_articles,
    get_article_by_slug,
    get_blog_hreflang_links,
    get_blog_switcher_links
)

_CONVERTER_HTML_CACHE: dict[tuple[str, str], str] = {}
_LEGAL_HTML_CACHE: dict[str, str] = {}
_BLOG_HTML_CACHE: dict[str, str] = {}

EDGE_HTML_HEADERS = {
    "Cache-Control": "public, max-age=0, s-maxage=86400, stale-while-revalidate=604800",
    "CDN-Cache-Control": "public, s-maxage=86400, stale-while-revalidate=604800",
    "Vercel-CDN-Cache-Control": "public, s-maxage=86400, stale-while-revalidate=604800",
}

def render_converter_page(request: Request, page_key: str, lang: str = "en"):
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Language not found")
    
    cache_key = (lang, page_key)
    html_str = _CONVERTER_HTML_CACHE.get(cache_key)
    if html_str is None:
        seo_data = get_page_content(lang, page_key)
        ui_strings = get_ui_strings(lang)
        hreflangs = get_hreflang_links(page_key)
        switcher = get_language_switcher_links(page_key, lang)
        current_meta = SUPPORTED_LANGUAGES[lang]
        tmpl = templates.env.get_template("index.html")
        html_str = tmpl.render(
            request=request,
            seo=seo_data,
            t=ui_strings,
            lang=lang,
            lang_dir=current_meta.get("dir", "ltr"),
            hreflangs=hreflangs,
            switcher=switcher,
            current_lang=current_meta,
            supported_languages=SUPPORTED_LANGUAGES
        )
        _CONVERTER_HTML_CACHE[cache_key] = html_str
    
    return HTMLResponse(content=html_str, headers=EDGE_HTML_HEADERS)

def render_legal_page(request: Request, page_key: str):
    html_str = _LEGAL_HTML_CACHE.get(page_key)
    if html_str is None:
        ui_strings = get_ui_strings("en")
        switcher = get_language_switcher_links("home", "en")
        current_meta = SUPPORTED_LANGUAGES["en"]
        tmpl = templates.env.get_template("page.html")
        html_str = tmpl.render(
            request=request,
            seo=LEGAL_PAGES[page_key],
            t=ui_strings,
            lang="en",
            lang_dir="ltr",
            switcher=switcher,
            current_lang=current_meta,
            supported_languages=SUPPORTED_LANGUAGES
        )
        _LEGAL_HTML_CACHE[page_key] = html_str
    return HTMLResponse(content=html_str, headers=EDGE_HTML_HEADERS)

def render_blog_hub(request: Request, lang: str = "en"):
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Language not found")
    
    html_str = _BLOG_HTML_CACHE.get(lang)
    if html_str is None:
        blog_data = get_blog_content(lang)
        ui_strings = get_ui_strings(lang)
        articles = get_blog_articles(lang)
        hreflangs = get_blog_hreflang_links(slug=None)
        switcher = get_blog_switcher_links(slug=None, current_lang=lang)
        current_meta = SUPPORTED_LANGUAGES[lang]
        
        canonical_url = "https://www.yt4mp3.com/blog" if lang == "en" else f"https://www.yt4mp3.com/{lang}/blog/"
        seo = {
            "title": blog_data["title"],
            "meta_desc": blog_data["meta_desc"],
            "canonical_url": canonical_url,
        }
        
        tmpl = templates.env.get_template("blog.html")
        html_str = tmpl.render(
            request=request,
            seo=seo,
            blog=blog_data,
            articles=articles,
            t=ui_strings,
            lang=lang,
            lang_dir=current_meta.get("dir", "ltr"),
            hreflangs=hreflangs,
            switcher=switcher,
            current_lang=current_meta,
            supported_languages=SUPPORTED_LANGUAGES,
            og_locale="en_US" if lang == "en" else f"{lang}_{lang.upper()}"
        )
        _BLOG_HTML_CACHE[lang] = html_str
    
    return HTMLResponse(content=html_str, headers=EDGE_HTML_HEADERS)

_ARTICLE_HTML_CACHE: dict[tuple[str, str], str] = {}

def render_blog_article(request: Request, slug: str, lang: str = "en"):
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Language not found")
    
    article = get_article_by_slug(slug, lang)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
        
    cache_key = (lang, slug)
    html_str = _ARTICLE_HTML_CACHE.get(cache_key)
    if html_str is None:
        blog_ui = get_blog_content(lang)
        ui_strings = get_ui_strings(lang)
        hreflangs = get_blog_hreflang_links(slug=slug)
        switcher = get_blog_switcher_links(slug=slug, current_lang=lang)
        current_meta = SUPPORTED_LANGUAGES[lang]
        
        canonical_url = f"https://www.yt4mp3.com/blog/{slug}" if lang == "en" else f"https://www.yt4mp3.com/{lang}/blog/{slug}"
        
        tmpl = templates.env.get_template("article.html")
        html_str = tmpl.render(
            request=request,
            article=article,
            blog_ui=blog_ui,
            t=ui_strings,
            lang=lang,
            lang_dir=current_meta.get("dir", "ltr"),
            hreflangs=hreflangs,
            switcher=switcher,
            current_lang=current_meta,
            supported_languages=SUPPORTED_LANGUAGES,
            canonical_url=canonical_url,
            og_locale="en_US" if lang == "en" else f"{lang}_{lang.upper()}"
        )
        _ARTICLE_HTML_CACHE[cache_key] = html_str
        
    return HTMLResponse(content=html_str, headers=EDGE_HTML_HEADERS)

# Root English Routes
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return render_converter_page(request, "home", "en")

@app.get("/index.html", response_class=HTMLResponse)
@app.get("/index.php", response_class=HTMLResponse)
@app.get("/home", response_class=HTMLResponse)
@app.get("/home/", response_class=HTMLResponse)
async def home_alias_redirect():
    return RedirectResponse(url="/", status_code=301)

@app.get("/youtube-to-mp3", response_class=HTMLResponse)
@app.get("/youtube-to-mp3/", response_class=HTMLResponse)
async def youtube_mp3_page(request: Request):
    if request.url.path.endswith("/"):
        return RedirectResponse(url="/youtube-to-mp3", status_code=301)
    return render_converter_page(request, "youtube-to-mp3", "en")

@app.get("/youtube-to-mp4", response_class=HTMLResponse)
@app.get("/youtube-to-mp4/", response_class=HTMLResponse)
async def youtube_mp4_page(request: Request):
    if request.url.path.endswith("/"):
        return RedirectResponse(url="/youtube-to-mp4", status_code=301)
    return render_converter_page(request, "youtube-to-mp4", "en")

@app.get("/youtube-shorts-downloader", response_class=HTMLResponse)
@app.get("/youtube-shorts-downloader/", response_class=HTMLResponse)
async def youtube_shorts_page(request: Request):
    if request.url.path.endswith("/"):
        return RedirectResponse(url="/youtube-shorts-downloader", status_code=301)
    return render_converter_page(request, "youtube-shorts-downloader", "en")

# Static Legal Pages (Universal English)
@app.get("/contact-us", response_class=HTMLResponse)
@app.get("/contact-us/", response_class=HTMLResponse)
async def contact_us_page(request: Request):
    if request.url.path.endswith("/"):
        return RedirectResponse(url="/contact-us", status_code=301)
    return render_legal_page(request, "contact-us")

@app.get("/terms-of-service", response_class=HTMLResponse)
@app.get("/terms-of-service/", response_class=HTMLResponse)
async def terms_page(request: Request):
    if request.url.path.endswith("/"):
        return RedirectResponse(url="/terms-of-service", status_code=301)
    return render_legal_page(request, "terms-of-service")

@app.get("/privacy-policy", response_class=HTMLResponse)
@app.get("/privacy-policy/", response_class=HTMLResponse)
async def privacy_page(request: Request):
    if request.url.path.endswith("/"):
        return RedirectResponse(url="/privacy-policy", status_code=301)
    return render_legal_page(request, "privacy-policy")

# Blog Routes (English)
@app.get("/blog", response_class=HTMLResponse)
@app.get("/blog/", response_class=HTMLResponse)
async def blog_hub_page(request: Request):
    if request.url.path.endswith("/"):
        return RedirectResponse(url="/blog", status_code=301)
    return render_blog_hub(request, "en")

@app.get("/blog/{slug}", response_class=HTMLResponse)
@app.get("/blog/{slug}/", response_class=HTMLResponse)
async def blog_article_page(request: Request, slug: str):
    if request.url.path.endswith("/"):
        return RedirectResponse(url=f"/blog/{slug}", status_code=301)
    article = get_article_by_slug(slug, "en")
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return render_blog_article(request, slug, "en")

# /dmca redirects to contact-us which contains the full DMCA section
@app.get("/dmca", response_class=HTMLResponse)
@app.get("/dmca/", response_class=HTMLResponse)
async def dmca_page(request: Request):
    return RedirectResponse(url="/contact-us#dmca", status_code=301)

@app.get("/about", response_class=HTMLResponse)
@app.get("/about/", response_class=HTMLResponse)
async def about_page_redirect(request: Request):
    return RedirectResponse(url="/contact-us#about", status_code=301)

@app.api_route("/robots.text", methods=["GET", "HEAD"])
async def robots_text_redirect():
    return RedirectResponse(url="https://www.yt4mp3.com/robots.txt", status_code=301)

def render_shortcut_page(request: Request):
    seo_data = get_page_content("en", "home")
    ui_strings = get_ui_strings("en")
    hreflangs = get_hreflang_links("home")
    switcher = get_language_switcher_links("home", "en")
    current_meta = SUPPORTED_LANGUAGES["en"]
    tmpl = templates.env.get_template("index.html")
    html_str = tmpl.render(
        request=request,
        seo=seo_data,
        t=ui_strings,
        lang="en",
        lang_dir="ltr",
        hreflangs=hreflangs,
        switcher=switcher,
        current_lang=current_meta,
        supported_languages=SUPPORTED_LANGUAGES,
        robots_meta="noindex, nofollow"
    )
    resp = HTMLResponse(content=html_str)
    resp.headers["X-Robots-Tag"] = "noindex, nofollow"
    resp.headers["Cache-Control"] = "private, no-store"
    return resp

# Direct URL Shortcut Routes (e.g. yt4mp3.com/watch?v=..., yt4mp3.com/shorts/..., yt4mp3.com/4youtube/...)
@app.get("/watch", response_class=HTMLResponse)
async def watch_shortcut_page(request: Request):
    return render_shortcut_page(request)

@app.get("/shorts/{short_id:path}", response_class=HTMLResponse)
async def shorts_shortcut_page(request: Request, short_id: str):
    return render_shortcut_page(request)

@app.get("/4youtube", response_class=HTMLResponse)
@app.get("/4youtube/{path:path}", response_class=HTMLResponse)
async def four_youtube_shortcut_page(request: Request, path: str = ""):
    return render_shortcut_page(request)

@app.get("/4/{path:path}", response_class=HTMLResponse)
async def four_shortcut_page(request: Request, path: str = ""):
    return render_shortcut_page(request)

# PWA Endpoints
@app.get("/manifest.json")
async def manifest_endpoint():
    manifest_file = os.path.join(BASE_DIR, "public", "manifest.json")
    if os.path.exists(manifest_file):
        with open(manifest_file, "r", encoding="utf-8") as f:
            return Response(content=f.read(), media_type="application/manifest+json; charset=utf-8", headers=EDGE_HTML_HEADERS)
    raise HTTPException(status_code=404, detail="Manifest not found")

@app.get("/sw.js")
async def service_worker_endpoint():
    sw_file = os.path.join(BASE_DIR, "public", "sw.js")
    if os.path.exists(sw_file):
        with open(sw_file, "r", encoding="utf-8") as f:
            return Response(content=f.read(), media_type="application/javascript; charset=utf-8")
    raise HTTPException(status_code=404, detail="Service worker not found")


# SEO, Discovery & System Endpoints
@app.api_route("/BingSiteAuth.xml", methods=["GET", "HEAD"])
@app.api_route("/bingsiteauth.xml", methods=["GET", "HEAD"])
async def bing_site_auth():
    bing_file = os.path.join(BASE_DIR, "public", "BingSiteAuth.xml")
    if os.path.exists(bing_file):
        with open(bing_file, "r", encoding="utf-8") as f:
            content = f.read()
        return Response(content=content, media_type="application/xml; charset=utf-8", headers=EDGE_HTML_HEADERS)
    content = '<?xml version="1.0"?>\n<users>\n\t<user>98533D5A610C8BB068BDE589D75E9C6F</user>\n</users>\n'
    return Response(content=content, media_type="application/xml; charset=utf-8", headers=EDGE_HTML_HEADERS)

@app.api_route("/ads.txt", methods=["GET", "HEAD"])
async def ads_txt():
    ads_file = os.path.join(BASE_DIR, "public", "ads.txt")
    if os.path.exists(ads_file):
        with open(ads_file, "r", encoding="utf-8") as f:
            content = f.read()
        return Response(content=content, media_type="text/plain; charset=utf-8", headers=EDGE_HTML_HEADERS)
    content = "google.com, pub-2350272227833258, DIRECT, f08c47fec0942fa0\n"
    return Response(content=content, media_type="text/plain; charset=utf-8", headers=EDGE_HTML_HEADERS)

@app.api_route("/robots.txt", methods=["GET", "HEAD"])
async def robots_txt():
    robots_file = os.path.join(BASE_DIR, "public", "robots.txt")
    if os.path.exists(robots_file):
        with open(robots_file, "r", encoding="utf-8") as f:
            return Response(content=f.read(), media_type="text/plain; charset=utf-8", headers=EDGE_HTML_HEADERS)
    content = """User-agent: *
Allow: /
Disallow: /api/
Disallow: /watch
Disallow: /shorts/
Disallow: /*?s=
Disallow: /*&s=
Disallow: /*?q=
Disallow: /*?ref=

Sitemap: https://www.yt4mp3.com/sitemap.xml
"""
    return Response(content=content, media_type="text/plain; charset=utf-8", headers=EDGE_HTML_HEADERS)

_SITEMAP_CACHE_XML = None

def get_authoritative_sitemap_xml() -> str:
    global _SITEMAP_CACHE_XML
    if _SITEMAP_CACHE_XML:
        return _SITEMAP_CACHE_XML
    sitemap_file = os.path.join(BASE_DIR, "public", "sitemap.xml")
    if os.path.exists(sitemap_file):
        try:
            with open(sitemap_file, "r", encoding="utf-8") as f:
                content = f.read()
                if content and "<urlset" in content:
                    _SITEMAP_CACHE_XML = content
                    return _SITEMAP_CACHE_XML
        except Exception:
            pass
    # Dynamic fallback: build sitemap from all 63 authoritative canonical URLs
    urls = get_all_sitemap_urls()
    items = []
    for u in urls:
        lmod = "2026-11-11"
        items.append(f"""  <url>
    <loc>{u}</loc>
    <lastmod>{lmod}</lastmod>
  </url>""")
    _SITEMAP_CACHE_XML = '<?xml version="1.0" encoding="UTF-8"?>\n<?xml-stylesheet type="text/xsl" href="/sitemap.xsl"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(items) + "\n</urlset>"
    return _SITEMAP_CACHE_XML

@app.api_route("/sitemap.xml", methods=["GET", "HEAD"])
async def sitemap_xml():
    xml_content = get_authoritative_sitemap_xml()
    sitemap_headers = dict(EDGE_HTML_HEADERS)
    sitemap_headers["Content-Disposition"] = 'inline; filename="sitemap.xml"'
    return Response(content=xml_content, media_type="application/xml; charset=utf-8", headers=sitemap_headers)

@app.api_route("/sitemap.xsl", methods=["GET", "HEAD"])
async def sitemap_xsl():
    xsl_file = os.path.join(BASE_DIR, "public", "sitemap.xsl")
    if os.path.exists(xsl_file):
        with open(xsl_file, "r", encoding="utf-8") as f:
            content = f.read()
        return Response(content=content, media_type="text/xsl; charset=utf-8", headers={"Cache-Control": "public, max-age=86400, s-maxage=86400"})
    raise HTTPException(status_code=404, detail="Sitemap stylesheet not found")

# Redirect any alternate/legacy sitemap endpoints to the single authoritative sitemap
@app.api_route("/sitemap_index.xml", methods=["GET", "HEAD"])
@app.api_route("/sitemap-index.xml", methods=["GET", "HEAD"])
@app.api_route("/sitemaps.xml", methods=["GET", "HEAD"])
@app.api_route("/sitemap1.xml", methods=["GET", "HEAD"])
@app.api_route("/sitemap.xml.gz", methods=["GET", "HEAD"])
@app.api_route("/sitemap", methods=["GET", "HEAD"])
@app.api_route("/sitemap/", methods=["GET", "HEAD"])
async def redirect_duplicate_sitemaps():
    return RedirectResponse(url="https://www.yt4mp3.com/sitemap.xml", status_code=301)

@app.api_route("/llms.txt", methods=["GET", "HEAD"])
async def llms_txt():
    llms_file = os.path.join(BASE_DIR, "public", "llms.txt")
    if os.path.exists(llms_file):
        with open(llms_file, "r", encoding="utf-8") as f:
            return Response(content=f.read(), media_type="text/plain; charset=utf-8", headers=EDGE_HTML_HEADERS)
    content = """# YT4MP3
> Free Online YouTube to MP3 and MP4 Converter

YT4MP3 is a fast, free, web-based tool for converting and downloading YouTube videos into high-quality MP3 audio (up to 320kbps) and HD/4K MP4 video files.

## Core Features
- YouTube to MP3 converter with 320kbps, 256kbps, and 128kbps bitrate selection.
- YouTube to MP4 video downloader supporting 1080p, 720p, and 4K resolutions.
- Direct browser downloads with zero software installation and no user registration required.
- Fully compatible with desktop and mobile devices including Android, iOS, Windows, and macOS.

## Available Pages
- [Home](https://www.yt4mp3.com/): Free Online YouTube to MP3 and MP4 Converter.
- [YouTube to MP3 Converter](https://www.yt4mp3.com/youtube-to-mp3): Convert YouTube videos and music into high quality 320kbps MP3 audio files.
- [YouTube to MP4 Converter](https://www.yt4mp3.com/youtube-to-mp4): Download YouTube videos in 1080p, 720p, and 4K MP4 format.
- [YouTube Shorts Downloader](https://www.yt4mp3.com/youtube-shorts-downloader): Download YouTube Shorts videos in HD MP4 or convert Shorts to MP3.
- [Contact Us](https://www.yt4mp3.com/contact-us): Official support and DMCA contact (contact.yt4mp3@gmail.com).
- [Terms of Service](https://www.yt4mp3.com/terms-of-service): Terms governing the personal and fair use of the converter tool.
- [Privacy Policy](https://www.yt4mp3.com/privacy-policy): Privacy practices and data handling information.
"""
    return Response(content=content, media_type="text/plain; charset=utf-8", headers=EDGE_HTML_HEADERS)


_FEED_CACHE_XML = None

def get_authoritative_feed_xml() -> str:
    global _FEED_CACHE_XML
    if _FEED_CACHE_XML:
        return _FEED_CACHE_XML
    feed_file = os.path.join(BASE_DIR, "public", "feed.xml")
    if os.path.exists(feed_file):
        try:
            with open(feed_file, "r", encoding="utf-8") as f:
                content = f.read()
                if content and "<rss" in content:
                    _FEED_CACHE_XML = content
                    return _FEED_CACHE_XML
        except Exception:
            pass
    import html
    pages = ["home", "youtube-to-mp3", "youtube-to-mp4", "youtube-shorts-downloader"]
    release_dates = {
        "youtube-to-mp3": "Tue, 18 Aug 2026",
        "youtube-to-mp4": "Tue, 15 Sep 2026",
        "youtube-shorts-downloader": "Thu, 15 Oct 2026",
        "home": "Wed, 04 Nov 2026",
        "blog": "Thu, 12 Nov 2026",
        "article": "Thu, 12 Nov 2026",
    }
    urls = []
    # 1. Main Tools
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
            pub_date = release_dates.get(p, "Wed, 04 Nov 2026")
            urls.append((link, title, desc, lang, pub_date))
            
    # 2. Blog Hub Pages
    from app.blog_data import BLOG_I18N_PAGES
    for lang in SUPPORTED_LANGUAGES:
        blog_meta = BLOG_I18N_PAGES.get(lang, BLOG_I18N_PAGES["en"])
        if lang == "en":
            link = "https://www.yt4mp3.com/blog"
        else:
            link = f"https://www.yt4mp3.com/{lang}/blog/"
        title = blog_meta.get("title", "YT4MP3 Blog")
        desc = blog_meta.get("meta_desc", "Expert guides and tutorials on media conversion.")
        pub_date = release_dates["blog"]
        urls.append((link, title, desc, lang, pub_date))

    # 3. Blog Article Pages
    from app.articles_data import BLOG_ARTICLES
    if BLOG_ARTICLES:
        art = BLOG_ARTICLES[0]
        slug = art.get("slug", "youtube-to-mp3-converter-free-guide")
        for lang in SUPPORTED_LANGUAGES:
            if lang == "en":
                link = f"https://www.yt4mp3.com/blog/{slug}"
                title = art.get("title", "YouTube Audio Extraction and Free MP3 Guide")
                desc = art.get("meta_desc") or art.get("excerpt") or ""
            else:
                link = f"https://www.yt4mp3.com/{lang}/blog/{slug}"
                trans = art.get("translations", {}).get(lang, {})
                title = trans.get("title", art.get("title"))
                desc = trans.get("meta_desc") or trans.get("excerpt") or art.get("meta_desc", "")
            pub_date = release_dates["article"]
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
    _FEED_CACHE_XML = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel>
    <title>YT4MP3 - YouTube Media Converter Tools &amp; Updates</title>
    <link>https://www.yt4mp3.com/</link>
    <description>Latest tools, guides, and multilingual updates for converting YouTube videos to MP3 and MP4.</description>
    <language>en-us</language>
    <lastBuildDate>Thu, 12 Nov 2026</lastBuildDate>
    <atom:link href="https://www.yt4mp3.com/feed.xml" rel="self" type="application/rss+xml" />
{items_xml}  </channel>
</rss>"""
    return _FEED_CACHE_XML

@app.api_route("/feed.xml", methods=["GET", "HEAD"])
@app.api_route("/rss.xml", methods=["GET", "HEAD"])
@app.api_route("/feed", methods=["GET", "HEAD"])
async def rss_feed():
    feed_xml = get_authoritative_feed_xml()
    headers = dict(EDGE_HTML_HEADERS)
    headers["Content-Type"] = "application/rss+xml; charset=utf-8"
    headers["Content-Disposition"] = 'inline; filename="feed.xml"'
    return Response(content=feed_xml, media_type="application/rss+xml; charset=utf-8", headers=headers)

@app.get("/8f9b3e1c4a2d7e5f9a0b1c2d3e4f5a6b.txt")
async def indexnow_key():
    return Response(content="8f9b3e1c4a2d7e5f9a0b1c2d3e4f5a6b", media_type="text/plain; charset=utf-8", headers=EDGE_HTML_HEADERS)

def get_all_sitemap_urls() -> list:
    sitemap_file = os.path.join(BASE_DIR, "public", "sitemap.xml")
    urls = []
    if os.path.exists(sitemap_file):
        try:
            with open(sitemap_file, "r", encoding="utf-8") as f:
                xml_content = f.read()
            found = re.findall(r"<loc>\s*(https?://[^<\s]+)\s*</loc>", xml_content, re.I)
            for u in found:
                if u not in urls:
                    urls.append(u)
        except Exception:
            pass
    if not urls:
        urls = (
            [
                "https://www.yt4mp3.com/",
                "https://www.yt4mp3.com/youtube-to-mp3",
                "https://www.yt4mp3.com/youtube-to-mp4",
                "https://www.yt4mp3.com/youtube-shorts-downloader",
                "https://www.yt4mp3.com/contact-us",
                "https://www.yt4mp3.com/terms-of-service",
                "https://www.yt4mp3.com/privacy-policy"
            ] + [
                f"https://www.yt4mp3.com/{c}/" for c in SUPPORTED_LANGUAGES if c != "en"
            ] + [
                f"https://www.yt4mp3.com/{c}/youtube-to-mp3" for c in SUPPORTED_LANGUAGES if c != "en"
            ] + [
                f"https://www.yt4mp3.com/{c}/youtube-to-mp4" for c in SUPPORTED_LANGUAGES if c != "en"
            ] + [
                f"https://www.yt4mp3.com/{c}/youtube-shorts-downloader" for c in SUPPORTED_LANGUAGES if c != "en"
            ]
        )
    return urls

@app.api_route("/api/indexnow", methods=["GET", "POST"])
async def trigger_indexnow(key: str = "8f9b3e1c4a2d7e5f9a0b1c2d3e4f5a6b"):
    clean_key = re.sub(r"[^a-zA-Z0-9-]", "", key or "") or "8f9b3e1c4a2d7e5f9a0b1c2d3e4f5a6b"
    url_list = list(get_all_sitemap_urls())
    for extra_url in ["https://www.yt4mp3.com/sitemap.xml", "https://www.yt4mp3.com/feed.xml"]:
        if extra_url not in url_list:
            url_list.append(extra_url)
    payload = {
        "host": "www.yt4mp3.com",
        "key": clean_key,
        "keyLocation": f"https://www.yt4mp3.com/{clean_key}.txt",
        "urlList": url_list
    }
    data = json.dumps(payload).encode("utf-8")
    # Official unified IndexNow endpoints (shares with Bing, Yandex, Seznam, Naver, Yep)
    endpoints = [
        "https://api.indexnow.org/indexnow",
        "https://www.bing.com/indexnow",
        "https://yandex.com/indexnow"
    ]
    results = {}
    for ep in endpoints:
        try:
            req = urllib.request.Request(
                ep,
                data=data,
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "User-Agent": "Mozilla/5.0 (compatible; YT4MP3-SitemapNotifier/1.0; +https://www.yt4mp3.com)"
                }
            )
            with urllib.request.urlopen(req, timeout=6) as res:
                results[ep] = {"status": res.status, "msg": "ok"}
        except urllib.error.HTTPError as he:
            results[ep] = {"status": he.code, "msg": "accepted" if he.code in [200, 202] else str(he)}
        except Exception as e:
            results[ep] = {"status": "error", "detail": str(e)}
    return {
        "submitted": True,
        "url_count": len(url_list),
        "results": results
    }

@app.on_event("startup")
async def start_auto_indexnow_scheduler():
    import asyncio
    async def _auto_index_loop():
        # Wait 90 seconds after server startup before initial run
        await asyncio.sleep(90)
        while True:
            try:
                await trigger_indexnow()
            except Exception as e:
                print(f"[AUTO_INDEXNOW_WARN] {e}")
            # Automatically push all URLs to Bing/IndexNow every 4 hours (14,400 seconds)
            await asyncio.sleep(14400)
    asyncio.create_task(_auto_index_loop())

@app.get("/api/report-issue")
@app.post("/api/report-issue")
async def report_issue(request: Request):
    try:
        if request.method == "POST":
            try:
                body = await request.json()
            except Exception:
                body = {}
        else:
            body = dict(request.query_params)

        video_url = str(body.get("video_url", "Unknown"))
        video_title = str(body.get("video_title", "Unknown"))
        selected_format = str(body.get("format", body.get("selected_format", "Unknown")))
        error_detail = str(body.get("error", body.get("error_detail", "Stream conversion failed")))
        user_agent = request.headers.get("user-agent", "Unknown")
        client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "Unknown")
        
        # Ignore malformed or fake URLs (e.g. "www.youtube", empty, or non-YouTube inputs)
        has_valid_id = bool(re.search(r"(?:v=|\/shorts\/|\/live\/|\/)([a-zA-Z0-9_-]{11})(?:[?&#/\s]|$)", video_url))
        if not has_valid_id or "www.youtube" in video_url.lower() and not re.search(r"v=[a-zA-Z0-9_-]{11}", video_url):
            return {"success": False, "ignored": True, "reason": "invalid_url_input"}

        # Log incident for analytics
        print(f"[CONVERSION_ISSUE_REPORT] URL: {video_url} | Title: {video_title} | Format: {selected_format} | Error: {error_detail} | IP: {client_ip}")
        
        # Real-time Telegram Bot Notification
        tg_token = os.environ.get("TELEGRAM_BOT_TOKEN") or "8717205816:AAGdAXIPjaUg986TTJU3n0UFe0wZxfIO3oo"
        tg_chat_id = os.environ.get("TELEGRAM_CHAT_ID") or "7396061312"
        if tg_token and tg_chat_id:
            try:
                import html as html_lib
                safe_title = html_lib.escape(video_title[:90])
                safe_url = html_lib.escape(video_url)
                safe_fmt = html_lib.escape(selected_format)
                safe_err = html_lib.escape(error_detail)
                safe_ip = html_lib.escape(client_ip)

                is_expected_restr = any(k.lower() in error_detail.lower() for k in [
                    "broadcaster", "live stream", "private video", "age-restricted", "video too long", 
                    "membership required", "paid video", "video unavailable", "region restricted", 
                    "duration limits", "up to 3 hours", "exceeds", "not available in your country", 
                    "blocked in your country", "🔞", "🔒", "📡", "💰", "❌", "⏱", "senderschutz"
                ])
                # Suppress Telegram alerts for expected user notices (video too long, 18+ age restricted, DRM)
                # to keep owner's phone quiet and free of false alarms. Only real crashes trigger alerts!
                if is_expected_restr:
                    print(f"[EXPECTED_NOTICE_LOCAL_LOG] {video_title} | {error_detail} (Telegram muted)")
                    return {"success": True, "message": "Expected restriction handled gracefully on client; Telegram alert muted."}

                header_badge = "🚨 <b>YT4MP3 Conversion Alert</b>"

                alert_text = (
                    f"{header_badge}\n\n"
                    f"🎬 <b>Video:</b> {safe_title}\n"
                    f"🔗 <b>Link:</b> {safe_url}\n"
                    f"🎛 <b>Format:</b> {safe_fmt}\n"
                    f"⚠️ <b>Status:</b> {safe_err}\n"
                    f"🌐 <b>User IP:</b> <code>{safe_ip}</code>"
                )
                tg_url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
                tg_payload = json.dumps({
                    "chat_id": tg_chat_id,
                    "text": alert_text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True
                }).encode("utf-8")
                tg_req = urllib.request.Request(
                    tg_url, 
                    data=tg_payload, 
                    headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(tg_req, timeout=6) as tg_res:
                    tg_resp_data = json.loads(tg_res.read().decode('utf-8'))
                    return {"success": True, "message": "Issue recorded and Telegram alert sent!", "telegram": tg_resp_data}
            except Exception as tg_err:
                print(f"Telegram notification dispatch error: {tg_err}")
                return {"success": True, "message": "Issue recorded", "telegram_error": str(tg_err)}
                
        return {"success": True, "message": "Issue recorded. Thank you for reporting!"}
    except Exception as e:
        return {"success": False, "detail": str(e)}


# ==============================================================================
# FASTSAVER PRO ENGINE — primary paid API with 4K support, high-speed stream delivery
# Uses api.fastsaver.io with API key. Costs credits per download.
# ==============================================================================
FASTSAVER_API_KEY = os.environ.get("FASTSAVER_API_KEY") or "fs_sk_9w9n0d9x3t0r0g2g0d3e0j3f6u7q"
FASTSAVER_LOW_CREDIT_THRESHOLD = 10000
_LAST_FS_BALANCE_CHECK_TS = 0.0
_LAST_FS_LOW_ALERT_TS = 0.0

def _fetch_fastsaver_balance() -> dict:
    try:
        req = urllib.request.Request(
            "https://api.fastsaver.io/v1/balance",
            headers={
                "X-Api-Key": FASTSAVER_API_KEY,
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130 Safari/537.36",
            },
        )
        with urllib.request.urlopen(req, timeout=6) as res:
            data = json.loads(res.read().decode("utf-8"))
            if isinstance(data, dict) and data.get("ok"):
                return data
    except Exception:
        pass
    return {}

def _check_fastsaver_credits_and_alert(force_check: bool = False, test_alert: bool = False) -> dict:
    global _LAST_FS_BALANCE_CHECK_TS, _LAST_FS_LOW_ALERT_TS
    import time
    now = time.time()
    if not force_check and not test_alert and (now - _LAST_FS_BALANCE_CHECK_TS < 300):
        return {"checked": False}
    _LAST_FS_BALANCE_CHECK_TS = now

    bal = _fetch_fastsaver_balance()
    if not bal:
        return {"checked": True, "ok": False}

    credits = int(bal.get("credits", 0))
    plan_credits = int(bal.get("plan_credits", 100000))
    plan_name = str(bal.get("plan", "Pro"))
    expire_label = str(bal.get("expire_label", ""))

    should_alert = test_alert or (credits <= FASTSAVER_LOW_CREDIT_THRESHOLD)
    alert_sent = False

    if should_alert:
        stats = _load_analytics(force_cloud=False)
        last_alert_ts = max(float(_LAST_FS_LOW_ALERT_TS), float(stats.get("fs_al_ts", 0) or 0))
        # Send immediately on first drop <= 10k, then remind at most once every 6 hours
        if test_alert or (now - last_alert_ts >= 21600):
            tg_token = os.environ.get("TELEGRAM_BOT_TOKEN") or "8717205816:AAGdAXIPjaUg986TTJU3n0UFe0wZxfIO3oo"
            tg_chat_id = os.environ.get("TELEGRAM_CHAT_ID") or "7396061312"
            if tg_token and tg_chat_id:
                try:
                    header_tag = "🧪 <b>[TEST] FastSaver Low Credits Alert</b>" if test_alert else "⚠️ <b>FastSaver API Low Credits Alert!</b>"
                    msg = (
                        f"{header_tag}\n\n"
                        f"🔋 <b>Remaining Credits:</b> <code>{credits:,}</code> / <code>{plan_credits:,}</code>\n"
                        f"📉 <b>Alert Threshold:</b> <code>{FASTSAVER_LOW_CREDIT_THRESHOLD:,} credits</code>\n"
                        f"📦 <b>Current Plan:</b> {plan_name} ({expire_label})\n\n"
                        "⚡ <i>Aapke FastSaver API me 10,000 ya us se kam credits reh gaye hain. 4K aur long videos ka backup chalta rakhne ke liye credits top-up kar lein:</i>\n"
                        "🔗 https://api.fastsaver.io/pricing"
                    )
                    tg_payload = json.dumps({
                        "chat_id": tg_chat_id,
                        "text": msg,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": True,
                    }).encode("utf-8")
                    tg_req = urllib.request.Request(
                        f"https://api.telegram.org/bot{tg_token}/sendMessage",
                        data=tg_payload,
                        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
                    )
                    with urllib.request.urlopen(tg_req, timeout=6) as tg_res:
                        tg_data = json.loads(tg_res.read().decode("utf-8"))
                        alert_sent = bool(tg_data.get("ok"))
                    if alert_sent and not test_alert:
                        _LAST_FS_LOW_ALERT_TS = now
                        stats["fs_al_ts"] = int(now)
                        _save_analytics(stats, force_cloud=True)
                except Exception as e:
                    print(f"FastSaver low-credit Telegram alert error: {e}")

    return {
        "checked": True,
        "ok": True,
        "credits": credits,
        "plan_credits": plan_credits,
        "plan": plan_name,
        "threshold": FASTSAVER_LOW_CREDIT_THRESHOLD,
        "is_low": credits <= FASTSAVER_LOW_CREDIT_THRESHOLD,
        "alert_sent": alert_sent,
    }

@app.get("/api/fastsaver-balance-check")
async def fastsaver_balance_check(test_alert: int = 0):
    return _check_fastsaver_credits_and_alert(force_check=True, test_alert=(int(test_alert) == 1))

# ==============================================================================
# DATAIMPULSE RESIDENTIAL PROXY ENGINE — Fallback for geo-restricted & locked videos
# Capped strictly at 720p maximum as requested. Primary engine remains FastSaver Pro.
# ==============================================================================
DATAIMPULSE_HOST = "gw.dataimpulse.com"
DATAIMPULSE_PORT = 823
DATAIMPULSE_USER = os.environ.get("DATAIMPULSE_USER") or "c8f15994b4066af9b4b9"
DATAIMPULSE_PASS = os.environ.get("DATAIMPULSE_PASS") or "42eaaf24f75bc5fb"

_PROXY_STREAM_CACHE: dict[str, dict] = {}

def get_dataimpulse_proxy_url(country: str = None, session_id: str = None) -> str:
    user_parts = [DATAIMPULSE_USER]
    if country:
        c = re.sub(r"[^a-zA-Z]", "", country).lower()[:2]
        if c:
            user_parts.append(f"__cr.{c}")
    if session_id:
        s = re.sub(r"[^a-zA-Z0-9_-]", "", session_id)
        if s:
            user_parts.append(f";sid.{s}")
    username = "".join(user_parts)
    return f"http://{username}:{DATAIMPULSE_PASS}@{DATAIMPULSE_HOST}:{DATAIMPULSE_PORT}"

def pick_best_proxy_country(allowed_countries: list) -> str:
    if not allowed_countries:
        return None
    allowed_upper = [c.upper() for c in allowed_countries if isinstance(c, str)]
    preferred = ["US", "DE", "FR", "GB", "CA", "ES", "IT", "MX", "BR", "JP", "IN", "AU"]
    for p in preferred:
        if p in allowed_upper:
            return p.lower()
    return allowed_upper[0].lower() if allowed_upper else None

def get_proxy_format_selector(mode: str = "audio", quality: str = "720") -> str:
    if mode == "audio":
        return "140/ba[ext=m4a]/ba/251/bestaudio/18/best"
    # User requirement: Strictly capped at 720p maximum! Never exceed 720p.
    return "18/22/b[height<=720]/bv*[height<=720]+ba/best[height<=720]/best"

def _extract_via_innertube_android(vid: str, proxy_url: str, mode: str = "audio") -> dict:
    if not vid or len(vid) != 11:
        return {}
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url}))
    w_req = urllib.request.Request(
        f"https://www.youtube.com/watch?v={vid}&hl=en&gl=US",
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36"},
    )
    visitor_data = ""
    with opener.open(w_req, timeout=8) as r_w:
        w_html = r_w.read().decode("utf-8", "ignore")
    m_vis = re.search(r'"VISITOR_DATA":\s*"([^"]+)"|"visitorData":\s*"([^"]+)"', w_html)
    if m_vis:
        visitor_data = m_vis.group(1) or m_vis.group(2) or ""

    client_ctx = {
        "androidSdkVersion": 30,
        "clientName": "ANDROID",
        "clientVersion": "21.26.364",
        "hl": "en",
        "osName": "Android",
        "osVersion": "11",
        "userAgent": "com.google.android.youtube/21.26.364 (Linux; U; Android 11) gzip",
    }
    if visitor_data:
        client_ctx["visitorData"] = visitor_data

    payload = {
        "videoId": vid,
        "context": {"client": client_ctx},
        "contentCheckOk": True,
        "racyCheckOk": True,
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "com.google.android.youtube/21.26.364 (Linux; U; Android 11) gzip",
        "X-Goog-Api-Format-Version": "2",
        "X-YouTube-Client-Name": "3",
        "X-YouTube-Client-Version": "21.26.364",
    }
    if visitor_data:
        headers["X-Goog-Visitor-Id"] = visitor_data

    req = urllib.request.Request(
        "https://www.youtube.com/youtubei/v1/player?prettyPrint=false",
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with opener.open(req, timeout=10) as r:
        data = json.loads(r.read().decode("utf-8"))

    sd = data.get("streamingData") or {}
    vd = data.get("videoDetails") or {}
    title = vd.get("title") or "YouTube Media"
    prog_formats = [f for f in (sd.get("formats") or []) if f.get("url")]
    adap_formats = [f for f in (sd.get("adaptiveFormats") or []) if f.get("url")]

    chosen = None
    if mode == "audio":
        for pref_itag in [140, 251, 139, 250, 249]:
            for f in adap_formats:
                if f.get("itag") == pref_itag:
                    chosen = f
                    break
            if chosen:
                break
        if not chosen and prog_formats:
            chosen = prog_formats[0]
    else:
        valid_prog = [f for f in prog_formats if int(f.get("height") or 360) <= 720]
        if valid_prog:
            valid_prog.sort(key=lambda x: int(x.get("height") or 360), reverse=True)
            chosen = valid_prog[0]
        elif prog_formats:
            chosen = prog_formats[0]

    if chosen and chosen.get("url"):
        raw_h = int(chosen.get("height") or (360 if mode == "video" else 0))
        return {
            "url": chosen["url"],
            "title": title,
            "height": min(raw_h, 720) if mode == "video" else 0,
        }
    return {}

def resolve_dataimpulse_stream(yt_url: str, mode: str = "audio", quality: str = "720", target_country: str = None) -> dict:
    import yt_dlp
    import time
    session_id = uuid.uuid4().hex[:10]
    proxy_url = get_dataimpulse_proxy_url(country=target_country, session_id=session_id)
    fmt_selector = get_proxy_format_selector(mode=mode, quality=quality)

    m_vid = re.search(r"(?:v=|\/embed\/|\/shorts\/|youtu\.be\/|\/v\/|watch\?v=|\&v=|^)([a-zA-Z0-9_-]{11})(?:[&?]|$)", yt_url or "")
    vid = m_vid.group(1) if m_vid else ""

    info = None
    if vid:
        try:
            it_res = _extract_via_innertube_android(vid, proxy_url, mode=mode)
            if it_res and it_res.get("url"):
                info = it_res
        except Exception:
            info = None

    base_opts = {
        "proxy": proxy_url,
        "quiet": True,
        "no_warnings": True,
        "format": fmt_selector,
        "noplaylist": True,
        "extract_flat": False,
        "socket_timeout": 25,
    }
    
    last_err = None
    if not info:
        for client_try in [["android", "web"], None]:
            ydl_opts = dict(base_opts)
            if client_try:
                ydl_opts["extractor_args"] = {"youtube": {"player_client": client_try}}
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(yt_url, download=False)
                if info and (info.get("url") or info.get("requested_formats")):
                    break
            except Exception as e:
                last_err = e
                info = None
            
    if not info:
        raise last_err or ValueError("Could not extract stream info via residential proxy")
        
    stream_url = info.get("url")
    if not stream_url and info.get("requested_formats"):
        stream_url = info["requested_formats"][-1].get("url")
        
    if not stream_url:
        raise ValueError("Could not extract playable stream URL via residential proxy")
        
    title = info.get("title") or "YouTube Media"
    raw_h = info.get("height") or (720 if mode == "video" else 0)
    h = min(raw_h, 720) if mode == "video" else 0
    ext = "mp3" if mode == "audio" else "mp4"
    
    _PROXY_STREAM_CACHE[session_id] = {
        "stream_url": stream_url,
        "proxy_url": proxy_url,
        "title": title,
        "ext": ext,
        "mode": mode,
        "height": h,
        "created_at": time.time(),
    }
    
    return {
        "session_id": session_id,
        "stream_url": stream_url,
        "proxy_url": proxy_url,
        "title": title,
        "ext": ext,
        "height": h,
    }

def make_content_disposition(title: str, ext: str) -> str:
    clean = re.sub(r'[\/:*?"<>|\r\n\t]', "_", title or "download").strip()
    ascii_clean = clean.encode("ascii", "ignore").decode("ascii").strip()
    ascii_clean = re.sub(r'\s+', ' ', ascii_clean).strip(". ") or "download"
    encoded_utf8 = urllib.parse.quote(clean.encode("utf-8"))
    return f'attachment; filename="{ascii_clean}.{ext}"; filename*=UTF-8\'\'{encoded_utf8}.{ext}'

@app.get("/api/fastsaver-video")
async def fastsaver_video(url: str, mode: str = "audio", quality: str = "720"):
    if not re.search(r"(youtube\.com|youtu\.be)", url or ""):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    m_vid = re.search(r"(?:v=|\/embed\/|\/shorts\/|youtu\.be\/|\/v\/|watch\?v=|\&v=|^)([a-zA-Z0-9_-]{11})(?:[&?]|$)", url or "")
    vid = m_vid.group(1) if m_vid else ""

    # Check video resolution metadata (to identify regional / geo-blocked videos)
    res_meta = {}
    if vid:
        try:
            res_meta = await get_video_resolutions(vid, skip_fastsaver_info=False)
        except Exception:
            res_meta = {}

    is_regional = bool(res_meta.get("is_regional") or res_meta.get("is_geo_blocked"))
    allowed_countries = res_meta.get("allowed_countries", [])
    target_country = pick_best_proxy_country(allowed_countries)

    # 1. If video is Country-Locked (Geo-Restricted): ONLY then use DataImpulse Residential Proxy (capped at 720p max)
    if is_regional:
        try:
            clean_q = re.sub(r"[^0-9]", "", str(quality)) or "720"
            if mode == "video" and int(clean_q) > 720:
                clean_q = "720"

            stream_data = resolve_dataimpulse_stream(
                url,
                mode=mode,
                quality=clean_q,
                target_country=target_country
            )
            sid = stream_data["session_id"]
            title = stream_data["title"]
            ext = stream_data["ext"]
            stream_raw_url = stream_data.get("stream_url", "")
            surl = base64.urlsafe_b64encode(stream_raw_url.encode("utf-8")).decode("ascii") if stream_raw_url else ""
            clean_title = re.sub(r'[\/:*?"<>|\r\n\t]', "_", title).strip() or "video"
            download_url = f"/api/proxy-download?sid={sid}&vid={vid}&mode={mode}&ext={ext}&title={urllib.parse.quote(clean_title)}&country={target_country or ''}&surl={surl}"
            return {
                "success": True,
                "download_url": download_url,
                "filename": f"{clean_title}.{ext}",
                "engine": "residential_proxy",
                "capped_at_720": True,
            }
        except Exception as proxy_err:
            print(f"[DATAIMPULSE_PROXY_FAIL] {vid}: {proxy_err}")
            return {
                "success": False,
                "error": str(proxy_err),
                "is_unsupported": bool(res_meta.get("is_unsupported")),
                "unsupported_reason": res_meta.get("unsupported_reason"),
                "is_regional": True,
            }

    # 2. For ALL normal videos (NOT country locked): Use FastSaver Pro Paid API with auto-retry
    headers = {
        "X-Api-Key": FASTSAVER_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130 Safari/537.36",
    }
    if mode == "audio":
        fmt = "audio"
        fs_formats_to_try = ["audio"]
    else:
        q = re.sub(r"[^0-9]", "", str(quality)) or "720"
        fmt_map = {"2160": "2160p", "1440": "1440p", "1080": "1080p", "720": "720p", "480": "480p", "360": "360p", "240": "240p", "144": "144p"}
        fmt = fmt_map.get(q, "720p")
        fs_formats_to_try = [fmt]
        # If requested a lower/mid resolution like 480p or 360p, also allow fallback to 720p if needed
        if fmt not in ["720p", "1080p", "2160p"]:
            fs_formats_to_try.append("720p")

    detail_err = "Conversion could not be completed"
    import time
    fastsaver_succeeded = False
    for target_fmt in fs_formats_to_try:
        body = json.dumps({"url": url, "format": target_fmt}).encode("utf-8")
        # Try up to 2 times for each format with a 1.2s delay to absorb transient worker hiccups
        for attempt in range(2):
            try:
                req = urllib.request.Request(
                    "https://api.fastsaver.io/v1/youtube/download",
                    data=body,
                    headers=headers,
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=18) as res:
                    data = json.loads(res.read().decode("utf-8"))
                _check_fastsaver_credits_and_alert(force_check=True)
                if data.get("ok") and data.get("download_url"):
                    return {
                        "success": True,
                        "download_url": data["download_url"],
                        "filename": data.get("filename", ""),
                        "engine": "fastsaver",
                    }
                detail_err = str(data.get("detail", "fastsaver_unknown_error"))
                # If FastSaver returned transient download.failed on attempt 0, pause and retry
                if detail_err == "download.failed" and attempt == 0:
                    time.sleep(1.2)
                    continue
            except urllib.error.HTTPError as e:
                try:
                    err_body = json.loads(e.read().decode("utf-8", "ignore"))
                    detail_err = str(err_body.get("detail", f"HTTP {e.code}"))
                except Exception:
                    detail_err = f"HTTP {e.code}"
                _check_fastsaver_credits_and_alert(force_check=False)
                if attempt == 0:
                    time.sleep(1.0)
                    continue
            except Exception as e:
                detail_err = str(e)
                if attempt == 0:
                    time.sleep(1.0)
                    continue
            break  # Break inner loop if not continuing

    # 3. Fallback: If FastSaver failed (e.g. download.failed on YouTube Kids / special streams) and video is not unsupported,
    # automatically recover via DataImpulse Residential Proxy (strictly capped at 720p max)
    if not res_meta.get("is_unsupported"):
        try:
            clean_q = re.sub(r"[^0-9]", "", str(quality)) or "720"
            if mode == "video" and int(clean_q) > 720:
                clean_q = "720"
            stream_data = resolve_dataimpulse_stream(
                url,
                mode=mode,
                quality=clean_q,
                target_country=target_country or "us"
            )
            sid = stream_data["session_id"]
            title = stream_data["title"]
            ext = stream_data["ext"]
            stream_raw_url = stream_data.get("stream_url", "")
            surl = base64.urlsafe_b64encode(stream_raw_url.encode("utf-8")).decode("ascii") if stream_raw_url else ""
            clean_title = re.sub(r'[\/:*?"<>|\r\n\t]', "_", title).strip() or "video"
            download_url = f"/api/proxy-download?sid={sid}&vid={vid}&mode={mode}&ext={ext}&title={urllib.parse.quote(clean_title)}&country={target_country or 'us'}&surl={surl}"
            return {
                "success": True,
                "download_url": download_url,
                "filename": f"{clean_title}.{ext}",
                "engine": "residential_proxy_fallback",
                "capped_at_720": True,
            }
        except Exception as fallback_err:
            print(f"[DATAIMPULSE_FALLBACK_FAIL] {vid}: {fallback_err}")

    user_facing_error = detail_err
    if detail_err in ["download.failed", "fastsaver_unknown_error"]:
        user_facing_error = "Stream server is temporarily busy. Please tap Retry to reconnect."

    return {
        "success": False,
        "error": user_facing_error,
        "raw_error": detail_err,
        "is_unsupported": bool(res_meta.get("is_unsupported")),
        "unsupported_reason": res_meta.get("unsupported_reason"),
        "is_regional": False,
    }

@app.get("/api/proxy-download")
async def proxy_download(sid: str = "", vid: str = "", mode: str = "audio", ext: str = "mp4", title: str = "video", country: str = "", surl: str = ""):
    stream_url = None
    if surl:
        try:
            stream_url = base64.urlsafe_b64decode(surl.encode("ascii")).decode("utf-8")
        except Exception:
            stream_url = None

    if not stream_url:
        stream_info = _PROXY_STREAM_CACHE.get(sid)
        if stream_info:
            stream_url = stream_info.get("stream_url")

    if not stream_url and vid:
        try:
            stream_info = resolve_dataimpulse_stream(
                f"https://www.youtube.com/watch?v={vid}",
                mode=mode,
                quality="720",
                target_country=country or None
            )
            stream_url = stream_info.get("stream_url")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Proxy stream resolution failed: {e}")

    if not stream_url:
        raise HTTPException(status_code=404, detail="Stream expired or not found")

    proxy_url = get_dataimpulse_proxy_url(country=country, session_id=sid)
    media_type = "audio/mpeg" if ext == "mp3" else ("audio/mp4" if ext == "m4a" else "video/mp4")

    def iterfile():
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url}))
        req = urllib.request.Request(
            stream_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "Accept": "*/*",
            }
        )
        with opener.open(req, timeout=35) as res:
            while True:
                chunk = res.read(64 * 1024)
                if not chunk:
                    break
                yield chunk

    return StreamingResponse(
        iterfile(),
        media_type=media_type,
        headers={
            "Content-Disposition": make_content_disposition(title, ext),
            "Cache-Control": "no-cache",
        }
    )

@app.get("/api/geo-stream")
async def geo_stream(url: str, format: str = "mp3", quality: str = "720"):
    # Direct alias for legacy links: resolves and streams via DataImpulse Residential Proxy
    mode = "audio" if format.lower() in ["mp3", "m4a", "flac", "wav", "aac", "ogg", "opus"] else "video"
    m_vid = re.search(r"(?:v=|\/embed\/|\/shorts\/|youtu\.be\/|\/v\/|watch\?v=|\&v=|^)([a-zA-Z0-9_-]{11})(?:[&?]|$)", url or "")
    vid = m_vid.group(1) if m_vid else ""

    target_country = None
    if vid:
        try:
            res_meta = await get_video_resolutions(vid, skip_fastsaver_info=True)
            target_country = pick_best_proxy_country(res_meta.get("allowed_countries", []))
        except Exception:
            target_country = None

    clean_q = re.sub(r"[^0-9]", "", str(quality)) or "720"
    if mode == "video" and int(clean_q) > 720:
        clean_q = "720"

    stream_info = resolve_dataimpulse_stream(url, mode=mode, quality=clean_q, target_country=target_country)
    ext = "mp3" if mode == "audio" else "mp4"
    safe_title = re.sub(r'[\/:*?"<>|]', "_", stream_info.get("title", "download")).strip()
    media_type = "audio/mpeg" if ext == "mp3" else "video/mp4"

    def iterfile():
        proxy_url = stream_info["proxy_url"]
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url}))
        req = urllib.request.Request(
            stream_info["stream_url"],
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "Accept": "*/*",
            }
        )
        with opener.open(req, timeout=35) as res:
            while True:
                chunk = res.read(64 * 1024)
                if not chunk:
                    break
                yield chunk

    return StreamingResponse(
        iterfile(),
        media_type=media_type,
        headers={
            "Content-Disposition": make_content_disposition(stream_info.get("title", "download"), ext),
            "Cache-Control": "no-cache",
        }
    )


# ==============================================================================
# YOUTUBE WATCH INFO HELPER
# ==============================================================================
def _fetch_youtube_watch_html(vid: str) -> str:
    yt_url = f"https://www.youtube.com/watch?v={vid}&hl=en&gl=US"
    req_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    html = ""
    try:
        req = urllib.request.Request(yt_url, headers=req_headers)
        with urllib.request.urlopen(req, timeout=4) as r:
            html = r.read().decode("utf-8", "ignore")
    except Exception:
        html = ""
    if '"playabilityStatus"' not in html:
        try:
            proxy_url = get_dataimpulse_proxy_url(country="us", session_id=f"watch{vid[:6]}")
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url}))
            req_p = urllib.request.Request(yt_url, headers=req_headers)
            with opener.open(req_p, timeout=6) as r_p:
                html_p = r_p.read().decode("utf-8", "ignore")
                if '"playabilityStatus"' in html_p:
                    html = html_p
        except Exception:
            pass
    return html


_VIDEO_RES_CACHE = {}

@app.get("/api/video-resolutions")
async def get_video_resolutions(id: str, skip_fastsaver_info: bool = False):
    vid = re.sub(r"[^a-zA-Z0-9_-]", "", id or "")
    if len(vid) != 11:
        return {"has_4k": False, "has_2k": False, "max_height": 1080, "duration_sec": 0, "is_regional": False, "is_geo_blocked": False, "source": "invalid_id"}
    if vid in _VIDEO_RES_CACHE and not skip_fastsaver_info:
        cached = _VIDEO_RES_CACHE[vid]
        if cached.get("duration_sec", 0) > 0 or cached.get("is_unsupported") or cached.get("is_regional"):
            return cached
    if vid in _VIDEO_RES_CACHE and skip_fastsaver_info:
        cached = _VIDEO_RES_CACHE[vid]
        if cached.get("source") == "yt_watch":
            return cached

    yt_url = f"https://www.youtube.com/watch?v={vid}"
    duration_sec = 0

    # 1. Primary: FastSaver Paid API /v1/youtube/info (100% accurate 4K, 2K, 1080p, 720p, filesizes, title, author, duration)
    if not skip_fastsaver_info:
      try:
        info_url = f"https://api.fastsaver.io/v1/youtube/info?url={urllib.parse.quote(yt_url)}"
        req = urllib.request.Request(
            info_url,
            headers={
                "X-Api-Key": FASTSAVER_API_KEY,
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130 Safari/537.36",
            },
        )
        with urllib.request.urlopen(req, timeout=4.5) as res:
            data = json.loads(res.read().decode("utf-8"))
        _check_fastsaver_credits_and_alert(force_check=False)
        if data.get("ok"):
            raw_dur = data.get("duration") or data.get("lengthSeconds") or 0
            if isinstance(raw_dur, (int, float)):
                duration_sec = int(raw_dur)
            elif isinstance(raw_dur, str):
                if raw_dur.isdigit():
                    duration_sec = int(raw_dur)
                elif ":" in raw_dur:
                    parts = [int(p) for p in raw_dur.split(":") if p.isdigit()]
                    if len(parts) == 2:
                        duration_sec = parts[0] * 60 + parts[1]
                    elif len(parts) == 3:
                        duration_sec = parts[0] * 3600 + parts[1] * 60 + parts[2]
            raw_formats = data.get("formats", [])
            fmt_names = []
            available_heights = []
            filesizes = {}
            for f in raw_formats:
                fname = str(f.get("format", "")).lower().strip()
                ftype = str(f.get("type", "")).lower().strip()
                fsize = int(f.get("filesize") or 0)
                fmt_names.append(fname)
                if ftype == "audio" or fname == "audio":
                    if fsize > 0:
                        filesizes["audio"] = fsize
                else:
                    digits = re.sub(r"[^0-9]", "", fname)
                    if digits:
                        h_val = int(digits)
                        if h_val not in available_heights:
                            available_heights.append(h_val)
                        if fsize > 0:
                            filesizes[str(h_val)] = fsize
            has_4k = (2160 in available_heights) or any("2160" in f or "4k" in f for f in fmt_names)
            has_2k = (1440 in available_heights) or any("1440" in f or "2k" in f for f in fmt_names)
            has_1080 = (1080 in available_heights) or any("1080" in f for f in fmt_names)
            has_720 = (720 in available_heights) or any("720" in f for f in fmt_names)
            max_h = max(available_heights) if available_heights else (2160 if has_4k else (1440 if has_2k else 1080))
            result = {
                "has_4k": has_4k,
                "has_2k": has_2k,
                "has_1080": has_1080,
                "has_720": has_720,
                "max_height": max_h,
                "available_heights": sorted(available_heights, reverse=True),
                "filesizes": filesizes,
                "duration_sec": duration_sec,
                "title": str(data.get("title") or ""),
                "author": str(data.get("author") or ""),
                "thumbnail": str(data.get("thumbnail") or ""),
                "is_regional": False,
                "is_geo_blocked": False,
                "source": "fastsaver_info",
            }
            _VIDEO_RES_CACHE[vid] = result
            return result
      except Exception:
          pass

    # 2. Fallback: Check YouTube watch page if FastSaver info was unreachable or video is restricted
    try:
        html = _fetch_youtube_watch_html(vid)
        dur_match = re.search(r'"lengthSeconds":"(\d+)"', html)
        if dur_match:
            duration_sec = int(dur_match.group(1))

        m_c = re.search(r'"availableCountries":\s*(\[[^\]]+\])', html)
        allowed_countries = json.loads(m_c.group(1)) if m_c else []
        is_geo_blocked = bool(
            (len(allowed_countries) > 0 and len(allowed_countries) < 240) or
            (re.search(r'"status":\s*"UNPLAYABLE"', html) and len(allowed_countries) > 0) or
            re.search(r'not available in your country|blocked in your country|The uploader has not made this video available in your country', html, re.I)
        )

        # Detect unsupported video categories (18+ age-restricted, members-only, private, live streams, paid rentals)
        unsupported_reason = None
        if re.search(r'"reason":\s*"(?:This video is private|Private video)"|"status":\s*"LOGIN_REQUIRED".{0,200}private', html, re.I):
            unsupported_reason = "private_video"
        elif re.search(r'"reason":\s*"Sign in to confirm your age"|"adultContent":\s*true|"isRestricted":\s*true', html, re.I):
            unsupported_reason = "age_restricted"
        elif re.search(r'"isMembersOnly":\s*true|"reason":\s*"(?:This video is available to this channel\'s members|Join this channel to get access)"|UNPLAYABLE.{0,250}members', html, re.I):
            unsupported_reason = "channel_membership"
        elif re.search(r'"status":\s*"LOGIN_REQUIRED"', html) and not re.search(r'not a bot|Sign in to confirm you', html, re.I):
            unsupported_reason = "age_restricted"
        elif re.search(r'"isLive":\s*true|"isLiveNow":\s*true', html, re.I):
            unsupported_reason = "live_stream"
        elif re.search(r'Buy or rent|Rental duration|"offerId":|requiresPurchase', html, re.I):
            unsupported_reason = "paid_rental"
        elif re.search(r'"status":\s*"ERROR"|playabilityStatus":\{"status":"ERROR"', html):
            unsupported_reason = "video_unavailable"

        heights = [int(h) for h in re.findall(r'"qualityLabel":"(\d+)p', html)]
        if not heights:
            # Check og:video:width and og:video:height on watch page first (e.g., 4:3 SD videos have width=960/640/480, aspect <= 1.45)
            m_og_w = re.search(r'<meta\s+property=["\']og:video:width["\']\s+content=["\'](\d+)["\']', html, re.I)
            m_og_h = re.search(r'<meta\s+property=["\']og:video:height["\']\s+content=["\'](\d+)["\']', html, re.I)
            og_w = int(m_og_w.group(1)) if m_og_w else 0
            og_h = int(m_og_h.group(1)) if m_og_h else 0
            is_sd_4x3 = bool(og_w > 0 and og_h > 0 and ((og_w / og_h) <= 1.45 or og_w < 1280))

            # Probe YouTube's official image CDN (maxresdefault = HD 720p/1080p+, sddefault = 480p, hqdefault = 360p)
            has_maxres = False
            has_sd = False
            if not is_sd_4x3:
                try:
                    t_req = urllib.request.Request(f"https://i.ytimg.com/vi/{vid}/maxresdefault.jpg", method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(t_req, timeout=2.5) as t_res:
                        if t_res.status == 200:
                            has_maxres = True
                except Exception:
                    pass
            if has_maxres and not is_sd_4x3:
                heights = [1080, 720, 480, 360]
            else:
                try:
                    t_req2 = urllib.request.Request(f"https://i.ytimg.com/vi/{vid}/sddefault.jpg", method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(t_req2, timeout=2.5) as t_res2:
                        if t_res2.status == 200:
                            has_sd = True
                except Exception:
                    pass
                heights = [480, 360] if (has_sd or (og_h >= 480)) else [360]
        max_h = max(heights) if heights else 1080
        yt_watch_title = ""
        m_title = re.search(r'<title>([^<]+)</title>', html)
        if m_title:
            yt_watch_title = m_title.group(1).replace(' - YouTube', '').strip()

        if is_geo_blocked:
            # Strictly cap at 720p maximum for geo-locked / proxy downloads
            max_h = min(max_h, 720)
            has_4k = False
            has_2k = False
            has_1080 = False
            has_720 = max_h >= 720
            heights = [h for h in heights if h <= 720]
        else:
            has_4k = max_h >= 2160 or 2160 in heights
            has_2k = max_h >= 1440 or 1440 in heights
            has_1080 = max_h >= 1080 or 1080 in heights
            has_720 = max_h >= 720 or 720 in heights

        result = {
            "has_4k": has_4k,
            "has_2k": has_2k,
            "has_1080": has_1080,
            "has_720": has_720,
            "max_height": max_h,
            "available_heights": sorted(list(set(heights)), reverse=True),
            "filesizes": {},
            "duration_sec": duration_sec,
            "title": yt_watch_title,
            "is_regional": is_geo_blocked,
            "is_geo_blocked": is_geo_blocked,
            "allowed_countries": allowed_countries,
            "is_unsupported": bool(unsupported_reason),
            "unsupported_reason": unsupported_reason,
            "source": "yt_watch",
        }
        if duration_sec > 0 or unsupported_reason or is_geo_blocked:
            _VIDEO_RES_CACHE[vid] = result
        return result
    except Exception:
        pass

    return {"has_4k": False, "has_2k": False, "max_height": 1080, "duration_sec": duration_sec, "is_regional": False, "is_geo_blocked": False, "source": "default"}


@app.get("/api/download-thumbnail")
async def download_thumbnail(id: str = ""):
    vid = (id or "").strip()
    if not re.match(r"^[a-zA-Z0-9_-]{11}$", vid):
        raise HTTPException(status_code=400, detail="Invalid YouTube video ID")
    for tier in ("maxresdefault", "sddefault", "hqdefault"):
        thumb_url = f"https://i.ytimg.com/vi/{vid}/{tier}.jpg"
        try:
            req = urllib.request.Request(
                thumb_url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130 Safari/537.36"},
            )
            with urllib.request.urlopen(req, timeout=6) as res:
                if res.status == 200:
                    img_bytes = res.read()
                    if len(img_bytes) > 1500:
                        return Response(
                            content=img_bytes,
                            media_type="image/jpeg",
                            headers={
                                "Content-Disposition": f'attachment; filename="YT4MP3-Thumbnail-{vid}-HD.jpg"',
                                "Cache-Control": "public, max-age=86400",
                            },
                        )
        except Exception:
            continue
    return RedirectResponse(url=f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg")


# ==============================================================================
# REAL-TIME VISITOR, DWELL-TIME & 12-HOUR PKT TELEGRAM ANALYTICS SYSTEM
# ==============================================================================
ANALYTICS_TMP_FILE = "/tmp/yt4mp3_analytics.json"
_LAST_CLOUD_SYNC_TS = 0.0

def _default_analytics() -> dict:
    import time
    return {
        "ts": int(time.time()),
        "all_u": 0,
        "all_dl": 0,
        "u": 0,
        "pv": 0,
        "dur_s": 0,
        "dur_n": 0,
        "max_s": 0,
        "dl": 0,
        "mp3": 0,
        "mp4": 0,
        "mob": 0,
        "dsk": 0,
        "c": {}
    }

def _fetch_cloud_analytics() -> dict:
    tg_token = os.environ.get("TELEGRAM_BOT_TOKEN") or "8717205816:AAGdAXIPjaUg986TTJU3n0UFe0wZxfIO3oo"
    if not tg_token:
        return {}
    try:
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{tg_token}/getMyDescription",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=4) as res:
            data = json.loads(res.read().decode("utf-8"))
            desc = (data.get("result") or {}).get("description", "")
            if desc and desc.startswith("YT4MP3_STATS:"):
                raw_json = desc[len("YT4MP3_STATS:"):]
                parsed = json.loads(raw_json)
                if isinstance(parsed, dict):
                    return parsed
    except Exception as e:
        print(f"Cloud analytics fetch notice: {e}")
    return {}

def _merge_analytics(base: dict, incoming: dict) -> dict:
    if not incoming:
        return base
    merged = _default_analytics()
    # If incoming has a newer period reset timestamp, prefer the newer period counters
    base_ts = int(base.get("ts") or 0)
    inc_ts = int(incoming.get("ts") or 0)
    merged["all_u"] = max(int(base.get("all_u") or 0), int(incoming.get("all_u") or 0))
    merged["all_dl"] = max(int(base.get("all_dl") or 0), int(incoming.get("all_dl") or 0))

    if abs(base_ts - inc_ts) <= 60 or base_ts == 0 or inc_ts == 0:
        merged["ts"] = max(base_ts, inc_ts) or merged["ts"]
        for k in ["u", "pv", "dur_s", "dur_n", "max_s", "dl", "mp3", "mp4", "mob", "dsk"]:
            merged[k] = max(int(base.get(k) or 0), int(incoming.get(k) or 0))
        c_merged = {}
        for src in [base.get("c") or {}, incoming.get("c") or {}]:
            if isinstance(src, dict):
                for ck, cv in src.items():
                    c_merged[ck] = max(int(c_merged.get(ck) or 0), int(cv or 0))
        merged["c"] = dict(sorted(c_merged.items(), key=lambda x: x[1], reverse=True)[:6])
    else:
        newer = incoming if inc_ts > base_ts else base
        merged["ts"] = int(newer.get("ts") or merged["ts"])
        for k in ["u", "pv", "dur_s", "dur_n", "max_s", "dl", "mp3", "mp4", "mob", "dsk"]:
            merged[k] = int(newer.get(k) or 0)
        c_new = newer.get("c") if isinstance(newer.get("c"), dict) else {}
        merged["c"] = dict(sorted(c_new.items(), key=lambda x: x[1], reverse=True)[:6])
    return merged

def _load_analytics(force_cloud: bool = False) -> dict:
    local_data = {}
    if os.path.exists(ANALYTICS_TMP_FILE):
        try:
            with open(ANALYTICS_TMP_FILE, "r", encoding="utf-8") as f:
                local_data = json.load(f)
        except Exception:
            local_data = {}

    if not local_data or force_cloud:
        cloud_data = _fetch_cloud_analytics()
        merged = _merge_analytics(local_data or _default_analytics(), cloud_data)
        try:
            with open(ANALYTICS_TMP_FILE, "w", encoding="utf-8") as f:
                json.dump(merged, f, separators=(",", ":"))
        except Exception:
            pass
        return merged

    base = _default_analytics()
    base.update(local_data)
    return base

def _save_analytics(stats: dict, force_cloud: bool = False) -> None:
    global _LAST_CLOUD_SYNC_TS
    import time
    # Keep top 6 countries so compact JSON stays well under 512 chars
    if isinstance(stats.get("c"), dict):
        stats["c"] = dict(sorted(stats["c"].items(), key=lambda x: x[1], reverse=True)[:6])
    else:
        stats["c"] = {}

    try:
        with open(ANALYTICS_TMP_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, separators=(",", ":"))
    except Exception:
        pass

    now = time.time()
    if force_cloud or (now - _LAST_CLOUD_SYNC_TS >= 12.0):
        _LAST_CLOUD_SYNC_TS = now
        tg_token = os.environ.get("TELEGRAM_BOT_TOKEN") or "8717205816:AAGdAXIPjaUg986TTJU3n0UFe0wZxfIO3oo"
        if tg_token:
            try:
                compact = "YT4MP3_STATS:" + json.dumps(stats, separators=(",", ":"))
                if len(compact) <= 512:
                    payload = json.dumps({"description": compact}).encode("utf-8")
                    req = urllib.request.Request(
                        f"https://api.telegram.org/bot{tg_token}/setMyDescription",
                        data=payload,
                        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
                    )
                    urllib.request.urlopen(req, timeout=3).read()
            except Exception as e:
                print(f"Cloud analytics sync notice: {e}")

def _format_duration_human(seconds: float) -> str:
    sec = max(0, int(round(seconds)))
    if sec < 60:
        return f"{sec} sec"
    mins, rem_sec = divmod(sec, 60)
    if mins < 60:
        return f"{mins}m {rem_sec}s"
    hrs, rem_mins = divmod(mins, 60)
    return f"{hrs}h {rem_mins}m {rem_sec}s"

@app.post("/api/analytics-ping")
async def analytics_ping(request: Request):
    try:
        raw_body = await request.body()
        body = json.loads(raw_body.decode("utf-8")) if raw_body else {}
    except Exception:
        body = {}

    event_type = str(body.get("event", "visit")).lower()
    stats = _load_analytics(force_cloud=False)
    ua = request.headers.get("user-agent", "").lower()
    country = (
        request.headers.get("x-vercel-ip-country")
        or request.headers.get("cf-ipcountry")
        or str(body.get("country", ""))
        or "GLB"
    ).upper()[:4]

    force_sync = False
    if event_type == "visit":
        is_new_session = bool(body.get("new_session", True))
        stats["pv"] = int(stats.get("pv", 0)) + 1
        if is_new_session:
            stats["u"] = int(stats.get("u", 0)) + 1
            stats["all_u"] = int(stats.get("all_u", 0)) + 1
            is_mobile = any(m in ua for m in ["mobile", "android", "iphone", "ipad", "ipod"])
            if is_mobile:
                stats["mob"] = int(stats.get("mob", 0)) + 1
            else:
                stats["dsk"] = int(stats.get("dsk", 0)) + 1
            c_map = stats.get("c") if isinstance(stats.get("c"), dict) else {}
            c_map[country] = int(c_map.get(country, 0)) + 1
            stats["c"] = c_map
            force_sync = True

    elif event_type == "duration":
        delta_sec = max(0, min(600, int(body.get("delta_sec", 0) or 0)))
        total_sec = max(0, min(14400, int(body.get("total_sec", 0) or 0)))
        first_ping = bool(body.get("first_ping", False))
        if delta_sec > 0:
            stats["dur_s"] = int(stats.get("dur_s", 0)) + delta_sec
        if first_ping:
            stats["dur_n"] = int(stats.get("dur_n", 0)) + 1
        if total_sec > int(stats.get("max_s", 0)):
            stats["max_s"] = total_sec

    elif event_type == "download":
        fmt = str(body.get("format", "mp3")).lower()
        stats["dl"] = int(stats.get("dl", 0)) + 1
        stats["all_dl"] = int(stats.get("all_dl", 0)) + 1
        if fmt in ["mp3", "m4a", "flac", "wav", "ogg", "opus", "aac"]:
            stats["mp3"] = int(stats.get("mp3", 0)) + 1
        else:
            stats["mp4"] = int(stats.get("mp4", 0)) + 1
        force_sync = True

    _save_analytics(stats, force_cloud=force_sync)
    return {"ok": True}

@app.get("/api/telegram-stats-report")
@app.post("/api/telegram-stats-report")
async def telegram_stats_report(reset: int = 0):
    # 12-hour traffic report disabled per user request; only check FastSaver <= 10k credits alert
    stats = _load_analytics(force_cloud=True)
    fs_status = _check_fastsaver_credits_and_alert(force_check=True, test_alert=False)
    return {
        "success": True,
        "report_disabled": True,
        "stats_snapshot": stats,
        "fastsaver_check": fs_status
    }

FAVICON_SVG_CONTENT = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a" />
      <stop offset="100%" stop-color="#020617" />
    </linearGradient>
    <linearGradient id="roseGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fb7185" />
      <stop offset="50%" stop-color="#f43f5e" />
      <stop offset="100%" stop-color="#e11d48" />
    </linearGradient>
    <linearGradient id="blueGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8" />
      <stop offset="100%" stop-color="#2563eb" />
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#f43f5e" flood-opacity="0.35" />
    </filter>
  </defs>

  <!-- Dark tactile badge background -->
  <rect width="512" height="512" rx="128" fill="url(#bgGrad)" />
  <rect x="8" y="8" width="496" height="496" rx="120" fill="none" stroke="#334155" stroke-width="4" opacity="0.6" />

  <!-- Stylized Fast Play Arrow + Audio Wave combination -->
  <!-- Triangle Play Body with rounded corners -->
  <path d="M168 136 C168 118 188 108 204 118 L386 238 C400 248 400 264 386 274 L204 394 C188 404 168 394 168 376 Z" 
        fill="url(#roseGrad)" filter="url(#glow)" />

  <!-- Modern Inset Dynamic Sound Wavebars inside the play icon -->
  <rect x="220" y="216" width="14" height="80" rx="7" fill="#ffffff" opacity="0.95" />
  <rect x="246" y="186" width="14" height="140" rx="7" fill="#ffffff" opacity="0.95" />
  <rect x="272" y="226" width="14" height="60" rx="7" fill="#ffffff" opacity="0.95" />

  <!-- Subtle Cyan Sound Accent Arc on right -->
  <circle cx="396" cy="180" r="14" fill="url(#blueGrad)" />
  <circle cx="420" cy="220" r="10" fill="url(#blueGrad)" opacity="0.8" />
</svg>"""

@app.get("/favicon.ico")
@app.get("/static/favicon.ico")
async def favicon_ico():
    ico_file = os.path.join(BASE_DIR, "public", "favicon.ico")
    if os.path.exists(ico_file):
        with open(ico_file, "rb") as f:
            return Response(content=f.read(), media_type="image/x-icon", headers=EDGE_HTML_HEADERS)
    return HTMLResponse(content=FAVICON_SVG_CONTENT, media_type="image/svg+xml")

@app.get("/favicon.svg")
@app.get("/static/favicon.svg")
async def favicon():
    return HTMLResponse(content=FAVICON_SVG_CONTENT, media_type="image/svg+xml")

@app.get("/youtube-to-mp3-320kbps")
@app.get("/youtube-to-mp3-320kbps/")
async def youtube_320k_redirect():
    return RedirectResponse(url="/youtube-to-mp3", status_code=301)

@app.get("/tiktok-downloader")
@app.get("/tiktok-downloader/")
@app.get("/instagram-downloader")
@app.get("/instagram-downloader/")
@app.get("/facebook-downloader")
@app.get("/facebook-downloader/")
async def legacy_redirect():
    return RedirectResponse(url="/", status_code=301)

# Localized Routes (14 international languages)
@app.get("/{lang}/contact-us", response_class=HTMLResponse)
@app.get("/{lang}/contact-us/", response_class=HTMLResponse)
async def localized_contact_redirect():
    return RedirectResponse(url="/contact-us", status_code=301)

@app.get("/{lang}/terms-of-service", response_class=HTMLResponse)
@app.get("/{lang}/terms-of-service/", response_class=HTMLResponse)
async def localized_terms_redirect():
    return RedirectResponse(url="/terms-of-service", status_code=301)

@app.get("/{lang}/privacy-policy", response_class=HTMLResponse)
@app.get("/{lang}/privacy-policy/", response_class=HTMLResponse)
async def localized_privacy_redirect():
    return RedirectResponse(url="/privacy-policy", status_code=301)

@app.get("/{lang}", response_class=HTMLResponse)
@app.get("/{lang}/", response_class=HTMLResponse)
async def localized_home_page(request: Request, lang: str):
    lower_lang = lang.lower()
    if lower_lang == "en":
        return RedirectResponse(url="/", status_code=301)
    if lower_lang in SUPPORTED_LANGUAGES and lang != lower_lang:
        return RedirectResponse(url=f"/{lower_lang}/", status_code=301)
    if lang not in SUPPORTED_LANGUAGES:
        clean_id = lang.strip("/")
        if re.match(r'^[a-fA-F0-9-]{16,64}\.txt$', clean_id):
            key_val = clean_id[:-4]
            return Response(content=key_val, media_type="text/plain; charset=utf-8", headers=EDGE_HTML_HEADERS)
        if len(clean_id) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', clean_id):
            return render_shortcut_page(request)
        if clean_id.startswith("4youtube") or clean_id.startswith("watch"):
            return render_shortcut_page(request)
        raise HTTPException(status_code=404, detail="Page not found")
    if not request.url.path.endswith("/"):
        return RedirectResponse(url=f"/{lang}/", status_code=301)
    return render_converter_page(request, "home", lang)

@app.get("/{lang}/youtube-to-mp3", response_class=HTMLResponse)
@app.get("/{lang}/youtube-to-mp3/", response_class=HTMLResponse)
async def localized_youtube_mp3_page(request: Request, lang: str):
    lower_lang = lang.lower()
    if lower_lang == "en":
        return RedirectResponse(url="/youtube-to-mp3", status_code=301)
    if lower_lang in SUPPORTED_LANGUAGES and lang != lower_lang:
        return RedirectResponse(url=f"/{lower_lang}/youtube-to-mp3", status_code=301)
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Page not found")
    if request.url.path.endswith("/"):
        return RedirectResponse(url=f"/{lang}/youtube-to-mp3", status_code=301)
    return render_converter_page(request, "youtube-to-mp3", lang)

@app.get("/{lang}/youtube-to-mp4", response_class=HTMLResponse)
@app.get("/{lang}/youtube-to-mp4/", response_class=HTMLResponse)
async def localized_youtube_mp4_page(request: Request, lang: str):
    lower_lang = lang.lower()
    if lower_lang == "en":
        return RedirectResponse(url="/youtube-to-mp4", status_code=301)
    if lower_lang in SUPPORTED_LANGUAGES and lang != lower_lang:
        return RedirectResponse(url=f"/{lower_lang}/youtube-to-mp4", status_code=301)
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Page not found")
    if request.url.path.endswith("/"):
        return RedirectResponse(url=f"/{lang}/youtube-to-mp4", status_code=301)
    return render_converter_page(request, "youtube-to-mp4", lang)

@app.get("/{lang}/youtube-shorts-downloader", response_class=HTMLResponse)
@app.get("/{lang}/youtube-shorts-downloader/", response_class=HTMLResponse)
async def localized_youtube_shorts_page(request: Request, lang: str):
    lower_lang = lang.lower()
    if lower_lang == "en":
        return RedirectResponse(url="/youtube-shorts-downloader", status_code=301)
    if lower_lang in SUPPORTED_LANGUAGES and lang != lower_lang:
        return RedirectResponse(url=f"/{lower_lang}/youtube-shorts-downloader", status_code=301)
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Page not found")
    if request.url.path.endswith("/"):
        return RedirectResponse(url=f"/{lang}/youtube-shorts-downloader", status_code=301)
    return render_converter_page(request, "youtube-shorts-downloader", lang)

@app.get("/{lang}/blog", response_class=HTMLResponse)
@app.get("/{lang}/blog/", response_class=HTMLResponse)
async def localized_blog_hub_page(request: Request, lang: str):
    lower_lang = lang.lower()
    if lower_lang == "en":
        return RedirectResponse(url="/blog", status_code=301)
    if lower_lang in SUPPORTED_LANGUAGES and lang != lower_lang:
        return RedirectResponse(url=f"/{lower_lang}/blog/", status_code=301)
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Page not found")
    if not request.url.path.endswith("/"):
        return RedirectResponse(url=f"/{lang}/blog/", status_code=301)
    return render_blog_hub(request, lang)

@app.get("/{lang}/blog/{slug}", response_class=HTMLResponse)
@app.get("/{lang}/blog/{slug}/", response_class=HTMLResponse)
async def localized_blog_article_page(request: Request, lang: str, slug: str):
    lower_lang = lang.lower()
    if lower_lang == "en":
        return RedirectResponse(url=f"/blog/{slug}", status_code=301)
    if lower_lang in SUPPORTED_LANGUAGES and lang != lower_lang:
        return RedirectResponse(url=f"/{lower_lang}/blog/{slug}", status_code=301)
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Page not found")
    if request.url.path.endswith("/"):
        return RedirectResponse(url=f"/{lang}/blog/{slug}", status_code=301)
    article = get_article_by_slug(slug, lang)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return render_blog_article(request, slug, lang)


