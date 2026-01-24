# Downloadix

A modern web application for downloading videos from YouTube, X/Twitter, TikTok, and Instagram.

## Features

- **Multi-platform support**: Download videos from YouTube, X/Twitter, TikTok, and Instagram
- **Real-time download progress** with:
  - Progress bar with percentage
  - Downloaded size / Total size
  - Download speed
  - Estimated time remaining (ETA)
- **Cancel downloads**: Abort any ongoing download with the cancel button
- **Multiple simultaneous downloads**: Download several videos at the same time
- **Downloads Manager**: A floating panel to manage and monitor all downloads
  - View all active and completed downloads
  - Cancel any download in progress
  - Re-download completed files
  - Clear completed downloads
- **Quality selection** (360p, 480p, 720p, 1080p, etc.)
- **Configurable download folder**
- **Clean and modern UI**

## Requirements

- Python 3.8+
- Node.js 16+
- FFmpeg (required for merging video/audio streams)

### Installing FFmpeg

**Windows:**
```bash
# Using winget
winget install FFmpeg

# Or using Chocolatey
choco install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

## Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

### Development Mode

1. Start the backend server (in one terminal):
```bash
cd backend
python app.py
```
The backend will run on http://localhost:5000

2. Start the frontend dev server (in another terminal):
```bash
cd frontend
npm run dev
```
The frontend will run on http://localhost:5173

3. Open your browser and navigate to http://localhost:5173

### Production Build

1. Build the frontend:
```bash
cd frontend
npm run build
```

2. Serve the built files with the Flask backend or a web server like Nginx.

## Usage

1. **Paste a URL**: Enter a video URL from YouTube, X/Twitter, TikTok, or Instagram in the input field and click "Fetch".

2. **Select Quality**: Choose the video quality from the available options.

3. **Download**: Click the "Download Video" button. You'll see real-time progress including:
   - Download percentage
   - Downloaded size / Total size
   - Current download speed
   - Estimated time remaining

4. **Cancel a Download**: While downloading, click the "Cancel" button to abort the download.

5. **Multiple Downloads**: You can start multiple downloads simultaneously. Use the Downloads Manager (floating button at bottom-right) to monitor and manage all downloads.

6. **Downloads Manager**: Click the download icon at the bottom-right corner to:
   - See all active and completed downloads
   - Cancel any download in progress
   - Download completed files again
   - Clear completed/cancelled downloads from the list

7. **Configure Download Folder** (optional): Click the settings icon (gear) in the top-right corner to change where videos are saved.

## Supported Platforms

| Platform | URL Examples |
|----------|-------------|
| YouTube | `https://youtube.com/watch?v=...`, `https://youtu.be/...` |
| X/Twitter | `https://twitter.com/.../status/...`, `https://x.com/.../status/...` |
| TikTok | `https://tiktok.com/@.../video/...` |
| Instagram | `https://instagram.com/p/...`, `https://instagram.com/reel/...` |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/info` | GET | Get video information from URL |
| `/api/download/start` | POST | Start a download and get download ID |
| `/api/download/progress/<id>` | GET | SSE endpoint for download progress |
| `/api/download/cancel/<id>` | POST | Cancel an ongoing download |
| `/api/download/file/<id>` | GET | Download the completed file |
| `/api/download/list` | GET | List all active and recent downloads |
| `/api/download/clear` | POST | Clear completed/cancelled downloads |
| `/api/settings` | GET | Get current settings |
| `/api/settings` | POST | Update settings |
| `/api/health` | GET | Health check |

## Project Structure

```
Downloadix/
├── backend/
│   ├── app.py              # Flask backend
│   ├── requirements.txt    # Python dependencies
│   ├── settings.json       # User settings (auto-generated)
│   └── downloads/          # Default download folder
├── frontend/
│   ├── src/
│   │   ├── App.vue         # Main application component
│   │   ├── main.js         # Vue entry point
│   │   ├── assets/
│   │   │   └── style.css   # Global styles
│   │   └── components/
│   │       ├── VideoForm.vue        # URL input form
│   │       ├── VideoPreview.vue     # Video preview card
│   │       ├── DownloadBtn.vue      # Download button with progress
│   │       ├── ProgressBar.vue      # Progress bar component
│   │       ├── Settings.vue         # Settings panel
│   │       └── DownloadsManager.vue # Multiple downloads manager
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Technologies

- **Backend**: Flask, yt-dlp
- **Frontend**: Vue 3, Vite
- **Streaming**: Server-Sent Events (SSE) for real-time progress

## Notes

- **Instagram**: Some Instagram content may require login. Public posts should work without authentication.
- **TikTok**: Works with public videos.
- **Rate Limiting**: Be mindful of rate limits when downloading many videos in quick succession.

## License

MIT
