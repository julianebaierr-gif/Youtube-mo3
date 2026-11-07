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
    es, id, pt, fr, de, tr, it, ru, vi, ja, ko, ar, hi, my
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
    'my': {'code': 'my', 'dir': 'ltr', 'flag': '🇲🇲', 'name': 'Burmese', 'native': 'မြန်မာစာ'},
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
    'comp_subtitle': 'Compare YT4MP3 speed, format options, and browser compatibility against standard online converters.',
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
    'comp_row3_yt4mp3': 'Up to 320 kbps MP3 & 1080p/4K MP4 with synced audio',
    'comp_row3_others': 'Capped at compressed 128 kbps or low 360p resolution',
    'comp_row4_title': 'Annoying Ads & Redirects',
    'comp_row4_yt4mp3': 'Clean & safe: Zero pop-unders, no fake download buttons',
    'comp_row4_others': 'Spammy redirects, intrusive popups & unwanted ads',
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
    'shortcut_title': 'Quick URL Format: Direct Link Support',
    'shortcut_badge': 'No Copy-Paste Needed',
    'shortcut_guide_prefix': 'When watching a video on YouTube, simply replace',
    'shortcut_guide_suffix': 'with',
    'shortcut_guide_end': 'in your browser address bar and press Enter:',
    'shortcut_before': 'Before:',
    'shortcut_after': 'After:',
    'shortcut_test_btn': 'Try Example',
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
    'system_update_badge': 'Notice:',
    'system_update_note': 'Standard YouTube videos & Shorts supported. 18+ age-restricted, members-only, private, paid rentals, and live streams are not supported.',
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
    'my': my.UI,
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
    'my': my.PAGES,
}


SHORTCUT_AND_PWA_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'es': {
        'shortcut_title': 'Atajo Rápido de URL: Enlace Directo',
        'shortcut_badge': 'Sin Copiar y Pegar',
        'shortcut_guide_prefix': 'Al mirar un video en YouTube, simplemente reemplaza',
        'shortcut_guide_suffix': 'por',
        'shortcut_guide_end': 'en la barra de direcciones de tu navegador y presiona Enter:',
        'shortcut_before': 'Antes:',
        'shortcut_after': 'Después:',
        'shortcut_test_btn': 'Probar Ejemplo',
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
        'pwa_ios_btn': '¡Entendido!',
        'system_update_badge': 'Aviso:',
        'system_update_note': 'Videos estándar y Shorts compatibles. No se admiten videos con restricción de edad (+18), solo miembros, privados, de pago o en vivo.'
    },
    'id': {
        'shortcut_title': 'Pintasan Cepat URL: Tautan Langsung',
        'shortcut_badge': 'Tanpa Perlu Salin-Tempel',
        'shortcut_guide_prefix': 'Saat menonton video di YouTube, cukup ganti',
        'shortcut_guide_suffix': 'dengan',
        'shortcut_guide_end': 'di bilah alamat browser Anda dan tekan Enter:',
        'shortcut_before': 'Sebelum:',
        'shortcut_after': 'Sesudah:',
        'shortcut_test_btn': 'Coba Contoh',
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
        'pwa_ios_btn': 'Mengerti!',
        'system_update_badge': 'Pemberitahuan:',
        'system_update_note': 'Video standar & Shorts didukung. Video berbatas usia 18+, khusus langganan anggota, video privat, berbayar, dan siaran langsung tidak didukung.'
    },
    'pt': {
        'shortcut_title': 'Atalho Rápido de URL: Link Direto',
        'shortcut_badge': 'Sem Copiar e Colar',
        'shortcut_guide_prefix': 'Ao assistir a um vídeo no YouTube, basta substituir',
        'shortcut_guide_suffix': 'por',
        'shortcut_guide_end': 'na barra de endereços do seu navegador e pressionar Enter:',
        'shortcut_before': 'Antes:',
        'shortcut_after': 'Depois:',
        'shortcut_test_btn': 'Testar Exemplo',
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
        'pwa_ios_btn': 'Entendi!',
        'system_update_badge': 'Aviso:',
        'system_update_note': 'Vídeos padrão e Shorts suportados. Vídeos com restrição de idade (18+), exclusivos para membros, privados, pagos ou ao vivo não são suportados.'
    },
    'fr': {
        'shortcut_title': 'Raccourci Rapide URL : Lien Direct',
        'shortcut_badge': 'Sans Copier-Coller',
        'shortcut_guide_prefix': 'Lorsque vous regardez une vidéo sur YouTube, remplacez simplement',
        'shortcut_guide_suffix': 'par',
        'shortcut_guide_end': "dans la barre d'adresse de votre navigateur et appuyez sur Entrée :",
        'shortcut_before': 'Avant :',
        'shortcut_after': 'Après :',
        'shortcut_test_btn': "Tester l'exemple",
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
        'pwa_ios_btn': 'Compris !',
        'system_update_badge': 'Avis :',
        'system_update_note': 'Vidéos standard et Shorts pris en charge. Les vidéos 18+, réservées aux membres, privées, payantes ou en direct ne sont pas prises en charge.'
    },
    'de': {
        'shortcut_title': 'Schneller URL-Kurzbefehl: Direkter Link',
        'shortcut_badge': 'Kein Kopieren nötig',
        'shortcut_guide_prefix': 'Wenn Sie ein Video auf YouTube ansehen, ersetzen Sie einfach',
        'shortcut_guide_suffix': 'durch',
        'shortcut_guide_end': 'in Ihrer Browser-Adressleiste und drücken Sie die Eingabetaste:',
        'shortcut_before': 'Vorher:',
        'shortcut_after': 'Nachher:',
        'shortcut_test_btn': 'Beispiel testen',
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
        'pwa_ios_btn': 'Verstanden!',
        'system_update_badge': 'Hinweis:',
        'system_update_note': 'Standard-Videos & Shorts werden unterstützt. Videos ab 18 Jahren, Mitglieder-Videos, private, kostenpflichtige Videos und Live-Streams werden nicht unterstützt.'
    },
    'tr': {
        'shortcut_title': 'Hızlı URL Kısayolu: Doğrudan Bağlantı',
        'shortcut_badge': 'Kopyala-Yapıştır Gerekmez',
        'shortcut_guide_prefix': "YouTube'da bir video izlerken adres çubuğunda",
        'shortcut_guide_suffix': 'yerine',
        'shortcut_guide_end': "yazın ve Enter'a basın:",
        'shortcut_before': 'Önce:',
        'shortcut_after': 'Sonra:',
        'shortcut_test_btn': 'Örneği Dene',
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
        'pwa_ios_btn': 'Anladım!',
        'system_update_badge': 'Uyarı:',
        'system_update_note': 'Standart videolar ve Shorts desteklenir. 18+ yaş kısıtlamalı, üyelere özel, gizli, ücretli kiralanan ve canlı yayın videoları desteklenmez.'
    },
    'it': {
        'shortcut_title': 'Scorciatoia Rapida URL: Link Diretto',
        'shortcut_badge': 'Senza Copia-Incolla',
        'shortcut_guide_prefix': 'Mentre guardi un video su YouTube, sostituisci semplicemente',
        'shortcut_guide_suffix': 'con',
        'shortcut_guide_end': 'nella barra degli indirizzi del browser e premi Invio:',
        'shortcut_before': 'Prima:',
        'shortcut_after': 'Dopo:',
        'shortcut_test_btn': 'Prova Esempio',
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
        'pwa_ios_btn': 'Ho capito!',
        'system_update_badge': 'Avviso:',
        'system_update_note': 'Video standard e Shorts supportati. I video 18+, solo per membri, privati, a pagamento e live streaming non sono supportati.'
    },
    'ru': {
        'shortcut_title': 'Быстрый формат URL: Прямая ссылка',
        'shortcut_badge': 'Без копирования и вставки',
        'shortcut_guide_prefix': 'При просмотре видео на YouTube просто замените',
        'shortcut_guide_suffix': 'на',
        'shortcut_guide_end': 'в адресной строке браузера и нажмите Enter:',
        'shortcut_before': 'До:',
        'shortcut_after': 'После:',
        'shortcut_test_btn': 'Проверить пример',
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
        'pwa_ios_btn': 'Понятно!',
        'system_update_badge': 'Уведомление:',
        'system_update_note': 'Поддерживаются обычные видео и Shorts. Видео 18+, только для спонсоров, приватные, платные и прямые эфиры не поддерживаются.'
    },
    'vi': {
        'shortcut_title': 'Phím tắt URL nhanh: Liên kết trực tiếp',
        'shortcut_badge': 'Không cần sao chép-dán',
        'shortcut_guide_prefix': 'Khi xem video trên YouTube, chỉ cần thay thế',
        'shortcut_guide_suffix': 'bằng',
        'shortcut_guide_end': 'trong thanh địa chỉ trình duyệt của bạn và nhấn Enter:',
        'shortcut_before': 'Trước:',
        'shortcut_after': 'Sau:',
        'shortcut_test_btn': 'Thử ví dụ',
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
        'pwa_ios_btn': 'Đã hiểu!',
        'system_update_badge': 'Thông báo:',
        'system_update_note': 'Hỗ trợ video tiêu chuẩn và Shorts. Không hỗ trợ video giới hạn độ tuổi 18+, chỉ dành cho hội viên, video riêng tư, video trả phí và trực tiếp.'
    },
    'ja': {
        'shortcut_title': 'クイックURLショートカット：ダイレクトリンク',
        'shortcut_badge': 'コピペ不要',
        'shortcut_guide_prefix': 'YouTubeで動画を見ているとき、ブラウザのアドレスバーで',
        'shortcut_guide_suffix': 'を',
        'shortcut_guide_end': 'に書き換えてEnterを押してください：',
        'shortcut_before': '変更前:',
        'shortcut_after': '変更後:',
        'shortcut_test_btn': 'サンプルを試す',
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
        'pwa_ios_btn': '了解！',
        'system_update_badge': 'お知らせ:',
        'system_update_note': '標準動画とShortsに対応しています。18禁・年齢制限、メンバー限定、非公開、有料レンタル、ライブ配信は対応していません。'
    },
    'ko': {
        'shortcut_title': '빠른 URL 바로가기: 직접 링크 지원',
        'shortcut_badge': '복사-붙여넣기 불필요',
        'shortcut_guide_prefix': 'YouTube에서 동영상을 시청할 때 브라우저 주소창에서',
        'shortcut_guide_suffix': '을',
        'shortcut_guide_end': '로 바꾸고 Enter를 누르세요:',
        'shortcut_before': '변경 전:',
        'shortcut_after': '변경 후:',
        'shortcut_test_btn': '예시 테스트',
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
        'pwa_ios_btn': '알겠습니다!',
        'system_update_badge': '알림:',
        'system_update_note': '표준 동영상 및 Shorts 지원. 18세 이상 연령 제한, 멤버십 전용, 비공개, 유료 대여, 라이브 스트리밍은 지원되지 않습니다.'
    },
    'ar': {
        'shortcut_title': 'اختصار الرابط السريع: تنزيل مباشر',
        'shortcut_badge': 'لا حاجة للنسخ واللصق',
        'shortcut_guide_prefix': 'عند مشاهدة فيديو على YouTube، ما عليك سوى استبدال',
        'shortcut_guide_suffix': 'بـ',
        'shortcut_guide_end': 'في شريط عنوان المتصفح واضغط على Enter:',
        'shortcut_before': 'قبل:',
        'shortcut_after': 'بعد:',
        'shortcut_test_btn': 'تجربة المثال',
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
        'pwa_ios_btn': 'فهمت!',
        'system_update_badge': 'تنبيه:',
        'system_update_note': 'ندعم مقاطع الفيديو و Shorts القياسية. لا يتم دعم الفيديوهات 18+، الحصرية للأعضاء، الخاصة، المدفوعة، أو البث المباشر.'
    },
    'hi': {
        'shortcut_title': 'क्विक URL शॉर्टकट: डायरेक्ट लिंक',
        'shortcut_badge': 'कॉपी-पेस्ट की ज़रूरत नहीं',
        'shortcut_guide_prefix': 'YouTube पर वीडियो देखते समय ब्राउज़र एड्रेस बार में',
        'shortcut_guide_suffix': 'की जगह',
        'shortcut_guide_end': 'लिखकर Enter दबाएं:',
        'shortcut_before': 'पहले:',
        'shortcut_after': 'बाद में:',
        'shortcut_test_btn': 'उदाहरण देखें',
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
        'pwa_ios_btn': 'समझ गया!',
        'system_update_badge': 'सूचना:',
        'system_update_note': 'मानक यूट्यूब वीडियो और शॉर्ट्स समर्थित हैं। 18+ आयु-प्रतिबंधित, केवल सदस्यों के लिए, निजी (प्राइवेट), सशुल्क रेंटल और लाइव स्ट्रीम समर्थित नहीं हैं।'
    },
    'my': {
        'shortcut_title': 'အမြန် URL လမ်းကြောင်း: တိုက်ရိုက်ဒေါင်းနည်း',
        'shortcut_badge': 'Copy-Paste လုပ်စရာမလို',
        'shortcut_guide_prefix': 'YouTube ဗီဒီယိုကြည့်နေစဉ် Browser လိပ်စာဘားရှိ',
        'shortcut_guide_suffix': 'နေရာတွင်',
        'shortcut_guide_end': 'ဟု အစားထိုးရိုက်ထည့်ပြီး Enter နှိပ်လိုက်ပါ:',
        'shortcut_before': 'မပြောင်းမီ:',
        'shortcut_after': 'ပြောင်းပြီးနောက်:',
        'shortcut_test_btn': 'စမ်းသပ်ကြည့်မည်',
        'shortcut_shorts_note': 'YouTube Shorts တွင်လည်း အလုပ်လုပ်ပါသည်:',
        'shortcut_instant_note': 'တိုက်ရိုက် အလိုအလျောက် ဒေါင်းလုဒ်စတင်ပါမည်!',
        'pwa_install_btn': 'App သွင်းမည်',
        'pwa_install_short': 'App',
        'pwa_banner_title': 'YT4MP3 App ကို ဖုန်းထဲထည့်ပါ',
        'pwa_banner_desc': 'Home Screen မှ ၁-ချက်နှိပ် YouTube Downloader',
        'pwa_banner_install': 'ထည့်သွင်းမည်',
        'pwa_ios_title': 'iPhone တွင် YT4MP3 ထည့်သွင်းနည်း',
        'pwa_ios_desc': '၁-ချက်နှိပ် အမြန်ဒေါင်းရန် Home Screen သို့ ထည့်ပါ:',
        'pwa_ios_step1': 'Safari အောက်ခြေဘားရှိ မျှဝေမည် (Share) ကို နှိပ်ပါ။',
        'pwa_ios_step2': "'Add to Home Screen' ကို အောက်သို့ဆွဲချ၍ ရွေးပါ။",
        'pwa_ios_step3': "ညာဘက်ထိပ်ရှိ 'Add' ကို နှိပ်ပါ။ ပြီးပါပြီ!",
        'pwa_ios_btn': 'နားလည်ပါပြီ!',
        'system_update_badge': 'သတိပေးချက်:',
        'system_update_note': 'ပုံမှန် ဗီဒီယိုများနှင့် Shorts များကို ဒေါင်းလုဒ်လုပ်နိုင်သည်။ အသက် ၁၈ နှစ်အထက်၊ အသင်းဝင်သီးသန့်၊ သီးသန့်နှင့် တိုက်ရိုက်ထုတ်လွှင့်မှုများကို ဒေါင်းလုဒ်လုပ်၍ မရပါ။'
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
    'my': my.KEYWORDS_RESEARCH,
}

def get_supported_languages() -> Dict[str, Dict[str, str]]:
    return SUPPORTED_LANGUAGES


EXTRA_UI_TRANSLATIONS: Dict[str, Dict[str, str]] = {'en': {'og_locale': 'en_US',
        'comp_subtitle': 'Compare YT4MP3 speed, format options, and browser compatibility against '
                         'standard online converters.',
        'comp_row3_yt4mp3': 'Up to 320 kbps MP3 & 1080p/4K MP4 with synced audio',
        'fetching_bitrates': 'Fetching available MP3 & MP4 quality bitrates...',
        'simple_process_badge': 'Simple Process',
        'how_it_works_subtitle': 'No registration, no software installation, completely free.',
        'utility_badge': 'Utility',
        'features_subtitle': 'Engineered for clean audio extraction and high-resolution video '
                             'streams.',
        'questions_badge': 'Questions',
        'faq_subtitle': 'Practical answers about audio quality, formats, and device compatibility.',
        'more_tools_badge': 'More Tools',
        'more_tools_subtitle': 'High-speed media extraction tools for audio, video, and Shorts.',
        'related_tools_title': 'Explore YouTube Converters & Tools',
        'tool_mp3_desc': 'Extract high-bitrate 320kbps MP3 audio from YouTube videos, music, and '
                         'podcasts.',
        'tool_mp3_cta': 'Convert MP3',
        'tool_mp4_desc': 'Download 1080p Full HD, 720p, and 4K MP4 video files directly.',
        'tool_mp4_cta': 'Download MP4',
        'tool_shorts_desc': 'Save YouTube Shorts in vertical MP4 video or MP3 audio format.',
        'tool_shorts_cta': 'Get Shorts',
        'tool_home_desc': 'Universal converter supporting YouTube links, bitrates, resolutions, '
                          'and formats.',
        'tool_home_cta': 'Open Tool',
        'footer_brand_desc': 'Fast YouTube to MP3 (320kbps) audio converter and YouTube to MP4 '
                             '(1080p / 4K) video downloader.',
        'service_status_online': 'Service Status: Online',
        'footer_audio_heading': 'YouTube Audio',
        'footer_video_heading': 'YouTube Video',
        'footer_legal_heading': 'Legal & DMCA',
        'footer_music_mp3': 'YouTube Music to MP3',
        'footer_shorts_mp3': 'YouTube Shorts to MP3',
        'footer_1080p_dl': 'YouTube 1080p Downloader',
        'footer_4k_uhd': 'YouTube 4K UHD Video',
        'footer_privacy_link': 'Privacy',
        'footer_terms_link': 'Terms',
        'footer_contact_link': 'About / DMCA / Contact',
        'about_section_badge': 'About & Standards',
        'about_section_title': 'About YT4MP3 & Our Technical Standards',
        'about_section_p1': 'YT4MP3 is an independent browser-based media format utility developed '
                            'and maintained by the YT4MP3 Engineering Team. Our mission is to '
                            'provide educators, students, journalists, and creators with a '
                            'reliable tool for archiving public-domain recordings, Creative '
                            'Commons content, and personal video backups without requiring desktop '
                            'software or browser extensions.',
        'about_section_p2': 'All audio and video streams are processed on-demand using standard '
                            'H.264, AAC, and LAME MP3 encoding profiles. Temporary conversion '
                            'buffers are automatically purged after transfer, and we strictly '
                            'respect copyright holders under the Digital Millennium Copyright Act '
                            '(DMCA).'},
 'es': {'og_locale': 'es_ES',
        'comp_subtitle': 'Compara la velocidad, formatos y compatibilidad de YT4MP3 frente a los '
                         'convertidores online tradicionales.',
        'comp_row3_yt4mp3': 'MP3 hasta 320 kbps y MP4 en 1080p/4K con audio sincronizado',
        'fetching_bitrates': 'Obteniendo calidades y tasas de bits MP3 y MP4 disponibles...',
        'simple_process_badge': 'Proceso Simple',
        'how_it_works_subtitle': 'Sin registro, sin instalar programas y totalmente gratis.',
        'utility_badge': 'Utilidad',
        'features_subtitle': 'Diseñado para una extracción de audio limpia y video en alta '
                             'resolución.',
        'questions_badge': 'Preguntas',
        'faq_subtitle': 'Respuestas prácticas sobre calidad de audio, formatos y compatibilidad de '
                        'dispositivos.',
        'more_tools_badge': 'Más Herramientas',
        'more_tools_subtitle': 'Herramientas rápidas de extracción multimedia para audio, video y '
                               'Shorts.',
        'related_tools_title': 'Explora Nuestros Convertidores y Herramientas de YouTube',
        'tool_mp3_desc': 'Extrae audio MP3 de 320kbps de alta calidad de videos, música y podcasts '
                         'de YouTube.',
        'tool_mp3_cta': 'Convertir MP3',
        'tool_mp4_desc': 'Descarga archivos de video MP4 en 1080p Full HD, 720p y 4K directamente.',
        'tool_mp4_cta': 'Descargar MP4',
        'tool_shorts_desc': 'Guarda YouTube Shorts en formato de video vertical MP4 o solo audio '
                            'MP3.',
        'tool_shorts_cta': 'Bajar Shorts',
        'tool_home_desc': 'Convertidor universal compatible con enlaces, tasas de bits, '
                          'resoluciones y formatos de YouTube.',
        'tool_home_cta': 'Abrir Herramienta',
        'footer_brand_desc': 'Convertidor rápido de YouTube a MP3 (320kbps) y descargador de video '
                             'YouTube a MP4 (1080p / 4K).',
        'service_status_online': 'Estado del servicio: En línea',
        'footer_audio_heading': 'Audio de YouTube',
        'footer_video_heading': 'Video de YouTube',
        'footer_legal_heading': 'Legal y DMCA',
        'footer_music_mp3': 'YouTube Music a MP3',
        'footer_shorts_mp3': 'YouTube Shorts a MP3',
        'footer_1080p_dl': 'Descargador YouTube 1080p',
        'footer_4k_uhd': 'Video YouTube 4K UHD',
        'footer_privacy_link': 'Privacidad',
        'footer_terms_link': 'Términos',
        'footer_contact_link': 'Acerca de / DMCA / Contacto',
        'about_section_badge': 'Acerca de y Estándares',
        'about_section_title': 'Acerca de YT4MP3 y Nuestros Estándares Técnicos',
        'about_section_p1': 'YT4MP3 es una herramienta web independiente de conversión de formatos '
                            'multimedia desarrollada por el equipo de ingeniería de YT4MP3 para '
                            'facilitar el respaldo personal, educativo y de contenido bajo '
                            'licencias Creative Commons sin instalar software.',
        'about_section_p2': 'Todos los flujos de audio y video se procesan bajo demanda con '
                            'perfiles estándar H.264, AAC y LAME MP3. Los búferes temporales se '
                            'eliminan automáticamente tras la descarga y cumplimos estrictamente '
                            'con las normas de derechos de autor y DMCA.'},
 'id': {'og_locale': 'id_ID',
        'comp_subtitle': 'Bandingkan kecepatan, pilihan format, dan kompatibilitas YT4MP3 dengan '
                         'situs konverter biasa.',
        'comp_row3_yt4mp3': 'MP3 hingga 320 kbps & MP4 1080p/4K dengan audio sinkron',
        'fetching_bitrates': 'Mengambil pilihan kualitas bitrate MP3 & MP4 yang tersedia...',
        'simple_process_badge': 'Proses Mudah',
        'how_it_works_subtitle': 'Tanpa registrasi, tanpa instal aplikasi, sepenuhnya gratis.',
        'utility_badge': 'Fitur Utama',
        'features_subtitle': 'Dirancang untuk ekstraksi audio jernih dan unduhan video resolusi '
                             'tinggi.',
        'questions_badge': 'Pertanyaan',
        'faq_subtitle': 'Jawaban praktis seputar kualitas audio, format file, dan kompatibilitas '
                        'perangkat.',
        'more_tools_badge': 'Alat Lainnya',
        'more_tools_subtitle': 'Alat ekstraksi media berkecepatan tinggi untuk audio, video, dan '
                               'Shorts.',
        'related_tools_title': 'Jelajahi Alat & Konverter YouTube',
        'tool_mp3_desc': 'Ekstrak audio MP3 320kbps berkualitas tinggi dari video, musik, dan '
                         'podcast YouTube.',
        'tool_mp3_cta': 'Konversi MP3',
        'tool_mp4_desc': 'Unduh file video MP4 1080p Full HD, 720p, dan 4K secara langsung.',
        'tool_mp4_cta': 'Unduh MP4',
        'tool_shorts_desc': 'Simpan video YouTube Shorts dalam format MP4 vertikal atau audio MP3.',
        'tool_shorts_cta': 'Unduh Shorts',
        'tool_home_desc': 'Konverter universal yang mendukung semua tautan, bitrate, resolusi, dan '
                          'format YouTube.',
        'tool_home_cta': 'Buka Alat',
        'footer_brand_desc': 'Konverter audio YouTube ke MP3 (320kbps) dan pengunduh video YouTube '
                             'ke MP4 (1080p / 4K) cepat.',
        'service_status_online': 'Status Layanan: Aktif',
        'footer_audio_heading': 'Audio YouTube',
        'footer_video_heading': 'Video YouTube',
        'footer_legal_heading': 'Legal & DMCA',
        'footer_music_mp3': 'YouTube Music ke MP3',
        'footer_shorts_mp3': 'YouTube Shorts ke MP3',
        'footer_1080p_dl': 'Pengunduh YouTube 1080p',
        'footer_4k_uhd': 'Video YouTube 4K UHD',
        'footer_privacy_link': 'Privasi',
        'footer_terms_link': 'Ketentuan',
        'footer_contact_link': 'Tentang / DMCA / Kontak',
        'about_section_badge': 'Tentang & Standar',
        'about_section_title': 'Tentang YT4MP3 & Standar Teknis Kami',
        'about_section_p1': 'YT4MP3 adalah utilitas konversi format media berbasis browser '
                            'independen yang dikembangkan untuk membantu pelajar, pendidik, dan '
                            'kreator mengarsipkan materi domain publik, Creative Commons, dan '
                            'cadangan pribadi tanpa instalasi perangkat lunak.',
        'about_section_p2': 'Semua aliran audio dan video diproses sesuai permintaan menggunakan '
                            'profil standar H.264, AAC, dan LAME MP3. Buffer sementara dihapus '
                            'secara otomatis setelah pengunduhan selesai dan kami mematuhi '
                            'kebijakan hak cipta DMCA.'},
 'pt': {'og_locale': 'pt_BR',
        'comp_subtitle': 'Compare a velocidade, opções de formato e compatibilidade do YT4MP3 com '
                         'conversores online comuns.',
        'comp_row3_yt4mp3': 'MP3 até 320 kbps e MP4 em 1080p/4K com áudio sincronizado',
        'fetching_bitrates': 'Buscando taxas de bits e qualidades MP3 e MP4 disponíveis...',
        'simple_process_badge': 'Processo Simples',
        'how_it_works_subtitle': 'Sem cadastro, sem instalação de programas, totalmente gratuito.',
        'utility_badge': 'Utilidade',
        'features_subtitle': 'Projetado para extração de áudio limpa e vídeos em alta resolução.',
        'questions_badge': 'Perguntas',
        'faq_subtitle': 'Respostas práticas sobre qualidade de áudio, formatos e compatibilidade '
                        'de dispositivos.',
        'more_tools_badge': 'Mais Ferramentas',
        'more_tools_subtitle': 'Ferramentas rápidas de extração de mídia para áudio, vídeo e '
                               'Shorts.',
        'related_tools_title': 'Explore Conversores e Ferramentas do YouTube',
        'tool_mp3_desc': 'Extraia áudio MP3 de 320kbps de alta qualidade de vídeos, músicas e '
                         'podcasts do YouTube.',
        'tool_mp3_cta': 'Converter MP3',
        'tool_mp4_desc': 'Baixe arquivos de vídeo MP4 em 1080p Full HD, 720p e 4K diretamente.',
        'tool_mp4_cta': 'Baixar MP4',
        'tool_shorts_desc': 'Salve YouTube Shorts em vídeo MP4 vertical ou formato de áudio MP3.',
        'tool_shorts_cta': 'Baixar Shorts',
        'tool_home_desc': 'Conversor universal compatível com todos os links, bitrates, resoluções '
                          'e formatos do YouTube.',
        'tool_home_cta': 'Abrir Ferramenta',
        'footer_brand_desc': 'Conversor rápido de YouTube para MP3 (320kbps) e baixador de vídeo '
                             'YouTube para MP4 (1080p / 4K).',
        'service_status_online': 'Status do Serviço: Online',
        'footer_audio_heading': 'Áudio do YouTube',
        'footer_video_heading': 'Vídeo do YouTube',
        'footer_legal_heading': 'Legal e DMCA',
        'footer_music_mp3': 'YouTube Music para MP3',
        'footer_shorts_mp3': 'YouTube Shorts para MP3',
        'footer_1080p_dl': 'Baixador YouTube 1080p',
        'footer_4k_uhd': 'Vídeo YouTube 4K UHD',
        'footer_privacy_link': 'Privacidade',
        'footer_terms_link': 'Termos',
        'footer_contact_link': 'Sobre / DMCA / Contato',
        'about_section_badge': 'Sobre e Padrões',
        'about_section_title': 'Sobre o YT4MP3 e Nossos Padrões Técnicos',
        'about_section_p1': 'O YT4MP3 é um utilitário independente de conversão de mídia baseado '
                            'no navegador, desenvolvido para estudantes, educadores e criadores '
                            'fazerem backup pessoal de conteúdos em domínio público e Creative '
                            'Commons sem instalar programas.',
        'about_section_p2': 'Todos os fluxos de áudio e vídeo são processados sob demanda usando '
                            'perfis padrão H.264, AAC e LAME MP3. Os buffers temporários são '
                            'limpos automaticamente após a transferência e respeitamos '
                            'rigorosamente os direitos autorais e o DMCA.'},
 'fr': {'og_locale': 'fr_FR',
        'comp_subtitle': 'Comparez la vitesse, les formats et la compatibilité de YT4MP3 avec les '
                         'convertisseurs en ligne classiques.',
        'comp_row3_yt4mp3': 'MP3 jusqu’à 320 kbps & MP4 1080p/4K avec son synchronisé',
        'fetching_bitrates': 'Récupération des débits et qualités MP3 & MP4 disponibles...',
        'simple_process_badge': 'Processus Simple',
        'how_it_works_subtitle': 'Sans inscription, sans installation de logiciel, entièrement '
                                 'gratuit.',
        'utility_badge': 'Utilité',
        'features_subtitle': 'Conçu pour une extraction audio nette et des flux vidéo haute '
                             'résolution.',
        'questions_badge': 'Questions',
        'faq_subtitle': 'Réponses pratiques sur la qualité audio, les formats et la compatibilité '
                        'des appareils.',
        'more_tools_badge': "Plus d'Outils",
        'more_tools_subtitle': "Outils d'extraction multimédia rapides pour l'audio, la vidéo et "
                               'les Shorts.',
        'related_tools_title': 'Découvrez nos Convertisseurs et Outils YouTube',
        'tool_mp3_desc': 'Extrayez un son MP3 320kbps haute qualité à partir de vidéos, musiques '
                         'et podcasts YouTube.',
        'tool_mp3_cta': 'Convertir MP3',
        'tool_mp4_desc': 'Téléchargez directement des fichiers vidéo MP4 en 1080p Full HD, 720p et '
                         '4K.',
        'tool_mp4_cta': 'Télécharger MP4',
        'tool_shorts_desc': 'Enregistrez les YouTube Shorts au format vidéo vertical MP4 ou audio '
                            'MP3.',
        'tool_shorts_cta': 'Télécharger Shorts',
        'tool_home_desc': 'Convertisseur universel prenant en charge les liens, débits, '
                          'résolutions et formats YouTube.',
        'tool_home_cta': "Ouvrir l'Outil",
        'footer_brand_desc': 'Convertisseur rapide YouTube en MP3 (320kbps) et téléchargeur vidéo '
                             'YouTube en MP4 (1080p / 4K).',
        'service_status_online': 'État du service : En ligne',
        'footer_audio_heading': 'Audio YouTube',
        'footer_video_heading': 'Vidéo YouTube',
        'footer_legal_heading': 'Mentions Légales & DMCA',
        'footer_music_mp3': 'YouTube Music en MP3',
        'footer_shorts_mp3': 'YouTube Shorts en MP3',
        'footer_1080p_dl': 'Téléchargeur YouTube 1080p',
        'footer_4k_uhd': 'Vidéo YouTube 4K UHD',
        'footer_privacy_link': 'Confidentialité',
        'footer_terms_link': 'Conditions',
        'footer_contact_link': 'À propos / DMCA / Contact',
        'about_section_badge': 'À propos & Standards',
        'about_section_title': 'À propos de YT4MP3 et de nos Standards Techniques',
        'about_section_p1': 'YT4MP3 est un utilitaire web indépendant de conversion multimédia '
                            'conçu pour permettre aux étudiants, enseignants et créateurs '
                            "d'archiver des contenus du domaine public, sous licence Creative "
                            'Commons ou leurs propres vidéos sans installer de logiciel.',
        'about_section_p2': 'Tous les flux audio et vidéo sont traités à la demande selon les '
                            'profils standards H.264, AAC et LAME MP3. Les fichiers temporaires '
                            'sont automatiquement supprimés après le transfert et nous respectons '
                            "strictement le droit d'auteur (DMCA)."},
 'de': {'og_locale': 'de_DE',
        'comp_subtitle': 'Vergleichen Sie Geschwindigkeit, Formatoptionen und '
                         'Browser-Kompatibilität von YT4MP3 mit herkömmlichen Online-Konvertern.',
        'comp_row3_yt4mp3': 'Bis zu 320 kbps MP3 & 1080p/4K MP4 mit synchronisiertem Ton',
        'fetching_bitrates': 'Verfügbare MP3- & MP4-Qualitätsstufen werden geladen...',
        'simple_process_badge': 'Einfacher Ablauf',
        'how_it_works_subtitle': 'Keine Registrierung, keine Softwareinstallation, komplett '
                                 'kostenlos.',
        'utility_badge': 'Funktionen',
        'features_subtitle': 'Entwickelt für saubere Audio-Extraktion und hochauflösende '
                             'Videostreams.',
        'questions_badge': 'Fragen',
        'faq_subtitle': 'Praktische Antworten zu Audioqualität, Formaten und Gerätekompatibilität.',
        'more_tools_badge': 'Weitere Tools',
        'more_tools_subtitle': 'Schnelle Medien-Tools für Audio, Video und YouTube Shorts.',
        'related_tools_title': 'YouTube Konverter & Werkzeuge entdecken',
        'tool_mp3_desc': 'Extrahieren Sie 320kbps MP3-Audio aus YouTube-Videos, Musik und '
                         'Podcasts.',
        'tool_mp3_cta': 'MP3 umwandeln',
        'tool_mp4_desc': 'Laden Sie 1080p Full HD, 720p und 4K MP4-Videodateien direkt herunter.',
        'tool_mp4_cta': 'MP4 herunterladen',
        'tool_shorts_desc': 'Speichern Sie YouTube Shorts im vertikalen MP4-Videoformat oder als '
                            'MP3-Audiodatei.',
        'tool_shorts_cta': 'Shorts laden',
        'tool_home_desc': 'Universeller Konverter für YouTube-Links, Bitraten, Auflösungen und '
                          'Formate.',
        'tool_home_cta': 'Tool öffnen',
        'footer_brand_desc': 'Schneller YouTube zu MP3 (320kbps) Audio-Konverter und YouTube zu '
                             'MP4 (1080p / 4K) Video-Downloader.',
        'service_status_online': 'Systemstatus: Online',
        'footer_audio_heading': 'YouTube Audio',
        'footer_video_heading': 'YouTube Video',
        'footer_legal_heading': 'Rechtliches & DMCA',
        'footer_music_mp3': 'YouTube Music zu MP3',
        'footer_shorts_mp3': 'YouTube Shorts zu MP3',
        'footer_1080p_dl': 'YouTube 1080p Downloader',
        'footer_4k_uhd': 'YouTube 4K UHD Video',
        'footer_privacy_link': 'Datenschutz',
        'footer_terms_link': 'Nutzungsbedingungen',
        'footer_contact_link': 'Über uns / DMCA / Kontakt',
        'about_section_badge': 'Über uns & Standards',
        'about_section_title': 'Über YT4MP3 & unsere technischen Standards',
        'about_section_p1': 'YT4MP3 ist ein unabhängiges browserbasiertes '
                            'Medien-Konvertierungstool, das Lehrenden, Studierenden und Kreativen '
                            'hilft, gemeinfreie Aufnahmen, Creative-Commons-Inhalte und eigene '
                            'Videos ohne Zusatzsoftware zu sichern.',
        'about_section_p2': 'Alle Audio- und Videostreams werden bei Bedarf mit standardisierten '
                            'H.264-, AAC- und LAME-MP3-Profilen verarbeitet. Temporäre '
                            'Zwischenspeicher werden nach dem Transfer automatisch gelöscht, und '
                            'wir achten strikt das Urheberrecht (DMCA).'},
 'tr': {'og_locale': 'tr_TR',
        'mp4_video_tab': 'MP4 Video İndir',
        'comp_subtitle': "YT4MP3'ün hızını, format seçeneklerini ve tarayıcı uyumluluğunu standart "
                         'çevrimiçi dönüştürücülerle karşılaştırın.',
        'comp_row3_yt4mp3': '320 kbps MP3 ve senkronize sesli 1080p/4K MP4 desteği',
        'fetching_bitrates': 'Mevcut MP3 ve MP4 kalite seçenekleri getiriliyor...',
        'simple_process_badge': 'Kolay İşlem',
        'how_it_works_subtitle': 'Kayıt yok, program kurulumu yok, tamamen ücretsiz.',
        'utility_badge': 'Özellikler',
        'features_subtitle': 'Temiz ses ayrıştırma ve yüksek çözünürlüklü video akışları için '
                             'tasarlandı.',
        'questions_badge': 'Sorular',
        'faq_subtitle': 'Ses kalitesi, formatlar ve cihaz uyumluluğu hakkında pratik yanıtlar.',
        'more_tools_badge': 'Diğer Araçlar',
        'more_tools_subtitle': 'Ses, video ve Shorts için yüksek hızlı medya dönüştürme araçları.',
        'related_tools_title': 'YouTube Dönüştürücü ve Araçlarını Keşfedin',
        'tool_mp3_desc': 'YouTube videolarından, müziklerden ve podcastlerden 320kbps MP3 ses '
                         'ayıklayın.',
        'tool_mp3_cta': 'MP3 Dönüştür',
        'tool_mp4_desc': '1080p Full HD, 720p ve 4K MP4 video dosyalarını doğrudan indirin.',
        'tool_mp4_cta': 'MP4 İndir',
        'tool_shorts_desc': 'YouTube Shorts videolarını dikey MP4 veya yalnızca MP3 ses olarak '
                            'kaydedin.',
        'tool_shorts_cta': 'Shorts İndir',
        'tool_home_desc': 'Tüm YouTube bağlantılarını, bit hızlarını ve çözünürlükleri destekleyen '
                          'evrensel dönüştürücü.',
        'tool_home_cta': 'Aracı Aç',
        'footer_brand_desc': 'Hızlı YouTube MP3 (320kbps) ses dönüştürücü ve YouTube MP4 (1080p / '
                             '4K) video indirici.',
        'service_status_online': 'Servis Durumu: Çevrimiçi',
        'footer_audio_heading': 'YouTube Ses',
        'footer_video_heading': 'YouTube Video',
        'footer_legal_heading': 'Yasal & DMCA',
        'footer_music_mp3': 'YouTube Music MP3 Dönüştürücü',
        'footer_shorts_mp3': 'YouTube Shorts MP3 İndir',
        'footer_1080p_dl': 'YouTube 1080p İndirici',
        'footer_4k_uhd': 'YouTube 4K UHD Video',
        'footer_privacy_link': 'Gizlilik',
        'footer_terms_link': 'Koşullar',
        'footer_contact_link': 'Hakkımızda / DMCA / İletişim',
        'about_section_badge': 'Hakkımızda & Standartlar',
        'about_section_title': 'YT4MP3 Hakkında ve Teknik Standartlarımız',
        'about_section_p1': 'YT4MP3, eğitimcilerin, öğrencilerin ve içerik üreticilerinin kamu '
                            'malı kayıtları, Creative Commons lisanslı içerikleri ve kişisel video '
                            'yedeklerini ek yazılım kurmadan arşivlemesi için geliştirilmiş '
                            'bağımsız bir web aracıdır.',
        'about_section_p2': 'Tüm ses ve video akışları standart H.264, AAC ve LAME MP3 '
                            'profilleriyle anlık olarak işlenir. Geçici önbellek dosyaları aktarım '
                            'sonrasında otomatik olarak silinir ve DMCA telif hakkı kurallarına '
                            'tam uyum sağlanır.'},
 'it': {'og_locale': 'it_IT',
        'comp_subtitle': 'Confronta la velocità, i formati e la compatibilità di YT4MP3 rispetto '
                         'ai convertitori online tradizionali.',
        'comp_row3_yt4mp3': 'MP3 fino a 320 kbps e MP4 1080p/4K con audio sincronizzato',
        'fetching_bitrates': 'Recupero delle qualità e dei bitrate MP3 e MP4 disponibili...',
        'simple_process_badge': 'Processo Semplice',
        'how_it_works_subtitle': 'Nessuna registrazione, nessuna installazione software, '
                                 'completamente gratuito.',
        'utility_badge': 'Funzionalità',
        'features_subtitle': 'Progettato per un’estrazione audio pulita e flussi video ad alta '
                             'risoluzione.',
        'questions_badge': 'Domande',
        'faq_subtitle': 'Risposte pratiche su qualità audio, formati e compatibilità dei '
                        'dispositivi.',
        'more_tools_badge': 'Altri Strumenti',
        'more_tools_subtitle': 'Strumenti rapidi di estrazione multimediale per audio, video e '
                               'Shorts.',
        'related_tools_title': 'Esplora i Convertitori e gli Strumenti YouTube',
        'tool_mp3_desc': 'Estrai audio MP3 a 320kbps da video, musica e podcast di YouTube.',
        'tool_mp3_cta': 'Converti MP3',
        'tool_mp4_desc': 'Scarica direttamente file video MP4 in 1080p Full HD, 720p e 4K.',
        'tool_mp4_cta': 'Scarica MP4',
        'tool_shorts_desc': 'Salva gli YouTube Shorts in formato video verticale MP4 o solo audio '
                            'MP3.',
        'tool_shorts_cta': 'Scarica Shorts',
        'tool_home_desc': 'Convertitore universale compatibile con link, bitrate, risoluzioni e '
                          'formati YouTube.',
        'tool_home_cta': 'Apri Strumento',
        'footer_brand_desc': 'Convertitore veloce da YouTube a MP3 (320kbps) e downloader video da '
                             'YouTube a MP4 (1080p / 4K).',
        'service_status_online': 'Stato del servizio: Online',
        'footer_audio_heading': 'Audio YouTube',
        'footer_video_heading': 'Video YouTube',
        'footer_legal_heading': 'Note Legali & DMCA',
        'footer_music_mp3': 'YouTube Music in MP3',
        'footer_shorts_mp3': 'YouTube Shorts in MP3',
        'footer_1080p_dl': 'Downloader YouTube 1080p',
        'footer_4k_uhd': 'Video YouTube 4K UHD',
        'footer_privacy_link': 'Privacy',
        'footer_terms_link': 'Termini',
        'footer_contact_link': 'Chi siamo / DMCA / Contatti',
        'about_section_badge': 'Chi siamo & Standard',
        'about_section_title': 'Informazioni su YT4MP3 e i Nostri Standard Tecnici',
        'about_section_p1': 'YT4MP3 è uno strumento web indipendente di conversione multimediale '
                            'sviluppato per consentire a studenti, docenti e creatori di '
                            'archiviare contenuti di pubblico dominio, Creative Commons e backup '
                            'personali senza installare programmi.',
        'about_section_p2': 'Tutti i flussi audio e video vengono elaborati su richiesta '
                            'utilizzando profili standard H.264, AAC e LAME MP3. I buffer '
                            'temporanei vengono eliminati automaticamente dopo il trasferimento '
                            'nel pieno rispetto del diritto d’autore (DMCA).'},
 'ru': {'og_locale': 'ru_RU',
        'comp_subtitle': 'Сравните скорость, выбор форматов и совместимость YT4MP3 с обычными '
                         'онлайн-конвертерами.',
        'comp_row3_yt4mp3': 'MP3 до 320 кбит/с и MP4 1080p/4K с синхронизированным звуком',
        'fetching_bitrates': 'Получение доступных вариантов качества MP3 и MP4...',
        'simple_process_badge': 'Простой процесс',
        'how_it_works_subtitle': 'Без регистрации, без установки программ, полностью бесплатно.',
        'utility_badge': 'Возможности',
        'features_subtitle': 'Разработано для чистого извлечения звука и видео в высоком '
                             'разрешении.',
        'questions_badge': 'Вопросы',
        'faq_subtitle': 'Практические ответы о качестве звука, форматах и совместимости устройств.',
        'more_tools_badge': 'Другие инструменты',
        'more_tools_subtitle': 'Быстрые инструменты для извлечения аудио, видео и роликов Shorts.',
        'related_tools_title': 'Конвертеры и инструменты для YouTube',
        'tool_mp3_desc': 'Извлекайте аудио MP3 320 кбит/с из видео, музыки и подкастов YouTube.',
        'tool_mp3_cta': 'Конвертировать MP3',
        'tool_mp4_desc': 'Скачивайте видеофайлы MP4 в качестве 1080p Full HD, 720p и 4K напрямую.',
        'tool_mp4_cta': 'Скачать MP4',
        'tool_shorts_desc': 'Сохраняйте вертикальные видео YouTube Shorts в формате MP4 или аудио '
                            'MP3.',
        'tool_shorts_cta': 'Скачать Shorts',
        'tool_home_desc': 'Универсальный конвертер с поддержкой всех ссылок, битрейтов и '
                          'разрешений YouTube.',
        'tool_home_cta': 'Открыть',
        'footer_brand_desc': 'Быстрый конвертер YouTube в MP3 (320 кбит/с) и загрузчик видео '
                             'YouTube в MP4 (1080p / 4K).',
        'service_status_online': 'Статус сервиса: Онлайн',
        'footer_audio_heading': 'Аудио YouTube',
        'footer_video_heading': 'Видео YouTube',
        'footer_legal_heading': 'Правовая информация и DMCA',
        'footer_music_mp3': 'YouTube Music в MP3',
        'footer_shorts_mp3': 'YouTube Shorts в MP3',
        'footer_1080p_dl': 'Загрузчик YouTube 1080p',
        'footer_4k_uhd': 'Видео YouTube 4K UHD',
        'footer_privacy_link': 'Конфиденциальность',
        'footer_terms_link': 'Условия',
        'footer_contact_link': 'О сервисе / DMCA / Контакты',
        'about_section_badge': 'О проекте и стандартах',
        'about_section_title': 'О сервисе YT4MP3 и наших технических стандартах',
        'about_section_p1': 'YT4MP3 — это независимый браузерный инструмент конвертации '
                            'мультимедиа, созданный для преподавателей, студентов и авторов '
                            'контента для резервного копирования материалов общественного '
                            'достояния и Creative Commons без установки программ.',
        'about_section_p2': 'Все аудио- и видеопотоки обрабатываются по запросу с использованием '
                            'стандартных профилей H.264, AAC и LAME MP3. Временные буферы '
                            'автоматически очищаются после завершения передачи, и мы строго '
                            'соблюдаем нормы авторского права (DMCA).'},
 'vi': {'og_locale': 'vi_VN',
        'comp_subtitle': 'So sánh tốc độ, tùy chọn định dạng và khả năng tương thích của YT4MP3 '
                         'với các công cụ chuyển đổi thông thường.',
        'comp_row3_yt4mp3': 'MP3 lên tới 320 kbps & MP4 1080p/4K âm thanh đồng bộ',
        'fetching_bitrates': 'Đang lấy danh sách chất lượng MP3 & MP4 khả dụng...',
        'simple_process_badge': 'Quy Trình Đơn Giản',
        'how_it_works_subtitle': 'Không cần đăng ký, không cần cài đặt phần mềm, hoàn toàn miễn '
                                 'phí.',
        'utility_badge': 'Tính Năng',
        'features_subtitle': 'Được tối ưu hóa để trích xuất âm thanh rõ nét và tải video độ phân '
                             'giải cao.',
        'questions_badge': 'Câu Hỏi',
        'faq_subtitle': 'Giải đáp thực tế về chất lượng âm thanh, định dạng và khả năng tương '
                        'thích thiết bị.',
        'more_tools_badge': 'Công Cụ Khác',
        'more_tools_subtitle': 'Bộ công cụ trích xuất âm thanh, video và YouTube Shorts tốc độ '
                               'cao.',
        'related_tools_title': 'Khám Phá Công Cụ Chuyển Đổi YouTube',
        'tool_mp3_desc': 'Trích xuất âm thanh MP3 320kbps chất lượng cao từ video, nhạc và podcast '
                         'YouTube.',
        'tool_mp3_cta': 'Chuyển đổi MP3',
        'tool_mp4_desc': 'Tải trực tiếp tệp video MP4 1080p Full HD, 720p và 4K về thiết bị.',
        'tool_mp4_cta': 'Tải xuống MP4',
        'tool_shorts_desc': 'Lưu video YouTube Shorts ở định dạng MP4 dọc hoặc âm thanh MP3.',
        'tool_shorts_cta': 'Tải Shorts',
        'tool_home_desc': 'Trình chuyển đổi đa năng hỗ trợ mọi liên kết, bitrate, độ phân giải và '
                          'định dạng YouTube.',
        'tool_home_cta': 'Mở Công Cụ',
        'footer_brand_desc': 'Trình chuyển đổi âm thanh YouTube sang MP3 (320kbps) và tải video '
                             'YouTube sang MP4 (1080p / 4K) nhanh chóng.',
        'service_status_online': 'Trạng thái dịch vụ: Trực tuyến',
        'footer_audio_heading': 'Âm Thanh YouTube',
        'footer_video_heading': 'Video YouTube',
        'footer_legal_heading': 'Pháp Lý & DMCA',
        'footer_music_mp3': 'YouTube Music sang MP3',
        'footer_shorts_mp3': 'YouTube Shorts sang MP3',
        'footer_1080p_dl': 'Trình tải YouTube 1080p',
        'footer_4k_uhd': 'Video YouTube 4K UHD',
        'footer_privacy_link': 'Quyền riêng tư',
        'footer_terms_link': 'Điều khoản',
        'footer_contact_link': 'Giới thiệu / DMCA / Liên hệ',
        'about_section_badge': 'Giới Thiệu & Tiêu Chuẩn',
        'about_section_title': 'Giới Thiệu Về YT4MP3 & Tiêu Chuẩn Kỹ Thuật',
        'about_section_p1': 'YT4MP3 là tiện ích chuyển đổi định dạng đa phương tiện trên trình '
                            'duyệt độc lập, hỗ trợ sinh viên, giáo viên và nhà sáng tạo lưu trữ '
                            'nội dung thuộc phạm vi công cộng, Creative Commons và bản sao lưu cá '
                            'nhân mà không cần cài đặt phần mềm.',
        'about_section_p2': 'Tất cả luồng âm thanh và video được xử lý theo yêu cầu bằng cấu hình '
                            'chuẩn H.264, AAC và LAME MP3. Bộ đệm tạm thời được xóa tự động sau '
                            'khi tải xong và chúng tôi tuân thủ nghiêm ngặt quy định bản quyền '
                            'DMCA.'},
 'ja': {'og_locale': 'ja_JP',
        'comp_subtitle': 'YT4MP3の変換速度、対応フォーマット、ブラウザ互換性を一般的な変換サイトと比較してください。',
        'comp_row3_yt4mp3': '最大320kbpsの高音質MP3＆音声同期済み1080p/4K MP4',
        'fetching_bitrates': '利用可能なMP3・MP4のビットレートと画質を取得しています...',
        'simple_process_badge': '簡単3ステップ',
        'how_it_works_subtitle': '会員登録不要、ソフトのインストール不要、完全無料で利用できます。',
        'utility_badge': '主な機能',
        'features_subtitle': 'クリアな音声抽出と高解像度ビデオストリームのために設計されています。',
        'questions_badge': 'よくある質問',
        'faq_subtitle': '音質、ファイル形式、デバイスの互換性に関する実用的な回答。',
        'more_tools_badge': '関連ツール',
        'more_tools_subtitle': '音声、動画、YouTubeショート向けの高速メディア変換ツール。',
        'related_tools_title': 'YouTube変換ツール一覧',
        'tool_mp3_desc': 'YouTubeの動画、音楽、ポッドキャストから高音質320kbpsのMP3音声を抽出します。',
        'tool_mp3_cta': 'MP3に変換',
        'tool_mp4_desc': '1080p フルHD、720p、4KのMP4動画ファイルを直接ダウンロードします。',
        'tool_mp4_cta': 'MP4を保存',
        'tool_shorts_desc': 'YouTubeショート動画を縦型MP4ビデオまたはMP3音声形式で保存します。',
        'tool_shorts_cta': 'ショートを保存',
        'tool_home_desc': 'すべてのYouTubeリンク、ビットレート、解像度、フォーマットに対応する万能コンバーター。',
        'tool_home_cta': 'ツールを開く',
        'footer_brand_desc': '高速YouTube MP3（320kbps）音声変換＆YouTube MP4（1080p / 4K）動画ダウンローダー。',
        'service_status_online': 'サービス状況: 正常稼働中',
        'footer_audio_heading': 'YouTube 音声変換',
        'footer_video_heading': 'YouTube 動画保存',
        'footer_legal_heading': '法的情報・DMCA',
        'footer_music_mp3': 'YouTube Music MP3変換',
        'footer_shorts_mp3': 'YouTube ショート MP3変換',
        'footer_1080p_dl': 'YouTube 1080p ダウンローダー',
        'footer_4k_uhd': 'YouTube 4K UHD 動画保存',
        'footer_privacy_link': 'プライバシー',
        'footer_terms_link': '利用規約',
        'footer_contact_link': '運営情報 / DMCA / お問い合わせ',
        'about_section_badge': '運営情報・技術基準',
        'about_section_title': 'YT4MP3について＆技術基準',
        'about_section_p1': 'YT4MP3は、教育関係者、学生、クリエイターがパブリックドメインの録音やCreative '
                            'Commonsライセンス作品、自身の動画バックアップをソフト不要で保存できるよう開発されたブラウザベースのメディア変換ユーティリティです。',
        'about_section_p2': 'すべての音声・映像ストリームは標準のH.264、AAC、LAME '
                            'MP3プロファイルでオンデマンド処理されます。一時バッファは転送後に自動消去され、DMCAおよび著作権法を厳格に遵守しています。'},
 'ko': {'og_locale': 'ko_KR',
        'comp_subtitle': 'YT4MP3의 변환 속도, 포맷 옵션 및 브라우저 호환성을 일반 온라인 변환기와 비교해 보세요.',
        'comp_row3_yt4mp3': '최대 320 kbps 고음질 MP3 및 오디오 동기화 1080p/4K MP4',
        'fetching_bitrates': '사용 가능한 MP3 및 MP4 화질/비트레이트 정보를 불러오는 중...',
        'simple_process_badge': '간편한 과정',
        'how_it_works_subtitle': '회원가입 없음, 프로그램 설치 없음, 100% 무료.',
        'utility_badge': '주요 기능',
        'features_subtitle': '깔끔한 오디오 추출과 고해상도 비디오 스트림을 위해 설계되었습니다.',
        'questions_badge': '자주 묻는 질문',
        'faq_subtitle': '음질, 파일 형식 및 기기 호환성에 대한 실용적인 답변.',
        'more_tools_badge': '관련 도구',
        'more_tools_subtitle': '오디오, 비디오 및 YouTube Shorts를 위한 고속 미디어 변환 도구.',
        'related_tools_title': 'YouTube 변환기 및 도구 둘러보기',
        'tool_mp3_desc': 'YouTube 동영상, 음악, 팟캐스트에서 320kbps 고음질 MP3 오디오를 추출합니다.',
        'tool_mp3_cta': 'MP3 변환',
        'tool_mp4_desc': '1080p Full HD, 720p 및 4K MP4 비디오 파일을 직접 다운로드합니다.',
        'tool_mp4_cta': 'MP4 다운로드',
        'tool_shorts_desc': 'YouTube Shorts 영상을 세로형 MP4 비디오 또는 MP3 오디오 형식으로 저장합니다.',
        'tool_shorts_cta': 'Shorts 저장',
        'tool_home_desc': '모든 YouTube 링크, 비트레이트, 해상도 및 포맷을 지원하는 올인원 변환기.',
        'tool_home_cta': '도구 열기',
        'footer_brand_desc': '빠른 YouTube MP3(320kbps) 오디오 변환기 및 YouTube MP4(1080p / 4K) 비디오 다운로더.',
        'service_status_online': '서비스 상태: 정상 운영 중',
        'footer_audio_heading': 'YouTube 오디오',
        'footer_video_heading': 'YouTube 비디오',
        'footer_legal_heading': '법적 고지 및 DMCA',
        'footer_music_mp3': 'YouTube Music MP3 변환',
        'footer_shorts_mp3': 'YouTube Shorts MP3 변환',
        'footer_1080p_dl': 'YouTube 1080p 다운로더',
        'footer_4k_uhd': 'YouTube 4K UHD 비디오',
        'footer_privacy_link': '개인정보처리방침',
        'footer_terms_link': '이용약관',
        'footer_contact_link': '소개 / DMCA / 문의하기',
        'about_section_badge': '서비스 소개 및 기술 표준',
        'about_section_title': 'YT4MP3 소개 및 기술 표준',
        'about_section_p1': 'YT4MP3는 교육자, 학생, 크리에이터가 별도의 프로그램 설치 없이 퍼블릭 도메인 자료, 크리에이티브 커먼즈(CC) 콘텐츠 '
                            '및 개인 동영상 백업을 보관할 수 있도록 개발된 웹 기반 미디어 포맷 변환 유틸리티입니다.',
        'about_section_p2': '모든 오디오 및 비디오 스트림은 표준 H.264, AAC 및 LAME MP3 인코딩 프로필을 사용하여 온디맨드로 처리됩니다. '
                            '임시 변환 버퍼는 전송 후 자동으로 삭제되며 DMCA 저작권 정책을 엄격히 준수합니다.'},
 'ar': {'og_locale': 'ar_SA',
        'comp_subtitle': 'قارن سرعة YT4MP3 وخيارات الصيغ وتوافق المتصفحات مع أدوات التحويل '
                         'التقليدية.',
        'comp_row3_yt4mp3': 'صوت MP3 حتى 320 كيلوبت وفيديو 1080p/4K متزامن',
        'fetching_bitrates': 'جاري جلب جودات وصيغ MP3 و MP4 المتاحة...',
        'simple_process_badge': 'خطوات بسيطة',
        'how_it_works_subtitle': 'بدون تسجيل حساب، بدون تثبيت برامج، مجاني بالكامل.',
        'utility_badge': 'المميزات',
        'features_subtitle': 'مصمم لاستخراج الصوت بنقاء عالٍ وتنزيل الفيديو بدقة فائقة.',
        'questions_badge': 'الأسئلة الشائعة',
        'faq_subtitle': 'إجابات عملية حول جودة الصوت والصيغ وتوافق الأجهزة.',
        'more_tools_badge': 'أدوات أخرى',
        'more_tools_subtitle': 'أدوات سريعة لاستخراج الصوت والفيديو ومقاطع Shorts.',
        'related_tools_title': 'استكشف أدوات ومحولات يوتيوب',
        'tool_mp3_desc': 'استخرج صوت MP3 بجودة 320kbps من مقاطع فيديو يوتيوب والموسيقى والبودكاست.',
        'tool_mp3_cta': 'تحويل MP3',
        'tool_mp4_desc': 'قم بتنزيل ملفات فيديو MP4 بدقة 1080p Full HD و 720p و 4K مباشرة.',
        'tool_mp4_cta': 'تنزيل MP4',
        'tool_shorts_desc': 'احفظ مقاطع YouTube Shorts بصيغة فيديو MP4 عمودي أو صوت MP3.',
        'tool_shorts_cta': 'تنزيل Shorts',
        'tool_home_desc': 'محول شامل يدعم جميع روابط يوتيوب ومعدلات البت والدقات والصيغ.',
        'tool_home_cta': 'فتح الأداة',
        'footer_brand_desc': 'محول سريع من يوتيوب إلى MP3 (320kbps) وأداة تنزيل فيديو يوتيوب إلى '
                             'MP4 (1080p / 4K).',
        'service_status_online': 'حالة الخدمة: متصلة الآن',
        'footer_audio_heading': 'صوتيات يوتيوب',
        'footer_video_heading': 'فيديو يوتيوب',
        'footer_legal_heading': 'الشؤون القانونية و DMCA',
        'footer_music_mp3': 'تحويل YouTube Music إلى MP3',
        'footer_shorts_mp3': 'تحويل YouTube Shorts إلى MP3',
        'footer_1080p_dl': 'تنزيل يوتيوب 1080p',
        'footer_4k_uhd': 'فيديو يوتيوب 4K UHD',
        'footer_privacy_link': 'الخصوصية',
        'footer_terms_link': 'الشروط',
        'footer_contact_link': 'من نحن / DMCA / اتصل بنا',
        'about_section_badge': 'عن المنصة والمعايير',
        'about_section_title': 'حول YT4MP3 ومعاييرنا التقنية',
        'about_section_p1': 'منصة YT4MP3 هي أداة ويب مستقلة لتحويل صيغ الوسائط تم تطويرها لمساعدة '
                            'المعلمين والطلاب وصناع المحتوى على أرشفة التسجيلات العامة ومحتوى '
                            'المشاع الإبداعي (Creative Commons) والنسخ الاحتياطية الشخصية دون '
                            'الحاجة لتثبيت برامج.',
        'about_section_p2': 'تتم معالجة جميع مسارات الصوت والفيديو عند الطلب باستخدام معايير H.264 '
                            'و AAC و LAME MP3 القياسية، ويتم مسح الملفات المؤقتة تلقائياً بعد '
                            'انتهاء التحميل مع الالتزام التام بقوانين حقوق النشر (DMCA).'},
 'hi': {'og_locale': 'hi_IN',
        'comp_subtitle': 'सामान्य ऑनलाइन कनवर्टर की तुलना में YT4MP3 की गति, फ़ॉर्मेट विकल्प और '
                         'ब्राउज़र सपोर्ट देखें।',
        'comp_row3_yt4mp3': '320 kbps तक MP3 और सिंक किए गए ऑडियो के साथ 1080p/4K MP4',
        'fetching_bitrates': 'उपलब्ध MP3 और MP4 क्वालिटी विकल्प प्राप्त किए जा रहे हैं...',
        'simple_process_badge': 'आसान प्रक्रिया',
        'how_it_works_subtitle': 'कोई पंजीकरण नहीं, कोई सॉफ़्टवेयर इंस्टॉलेशन नहीं, पूरी तरह से '
                                 'मुफ़्त।',
        'utility_badge': 'विशेषताएं',
        'features_subtitle': 'साफ़ ऑडियो एक्सट्रैक्शन और हाई-रिज़ॉल्यूशन वीडियो स्ट्रीम के लिए '
                             'डिज़ाइन किया गया।',
        'questions_badge': 'सामान्य प्रश्न',
        'faq_subtitle': 'ऑडियो क्वालिटी, फ़ॉर्मेट और डिवाइस सपोर्ट के बारे में व्यावहारिक उत्तर।',
        'more_tools_badge': 'अन्य टूल्स',
        'more_tools_subtitle': 'ऑडियो, वीडियो और शॉर्ट्स के लिए हाई-स्पीड मीडिया कनवर्टर टूल्स।',
        'related_tools_title': 'YouTube कनवर्टर और टूल्स एक्सप्लोर करें',
        'tool_mp3_desc': 'YouTube वीडियो, संगीत और पॉडकास्ट से उच्च-गुणवत्ता वाला 320kbps MP3 '
                         'ऑडियो निकालें।',
        'tool_mp3_cta': 'MP3 कनवर्ट करें',
        'tool_mp4_desc': '1080p Full HD, 720p और 4K MP4 वीडियो फ़ाइलें सीधे डाउनलोड करें।',
        'tool_mp4_cta': 'MP4 डाउनलोड करें',
        'tool_shorts_desc': 'YouTube Shorts को वर्टिकल MP4 वीडियो या MP3 ऑडियो फ़ॉर्मेट में सेव '
                            'करें।',
        'tool_shorts_cta': 'Shorts डाउनलोड करें',
        'tool_home_desc': 'सभी YouTube लिंक, बिटरेट, रिज़ॉल्यूशन और फ़ॉर्मेट को सपोर्ट करने वाला '
                          'ऑल-इन-वन कनवर्टर।',
        'tool_home_cta': 'टूल खोलें',
        'footer_brand_desc': 'तेज़ YouTube से MP3 (320kbps) ऑडियो कनवर्टर और YouTube से MP4 (1080p '
                             '/ 4K) वीडियो डाउनलोडर।',
        'service_status_online': 'सेवा की स्थिति: ऑनलाइन',
        'footer_audio_heading': 'YouTube ऑडियो',
        'footer_video_heading': 'YouTube वीडियो',
        'footer_legal_heading': 'कानूनी और DMCA',
        'footer_music_mp3': 'YouTube Music से MP3',
        'footer_shorts_mp3': 'YouTube Shorts से MP3',
        'footer_1080p_dl': 'YouTube 1080p डाउनलोडर',
        'footer_4k_uhd': 'YouTube 4K UHD वीडियो',
        'footer_privacy_link': 'गोपनीयता',
        'footer_terms_link': 'शर्तें',
        'footer_contact_link': 'हमारे बारे में / DMCA / संपर्क',
        'about_section_badge': 'परिचय और तकनीकी मानक',
        'about_section_title': 'YT4MP3 के बारे में और हमारे तकनीकी मानक',
        'about_section_p1': 'YT4MP3 एक स्वतंत्र ब्राउज़र-आधारित मीडिया फ़ॉर्मेट कनवर्टर है जिसे '
                            'शिक्षकों, छात्रों और क्रिएटर्स के लिए पब्लिक डोमेन रिकॉर्डिंग, '
                            'क्रिएटिव कॉमन्स सामग्री और व्यक्तिगत वीडियो बैकअप को बिना किसी '
                            'सॉफ़्टवेयर इंस्टॉल किए सुरक्षित रखने के लिए विकसित किया गया है।',
        'about_section_p2': 'सभी ऑडियो और वीडियो स्ट्रीम मानक H.264, AAC और LAME MP3 प्रोफ़ाइल का '
                            'उपयोग करके ऑन-डिमांड प्रोसेस किए जाते हैं। डाउनलोड पूरा होने के बाद '
                            'अस्थायी बफ़र अपने आप साफ़ हो जाते हैं और हम DMCA कॉपीराइट नियमों का '
                            'सख्ती से पालन करते हैं।'},
 'my': {'og_locale': 'my_MM',
        'comp_subtitle': 'YT4MP3 ၏ မြန်နှုန်း၊ ဖိုင်အမျိုးအစား ရွေးချယ်မှုနှင့် Browser '
                         'ကိုက်ညီမှုတို့ကို သာမန်ဝက်ဘ်ဆိုက်များနှင့် နှိုင်းယှဉ်ကြည့်ပါ။',
        'comp_row3_yt4mp3': '320 kbps အထိ MP3 နှင့် အသံရုပ်ထွက်ကိုက်ညီသော 1080p/4K MP4',
        'fetching_bitrates': 'ရရှိနိုင်သော MP3 နှင့် MP4 အရည်အသွေးများကို ရှာဖွေနေပါသည်...',
        'simple_process_badge': 'လွယ်ကူသော အဆင့်များ',
        'how_it_works_subtitle': 'အကောင့်ဖွင့်ရန်မလို၊ ဆော့ဖ်ဝဲသွင်းရန်မလို၊ '
                                 'အခမဲ့အသုံးပြုနိုင်ပါသည်။',
        'utility_badge': 'အဓိက လုပ်ဆောင်ချက်များ',
        'features_subtitle': 'ကြည်လင်သော အသံဖိုင်ထုတ်ယူမှုနှင့် အရည်အသွေးမြင့် ဗီဒီယိုများအတွက် '
                             'တည်ဆောက်ထားသည်။',
        'questions_badge': 'မေးလေ့ရှိသော မေးခွန်းများ',
        'faq_subtitle': 'အသံအရည်အသွေး၊ ဖိုင်အမျိုးအစားနှင့် စက်ပစ္စည်း ကိုက်ညီမှုဆိုင်ရာ အဖြေများ။',
        'more_tools_badge': 'အခြား ကိရိယာများ',
        'more_tools_subtitle': 'အသံ၊ ဗီဒီယိုနှင့် Shorts များအတွက် အမြန်ဒေါင်းလုဒ် ကိရိယာများ။',
        'related_tools_title': 'YouTube ပြောင်းလဲရေး ကိရိယာများကို လေ့လာပါ',
        'tool_mp3_desc': 'YouTube ဗီဒီယို၊ သီချင်းနှင့် Podcast များမှ 320kbps MP3 အသံဖိုင်ကို '
                         'ထုတ်ယူပါ။',
        'tool_mp3_cta': 'MP3 ပြောင်းမည်',
        'tool_mp4_desc': '1080p Full HD၊ 720p နှင့် 4K MP4 ဗီဒီယိုဖိုင်များကို '
                         'တိုက်ရိုက်ဒေါင်းလုဒ်လုပ်ပါ။',
        'tool_mp4_cta': 'MP4 ဒေါင်းမည်',
        'tool_shorts_desc': 'YouTube Shorts များကို ဒေါင်လိုက် MP4 ဗီဒီယို သို့မဟုတ် MP3 '
                            'အသံဖိုင်အဖြစ် သိမ်းဆည်းပါ။',
        'tool_shorts_cta': 'Shorts ဒေါင်းမည်',
        'tool_home_desc': 'YouTube လင့်ခ်များနှင့် အရည်အသွေးအားလုံးကို ပံ့ပိုးပေးသော အထွေထွေ '
                          'ပြောင်းလဲစက်။',
        'tool_home_cta': 'ဖွင့်မည်',
        'footer_brand_desc': 'မြန်ဆန်သော YouTube MP3 (320kbps) အသံပြောင်းစက် နှင့် YouTube MP4 '
                             '(1080p / 4K) ဗီဒီယို ဒေါင်းလုဒ်စက်။',
        'service_status_online': 'ဝန်ဆောင်မှု အခြေအနေ: အွန်လိုင်း',
        'footer_audio_heading': 'YouTube အသံဖိုင်',
        'footer_video_heading': 'YouTube ဗီဒီယို',
        'footer_legal_heading': 'ဥပဒေရေးရာ နှင့် DMCA',
        'footer_music_mp3': 'YouTube Music မှ MP3',
        'footer_shorts_mp3': 'YouTube Shorts မှ MP3',
        'footer_1080p_dl': 'YouTube 1080p ဒေါင်းလုဒ်စက်',
        'footer_4k_uhd': 'YouTube 4K UHD ဗီဒီယို',
        'footer_privacy_link': 'ကိုယ်ရေးလုံခြုံမှု',
        'footer_terms_link': 'စည်းကမ်းချက်များ',
        'footer_contact_link': 'ကျွန်ုပ်တို့အကြောင်း / DMCA / ဆက်သွယ်ရန်',
        'about_section_badge': 'အကြောင်းအရာ နှင့် စံနှုန်းများ',
        'about_section_title': 'YT4MP3 အကြောင်း နှင့် နည်းပညာစံနှုန်းများ',
        'about_section_p1': 'YT4MP3 သည် ပညာရေးဝန်ထမ်းများ၊ ကျောင်းသားများနှင့် ဖန်တီးသူများအတွက် '
                            'အများပြည်သူဆိုင်ရာ မှတ်တမ်းများ၊ Creative Commons လိုင်စင်ရ '
                            'အကြောင်းအရာများနှင့် ကိုယ်ပိုင်ဗီဒီယိုများကို ဆော့ဖ်ဝဲသွင်းရန်မလိုဘဲ '
                            'သိမ်းဆည်းနိုင်ရန် တည်ဆောက်ထားသော Browser အခြေပြု ကိရိယာဖြစ်သည်။',
        'about_section_p2': 'အသံနှင့် ဗီဒီယိုဖိုင်အားလုံးကို H.264၊ AAC နှင့် LAME MP3 '
                            'စံနှုန်းများဖြင့် လိုအပ်သလို ပြောင်းလဲပေးပြီး ယာယီဖိုင်များကို '
                            'ဒေါင်းလုဒ်ပြီးဆုံးသည်နှင့် အလိုအလျောက် ဖျက်ပစ်ကာ DMCA '
                            'မူပိုင်ခွင့်စည်းမျဉ်းများကို အတိအကျ လိုက်နာပါသည်။'}}

def get_ui_strings(lang: str = "en") -> Dict[str, str]:
    base = ENGLISH_UI.copy()
    if "en" in EXTRA_UI_TRANSLATIONS:
        base.update(EXTRA_UI_TRANSLATIONS["en"])
    if lang in I18N_UI and lang != "en":
        base.update(I18N_UI[lang])
    if lang in SHORTCUT_AND_PWA_TRANSLATIONS:
        base.update(SHORTCUT_AND_PWA_TRANSLATIONS[lang])
    if lang in EXTRA_UI_TRANSLATIONS:
        base.update(EXTRA_UI_TRANSLATIONS[lang])
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
