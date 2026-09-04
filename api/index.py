from flask import Flask, request, jsonify, render_template, send_file
import yt_dlp
import os
import tempfile
import requests
from urllib.parse import urlparse

app = Flask(__name__, 
            template_folder='../templates', 
            static_folder='../static')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    format_type = data.get('format')

    if not url:
        return jsonify({'error': 'URL required'}), 400

    # تحقق من صحة الرابط
    if not (url.startswith('http://') or url.startswith('https://')):
        return jsonify({'error': 'Invalid URL'}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'no_color': True,
        'geo_bypass': True,
        'socket_timeout': 30,
        'retries': 10,
    }

    if format_type == 'mp3':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:  # mp4
        ydl_opts.update({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # استخرج المعلومات
            info = ydl.extract_info(url, download=False)
            
            if info is None:
                return jsonify({'error': 'Could not extract video info'}), 400

            title = info.get('title', 'video')
            
            if format_type == 'mp3':
                # جيب رابط الصوت
                audio_url = None
                for f in info.get('formats', []):
                    if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                        audio_url = f.get('url')
                        if audio_url:
                            break
                
                if not audio_url:
                    return jsonify({'error': 'No audio stream found'}), 400
                
                return jsonify({
                    'title': title,
                    'download_url': audio_url,
                    'format': 'mp3',
                    'thumbnail': info.get('thumbnail', ''),
                    'duration': info.get('duration', 0),
                    'views': info.get('view_count', 0)
                })
            else:
                # جيب رابط الفيديو
                video_url = None
                for f in info.get('formats', []):
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        if f.get('ext') == 'mp4':
                            video_url = f.get('url')
                            if video_url:
                                break
                
                if not video_url:
                    return jsonify({'error': 'No video stream found'}), 400
                
                return jsonify({
                    'title': title,
                    'download_url': video_url,
                    'format': 'mp4',
                    'thumbnail': info.get('thumbnail', ''),
                    'duration': info.get('duration', 0),
                    'views': info.get('view_count', 0)
                })
                
    except yt_dlp.utils.DownloadError as e:
        return jsonify({'error': f'Download error: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

# Route إضافية للتحقق من الصحة
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
