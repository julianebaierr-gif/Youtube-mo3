import importlib, os, pprint, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# Clean neutral replacements per language for competitor comparison headings, table headers, paragraphs, and watermark anchor IDs
PER_LANG = {
    "ar": [
        ("YT4MP3 مقابل ShortsNoob وSaveFrom وPubler", "YT4MP3 مقابل المحولات الأخرى عبر الإنترنت"),
        ("<th>ShortsNoob</th>\n<th>SaveFrom / SSYouTube</th>\n<th>Publer Downloader</th>", "<th>أدوات الويب التقليدية</th>\n<th>المواقع المليئة بالإعلانات</th>\n<th>الأدوات التي تتطلب حساباً</th>"),
        ("تضع مواقع مثل <strong>Savefrom</strong> و<strong>ShortsNoob</strong> المستخدم في مواجهة إشعارات مضللة ونوافذ إعلانية منبثقة. ويشترط موقع Publer إنشاء حساب مسبق.", "تضع العديد من مواقع التحويل التقليدية المستخدم في مواجهة إشعارات مضللة ونوافذ منبثقة، بينما تشترط أدوات أخرى إنشاء حساب مسبق."),
    ],
    "de": [
        ("YT4MP3 vs ShortsNoob vs SaveFrom vs Publer", "YT4MP3 im Vergleich zu anderen Web-Konvertern"),
        ("<th>ShortsNoob</th>\n<th>SaveFrom / SSYouTube</th>\n<th>Publer Downloader</th>", "<th>Einfache Web-Tools</th>\n<th>Werbelastige Portale</th>\n<th>Tools mit Kontopflicht</th>"),
        ("Portale wie <strong>Savefrom</strong> oder <strong>ShortsNoob</strong> belasten Nutzer nicht selten mit zweifelhaften Warnmeldungen. Publer setzt dagegen auf ein Pflichtkonto mit E-Mail-Adresse.", "Viele herkömmliche Web-Portale belasten Nutzer mit irreführenden Meldungen oder setzen ein Pflichtkonto mit E-Mail-Adresse voraus."),
    ],
    "es": [
        ("YT4MP3 vs ShortsNoob vs SaveFrom vs Publer", "YT4MP3 frente a otros convertidores en línea"),
        ("<th>ShortsNoob</th>\n<th>SaveFrom / SSYouTube</th>\n<th>Publer Downloader</th>", "<th>Herramientas web básicas</th>\n<th>Sitios con ventanas emergentes</th>\n<th>Servicios con registro</th>"),
        ("Servicios como <strong>Savefrom</strong> o <strong>ShortsNoob</strong> obligan en ocasiones a evitar ventanas emergentes molestas o notificaciones no deseadas. Por otro lado, aplicaciones corporativas como Publer imponen registros obligatorios.", "Muchos convertidores tradicionales obligan a esquivar ventanas emergentes molestas o exigen crear una cuenta obligatoria antes de descargar."),
    ],
    "fr": [
        ("YT4MP3 vs ShortsNoob vs SaveFrom vs Publer", "YT4MP3 face aux autres convertisseurs en ligne"),
        ("<th>ShortsNoob</th>\n<th>SaveFrom / SSYouTube</th>\n<th>Publer Downloader</th>", "<th>Outils web classiques</th>\n<th>Sites surchargés de pop-ups</th>\n<th>Outils avec compte requis</th>"),
        ("Des sites comme <strong>Savefrom</strong> ou <strong>ShortsNoob</strong> obligent souvent à esquiver de fausses alertes système ou des autorisations de notifications indésirables. Publer impose quant à lui un formulaire de création de compte.", "De nombreux convertisseurs web imposent de contourner des fenêtres intrusives ou demandent la création d'un compte avant toute conversion."),
    ],
    "hi": [
        ("no-watermark-quality-hi", "clean-original-quality-hi"),
    ],
    "id": [
        ("YT4MP3 vs ShortsNoob vs SaveFrom vs Publer", "YT4MP3 vs Konverter Online Lainnya"),
        ("<th>ShortsNoob</th>\n<th>SaveFrom / SSYouTube</th>\n<th>Publer Downloader</th>", "<th>Konverter Web Standar</th>\n<th>Situs Penuh Pop-up</th>\n<th>Layanan Wajib Akun</th>"),
        ("Situs seperti <strong>Savefrom</strong> dan <strong>ShortsNoob</strong> kerap menampilkan notifikasi jebakan yang mengganggu kenyamanan berselancar. Sementara Publer mewajibkan pengisian data akun.", "Banyak situs konverter konvensional menampilkan notifikasi mengganggu atau mewajibkan pendaftaran akun terlebih dahulu."),
        ("jaminan-tanpa-watermark-id", "kualitas-bersih-asli-id"),
    ],
    "it": [
        ("file-senza-watermark-it", "file-puliti-originali-it"),
    ],
    "ja": [
        ("YT4MP3 vs ShortsNoob vs SaveFrom vs Publer", "YT4MP3と一般的なオンライン変換ツールの比較"),
        ("<th>ShortsNoob</th>\n<th>SaveFrom / SSYouTube</th>\n<th>Publer Downloader</th>", "<th>一般的なWebツール</th>\n<th>ポップアップが多いサイト</th>\n<th>登録必須のツール</th>"),
        ("<strong>Savefrom</strong>や<strong>ShortsNoob</strong>では、迷惑なポップアップバナー広告や、不要な通知の許可を迫られるトラブルが後を絶ちません。またPublerはメールアドレス登録が必要です。", "従来の変換サイトの中には、不要な通知の許可を求めたり、メールアドレス登録を必要とするサービスも少なくありません。"),
    ],
    "ko": [
        ("YT4MP3 vs ShortsNoob vs SaveFrom vs Publer", "YT4MP3와 일반 온라인 변환 도구 비교"),
        ("<th>ShortsNoob</th>\n<th>SaveFrom / SSYouTube</th>\n<th>Publer Downloader</th>", "<th>일반 웹 변환기</th>\n<th>팝업이 많은 사이트</th>\n<th>계정 등록 필요 도구</th>"),
        ("watermark-eopneun-clean-video-ko", "clean-original-video-ko"),
    ],
    "tr": [
        ("YT4MP3 vs ShortsNoob vs SaveFrom vs Publer", "YT4MP3 ve Diğer Çevrimiçi Dönüştürücüler"),
        ("<th>ShortsNoob</th>\n<th>SaveFrom / SSYouTube</th>\n<th>Publer Downloader</th>", "<th>Standart Web Araçları</th>\n<th>Açılır Pencereli Siteler</th>\n<th>Üyelik Gerektiren Araçlar</th>"),
        ("<strong>Savefrom</strong> ve <strong>ShortsNoob</strong> gibi siteler kullanıcıları sık sık aldatıcı uyarılarla karşı karşıya bırakır. Publer ise zorunlu kayıt şartı koşar.", "Birçok geleneksel dönüştürücü sitesi kullanıcıları aldatıcı uyarılarla karşı karşıya bırakır veya zorunlu kayıt şartı koşar."),
    ],
    "vi": [
        ("YT4MP3 vs ShortsNoob vs SaveFrom vs Publer", "YT4MP3 so với các công cụ chuyển đổi trực tuyến khác"),
        ("<th>ShortsNoob</th>\n<th>SaveFrom / SSYouTube</th>\n<th>Publer Downloader</th>", "<th>Công cụ web thông thường</th>\n<th>Trang nhiều cửa sổ bật lên</th>\n<th>Công cụ yêu cầu tài khoản</th>"),
        ("Các trang như <strong>Savefrom</strong> hay <strong>ShortsNoob</strong> thường khiến người dùng phiền lòng bởi những cửa sổ quảng cáo bật lên. Trong khi đó Publer lại đòi hỏi khai báo tài khoản cá nhân.", "Nhiều trang chuyển đổi thông thường thường gây phiền toái với cửa sổ bật lên hoặc yêu cầu đăng ký tài khoản cá nhân."),
    ],
}

COMP_RE = re.compile(r"(savefrom|publer|shortsnoob|y2mate|ssyoutube|snappea)", re.I)

def clean_obj(obj, repls):
    if isinstance(obj, dict):
        return {k: clean_obj(v, repls) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_obj(v, repls) for v in obj]
    if isinstance(obj, str):
        for a, b in repls:
            obj = obj.replace(a, b)
        return obj
    return obj

def clean_kw(obj):
    if isinstance(obj, dict):
        return {k: clean_kw(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [x for x in obj if not (isinstance(x, str) and COMP_RE.search(x))]
    return obj

for lang in sorted(PER_LANG.keys()):
    mod = importlib.import_module(f"app.locales.{lang}")
    kw = clean_kw(mod.KEYWORDS_RESEARCH)
    pages = clean_obj(mod.PAGES, PER_LANG[lang])
    ui = clean_obj(mod.UI, PER_LANG[lang])
    out = (
        "# -*- coding: utf-8 -*-\n\n"
        + "KEYWORDS_RESEARCH = " + pprint.pformat(kw, width=120) + "\n\n"
        + "PAGES = " + pprint.pformat(pages, width=120) + "\n\n"
        + "UI = " + pprint.pformat(ui, width=120) + "\n"
    )
    path = os.path.join(ROOT, "app", "locales", f"{lang}.py")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    print(f"cleaned {lang}")
