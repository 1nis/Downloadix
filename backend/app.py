from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
import yt_dlp
import os
import re
import uuid
import threading
import time
import json
import requests as http_requests

app = Flask(__name__)
CORS(app)

# Settings file path
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'settings.json')

# Default settings
DEFAULT_SETTINGS = {
    'download_folder': os.path.join(os.path.dirname(__file__), 'downloads')
}

# In-memory storage for download progress and control
progress_data = {}
download_files = {}
download_threads = {}
cancel_flags = {}
download_history = []  # Session history of completed/cancelled/error downloads

def load_settings():
    """Load settings from file or return defaults."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return {**DEFAULT_SETTINGS, **json.load(f)}
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Save settings to file."""
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2)

def get_downloads_dir():
    """Get the current downloads directory."""
    settings = load_settings()
    downloads_dir = settings.get('download_folder', DEFAULT_SETTINGS['download_folder'])
    os.makedirs(downloads_dir, exist_ok=True)
    return downloads_dir

# Create default downloads directory
os.makedirs(get_downloads_dir(), exist_ok=True)

def detect_platform(url):
    """Detect the platform from the URL."""
    if 'youtube.com' in url or 'youtu.be' in url:
        return 'youtube'
    elif 'twitter.com' in url or 'x.com' in url:
        return 'twitter'
    elif 'tiktok.com' in url:
        return 'tiktok'
    elif 'instagram.com' in url or 'instagr.am' in url:
        return 'instagram'
    return 'unknown'

def format_duration(seconds):
    """Format duration in seconds to MM:SS or HH:MM:SS."""
    if seconds is None:
        return 'N/A'
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"

def format_eta(seconds):
    """Format ETA in seconds to human readable format."""
    if seconds is None or seconds <= 0:
        return '--:--'
    seconds = int(seconds)
    if seconds >= 3600:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:02d}"
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"

def format_speed(bytes_per_second):
    """Format speed in bytes/second to human readable format."""
    if bytes_per_second is None or bytes_per_second <= 0:
        return '0 B/s'
    if bytes_per_second >= 1024 * 1024:
        return f"{bytes_per_second / (1024 * 1024):.1f} MB/s"
    elif bytes_per_second >= 1024:
        return f"{bytes_per_second / 1024:.1f} KB/s"
    return f"{bytes_per_second:.0f} B/s"

def format_bytes(bytes_value):
    """Format bytes to human readable format."""
    if bytes_value is None or bytes_value <= 0:
        return '0 B'
    if bytes_value >= 1024 * 1024 * 1024:
        return f"{bytes_value / (1024 * 1024 * 1024):.2f} GB"
    elif bytes_value >= 1024 * 1024:
        return f"{bytes_value / (1024 * 1024):.2f} MB"
    elif bytes_value >= 1024:
        return f"{bytes_value / 1024:.2f} KB"
    return f"{bytes_value:.0f} B"

def cleanup_old_files():
    """Remove files older than 1 hour from downloads directory."""
    while True:
        time.sleep(3600)  # Check every hour
        now = time.time()
        downloads_dir = get_downloads_dir()
        for filename in os.listdir(downloads_dir):
            filepath = os.path.join(downloads_dir, filename)
            if os.path.isfile(filepath):
                if now - os.path.getmtime(filepath) > 3600:
                    try:
                        os.remove(filepath)
                    except Exception:
                        pass

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

@app.route('/api/info', methods=['GET'])
def get_video_info():
    """Get video information from URL."""
    url = request.args.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    platform = detect_platform(url)
    if platform == 'unknown':
        return jsonify({'error': 'Unsupported platform. Use YouTube, X/Twitter, TikTok, or Instagram URLs.'}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }

    # Add cookies for Instagram if needed
    if platform == 'instagram':
        ydl_opts['http_headers'] = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Get available formats
            formats = []
            seen_qualities = set()

            if 'formats' in info:
                for f in info['formats']:
                    height = f.get('height')
                    if height and height >= 360:
                        quality = f"{height}p"
                        if quality not in seen_qualities:
                            seen_qualities.add(quality)
                            # For YouTube, we need video + audio
                            if platform == 'youtube':
                                format_id = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"
                            else:
                                format_id = f.get('format_id', 'best')
                            formats.append({
                                'quality': quality,
                                'format_id': format_id,
                                'height': height
                            })

            # Sort by quality (height) descending
            formats.sort(key=lambda x: x.get('height', 0), reverse=True)

            # Remove height from response
            for f in formats:
                f.pop('height', None)

            # If no formats found, add a default
            if not formats:
                formats = [{'quality': 'best', 'format_id': 'best'}]

            return jsonify({
                'title': info.get('title', 'Unknown'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': format_duration(info.get('duration')),
                'platform': platform,
                'formats': formats,
                'uploader': info.get('uploader', 'Unknown')
            })

    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if 'Private video' in error_msg:
            return jsonify({'error': 'This video is private'}), 400
        elif 'Video unavailable' in error_msg:
            return jsonify({'error': 'This video is unavailable'}), 400
        elif 'login' in error_msg.lower():
            return jsonify({'error': 'This content requires login'}), 400
        return jsonify({'error': f'Could not fetch video info: {error_msg}'}), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/download/start', methods=['POST'])
def start_download():
    """Start a download and return a download ID for progress tracking."""
    data = request.get_json()
    url = data.get('url')
    format_id = data.get('format', 'best')
    title = data.get('title', 'Unknown')
    audio_only = data.get('audio_only', False)

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    platform = detect_platform(url)
    if platform == 'unknown':
        return jsonify({'error': 'Unsupported platform'}), 400

    download_id = str(uuid.uuid4())

    # Initialize cancel flag
    cancel_flags[download_id] = False

    # Initialize progress data
    progress_data[download_id] = {
        'status': 'starting',
        'downloaded_bytes': 0,
        'total_bytes': 0,
        'speed': 0,
        'eta': 0,
        'percent': 0,
        'filename': None,
        'title': title,
        'platform': platform,
        'audio_only': audio_only,
        'error': None
    }

    def progress_hook(d):
        # Check if cancelled
        if cancel_flags.get(download_id, False):
            raise Exception('Download cancelled by user')

        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            speed = d.get('speed', 0)
            eta = d.get('eta', 0)

            percent = 0
            if total and total > 0:
                percent = (downloaded / total) * 100

            progress_data[download_id] = {
                'status': 'downloading',
                'downloaded_bytes': downloaded,
                'total_bytes': total,
                'speed': speed,
                'eta': eta,
                'percent': percent,
                'downloaded_str': format_bytes(downloaded),
                'total_str': format_bytes(total),
                'speed_str': format_speed(speed),
                'eta_str': format_eta(eta),
                'filename': None,
                'title': title,
                'platform': platform,
                'error': None
            }
        elif d['status'] == 'finished':
            progress_data[download_id]['status'] = 'processing'

    def download_thread():
        try:
            # Check if cancelled before starting
            if cancel_flags.get(download_id, False):
                progress_data[download_id]['status'] = 'cancelled'
                return

            downloads_dir = get_downloads_dir()
            file_id = str(uuid.uuid4())
            output_template = os.path.join(downloads_dir, f'{file_id}.%(ext)s')

            if audio_only:
                # Audio-only download (MP3)
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': output_template,
                    'quiet': True,
                    'no_warnings': True,
                    'progress_hooks': [progress_hook],
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
            else:
                # Video download
                ydl_opts = {
                    'format': format_id,
                    'outtmpl': output_template,
                    'quiet': True,
                    'no_warnings': True,
                    'merge_output_format': 'mp4',
                    'progress_hooks': [progress_hook],
                }

            # Add headers for Instagram/TikTok
            if platform in ['instagram', 'tiktok']:
                ydl_opts['http_headers'] = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

                # Check if cancelled
                if cancel_flags.get(download_id, False):
                    # Clean up downloaded file
                    for filename in os.listdir(downloads_dir):
                        if filename.startswith(file_id):
                            try:
                                os.remove(os.path.join(downloads_dir, filename))
                            except:
                                pass
                    progress_data[download_id]['status'] = 'cancelled'
                    return

                # Find the downloaded file
                downloaded_file = None
                for filename in os.listdir(downloads_dir):
                    if filename.startswith(file_id):
                        downloaded_file = os.path.join(downloads_dir, filename)
                        break

                if not downloaded_file or not os.path.exists(downloaded_file):
                    progress_data[download_id]['status'] = 'error'
                    progress_data[download_id]['error'] = 'Download failed'
                    return

                # Get video title for filename
                video_title = info.get('title', 'video')
                safe_title = re.sub(r'[<>:"/\\|?*]', '', video_title)[:100]
                ext = os.path.splitext(downloaded_file)[1]
                download_name = f"{safe_title}{ext}"

                # Store file info
                download_files[download_id] = {
                    'path': downloaded_file,
                    'name': download_name
                }

                progress_data[download_id]['status'] = 'completed'
                progress_data[download_id]['percent'] = 100
                progress_data[download_id]['filename'] = download_name

        except Exception as e:
            error_msg = str(e)
            if 'cancelled' in error_msg.lower():
                progress_data[download_id]['status'] = 'cancelled'
            else:
                progress_data[download_id]['status'] = 'error'
                progress_data[download_id]['error'] = f'Download failed: {error_msg}'

    # Start download in background thread
    thread = threading.Thread(target=download_thread, daemon=True)
    download_threads[download_id] = thread
    thread.start()

    return jsonify({
        'download_id': download_id,
        'title': title,
        'platform': platform,
        'audio_only': audio_only
    })

@app.route('/api/download/cancel/<download_id>', methods=['POST'])
def cancel_download(download_id):
    """Cancel an ongoing download."""
    if download_id not in progress_data:
        return jsonify({'error': 'Download not found'}), 404

    # Set cancel flag
    cancel_flags[download_id] = True

    # Update status
    if progress_data[download_id]['status'] not in ['completed', 'error', 'cancelled']:
        progress_data[download_id]['status'] = 'cancelling'

    return jsonify({'success': True, 'message': 'Download cancellation requested'})

@app.route('/api/download/progress/<download_id>')
def download_progress(download_id):
    """SSE endpoint for download progress."""
    def generate():
        while True:
            if download_id in progress_data:
                data = progress_data[download_id]
                yield f"data: {json.dumps(data)}\n\n"

                if data['status'] in ['completed', 'error', 'cancelled']:
                    break
            else:
                yield f"data: {json.dumps({'status': 'not_found', 'error': 'Download not found'})}\n\n"
                break

            time.sleep(0.5)

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )

@app.route('/api/download/list')
def list_downloads():
    """List all active and recent downloads."""
    downloads = []
    for download_id, data in progress_data.items():
        downloads.append({
            'id': download_id,
            'title': data.get('title', 'Unknown'),
            'platform': data.get('platform', 'unknown'),
            'status': data.get('status', 'unknown'),
            'percent': data.get('percent', 0),
            'speed_str': data.get('speed_str', '0 B/s'),
            'eta_str': data.get('eta_str', '--:--'),
            'downloaded_str': data.get('downloaded_str', '0 B'),
            'total_str': data.get('total_str', '0 B'),
            'error': data.get('error')
        })
    return jsonify(downloads)

@app.route('/api/download/clear', methods=['POST'])
def clear_completed():
    """Clear completed, cancelled, and errored downloads from the list and add to history."""
    to_remove = []
    for download_id, data in progress_data.items():
        if data['status'] in ['completed', 'cancelled', 'error']:
            to_remove.append(download_id)
            # Add to history
            file_info = download_files.get(download_id, {})
            history_entry = {
                'id': download_id,
                'title': data.get('title', 'Unknown'),
                'platform': data.get('platform', 'unknown'),
                'status': data.get('status'),
                'total_str': data.get('total_str', '0 B'),
                'filename': data.get('filename'),
                'completed_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'error': data.get('error')
            }
            download_history.insert(0, history_entry)

    for download_id in to_remove:
        progress_data.pop(download_id, None)
        download_files.pop(download_id, None)
        cancel_flags.pop(download_id, None)
        download_threads.pop(download_id, None)

    # Keep only the last 50 entries in history
    while len(download_history) > 50:
        download_history.pop()

    return jsonify({'cleared': len(to_remove)})

@app.route('/api/download/history')
def get_download_history():
    """Get download history for the current session."""
    return jsonify(download_history)

@app.route('/api/download/history/clear', methods=['POST'])
def clear_history():
    """Clear download history."""
    download_history.clear()
    return jsonify({'success': True})

@app.route('/api/download/file/<download_id>')
def download_file(download_id):
    """Download the completed file."""
    if download_id not in download_files:
        return jsonify({'error': 'File not found'}), 404

    file_info = download_files[download_id]
    filepath = file_info['path']
    filename = file_info['name']

    if not os.path.exists(filepath):
        return jsonify({'error': 'File no longer exists'}), 404

    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename
    )

@app.route('/api/download/thumbnail', methods=['POST'])
def download_thumbnail():
    """Download thumbnail image from URL."""
    data = request.get_json()
    thumbnail_url = data.get('url')
    title = data.get('title', 'thumbnail')

    if not thumbnail_url:
        return jsonify({'error': 'Thumbnail URL is required'}), 400

    try:
        # Download the thumbnail
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = http_requests.get(thumbnail_url, headers=headers, timeout=30)
        response.raise_for_status()

        # Determine extension from content type
        content_type = response.headers.get('Content-Type', 'image/jpeg')
        ext = '.jpg'
        if 'png' in content_type:
            ext = '.png'
        elif 'webp' in content_type:
            ext = '.webp'
        elif 'gif' in content_type:
            ext = '.gif'

        # Save to downloads directory
        downloads_dir = get_downloads_dir()
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title)[:100]
        filename = f"{safe_title}_thumbnail{ext}"
        filepath = os.path.join(downloads_dir, filename)

        with open(filepath, 'wb') as f:
            f.write(response.content)

        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename
        )

    except http_requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to download thumbnail: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current settings."""
    settings = load_settings()
    return jsonify(settings)

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update settings."""
    data = request.get_json()

    download_folder = data.get('download_folder')

    if download_folder:
        # Validate that the folder exists or can be created
        try:
            os.makedirs(download_folder, exist_ok=True)
            if not os.path.isdir(download_folder):
                return jsonify({'error': 'Invalid folder path'}), 400
        except Exception as e:
            return jsonify({'error': f'Cannot create folder: {str(e)}'}), 400

    settings = load_settings()

    if download_folder:
        settings['download_folder'] = download_folder

    save_settings(settings)

    return jsonify(settings)

# Keep the old download endpoint for backward compatibility
@app.route('/api/download', methods=['GET'])
def download_video():
    """Download video and return the file (legacy endpoint)."""
    url = request.args.get('url')
    format_id = request.args.get('format', 'best')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    platform = detect_platform(url)
    if platform == 'unknown':
        return jsonify({'error': 'Unsupported platform'}), 400

    downloads_dir = get_downloads_dir()
    file_id = str(uuid.uuid4())
    output_template = os.path.join(downloads_dir, f'{file_id}.%(ext)s')

    ydl_opts = {
        'format': format_id,
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
    }

    # Add headers for Instagram/TikTok
    if platform in ['instagram', 'tiktok']:
        ydl_opts['http_headers'] = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            # Find the downloaded file
            downloaded_file = None
            for filename in os.listdir(downloads_dir):
                if filename.startswith(file_id):
                    downloaded_file = os.path.join(downloads_dir, filename)
                    break

            if not downloaded_file or not os.path.exists(downloaded_file):
                return jsonify({'error': 'Download failed'}), 500

            # Get video title for filename
            title = info.get('title', 'video')
            # Clean filename
            safe_title = re.sub(r'[<>:"/\\|?*]', '', title)[:100]
            ext = os.path.splitext(downloaded_file)[1]
            download_name = f"{safe_title}{ext}"

            return send_file(
                downloaded_file,
                as_attachment=True,
                download_name=download_name
            )

    except yt_dlp.utils.DownloadError as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
