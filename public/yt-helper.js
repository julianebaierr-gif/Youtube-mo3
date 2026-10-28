// YT4MP3 Client-Side 18+ Video & Audio Downloader Helper
// Runs directly in the user's authenticated YouTube tab to bypass age-restrictions
(function() {
    'use strict';

    if (!window.location.hostname.includes('youtube.com')) {
        alert('YT4MP3: Please open this bookmark while on YouTube watching the video you want to download!');
        return;
    }

    // Remove any previous helper modal
    var prev = document.getElementById('yt4mp3-helper-overlay');
    if (prev) prev.remove();

    var titleEl = document.querySelector('h1.ytd-watch-metadata, #title h1, h2.media-item-headline, .slim-video-metadata-title');
    var rawTitle = titleEl ? titleEl.textContent.trim() : (document.title || 'YouTube_Media').replace(/\s*-\s*YouTube$/i, '').trim();
    var safeFilename = rawTitle.replace(/[^\w\s-]/g, '').trim().substring(0, 80) || 'YouTube_Download';

    function extractStreams() {
        var audioUrl = null;
        var videoUrl = null;

        // Strategy 1: Network sniffer from PerformanceResourceTiming
        try {
            var entries = performance.getEntriesByType('resource') || [];
            for (var i = entries.length - 1; i >= 0; i--) {
                var u = entries[i].name || '';
                if (u.indexOf('googlevideo.com/videoplayback') !== -1) {
                    var cleanStreamUrl = u.replace(/&range=[^&]+/g, '');
                    if (!audioUrl && (u.indexOf('mime=audio') !== -1 || u.indexOf('itag=140') !== -1 || u.indexOf('itag=251') !== -1)) {
                        audioUrl = cleanStreamUrl;
                    }
                    if (!videoUrl && (u.indexOf('mime=video') !== -1 || u.indexOf('itag=18') !== -1 || u.indexOf('itag=22') !== -1 || u.indexOf('itag=137') !== -1)) {
                        videoUrl = cleanStreamUrl;
                    }
                }
            }
        } catch(e) {}

        // Strategy 2: Player Response inspection
        if (!audioUrl || !videoUrl) {
            try {
                var player = document.getElementById('movie_player');
                var pData = (player && typeof player.getPlayerResponse === 'function') ? player.getPlayerResponse() : (window.ytInitialPlayerResponse || null);
                if (pData && pData.streamingData) {
                    var allFmts = (pData.streamingData.adaptiveFormats || []).concat(pData.streamingData.formats || []);
                    for (var j = 0; j < allFmts.length; j++) {
                        var f = allFmts[j];
                        if (f && f.url) {
                            if (!audioUrl && (f.mimeType || '').indexOf('audio') !== -1) audioUrl = f.url;
                            if (!videoUrl && (f.mimeType || '').indexOf('video/mp4') !== -1) videoUrl = f.url;
                        }
                    }
                }
            } catch(e) {}
        }

        return { audio: audioUrl, video: videoUrl };
    }

    function triggerFileDownload(url, filename) {
        if (!url) return;
        var a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
        document.body.appendChild(a);
        a.click();
        setTimeout(function() {
            try { a.remove(); } catch(e) {}
        }, 1200);
    }

    function renderUI(streams) {
        var box = document.createElement('div');
        box.id = 'yt4mp3-helper-overlay';
        box.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:9999999;background:#0f172a;color:#ffffff;border-radius:16px;box-shadow:0 20px 40px rgba(0,0,0,0.6),0 0 0 1px rgba(255,255,255,0.1);padding:20px;max-width:380px;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;animation:yt4mp3Slide 0.3s ease-out;';

        var hasAudio = !!streams.audio;
        var hasVideo = !!streams.video;

        box.innerHTML = 
            '<style>@keyframes yt4mp3Slide{from{transform:translateY(30px);opacity:0}to{transform:translateY(0);opacity:1}}</style>' +
            '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">' +
                '<div style="display:flex;align-items:center;gap:8px;">' +
                    '<span style="background:#e11d48;color:#fff;font-size:11px;font-weight:bold;padding:3px 8px;border-radius:6px;letter-spacing:0.5px;">18+ UNLOCKED</span>' +
                    '<span style="font-weight:700;font-size:14px;color:#f8fafc;">YT4MP3 Helper</span>' +
                '</div>' +
                '<button id="yt4mp3-close-btn" style="background:transparent;border:none;color:#94a3b8;font-size:18px;cursor:pointer;line-height:1;padding:4px 8px;">✕</button>' +
            '</div>' +
            '<p style="font-size:12px;color:#cbd5e1;line-height:1.4;margin:0 0 14px 0;max-height:40px;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;">' +
                rawTitle +
            '</p>' +
            '<div style="display:flex;flex-direction:column;gap:10px;">' +
                '<button id="yt4mp3-dl-audio" style="background:#e11d48;color:#fff;font-weight:bold;font-size:13px;padding:12px 16px;border-radius:10px;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;box-shadow:0 4px 12px rgba(225,29,72,0.3);transition:all 0.2s;">' +
                    '<span>🎵</span> Download MP3 (Audio)' +
                '</button>' +
                '<button id="yt4mp3-dl-video" style="background:#334155;color:#fff;font-weight:bold;font-size:13px;padding:12px 16px;border-radius:10px;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;transition:all 0.2s;">' +
                    '<span>🎬</span> Download MP4 (Video)' +
                '</button>' +
            '</div>' +
            '<div id="yt4mp3-status" style="margin-top:12px;font-size:11px;color:#94a3b8;text-align:center;">' +
                (hasAudio ? '✓ Streams extracted successfully' : 'Buffering stream, click button to download...') +
            '</div>';

        document.body.appendChild(box);

        document.getElementById('yt4mp3-close-btn').onclick = function() { box.remove(); };

        var statusEl = document.getElementById('yt4mp3-status');

        document.getElementById('yt4mp3-dl-audio').onclick = function() {
            var curr = extractStreams();
            if (curr.audio) {
                statusEl.textContent = 'Starting MP3 download...';
                statusEl.style.color = '#34d399';
                triggerFileDownload(curr.audio, safeFilename + '.mp3');
            } else {
                var vid = document.querySelector('video');
                if (vid) { vid.muted = true; vid.play(); }
                statusEl.textContent = 'Buffering stream... please click again in 1 second.';
                statusEl.style.color = '#fbbf24';
            }
        };

        document.getElementById('yt4mp3-dl-video').onclick = function() {
            var curr = extractStreams();
            var target = curr.video || curr.audio;
            if (target) {
                statusEl.textContent = 'Starting MP4 download...';
                statusEl.style.color = '#34d399';
                triggerFileDownload(target, safeFilename + '.mp4');
            } else {
                var vid = document.querySelector('video');
                if (vid) { vid.muted = true; vid.play(); }
                statusEl.textContent = 'Buffering stream... please click again in 1 second.';
                statusEl.style.color = '#fbbf24';
            }
        };

        // If audio stream is already detected, auto-trigger MP3 download immediately!
        if (hasAudio) {
            statusEl.textContent = '✓ Auto-downloading MP3...';
            statusEl.style.color = '#34d399';
            triggerFileDownload(streams.audio, safeFilename + '.mp3');
        }
    }

    // Initial check
    var streams = extractStreams();
    if (!streams.audio && !streams.video) {
        // Try gentle play to load initial buffer
        try {
            var v = document.querySelector('video');
            if (v && v.paused) {
                v.muted = true;
                v.play().catch(function(){});
            }
        } catch(e) {}
        setTimeout(function() {
            renderUI(extractStreams());
        }, 600);
    } else {
        renderUI(streams);
    }
})();
