// MediaConvert Pro - High-Speed Client Engine with Live Conversion Modal

document.addEventListener('DOMContentLoaded', () => {
    const urlInput = document.getElementById('media-url-input');
    const pasteBtn = document.getElementById('paste-btn');
    const clearBtn = document.getElementById('clear-btn');
    const convertBtn = document.getElementById('convert-btn');
    const platformBadge = document.getElementById('platform-badge');
    const platformName = document.getElementById('platform-name');
    const platformIcon = document.getElementById('platform-icon');
    
    const loadingCard = document.getElementById('loading-card');
    const resultCard = document.getElementById('result-card');
    const errorCard = document.getElementById('error-card');
    const errorMessage = document.getElementById('error-message');

    // Result elements
    const resThumbnail = document.getElementById('res-thumbnail');
    const resTitle = document.getElementById('res-title');
    const resUploader = document.getElementById('res-uploader');
    const resDuration = document.getElementById('res-duration');
    const resViews = document.getElementById('res-views');
    const resPlatformTag = document.getElementById('res-platform-tag');

    const tabAudio = document.getElementById('tab-audio');
    const tabVideo = document.getElementById('tab-video');
    const audioFormatsContainer = document.getElementById('audio-formats');
    const videoFormatsContainer = document.getElementById('video-formats');

    // Modal elements
    const progressModal = document.getElementById('progress-modal');
    const modalCloseBtn = document.getElementById('modal-close-btn');
    const modalIconContainer = document.getElementById('modal-icon-container');
    const modalIcon = document.getElementById('modal-icon');
    const modalTitle = document.getElementById('modal-title');
    const modalSubtitle = document.getElementById('modal-subtitle');
    const modalProgressBar = document.getElementById('modal-progress-bar');
    const modalPctText = document.getElementById('modal-pct-text');
    const modalSpeedText = document.getElementById('modal-speed-text');
    const modalEtaText = document.getElementById('modal-eta-text');
    const modalStatusMsg = document.getElementById('modal-status-msg');
    const modalActionContainer = document.getElementById('modal-action-container');
    const modalDownloadLink = document.getElementById('modal-download-link');
    const modalBtnLabel = document.getElementById('modal-btn-label');

    let currentMediaData = null;
    let pollInterval = null;
    let isTaskCompleted = false;

    // Auto-detect platform icon and badge
    function updatePlatformIndicator(url) {
        const u = url.toLowerCase();
        let iconHtml = '<i class="fa-solid fa-link text-slate-400"></i>';
        let name = 'Auto-Detect';
        let badgeClass = 'bg-slate-100 text-slate-600 border-slate-200';

        if (u.includes('youtube.com') || u.includes('youtu.be')) {
            iconHtml = '<i class="fa-brands fa-youtube text-red-500"></i>';
            name = 'YouTube';
            badgeClass = 'bg-red-50 text-red-600 border-red-200';
        } else if (u.includes('tiktok.com')) {
            iconHtml = '<i class="fa-brands fa-tiktok text-slate-900"></i>';
            name = 'TikTok';
            badgeClass = 'bg-pink-50 text-pink-600 border-pink-200';
        } else if (u.includes('instagram.com')) {
            iconHtml = '<i class="fa-brands fa-instagram text-pink-500"></i>';
            name = 'Instagram';
            badgeClass = 'bg-purple-50 text-purple-600 border-purple-200';
        } else if (u.includes('facebook.com') || u.includes('fb.watch')) {
            iconHtml = '<i class="fa-brands fa-facebook text-blue-600"></i>';
            name = 'Facebook';
            badgeClass = 'bg-blue-50 text-blue-600 border-blue-200';
        } else if (u.includes('twitter.com') || u.includes('x.com')) {
            iconHtml = '<i class="fa-brands fa-x-twitter text-slate-800"></i>';
            name = 'Twitter/X';
            badgeClass = 'bg-slate-100 text-slate-800 border-slate-300';
        } else if (u.includes('soundcloud.com')) {
            iconHtml = '<i class="fa-brands fa-soundcloud text-orange-500"></i>';
            name = 'SoundCloud';
            badgeClass = 'bg-orange-50 text-orange-600 border-orange-200';
        }

        platformIcon.innerHTML = iconHtml;
        platformName.textContent = name;
        platformBadge.className = `inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border transition-all ${badgeClass}`;

        if (url.trim().length > 0) {
            clearBtn.classList.remove('hidden');
        } else {
            clearBtn.classList.add('hidden');
        }
    }

    urlInput.addEventListener('input', (e) => {
        updatePlatformIndicator(e.target.value);
    });

    pasteBtn.addEventListener('click', async () => {
        try {
            const text = await navigator.clipboard.readText();
            if (text) {
                urlInput.value = text;
                updatePlatformIndicator(text);
                startConversion();
            }
        } catch (err) {
            urlInput.focus();
        }
    });

    clearBtn.addEventListener('click', () => {
        urlInput.value = '';
        updatePlatformIndicator('');
        hideResults();
        urlInput.focus();
    });

    convertBtn.addEventListener('click', () => {
        startConversion();
    });

    urlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            startConversion();
        }
    });

    document.querySelectorAll('.sample-url-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const sample = btn.getAttribute('data-url');
            if (sample) {
                urlInput.value = sample;
                updatePlatformIndicator(sample);
                startConversion();
            }
        });
    });

    function hideResults() {
        loadingCard.classList.add('hidden');
        resultCard.classList.add('hidden');
        errorCard.classList.add('hidden');
    }

    async function startConversion() {
        const url = urlInput.value.trim();
        if (!url) {
            showError("Please enter or paste a valid video or audio URL.");
            return;
        }

        hideResults();
        loadingCard.classList.remove('hidden');
        convertBtn.disabled = true;
        convertBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin text-white"></i> <span>Analyzing Formats...</span>`;

        try {
            const response = await fetch('/api/extract', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.error || "Could not extract video details. Please verify the URL and try again.");
            }

            currentMediaData = data;
            renderResult(data);
        } catch (err) {
            showError(err.message);
        } finally {
            loadingCard.classList.add('hidden');
            convertBtn.disabled = false;
            convertBtn.innerHTML = `<i class="fa-solid fa-bolt text-white"></i> <span>Convert Now</span>`;
        }
    }

    function showError(msg) {
        hideResults();
        errorMessage.textContent = msg;
        errorCard.classList.remove('hidden');
    }

    function getResolutionBadgeStyle(res) {
        if (res.includes('4320') || res.includes('8K')) {
            return 'bg-gradient-to-r from-amber-500 to-rose-500 text-white font-black';
        } else if (res.includes('2160') || res.includes('4K')) {
            return 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-extrabold';
        } else if (res.includes('1440') || res.includes('2K')) {
            return 'bg-indigo-600 text-white font-bold';
        } else if (res.includes('1080')) {
            return 'bg-sky-600 text-white font-bold';
        } else if (res.includes('720')) {
            return 'bg-emerald-600 text-white font-bold';
        } else {
            return 'bg-slate-100 text-slate-700 font-semibold';
        }
    }

    function renderResult(data) {
        resThumbnail.src = data.thumbnail || 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=600&q=80';
        resTitle.textContent = data.title;
        resUploader.textContent = data.uploader || 'Creator';
        resDuration.textContent = data.duration || '00:00';
        resViews.textContent = data.views ? `${data.views} views` : '';
        resPlatformTag.textContent = data.platform.name;

        // Render Audio options
        audioFormatsContainer.innerHTML = '';
        data.audio_formats.forEach((fmt, index) => {
            const card = document.createElement('div');
            card.className = `format-card p-3.5 flex items-center justify-between cursor-pointer border ${index === 0 ? 'active' : ''}`;
            card.innerHTML = `
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 font-bold text-sm flex-shrink-0">
                        <i class="fa-solid fa-music"></i>
                    </div>
                    <div>
                        <div class="flex items-center gap-2 flex-wrap">
                            <span class="font-bold text-slate-800 text-sm">${fmt.label}</span>
                            ${fmt.is_popular ? '<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-indigo-600 text-white shadow-sm">320k Studio</span>' : ''}
                        </div>
                        <p class="text-xs text-slate-500 mt-0.5">Format: <span class="uppercase font-semibold text-slate-700">${fmt.format}</span> • Quality: <span class="font-medium text-slate-600">${fmt.tag}</span></p>
                    </div>
                </div>
                <div>
                    <button class="download-action-btn px-4 py-2 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition-all flex items-center gap-1.5 shadow-sm shadow-indigo-200 flex-shrink-0" 
                        data-format="${fmt.format}" data-quality="${fmt.quality}">
                        <i class="fa-solid fa-download"></i>
                        <span>Download</span>
                    </button>
                </div>
            `;

            card.querySelector('.download-action-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                openDownloadJob(fmt.format, fmt.quality, fmt.label);
            });

            audioFormatsContainer.appendChild(card);
        });

        // Render Video options
        videoFormatsContainer.innerHTML = '';
        data.video_formats.forEach((fmt, index) => {
            const card = document.createElement('div');
            const badgeClass = getResolutionBadgeStyle(fmt.badge);
            card.className = `format-card p-3.5 flex items-center justify-between cursor-pointer border ${index === 0 ? 'active' : ''}`;
            card.innerHTML = `
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-sky-50 border border-sky-100 flex items-center justify-center text-sky-600 font-bold text-sm flex-shrink-0">
                        <i class="fa-solid fa-video"></i>
                    </div>
                    <div>
                        <div class="flex items-center gap-2 flex-wrap">
                            <span class="font-bold text-slate-800 text-sm">${fmt.label}</span>
                            <span class="px-2 py-0.5 rounded-full text-[10px] shadow-sm ${badgeClass}">${fmt.badge}</span>
                            ${fmt.size ? `<span class="text-[11px] font-mono font-medium text-slate-400">~${fmt.size}</span>` : ''}
                        </div>
                        <p class="text-xs text-slate-500 mt-0.5">Format: <span class="uppercase font-semibold text-slate-700">${fmt.format}</span> • Quality: ${fmt.tag}</p>
                    </div>
                </div>
                <div>
                    <button class="download-action-btn px-4 py-2 rounded-xl text-xs font-bold text-white bg-sky-600 hover:bg-sky-700 active:scale-95 transition-all flex items-center gap-1.5 shadow-sm shadow-sky-200 flex-shrink-0" 
                        data-format="${fmt.format}" data-quality="${fmt.quality}">
                        <i class="fa-solid fa-download"></i>
                        <span>Download</span>
                    </button>
                </div>
            `;

            card.querySelector('.download-action-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                openDownloadJob(fmt.format, fmt.quality, fmt.label);
            });

            videoFormatsContainer.appendChild(card);
        });

        resultCard.classList.remove('hidden');
        resultCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    // Format Tab Switching
    tabAudio.addEventListener('click', () => {
        tabAudio.className = "flex-1 py-2.5 px-4 text-xs sm:text-sm font-bold rounded-xl bg-white text-indigo-600 shadow-sm border border-slate-200 transition-all flex items-center justify-center gap-2";
        tabVideo.className = "flex-1 py-2.5 px-4 text-xs sm:text-sm font-semibold rounded-xl text-slate-500 hover:text-slate-800 transition-all flex items-center justify-center gap-2";
        audioFormatsContainer.classList.remove('hidden');
        videoFormatsContainer.classList.add('hidden');
    });

    tabVideo.addEventListener('click', () => {
        tabVideo.className = "flex-1 py-2.5 px-4 text-xs sm:text-sm font-bold rounded-xl bg-white text-sky-600 shadow-sm border border-slate-200 transition-all flex items-center justify-center gap-2";
        tabAudio.className = "flex-1 py-2.5 px-4 text-xs sm:text-sm font-semibold rounded-xl text-slate-500 hover:text-slate-800 transition-all flex items-center justify-center gap-2";
        videoFormatsContainer.classList.remove('hidden');
        audioFormatsContainer.classList.add('hidden');
    });

    // Start Async Conversion Job and Download EXACTLY ONCE to PC
    async function openDownloadJob(format, quality, label) {
        if (!currentMediaData) return;

        // Reset state
        if (pollInterval) {
            clearInterval(pollInterval);
            pollInterval = null;
        }
        isTaskCompleted = false;
        
        progressModal.classList.remove('hidden');
        modalTitle.textContent = label;
        modalSubtitle.textContent = currentMediaData.title;
        modalProgressBar.style.width = '6%';
        modalPctText.textContent = '6%';
        modalSpeedText.textContent = '';
        modalEtaText.textContent = '';
        modalStatusMsg.textContent = 'Connecting to high-speed stream...';
        modalActionContainer.classList.add('hidden');
        modalIconContainer.className = "w-16 h-16 rounded-2xl bg-indigo-50 border border-indigo-100 text-indigo-600 flex items-center justify-center text-2xl mx-auto mb-4";
        modalIcon.className = "fa-solid fa-cog fa-spin";

        try {
            const resp = await fetch('/api/convert', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: currentMediaData.url,
                    format: format,
                    quality: quality
                })
            });

            const resData = await resp.json();
            if (!resp.ok || !resData.success) {
                throw new Error(resData.error || "Failed to start conversion job");
            }

            const taskId = resData.task_id;
            
            // Poll progress
            pollInterval = setInterval(async () => {
                if (isTaskCompleted) {
                    if (pollInterval) clearInterval(pollInterval);
                    return;
                }

                try {
                    const progResp = await fetch(`/api/progress/${taskId}`);
                    if (!progResp.ok) return;

                    const progData = await progResp.json();
                    
                    modalProgressBar.style.width = `${progData.progress}%`;
                    modalPctText.textContent = `${progData.progress}%`;
                    modalStatusMsg.textContent = progData.message || 'Processing...';

                    if (progData.speed) {
                        modalSpeedText.textContent = `⚡ ${progData.speed}`;
                    }
                    if (progData.eta) {
                        modalEtaText.textContent = `⏱️ ETA: ${progData.eta}`;
                    }

                    if (progData.status === 'completed' && !isTaskCompleted) {
                        isTaskCompleted = true;
                        if (pollInterval) clearInterval(pollInterval);

                        modalProgressBar.style.width = '100%';
                        modalPctText.textContent = '100%';
                        modalIconContainer.className = "w-16 h-16 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-600 flex items-center justify-center text-2xl mx-auto mb-4";
                        modalIcon.className = "fa-solid fa-circle-check";
                        modalStatusMsg.textContent = `Downloaded to PC! (Size: ${progData.size_mb} MB)`;
                        modalStatusMsg.className = "text-xs font-bold text-emerald-700 mb-6 bg-emerald-50 py-2 px-3 rounded-xl border border-emerald-200";
                        
                        modalDownloadLink.href = progData.download_url;
                        modalDownloadLink.download = progData.file_name;
                        modalBtnLabel.textContent = `Save Again (${progData.size_mb} MB)`;
                        modalActionContainer.classList.remove('hidden');

                        // Trigger SINGLE direct browser download to PC
                        window.location.href = progData.download_url;
                        
                    } else if (progData.status === 'error') {
                        isTaskCompleted = true;
                        if (pollInterval) clearInterval(pollInterval);

                        modalIconContainer.className = "w-16 h-16 rounded-2xl bg-red-50 border border-red-200 text-red-600 flex items-center justify-center text-2xl mx-auto mb-4";
                        modalIcon.className = "fa-solid fa-triangle-exclamation";
                        modalStatusMsg.textContent = progData.error || 'Conversion error';
                        modalStatusMsg.className = "text-xs font-semibold text-red-600 mb-6 bg-red-50 py-2 px-3 rounded-xl border border-red-200";
                    }
                } catch (e) {
                    console.error("Polling error:", e);
                }
            }, 600);

        } catch (err) {
            if (pollInterval) clearInterval(pollInterval);
            modalIcon.className = "fa-solid fa-triangle-exclamation";
            modalStatusMsg.textContent = err.message;
        }
    }

    modalCloseBtn.addEventListener('click', () => {
        if (pollInterval) clearInterval(pollInterval);
        progressModal.classList.add('hidden');
    });

    progressModal.addEventListener('click', (e) => {
        if (e.target === progressModal) {
            if (pollInterval) clearInterval(pollInterval);
            progressModal.classList.add('hidden');
        }
    });

    // FAQ Accordion
    document.querySelectorAll('.faq-question').forEach(btn => {
        btn.addEventListener('click', () => {
            const answer = btn.nextElementSibling;
            const icon = btn.querySelector('.faq-chevron');
            const isHidden = answer.classList.contains('hidden');

            document.querySelectorAll('.faq-answer').forEach(a => a.classList.add('hidden'));
            document.querySelectorAll('.faq-chevron').forEach(i => i.style.transform = 'rotate(0deg)');

            if (isHidden) {
                answer.classList.remove('hidden');
                icon.style.transform = 'rotate(180deg)';
            }
        });
    });
});
