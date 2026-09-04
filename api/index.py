from flask import Flask, request, jsonify, render_template
import yt_dlp
import json

app = Flask(__name__, template_folder='../templates', static_folder='../static')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    format_type = data.get('format')  # 'mp3' or 'mp4'

    if not url:
        return jsonify({'error': 'URL required'}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
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
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            # Extract download URLs
            if format_type == 'mp3':
                # Get audio only URL
                audio_url = None
                for f in formats:
                    if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                        audio_url = f.get('url')
                        break
                return jsonify({
                    'title': info.get('title'),
                    'download_url': audio_url,
                    'format': 'mp3'
                })
            else:
                # Get best video URL
                video_url = None
                for f in formats:
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        if f.get('ext') == 'mp4':
                            video_url = f.get('url')
                            break
                return jsonify({
                    'title': info.get('title'),
                    'download_url': video_url,
                    'format': 'mp4'
                })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel handler
def handler(request, context):
    return app(request, context)

# Local server
if __name__ == '__main__':
    app.run(debug=True)
