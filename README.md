# Downloadix

A modern web application for downloading videos from YouTube, X/Twitter, TikTok, and Instagram.

## Features

- **Multi-platform support**: Download videos from YouTube, X/Twitter, TikTok, and Instagram
- **Video & Audio downloads**:
  - Download videos in MP4 format
  - Download audio only in MP3 format (192 kbps)
- **Thumbnail download**: Download video thumbnails with one click
- **Auto-download to browser**: Files are automatically sent to your browser when ready
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
  - Download history with thumbnails
- **Quality selection** (360p, 480p, 720p, 1080p, etc.)
- **Modern UI**: Dark theme with glassmorphism design, neon accents, and smooth animations
- **One-click launch**: Start both servers with a single script

## Requirements

- Python 3.8+
- Node.js 16+
- FFmpeg (required for merging video/audio streams and MP3 conversion)

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

### Quick Start (Recommended)

Use the provided launch scripts to start both servers at once:

**Windows (Batch):**
```bash
# Double-click start.bat or run:
start.bat
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy Bypass -File start.ps1
```

The script will:
1. Check that Python and Node.js are installed
2. Start the backend server (port 5000)
3. Start the frontend server (port 3000)
4. Open your browser automatically
5. Press any key to stop both servers

### Manual Start (Development Mode)

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
The frontend will run on http://localhost:3000

3. Open your browser and navigate to http://localhost:3000

### Production Build

1. Build the frontend:
```bash
cd frontend
npm run build
```

2. Serve the built files with the Flask backend or a web server like Nginx.

### Docker Deployment

Deploy Downloadix using Docker Compose (perfect for Portainer/TrueNAS).

#### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/1nis/Downloadix.git
cd Downloadix

# Build and start containers
docker-compose up -d --build

# Access the application
# Open http://localhost:2084 in your browser
```

#### Deploy on Portainer (TrueNAS)

1. In Portainer, go to **Stacks** > **Add stack**
2. Choose **Repository** and enter the Git repository URL, or
3. Choose **Web editor** and paste the content of `docker-compose.portainer.yml`
4. Adjust the volume path to match your TrueNAS storage:
   ```yaml
   volumes:
     - /mnt/pool/appdata/downloadix/downloads:/app/downloads
   ```
5. Click **Deploy the stack**

#### Docker Configuration

| Service | Port | Description |
|---------|------|-------------|
| frontend | 2084 | Web interface (Nginx) |
| backend | 5000 | API server (internal) |

**Environment Variables (Backend):**
| Variable | Default | Description |
|----------|---------|-------------|
| `DOWNLOAD_FOLDER` | `/app/downloads` | Download directory path |
| `FLASK_ENV` | `production` | Flask environment |

**Volumes:**
| Container Path | Description |
|----------------|-------------|
| `/app/downloads` | Downloaded files storage |

## Usage

1. **Paste a URL**: Enter a video URL from YouTube, X/Twitter, TikTok, or Instagram in the input field and click "Fetch".

2. **Select Quality**: Choose the video quality from the available options.

3. **Download Video or Audio**:
   - Click **"Video"** to download the video in MP4 format
   - Click **"MP3"** to download audio only in MP3 format

4. **Download Thumbnail**: Hover over the video thumbnail and click the image icon to download the thumbnail.

5. **Monitor Progress**: You'll see real-time progress including:
   - Download percentage
   - Downloaded size / Total size
   - Current download speed
   - Estimated time remaining

6. **Cancel a Download**: While downloading, click the "Cancel" button to abort the download.

7. **Multiple Downloads**: You can start multiple downloads simultaneously. Use the Downloads Manager (floating button at bottom-right) to monitor and manage all downloads.

8. **Downloads Manager**: Click the download icon at the bottom-right corner to:
   - See all active and completed downloads
   - Cancel any download in progress
   - Download completed files again
   - Clear completed/cancelled downloads from the list
   - View download history



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
| `/api/download/start` | POST | Start a download (supports `audio_only` param) |
| `/api/download/progress/<id>` | GET | SSE endpoint for download progress |
| `/api/download/cancel/<id>` | POST | Cancel an ongoing download |
| `/api/download/file/<id>` | GET | Download the completed file |
| `/api/download/thumbnail` | POST | Download video thumbnail |
| `/api/download/list` | GET | List all active and recent downloads |
| `/api/download/clear` | POST | Clear completed/cancelled downloads |
| `/api/download/history` | GET | Get download history |
| `/api/download/history/clear` | POST | Clear download history |
| `/api/health` | GET | Health check |

## Project Structure

```
Downloadix/
├── backend/
│   ├── app.py              # Flask backend
│   ├── Dockerfile          # Backend Docker image
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
│   │       ├── VideoPreview.vue     # Video preview with thumbnail download
│   │       ├── DownloadBtn.vue      # Video & MP3 download buttons
│   │       ├── ProgressBar.vue      # Progress bar component
│   │       ├── Settings.vue         # Settings panel
│   │       └── DownloadsManager.vue # Downloads manager panel
│   ├── Dockerfile          # Frontend Docker image (multi-stage)
│   ├── nginx.conf          # Nginx configuration
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml      # Docker Compose configuration
├── docker-compose.portainer.yml  # Portainer-ready configuration
├── start.bat               # Windows batch launcher
├── start.ps1               # PowerShell launcher
└── README.md
```

## Technologies

- **Backend**: Flask, yt-dlp, Gunicorn
- **Frontend**: Vue 3, Vite, Nginx
- **Streaming**: Server-Sent Events (SSE) for real-time progress
- **Containerization**: Docker, Docker Compose

## Notes

- **Instagram**: Some Instagram content may require login. Public posts should work without authentication.
- **TikTok**: Works with public videos.
- **MP3 Conversion**: Requires FFmpeg for audio extraction and conversion.
- **Rate Limiting**: Be mindful of rate limits when downloading many videos in quick succession.

## License

MIT
