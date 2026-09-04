document.addEventListener('DOMContentLoaded', () => {
    const urlInput = document.getElementById('urlInput');
    const fetchBtn = document.getElementById('fetchBtn');
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');
    const videoTitle = document.getElementById('videoTitle');
    const downloadBtn = document.getElementById('downloadBtn');
    const playlistContainer = document.getElementById('playlistContainer');

    let currentData = null;

    fetchBtn.addEventListener('click', async () => {
        const url = urlInput.value.trim();
        if (!url) {
            alert('الرجاء إدخال رابط صحيح');
            return;
        }

        const format = document.querySelector('input[name="format"]:checked').value;

        loading.classList.remove('hidden');
        result.classList.add('hidden');
        playlistContainer.innerHTML = '';

        try {
            const response = await fetch('/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url, format })
            });

            const data = await response.json();

            if (data.error) {
                alert('خطأ: ' + data.error);
                loading.classList.add('hidden');
                return;
            }

            currentData = data;
            videoTitle.textContent = data.title || 'فيديو بدون عنوان';
            downloadBtn.dataset.url = data.download_url;

            // Check if playlist
            if (data.playlist) {
                data.playlist.forEach((item, index) => {
                    const div = document.createElement('div');
                    div.className = 'playlist-item';
                    div.innerHTML = `
                        <span>${index + 1}. ${item.title}</span>
                        <button class="btn-download-small" data-url="${item.url}">⬇️</button>
                    `;
                    playlistContainer.appendChild(div);
                });
            }

            result.classList.remove('hidden');
            loading.classList.add('hidden');

        } catch (error) {
            alert('حدث خطأ في الاتصال بالخادم');
            loading.classList.add('hidden');
            console.error(error);
        }
    });

    downloadBtn.addEventListener('click', () => {
        const url = downloadBtn.dataset.url;
        if (url) {
            window.open(url, '_blank');
        } else {
            alert('لا يوجد رابط للتحميل');
        }
    });

    // Enter key support
    urlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') fetchBtn.click();
    });
});