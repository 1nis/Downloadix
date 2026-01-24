# Downloadix

A modern web application for downloading videos from YouTube, X/Twitter, and TikTok.

## Features

- Download videos from YouTube, X/Twitter, and TikTok
- Real-time download progress with:
  - Progress bar with percentage
  - Downloaded size / Total size
  - Download speed
  - Estimated time remaining (ETA)
- Quality selection (360p, 480p, 720p, 1080p, etc.)
- Configurable download folder
- Clean and modern UI

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

1. **Paste a URL**: Enter a video URL from YouTube, X/Twitter, or TikTok in the input field and click "Fetch".

2. **Select Quality**: Choose the video quality from the available options.

3. **Download**: Click the "Download Video" button. You'll see real-time progress including:
   - Download percentage
   - Downloaded size / Total size
   - Current download speed
   - Estimated time remaining

4. **Configure Download Folder** (optional): Click the settings icon (gear) in the top-right corner to change where videos are saved.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/info` | GET | Get video information from URL |
| `/api/download/start` | POST | Start a download and get download ID |
| `/api/download/progress/<id>` | GET | SSE endpoint for download progress |
| `/api/download/file/<id>` | GET | Download the completed file |
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
│   │       ├── VideoForm.vue     # URL input form
│   │       ├── VideoPreview.vue  # Video preview card
│   │       ├── DownloadBtn.vue   # Download button with progress
│   │       ├── ProgressBar.vue   # Progress bar component
│   │       └── Settings.vue      # Settings panel
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Technologies

- **Backend**: Flask, yt-dlp
- **Frontend**: Vue 3, Vite
- **Streaming**: Server-Sent Events (SSE) for real-time progress

## License

MIT
