import os
import logging
from flask import Flask, render_template, request, jsonify, send_file, session, flash, redirect, url_for
import urllib.parse
from utils.downloader import get_video_info, download_video, VideoDownloadError, supported_sites

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")

# Configure logging
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html', supported_sites=supported_sites)

@app.route('/get_video_info', methods=['POST'])
def fetch_video_info():
    try:
        url = request.form.get('url', '')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Validate URL format
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return jsonify({'error': 'Invalid URL format'}), 400
        
        # Get video information
        video_info = get_video_info(url)
        return jsonify(video_info)
    except VideoDownloadError as e:
        logger.error(f"Error fetching video info: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in fetch_video_info: {str(e)}")
        return jsonify({'error': 'Unable to fetch video information. Please check the URL and try again.'}), 500

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url', '')
    format_id = request.form.get('format_id', 'best')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        # Download the video
        download_path, download_filename = download_video(url, format_id)
        
        # Log the download for debugging
        logger.info(f"Sending file: {download_path}, download name: {download_filename}")
        
        # Determine mime type based on extension
        ext = os.path.splitext(download_path)[1].lower()
        mime_type = 'video/mp4'  # Default
        
        if ext == '.mp4':
            mime_type = 'video/mp4'
        elif ext == '.webm':
            mime_type = 'video/webm'
        elif ext == '.mkv':
            mime_type = 'video/x-matroska'
        elif ext == '.mov':
            mime_type = 'video/quicktime'
        elif ext == '.avi':
            mime_type = 'video/x-msvideo'
        elif ext == '.flv':
            mime_type = 'video/x-flv'
        
        # Check if file exists and is readable
        if not os.path.exists(download_path):
            logger.error(f"File not found: {download_path}")
            return jsonify({'error': 'Downloaded file not found'}), 404
            
        if not os.access(download_path, os.R_OK):
            logger.error(f"File not readable: {download_path}")
            # Try to fix permissions
            try:
                os.chmod(download_path, 0o644)
            except Exception as e:
                logger.error(f"Failed to fix permissions: {str(e)}")
                return jsonify({'error': 'Permission denied to access file'}), 403
        
        # Get file size for logging
        file_size = os.path.getsize(download_path)
        logger.info(f"File size: {file_size} bytes")
        
        # Use a custom response to stream files
        # This helps avoid gunicorn timeouts with large files
        def generate():
            with open(download_path, 'rb') as f:
                chunk_size = 4096  # 4KB chunks
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        
        # Create a streaming response for larger files
        response = app.response_class(
            generate(),
            mimetype=mime_type,
            direct_passthrough=True
        )
        
        # Set Content-Disposition header for download
        response.headers.set(
            'Content-Disposition', 
            f'attachment; filename="{download_filename}"'
        )
        
        # Set Content-Length header if possible
        if file_size:
            response.headers.set('Content-Length', file_size)
        
        return response
        
    except VideoDownloadError as e:
        logger.error(f"Error downloading video: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error during download: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred during download'}), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('index.html', error='Server error, please try again later'), 500