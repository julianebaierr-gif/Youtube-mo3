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
    'nav_shorts': 'YouTube Shorts',
    'paste_placeholder': 'Paste YouTube video, Shorts, or Music URL here...',
    'quick_convert': 'Quick Convert',
    'select_format': 'Select Format & Quality',
    'step1_desc': 'Find your favorite video on YouTube, click Share, and copy the video URL.',
    'step1_title': 'Copy Video Link',
    'step2_desc': 'Paste the link into the converter box above and choose MP3 audio (up to 320kbps) or MP4 video (up to 4K).',
    'step2_title': 'Paste & Select Format',
    'step3_desc': 'Click Convert, wait a few seconds for the cloud server to prepare the file, and download directly to your device.',
    'step3_title': 'Download File',
    'comp_badge': 'Comparison',
    'comp_title': 'YT4MP3 vs. Other Converters',
    'comp_subtitle': 'See why millions choose YT4MP3 over slow, ad-heavy converter tools.',
    'comp_feature_col': 'Feature & Capability',
    'comp_yt4mp3_col': 'YT4MP3 (Recommended)',
    'comp_others_col': 'Other Converters',
    'comp_row1_title': 'Account & Sign-up',
    'comp_row1_yt4mp3': '100% Free, No Sign-up / No Credit Card',
    'comp_row1_others': 'Forced registration, paywalls, or spam newsletters',
    'comp_row2_title': 'Speed & Download Limits',
    'comp_row2_yt4mp3': 'Instant real-time conversion & direct download',
    'comp_row2_others': 'Long waiting queues, artificial throttling & timers',
    'comp_row3_title': 'Audio & Video Quality',
    'comp_row3_yt4mp3': 'Genuine 320 kbps MP3 & 1080p/4K MP4 with synced audio',
    'comp_row3_others': 'Capped at compressed 128 kbps or low 360p resolution',
    'comp_row4_title': 'Annoying Ads & Redirects',
    'comp_row4_yt4mp3': 'Clean & safe: Zero pop-unders, no fake download buttons',
    'comp_row4_others': 'Spammy redirects, intrusive popups & malware traps',
    'comp_row5_title': 'Device & Mobile Support',
    'comp_row5_yt4mp3': 'Seamless on iPhone Safari, Android Chrome, Mac & Windows',
    'comp_row5_others': 'Often breaks on iOS Safari or requires APK apps',
    'comp_row6_title': 'Shorts & Long Podcasts',
    'comp_row6_yt4mp3': 'Full support for Shorts, DJ sets & 2hr+ audiobooks',
    'comp_row6_others': 'Strict 10-20 min limit; cannot parse Shorts URLs',
    'benefits_badge': 'Key Advantages',
    'benefits_title': 'Why Convert YouTube Videos to MP3?',
    'benefits_subtitle': 'Free your favorite audio from online restrictions and enjoy offline freedom.',
    'benefit1_title': 'Offline Playback Anywhere',
    'benefit1_desc': 'Listen on airplanes, underground transit, or road trips without Wi-Fi or wasting mobile data.',
    'benefit2_title': 'Save Battery & Mobile Data',
    'benefit2_desc': 'Audio uses up to 90% less battery and zero streaming bandwidth compared to video playback.',
    'benefit3_title': 'Background Audio Playback',
    'benefit3_desc': 'Keep listening with your phone screen locked or while using other apps without paying for subscriptions.',
    'benefit4_title': 'Shorts, Podcasts & Long Mixes',
    'benefit4_desc': 'Extract clean sound from viral Shorts clips, educational lectures, and multi-hour DJ sets.',
    'shortcut_title': 'Viral URL Shortcut Trick: Direct Download',
    'shortcut_badge': 'No Copy-Paste Needed',
    'shortcut_guide_prefix': 'When watching a video on YouTube, simply replace',
    'shortcut_guide_suffix': 'with',
    'shortcut_guide_end': 'in your browser address bar and press Enter:',
    'shortcut_before': 'Before:',
    'shortcut_after': 'After:',
    'shortcut_test_btn': 'Test Trick',
    'shortcut_shorts_note': 'Also supports YouTube Shorts:',
    'shortcut_instant_note': 'Instant auto-download starts automatically!',
    'pwa_install_btn': 'Install App',
    'pwa_install_short': 'App',
    'pwa_banner_title': 'Install YT4MP3 App',
    'pwa_banner_desc': '1-Tap YouTube Downloader on Home Screen',
    'pwa_banner_install': 'Install',
    'pwa_ios_title': 'Install YT4MP3 on iPhone',
    'pwa_ios_desc': 'Add to Home Screen for lightning fast 1-tap downloads:',
    'pwa_ios_step1': 'Tap the Share button in Safari bottom bar.',
    'pwa_ios_step2': "Scroll down and select 'Add to Home Screen'.",
    'pwa_ios_step3': "Tap 'Add' in the top right corner. Done!",
    'pwa_ios_btn': 'Got it!',
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


SHORTCUT_AND_PWA_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'es': {
        'shortcut_title': 'Truco de Atajo Viral de URL: Descarga Directa',
        'shortcut_badge': 'Sin Copiar y Pegar',
        'shortcut_guide_prefix': 'Al mirar un video en YouTube, simplemente reemplaza',
        'shortcut_guide_suffix': 'por',
        'shortcut_guide_end': 'en la barra de direcciones de tu navegador y presiona Enter:',
        'shortcut_before': 'Antes:',
        'shortcut_after': 'Después:',
        'shortcut_test_btn': 'Probar Truco',
        'shortcut_shorts_note': 'También compatible con YouTube Shorts:',
        'shortcut_instant_note': '¡La descarga automática comienza al instante!',
        'pwa_install_btn': 'Instalar App',
        'pwa_install_short': 'App',
        'pwa_banner_title': 'Instalar aplicación YT4MP3',
        'pwa_banner_desc': 'Descargador de YouTube en 1 toque en tu pantalla de inicio',
        'pwa_banner_install': 'Instalar',
        'pwa_ios_title': 'Instalar YT4MP3 en iPhone',
        'pwa_ios_desc': 'Añade a la pantalla de inicio para descargas ultrarrápidas en 1 toque:',
        'pwa_ios_step1': 'Toca el botón Compartir en la barra inferior de Safari.',
        'pwa_ios_step2': "Desplázate hacia abajo y selecciona 'Añadir a pantalla de inicio'.",
        'pwa_ios_step3': "Toca 'Añadir' en la esquina superior derecha. ¡Listo!",
        'pwa_ios_btn': '¡Entendido!'
    },
    'id': {
        'shortcut_title': 'Trik Pintasan URL Viral: Unduh Langsung',
        'shortcut_badge': 'Tanpa Perlu Salin-Tempel',
        'shortcut_guide_prefix': 'Saat menonton video di YouTube, cukup ganti',
        'shortcut_guide_suffix': 'dengan',
        'shortcut_guide_end': 'di bilah alamat browser Anda dan tekan Enter:',
        'shortcut_before': 'Sebelum:',
        'shortcut_after': 'Sesudah:',
        'shortcut_test_btn': 'Coba Trik',
        'shortcut_shorts_note': 'Juga mendukung YouTube Shorts:',
        'shortcut_instant_note': 'Pengunduhan otomatis langsung dimulai!',
        'pwa_install_btn': 'Pasang Aplikasi',
        'pwa_install_short': 'Aplikasi',
        'pwa_banner_title': 'Pasang Aplikasi YT4MP3',
        'pwa_banner_desc': 'Pengunduh YouTube 1-Ketuk di Layar Utama',
        'pwa_banner_install': 'Pasang',
        'pwa_ios_title': 'Pasang YT4MP3 di iPhone',
        'pwa_ios_desc': 'Tambahkan ke Layar Utama untuk unduhan super cepat 1-ketukan:',
        'pwa_ios_step1': 'Ketuk tombol Bagikan di bilah bawah Safari.',
        'pwa_ios_step2': "Gulir ke bawah dan pilih 'Tambahkan ke Layar Utama'.",
        'pwa_ios_step3': "Ketuk 'Tambah' di sudut kanan atas. Selesai!",
        'pwa_ios_btn': 'Mengerti!'
    },
    'pt': {
        'shortcut_title': 'Truque de Atalho Viral de URL: Download Direto',
        'shortcut_badge': 'Sem Copiar e Colar',
        'shortcut_guide_prefix': 'Ao assistir a um vídeo no YouTube, basta substituir',
        'shortcut_guide_suffix': 'por',
        'shortcut_guide_end': 'na barra de endereços do seu navegador e pressionar Enter:',
        'shortcut_before': 'Antes:',
        'shortcut_after': 'Depois:',
        'shortcut_test_btn': 'Testar Truque',
        'shortcut_shorts_note': 'Também suporta YouTube Shorts:',
        'shortcut_instant_note': 'O download automático começa instantaneamente!',
        'pwa_install_btn': 'Instalar App',
        'pwa_install_short': 'App',
        'pwa_banner_title': 'Instalar Aplicativo YT4MP3',
        'pwa_banner_desc': 'Baixador do YouTube em 1 toque na tela inicial',
        'pwa_banner_install': 'Instalar',
        'pwa_ios_title': 'Instalar YT4MP3 no iPhone',
        'pwa_ios_desc': 'Adicione à Tela Inicial para downloads super rápidos em 1 toque:',
        'pwa_ios_step1': 'Toque no botão Compartilhar na barra inferior do Safari.',
        'pwa_ios_step2': "Role para baixo e selecione 'Adicionar à Tela de Início'.",
        'pwa_ios_step3': "Toque em 'Adicionar' no canto superior direito. Concluído!",
        'pwa_ios_btn': 'Entendi!'
    },
    'fr': {
        'shortcut_title': 'Astuce Raccourci URL Viral : Téléchargement Direct',
        'shortcut_badge': 'Sans Copier-Coller',
        'shortcut_guide_prefix': 'Lorsque vous regardez une vidéo sur YouTube, remplacez simplement',
        'shortcut_guide_suffix': 'par',
        'shortcut_guide_end': "dans la barre d'adresse de votre navigateur et appuyez sur Entrée :",
        'shortcut_before': 'Avant :',
        'shortcut_after': 'Après :',
        'shortcut_test_btn': "Tester l'astuce",
        'shortcut_shorts_note': 'Prend également en charge YouTube Shorts :',
        'shortcut_instant_note': 'Le téléchargement automatique démarre instantanément !',
        'pwa_install_btn': "Installer l'app",
        'pwa_install_short': 'App',
        'pwa_banner_title': "Installer l'application YT4MP3",
        'pwa_banner_desc': "Téléchargeur YouTube en 1 clic sur l'écran d'accueil",
        'pwa_banner_install': 'Installer',
        'pwa_ios_title': 'Installer YT4MP3 sur iPhone',
        'pwa_ios_desc': "Ajoutez à l'écran d'accueil pour des téléchargements ultra-rapides en 1 clic :",
        'pwa_ios_step1': 'Appuyez sur le bouton Partager dans la barre inférieure de Safari.',
        'pwa_ios_step2': "Faites défiler vers le bas et sélectionnez 'Sur l\'écran d\'accueil'.",
        'pwa_ios_step3': "Appuyez sur 'Ajouter' dans le coin supérieur droit. Terminé !",
        'pwa_ios_btn': 'Compris !'
    },
    'de': {
        'shortcut_title': 'Viraler URL-Kurzbefehl-Trick: Direkter Download',
        'shortcut_badge': 'Kein Kopieren nötig',
        'shortcut_guide_prefix': 'Wenn Sie ein Video auf YouTube ansehen, ersetzen Sie einfach',
        'shortcut_guide_suffix': 'durch',
        'shortcut_guide_end': 'in Ihrer Browser-Adressleiste und drücken Sie die Eingabetaste:',
        'shortcut_before': 'Vorher:',
        'shortcut_after': 'Nachher:',
        'shortcut_test_btn': 'Trick testen',
        'shortcut_shorts_note': 'Unterstützt auch YouTube Shorts:',
        'shortcut_instant_note': 'Der automatische Download startet sofort!',
        'pwa_install_btn': 'App installieren',
        'pwa_install_short': 'App',
        'pwa_banner_title': 'YT4MP3 App installieren',
        'pwa_banner_desc': '1-Klick YouTube Downloader auf dem Startbildschirm',
        'pwa_banner_install': 'Installieren',
        'pwa_ios_title': 'YT4MP3 auf dem iPhone installieren',
        'pwa_ios_desc': 'Zum Home-Bildschirm hinzufügen für blitzschnelle 1-Klick-Downloads:',
        'pwa_ios_step1': 'Tippen Sie auf die Teilen-Schaltfläche in der unteren Safari-Leiste.',
        'pwa_ios_step2': "Scrollen Sie nach unten und wählen Sie 'Zum Home-Bildschirm'.",
        'pwa_ios_step3': "Tippen Sie oben rechts auf 'Hinzufügen'. Fertig!",
        'pwa_ios_btn': 'Verstanden!'
    },
    'tr': {
        'shortcut_title': 'Viral URL Kısayol Hilesi: Doğrudan İndirme',
        'shortcut_badge': 'Kopyala-Yapıştır Gerekmez',
        'shortcut_guide_prefix': "YouTube'da bir video izlerken adres çubuğunda",
        'shortcut_guide_suffix': 'yerine',
        'shortcut_guide_end': "yazın ve Enter'a basın:",
        'shortcut_before': 'Önce:',
        'shortcut_after': 'Sonra:',
        'shortcut_test_btn': 'Hileyi Dene',
        'shortcut_shorts_note': 'YouTube Shorts videolarını da destekler:',
        'shortcut_instant_note': 'Otomatik indirme anında başlar!',
        'pwa_install_btn': 'Uygulamayı Yükle',
        'pwa_install_short': 'Uygulama',
        'pwa_banner_title': 'YT4MP3 Uygulamasını Yükle',
        'pwa_banner_desc': 'Ana ekranda 1 dokunuşla YouTube İndirici',
        'pwa_banner_install': 'Yükle',
        'pwa_ios_title': "iPhone'a YT4MP3 Yükle",
        'pwa_ios_desc': 'Yıldırım hızında 1 dokunuşla indirme için Ana Ekrana ekleyin:',
        'pwa_ios_step1': 'Safari alt çubuğundaki Paylaş düğmesine dokunun.',
        'pwa_ios_step2': "Aşağı kaydırın ve 'Ana Ekrana Ekle'yi seçin.",
        'pwa_ios_step3': "Sağ üst köşedeki 'Ekle'ye dokunun. Bitti!",
        'pwa_ios_btn': 'Anladım!'
    },
    'it': {
        'shortcut_title': 'Trucco Scorciatoia URL Virale: Download Diretto',
        'shortcut_badge': 'Senza Copia-Incolla',
        'shortcut_guide_prefix': 'Mentre guardi un video su YouTube, sostituisci semplicemente',
        'shortcut_guide_suffix': 'con',
        'shortcut_guide_end': 'nella barra degli indirizzi del browser e premi Invio:',
        'shortcut_before': 'Prima:',
        'shortcut_after': 'Dopo:',
        'shortcut_test_btn': 'Prova Trucco',
        'shortcut_shorts_note': 'Supporta anche YouTube Shorts:',
        'shortcut_instant_note': "Il download automatico si avvia all'istante!",
        'pwa_install_btn': 'Installa App',
        'pwa_install_short': 'App',
        'pwa_banner_title': "Installa l'App YT4MP3",
        'pwa_banner_desc': 'Downloader YouTube con 1 tocco sulla schermata iniziale',
        'pwa_banner_install': 'Installa',
        'pwa_ios_title': 'Installa YT4MP3 su iPhone',
        'pwa_ios_desc': 'Aggiungi alla schermata iniziale per download velocissimi con 1 tocco:',
        'pwa_ios_step1': 'Tocca il pulsante Condividi nella barra inferiore di Safari.',
        'pwa_ios_step2': "Scorri verso il basso e seleziona 'Aggiungi a schermata Home'.",
        'pwa_ios_step3': "Tocca 'Aggiungi' nell'angolo in alto a destra. Fatto!",
        'pwa_ios_btn': 'Ho capito!'
    },
    'ru': {
        'shortcut_title': 'Вирусный трюк с URL: Прямое скачивание',
        'shortcut_badge': 'Без копирования и вставки',
        'shortcut_guide_prefix': 'При просмотре видео на YouTube просто замените',
        'shortcut_guide_suffix': 'на',
        'shortcut_guide_end': 'в адресной строке браузера и нажмите Enter:',
        'shortcut_before': 'До:',
        'shortcut_after': 'После:',
        'shortcut_test_btn': 'Проверить трюк',
        'shortcut_shorts_note': 'Также поддерживает YouTube Shorts:',
        'shortcut_instant_note': 'Мгновенное автоматическое скачивание начинается само!',
        'pwa_install_btn': 'Установить приложение',
        'pwa_install_short': 'Приложение',
        'pwa_banner_title': 'Установить приложение YT4MP3',
        'pwa_banner_desc': 'Скачивание YouTube в 1 касание на главном экране',
        'pwa_banner_install': 'Установить',
        'pwa_ios_title': 'Установить YT4MP3 на iPhone',
        'pwa_ios_desc': 'Добавьте на главный экран для мгновенной загрузки в 1 касание:',
        'pwa_ios_step1': 'Нажмите кнопку «Поделиться» на нижней панели Safari.',
        'pwa_ios_step2': "Прокрутите вниз и выберите «На экран «Домой»».",
        'pwa_ios_step3': "Нажмите «Добавить» в правом верхнем углу. Готово!",
        'pwa_ios_btn': 'Понятно!'
    },
    'vi': {
        'shortcut_title': 'Mẹo phím tắt URL lan truyền: Tải xuống trực tiếp',
        'shortcut_badge': 'Không cần sao chép-dán',
        'shortcut_guide_prefix': 'Khi xem video trên YouTube, chỉ cần thay thế',
        'shortcut_guide_suffix': 'bằng',
        'shortcut_guide_end': 'trong thanh địa chỉ trình duyệt của bạn và nhấn Enter:',
        'shortcut_before': 'Trước:',
        'shortcut_after': 'Sau:',
        'shortcut_test_btn': 'Thử mẹo',
        'shortcut_shorts_note': 'Cũng hỗ trợ YouTube Shorts:',
        'shortcut_instant_note': 'Tải xuống tự động bắt đầu ngay lập tức!',
        'pwa_install_btn': 'Cài đặt ứng dụng',
        'pwa_install_short': 'Ứng dụng',
        'pwa_banner_title': 'Cài đặt ứng dụng YT4MP3',
        'pwa_banner_desc': 'Trình tải YouTube 1 chạm trên màn hình chính',
        'pwa_banner_install': 'Cài đặt',
        'pwa_ios_title': 'Cài đặt YT4MP3 trên iPhone',
        'pwa_ios_desc': 'Thêm vào Màn hình chính để tải xuống siêu nhanh với 1 lần chạm:',
        'pwa_ios_step1': 'Nhấn vào nút Chia sẻ ở thanh dưới cùng của Safari.',
        'pwa_ios_step2': "Cuộn xuống và chọn 'Thêm vào MH chính'.",
        'pwa_ios_step3': "Nhấn 'Thêm' ở góc trên cùng bên phải. Hoàn tất!",
        'pwa_ios_btn': 'Đã hiểu!'
    },
    'ja': {
        'shortcut_title': 'バイラルURLショートカット裏技：直接ダウンロード',
        'shortcut_badge': 'コピペ不要',
        'shortcut_guide_prefix': 'YouTubeで動画を見ているとき、ブラウザのアドレスバーで',
        'shortcut_guide_suffix': 'を',
        'shortcut_guide_end': 'に書き換えてEnterを押してください：',
        'shortcut_before': '変更前:',
        'shortcut_after': '変更後:',
        'shortcut_test_btn': '裏技をテスト',
        'shortcut_shorts_note': 'YouTube Shortsもサポート：',
        'shortcut_instant_note': '即座に自動ダウンロードが始まります！',
        'pwa_install_btn': 'アプリをインストール',
        'pwa_install_short': 'アプリ',
        'pwa_banner_title': 'YT4MP3アプリをインストール',
        'pwa_banner_desc': 'ホーム画面から1タップでYouTubeダウンロード',
        'pwa_banner_install': 'インストール',
        'pwa_ios_title': 'iPhoneにYT4MP3をインストール',
        'pwa_ios_desc': 'ホーム画面に追加して1タップで超高速ダウンロード：',
        'pwa_ios_step1': 'Safari下部バーの「共有」ボタンをタップします。',
        'pwa_ios_step2': "下にスクロールして「ホーム画面に追加」を選択します。",
        'pwa_ios_step3': "右上の「追加」をタップします。完了です！",
        'pwa_ios_btn': '了解！'
    },
    'ko': {
        'shortcut_title': '바이럴 URL 단축키 트릭: 직접 다운로드',
        'shortcut_badge': '복사-붙여넣기 불필요',
        'shortcut_guide_prefix': 'YouTube에서 동영상을 시청할 때 브라우저 주소창에서',
        'shortcut_guide_suffix': '을',
        'shortcut_guide_end': '로 바꾸고 Enter를 누르세요:',
        'shortcut_before': '변경 전:',
        'shortcut_after': '변경 후:',
        'shortcut_test_btn': '트릭 테스트',
        'shortcut_shorts_note': 'YouTube Shorts도 지원：',
        'shortcut_instant_note': '즉시 자동 다운로드가 시작됩니다!',
        'pwa_install_btn': '앱 설치',
        'pwa_install_short': '앱',
        'pwa_banner_title': 'YT4MP3 앱 설치',
        'pwa_banner_desc': '홈 화면에서 1탭으로 YouTube 다운로드',
        'pwa_banner_install': '설치',
        'pwa_ios_title': 'iPhone에 YT4MP3 설치',
        'pwa_ios_desc': '홈 화면에 추가하여 번개처럼 빠른 1탭 다운로드:',
        'pwa_ios_step1': 'Safari 하단 바에서 공유 버튼을 탭하세요.',
        'pwa_ios_step2': "아래로 스크롤하여 '홈 화면에 추가'를 선택하세요.",
        'pwa_ios_step3': "오른쪽 상단의 '추가'를 탭하세요. 완료!",
        'pwa_ios_btn': '알겠습니다!'
    },
    'ar': {
        'shortcut_title': 'خدعة اختصار الرابط الفيروسي: تنزيل مباشر',
        'shortcut_badge': 'لا حاجة للنسخ واللصق',
        'shortcut_guide_prefix': 'عند مشاهدة فيديو على YouTube، ما عليك سوى استبدال',
        'shortcut_guide_suffix': 'بـ',
        'shortcut_guide_end': 'في شريط عنوان المتصفح واضغط على Enter:',
        'shortcut_before': 'قبل:',
        'shortcut_after': 'بعد:',
        'shortcut_test_btn': 'تجربة الخدعة',
        'shortcut_shorts_note': 'يدعم أيضاً فيديوهات YouTube Shorts:',
        'shortcut_instant_note': 'يبدأ التنزيل التلقائي على الفور!',
        'pwa_install_btn': 'تثبيت التطبيق',
        'pwa_install_short': 'التطبيق',
        'pwa_banner_title': 'تثبيت تطبيق YT4MP3',
        'pwa_banner_desc': 'تنزيل من YouTube بنقرة واحدة على الشاشة الرئيسية',
        'pwa_banner_install': 'تثبيت',
        'pwa_ios_title': 'تثبيت YT4MP3 على iPhone',
        'pwa_ios_desc': 'أضف إلى الشاشة الرئيسية لتنزيلات سريعة للغاية بنقرة واحدة:',
        'pwa_ios_step1': 'اضغط على زر المشاركة في الشريط السفلي لـ Safari.',
        'pwa_ios_step2': "قم بالتمرير لأسفل وحدد 'إضافة إلى الصفحة الرئيسية'.",
        'pwa_ios_step3': "اضغط على 'إضافة' في الزاوية العلوية اليمنى. تم!",
        'pwa_ios_btn': 'فهمت!'
    },
    'hi': {
        'shortcut_title': 'वायरल URL शॉर्टकट ट्रिक: डायरेक्ट डाउनलोड',
        'shortcut_badge': 'कॉपी-पेस्ट की ज़रूरत नहीं',
        'shortcut_guide_prefix': 'YouTube पर वीडियो देखते समय ब्राउज़र एड्रेस बार में',
        'shortcut_guide_suffix': 'की जगह',
        'shortcut_guide_end': 'लिखकर Enter दबाएं:',
        'shortcut_before': 'पहले:',
        'shortcut_after': 'बाद में:',
        'shortcut_test_btn': 'ट्रिक टेस्ट करें',
        'shortcut_shorts_note': 'YouTube Shorts भी सपोर्ट करता है:',
        'shortcut_instant_note': 'तुरंत ऑटो-डाउनलोड शुरू हो जाता है!',
        'pwa_install_btn': 'ऐप इंस्टॉल करें',
        'pwa_install_short': 'ऐप',
        'pwa_banner_title': 'YT4MP3 ऐप इंस्टॉल करें',
        'pwa_banner_desc': 'होम स्क्रीन पर 1-टैप YouTube डाउनलोडर',
        'pwa_banner_install': 'इंस्टॉल',
        'pwa_ios_title': 'iPhone पर YT4MP3 इंस्टॉल करें',
        'pwa_ios_desc': 'बिजली की गति से 1-टैप डाउनलोड के लिए होम स्क्रीन पर जोड़ें:',
        'pwa_ios_step1': 'Safari के निचले बार में शेयर बटन पर टैप करें।',
        'pwa_ios_step2': "नीचे स्क्रॉल करें और 'होम स्क्रीन में जोड़ें' चुनें।",
        'pwa_ios_step3': "ऊपर दाईं ओर 'जोड़ें' पर टैप करें। हो गया!",
        'pwa_ios_btn': 'समझ गया!'
    }
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
    base = ENGLISH_UI.copy()
    if lang in I18N_UI and lang != "en":
        base.update(I18N_UI[lang])
    if lang in SHORTCUT_AND_PWA_TRANSLATIONS:
        base.update(SHORTCUT_AND_PWA_TRANSLATIONS[lang])
    return base

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
