import os
import re
import xml.etree.ElementTree as ET
import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from app.main import app
from app.i18n import SUPPORTED_LANGUAGES, get_page_content, get_hreflang_links
from app.legal_content import LEGAL_PAGES

client = TestClient(app)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# -------------------------------------------------------------
# 1. Sitemap XML Validation
# -------------------------------------------------------------
def test_sitemap_xml_parsing_and_namespace():
    res = client.get("/sitemap.xml")
    assert res.status_code == 200
    assert "application/xml" in res.headers.get("content-type", "")

    # Parse XML
    root = ET.fromstring(res.text)
    assert root.tag == "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset"


def test_sitemap_contains_exact_78_urls_and_no_duplicates():
    res = client.get("/sitemap.xml")
    root = ET.fromstring(res.text)
    ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = root.findall("ns:url", ns)
    
    # Requirement: 78 URLs (63 core converter + legal pages + 15 multilingual blog hubs)
    assert len(urls) == 78, f"Expected exactly 78 URLs in sitemap, found {len(urls)}"
    
    loc_list = [u.find("ns:loc", ns).text.strip() for u in urls]
    
    # Requirement: No duplicate URLs
    assert len(loc_list) == len(set(loc_list)), "Duplicate URLs detected in sitemap"

    # Requirement: All sitemap URLs use HTTPS and preferred domain
    for loc in loc_list:
        assert loc.startswith("https://www.yt4mp3.com/"), f"Invalid scheme or domain in {loc}"


def test_sitemap_removes_changefreq_and_priority():
    res = client.get("/sitemap.xml")
    root = ET.fromstring(res.text)
    ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = root.findall("ns:url", ns)
    
    for u in urls:
        loc = u.find("ns:loc", ns).text.strip()
        cf = u.find("ns:changefreq", ns)
        pr = u.find("ns:priority", ns)
        assert cf is None, f"Unwanted <changefreq> found in {loc}"
        assert pr is None, f"Unwanted <priority> found in {loc}"


def test_sitemap_valid_distinct_lastmod_dates():
    res = client.get("/sitemap.xml")
    root = ET.fromstring(res.text)
    ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = root.findall("ns:url", ns)
    
    for u in urls:
        loc = u.find("ns:loc", ns).text.strip()
        lm = u.find("ns:lastmod", ns)
        assert lm is not None, f"Missing lastmod in {loc}"
        lastmod = lm.text.strip()
        assert lastmod in ["2026-11-11", "2026-11-12"]

def test_sitemap_has_clean_xsl_stylesheet():
    res = client.get("/sitemap.xml")
    assert res.status_code == 200
    assert '<?xml-stylesheet type="text/xsl" href="/sitemap.xsl"?>' in res.text

    # Verify sitemap.xsl route is accessible and valid
    xsl_res = client.get("/sitemap.xsl")
    assert xsl_res.status_code == 200
    assert "text/xsl" in xsl_res.headers.get("content-type", "")
    assert "<xsl:stylesheet" in xsl_res.text
    assert "XML Sitemap" in xsl_res.text


# -------------------------------------------------------------
# 2. RSS Feed XML Validation
# -------------------------------------------------------------
def test_rss_xml_parsing_and_structure():
    res = client.get("/feed.xml")
    assert res.status_code == 200
    assert ("application/rss+xml" in res.headers.get("content-type", "") or 
            "application/xml" in res.headers.get("content-type", ""))

    root = ET.fromstring(res.text)
    assert root.tag == "rss"
    assert root.attrib.get("version") == "2.0"

    channel = root.find("channel")
    assert channel is not None
    assert channel.find("title").text == "YT4MP3 - YouTube Media Converter Tools & Updates"
    assert channel.find("link").text == "https://www.yt4mp3.com/"
    assert "converting YouTube videos to MP3 and MP4" in channel.find("description").text
    assert channel.find("language").text == "en-us"
    assert "11 Nov 2026" in channel.find("lastBuildDate").text


def test_rss_feed_contains_60_items_with_stable_guids_and_3_month_dates():
    res = client.get("/feed.xml")
    root = ET.fromstring(res.text)
    channel = root.find("channel")
    items = channel.findall("item")

    # Exactly 60 items (15 languages * 4 tools)
    assert len(items) == 60, f"Expected 60 RSS feed items, found {len(items)}"

    guids = set()
    links = set()
    found_months = set()
    
    for item in items:
        link = item.find("link").text.strip()
        guid = item.find("guid").text.strip()
        title = item.find("title").text.strip()
        desc = item.find("description").text.strip()
        pub_date = item.find("pubDate").text.strip()

        assert link.startswith("https://www.yt4mp3.com/"), f"Invalid link: {link}"
        assert guid == link, f"GUID is not stable permalink for {link}"
        assert title, f"Empty title in {link}"
        assert desc, f"Empty description in {link}"
        assert pub_date, f"Empty pubDate in {link}"

        # Verify dates span the last 3 months
        parsed_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S +0000")
        found_months.add(parsed_date.strftime("%b %Y"))

        assert "Cepat, cepat" not in desc, f"Repeated words 'Cepat, cepat' found in {link}"

        guids.add(guid)
        links.add(link)

    assert len(guids) == 60, "Duplicate GUIDs found in feed"
    assert len(links) == 60, "Duplicate links found in feed"
    
    # Must contain dates spanning the last 3 months (Aug, Sep, Oct, Nov 2026)
    expected_months = {"Aug 2026", "Sep 2026", "Oct 2026", "Nov 2026"}
    assert found_months == expected_months, f"Expected {expected_months}, got {found_months}"


def test_rss_dates_stable_and_not_dynamically_changing():
    res1 = client.get("/feed.xml")
    res2 = client.get("/feed.xml")
    
    # Exact byte comparison to prove dates do not change on every request
    assert res1.text == res2.text, "RSS feed content changes dynamically across requests!"


# -------------------------------------------------------------
# 3. Multilingual Hreflang and Canonical SEO
# -------------------------------------------------------------
def test_all_15_languages_and_burmese():
    expected_langs = {'en', 'ar', 'de', 'es', 'fr', 'hi', 'id', 'it', 'ja', 'ko', 'pt', 'ru', 'tr', 'vi', 'my'}
    assert set(SUPPORTED_LANGUAGES.keys()) == expected_langs
    assert len(SUPPORTED_LANGUAGES) == 15
    assert SUPPORTED_LANGUAGES['my']['name'] == 'Burmese'
    assert SUPPORTED_LANGUAGES['my']['native'] == 'မြန်မာစာ'


def test_hreflang_groups_complete_and_reciprocal():
    """
    Every tool/homepage across all 15 languages must have:
    - 16 alternate links (x-default + 15 supported languages)
    - Fully reciprocal relationships (Group A page has same set of hreflangs as Group B page)
    - Self-referencing hreflang matching the canonical URL
    """
    page_keys = ["home", "youtube-to-mp3", "youtube-to-mp4", "youtube-shorts-downloader"]

    for pk in page_keys:
        expected_hreflangs = get_hreflang_links(pk)
        assert len(expected_hreflangs) == 16  # 15 languages + 1 x-default
        
        # Verify x-default points to English
        x_default = [h for h in expected_hreflangs if h['lang'] == 'x-default'][0]
        en_version = [h for h in expected_hreflangs if h['lang'] == 'en'][0]
        assert x_default['url'] == en_version['url']
        
        # Verify each language page renders the reciprocal hreflangs in HTML
        for lang in SUPPORTED_LANGUAGES:
            if lang == "en":
                url_path = "/" if pk == "home" else f"/{pk}"
            else:
                url_path = f"/{lang}/" if pk == "home" else f"/{lang}/{pk}"
            
            res = client.get(url_path)
            assert res.status_code == 200, f"Failed loading {url_path}"
            html = res.text

            # Check self-referencing canonical
            expected_canonical = f"https://www.yt4mp3.com{url_path}"
            assert f'<link rel="canonical" href="{expected_canonical}">' in html, \
                f"Canonical mismatch on {url_path}"

            # Check reciprocal hreflangs exist on this page
            for h in expected_hreflangs:
                tag = f'<link rel="alternate" hreflang="{h["lang"]}" href="{h["url"]}">'
                assert tag in html, f"Missing hreflang tag {tag} on page {url_path}"


# -------------------------------------------------------------
# 4. Robots.txt Validation
# -------------------------------------------------------------
def test_robots_txt_spec():
    res = client.get("/robots.txt")
    assert res.status_code == 200
    assert "text/plain" in res.headers.get("content-type", "")

    content = res.text
    assert "Sitemap: https://www.yt4mp3.com/sitemap.xml" in content
    assert "Allow: /" in content
    assert "Disallow: /api/" in content
    assert "Disallow: /watch" in content
    assert "Disallow: /shorts/" in content
    assert "Disallow: /*?s=" in content
    assert "Disallow: /*&s=" in content
    assert "Disallow: /*?q=" in content
    assert "Disallow: /*?ref=" in content
    assert "Disallow: /*?*s=" not in content
    # Ensure important language paths are NOT disallowed
    for lang in SUPPORTED_LANGUAGES:
        assert f"Disallow: /{lang}" not in content


def test_sitemap_xhtml_hreflang_links():
    res = client.get("/sitemap.xml")
    assert res.status_code == 200
    root = ET.fromstring(res.text)
    ns = {
        "ns": "http://www.sitemaps.org/schemas/sitemap/0.9",
        "xhtml": "http://www.w3.org/1999/xhtml",
    }
    urls = root.findall("ns:url", ns)
    localized_count = 0
    for u in urls:
        loc = u.find("ns:loc", ns).text.strip()
        if any(legal in loc for legal in ["contact-us", "terms-of-service", "privacy-policy"]):
            continue
        localized_count += 1
        xhtml_links = u.findall("xhtml:link", ns)
        assert len(xhtml_links) == 16, f"Expected 16 xhtml:link hreflang tags in {loc}, found {len(xhtml_links)}"
        langs = {xl.attrib.get("hreflang") for xl in xhtml_links}
        assert "x-default" in langs
        assert "en" in langs
        assert "es" in langs
    assert localized_count == 75


def test_shortcut_routes_noindex_and_no_spam():
    for path in ["/watch?v=dQw4w9WgXcQ", "/shorts/dQw4w9WgXcQ"]:
        res = client.get(path)
        assert res.status_code == 200
        assert "noindex" in res.headers.get("x-robots-tag", "").lower()
        assert '<meta name="robots" content="noindex, nofollow">' in res.text

    # Verify Spanish page has localized og:locale, og:image:alt, UI strings, and zero keyword stuffing
    res_es = client.get("/es/")
    assert res_es.status_code == 200
    html_es = res_es.text
    assert '<meta property="og:locale" content="es_ES">' in html_es
    assert "Fetching available MP3" not in html_es
    assert ">Simple Process<" not in html_es
    assert ">Utility<" not in html_es
    assert ">Questions<" not in html_es
    assert ">Service Status: Online<" not in html_es
    assert "descargar mp3 de youtube --" not in html_es
    assert "yo a mp3" not in html_es

    # Verify English home page has zero keyword stuffing and no soft-404 error text
    res_en = client.get("/")
    html_en = res_en.text
    for bad in ["youtube downlader", "yt downlaoder", "youtibe downloader", "youtube to m[3", "sss.fb", "yotuube to mp", "Unable to fetch video information."]:
        assert bad not in html_en, f"Found banned phrase '{bad}' on homepage!"


# -------------------------------------------------------------
# 5. Technical Indexing & Status 200 for all 78 URLs
# -------------------------------------------------------------
def test_all_78_sitemap_urls_accessible_and_indexable():
    res = client.get("/sitemap.xml")
    root = ET.fromstring(res.text)
    ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [u.find("ns:loc", ns).text.strip() for u in root.findall("ns:url", ns)]

    assert len(urls) == 78

    for url in urls:
        path = url.replace("https://www.yt4mp3.com", "")
        if not path:
            path = "/"
        res_page = client.get(path)
        assert res_page.status_code == 200, f"URL {url} returned {res_page.status_code}"
        
        # Verify page is indexable (not noindex)
        assert "noindex" not in res_page.headers.get("x-robots-tag", "").lower(), \
            f"X-Robots-Tag noindex on public page {url}"
        
        html = res_page.text
        # Verify meta robots allows indexing
        assert '<meta name="robots" content="index, follow' in html, \
            f"Meta robots does not allow index on {url}"


# -------------------------------------------------------------
# 6. Converter Functionality Preservation
# -------------------------------------------------------------
def test_converter_ui_and_scripts_preserved():
    res = client.get("/")
    assert res.status_code == 200
    html = res.text
    
    # Form / input preservation
    assert 'id="urlInput"' in html or 'name="url"' in html or 'placeholder=' in html
    # FastSaver / converter engine script preservation
    assert 'convert_btn' in html or 'Convert' in html
    # Language switcher dropdown preservation
    assert 'class="language-selector' in html or 'id="langSelect' in html or 'href="/es/"' in html


# -------------------------------------------------------------
# 7. Canonical Domain Host 301 Redirect Tests (SEO Duplicate Host Protection)
# -------------------------------------------------------------
def test_non_www_to_www_301_redirect():
    # Test FastAPI application level middleware
    test_client = TestClient(app, follow_redirects=False)
    
    # 1. Root path on non-www
    r1 = test_client.get("/", headers={"Host": "yt4mp3.com"})
    assert r1.status_code == 301
    assert r1.headers.get("location") == "https://www.yt4mp3.com/"
    
    # 2. Sub-path on non-www
    r2 = test_client.get("/youtube-to-mp3", headers={"Host": "yt4mp3.com"})
    assert r2.status_code == 301
    assert r2.headers.get("location") == "https://www.yt4mp3.com/youtube-to-mp3"
    
    # 3. Canonical www domain serves 200 OK
    r3 = test_client.get("/", headers={"Host": "www.yt4mp3.com"})
    assert r3.status_code == 200
    
    # 4. Verify vercel.json has top-priority Edge 301 redirect rule
    import json
    with open("vercel.json", "r") as f:
        vcfg = json.load(f)
    routes = vcfg.get("routes", [])
    assert len(routes) > 0
    top_route = routes[0]
    assert top_route.get("status") == 301
    assert top_route.get("has", [{}])[0].get("value") == "yt4mp3.com"
    assert top_route.get("headers", {}).get("Location") == "https://www.yt4mp3.com/$1"


# -------------------------------------------------------------
# 8. Multilingual Blog Hub Tests
# -------------------------------------------------------------
def test_blog_hub_english():
    res = client.get("/blog")
    assert res.status_code == 200
    html = res.text
    assert "<title>YT4MP3 Blog" in html
    assert 'rel="canonical" href="https://www.yt4mp3.com/blog"' in html
    assert 'dir="ltr"' in html
    assert 'lang="en"' in html
    assert "Editorial Guides Coming Soon" in html
    # Check all 16 reciprocal hreflangs
    assert 'hreflang="x-default"' in html
    assert 'hreflang="en"' in html
    assert 'hreflang="ar" href="https://www.yt4mp3.com/ar/blog/"' in html
    assert html.count("hreflang=") == 16


def test_blog_hub_arabic_rtl():
    res = client.get("/ar/blog/")
    assert res.status_code == 200
    html = res.text
    assert "مدونة YT4MP3" in html
    assert 'rel="canonical" href="https://www.yt4mp3.com/ar/blog/"' in html
    assert 'dir="rtl"' in html
    assert 'lang="ar"' in html
    assert "المقالات والأدلة قادمة قريباً" in html
    assert html.count("hreflang=") == 16


def test_blog_redirects():
    test_client = TestClient(app, follow_redirects=False)
    
    # English trailing slash redirect
    r1 = test_client.get("/blog/")
    assert r1.status_code == 301
    assert r1.headers.get("location") == "/blog"
    
    # Localized non-trailing slash redirect
    r2 = test_client.get("/ar/blog")
    assert r2.status_code == 301
    assert r2.headers.get("location") == "/ar/blog/"
    
    # Uppercase or invalid language
    r3 = test_client.get("/AR/blog/")
    assert r3.status_code == 301
    assert r3.headers.get("location") == "/ar/blog/"


