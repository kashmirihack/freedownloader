# Video Downloader Web Application

A modern Flask-based web application that allows users to download videos from multiple platforms (YouTube, Facebook, Instagram, TikTok) with a beautiful Nicepage-inspired interface.

## Features

- 🎥 Download videos from YouTube, Facebook, Instagram, and TikTok
- 🎨 Modern, colorful Nicepage-inspired design
- 📱 Mobile-responsive interface
- ⚡ High-quality video downloads with multiple format options
- 🔄 Automatic file cleanup (keeps 5 most recent downloads)
- 💫 Smooth animations and hover effects
- 🛡️ Robust error handling with user-friendly messages

## Installation

1. **Clone or download this package**
2. **Install Python dependencies:**
   ```bash
   pip install flask yt-dlp gunicorn
   ```

3. **Run the application:**
   ```bash
   python -m flask run
   # Or with gunicorn for production:
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

4. **Open your browser and go to:**
   ```
   http://localhost:5000
   ```

## Project Structure

```
video-downloader-package/
├── app.py                 # Main Flask application
├── main.py               # Entry point for gunicorn
├── utils/
│   ├── __init__.py
│   └── downloader.py     # Video download logic
├── templates/
│   ├── layout.html       # Base template
│   └── index.html        # Main page template
├── static/
│   ├── css/
│   │   └── style.css     # Nicepage-inspired styles
│   ├── js/
│   │   └── main.js       # Frontend JavaScript
│   └── downloads/        # Downloaded videos (auto-created)
├── pyproject.toml        # Python dependencies
└── README.md            # This file
```

## Dependencies

- **Flask**: Web framework
- **yt-dlp**: Video downloading library
- **gunicorn**: WSGI HTTP Server (for production)

## Usage

1. **Paste a video URL** from any supported platform
2. **Click "Get Video"** to fetch video information
3. **Select quality** from available options
4. **Click "Download Now"** to save the video

## Supported Platforms

- YouTube (youtube.com, youtu.be)
- Facebook (facebook.com, fb.com, fb.watch)
- Instagram (instagram.com)
- TikTok (tiktok.com)

## Configuration

### Environment Variables

- `SESSION_SECRET`: Secret key for Flask sessions (optional, defaults to development key)

### Customization

- Modify `static/css/style.css` to change the appearance
- Update `utils/downloader.py` to add more platforms or change download behavior
- Edit templates in `templates/` to modify the user interface

## Error Handling

The application includes comprehensive error handling for:
- Network connectivity issues
- SSL/Certificate problems
- Private or unavailable videos
- Invalid URLs
- Download timeouts

## Production Deployment

For production deployment:

1. Set the `SESSION_SECRET` environment variable
2. Use gunicorn or another WSGI server
3. Consider using nginx as a reverse proxy
4. Set up proper logging and monitoring

Example production command:
```bash
gunicorn --bind 0.0.0.0:8000 --workers 4 main:app
```

## License

This project is for educational purposes. Please respect the terms of service of the platforms you're downloading from.

## Troubleshooting

### Common Issues

1. **"Network connection error"**: Check your internet connection
2. **"Video not found"**: Verify the URL is correct and the video exists
3. **"Download failed"**: Try a different quality option or try again later

### Getting Help

- Check the browser console for JavaScript errors
- Look at the server logs for detailed error messages
- Ensure all dependencies are properly installed

## Updates

This application uses yt-dlp which is actively maintained. For the latest video platform support, update yt-dlp:

```bash
pip install --upgrade yt-dlp
```