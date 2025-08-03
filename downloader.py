import os
import tempfile
import yt_dlp
import logging
import re
import json
import time
import glob
from urllib.parse import urlparse

# Configure logging
logger = logging.getLogger(__name__)

# List of supported sites
supported_sites = [
    {"name": "YouTube", "icon": "fab fa-youtube", "domains": ["youtube.com", "youtu.be"]},
    {"name": "Facebook", "icon": "fab fa-facebook", "domains": ["facebook.com", "fb.com", "fb.watch"]},
    {"name": "Instagram", "icon": "fab fa-instagram", "domains": ["instagram.com"]},
    {"name": "TikTok", "icon": "fab fa-tiktok", "domains": ["tiktok.com"]}
]

class VideoDownloadError(Exception):
    """Custom exception for video download errors"""
    pass

def is_supported_url(url):
    """Check if the URL is from a supported site"""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    
    # Remove 'www.' prefix if present
    if domain.startswith('www.'):
        domain = domain[4:]
    
    for site in supported_sites:
        if any(d in domain for d in site["domains"]):
            return True
    
    return False

def cleanup_downloads(directory, max_files=5):
    """Clean up old downloads, keeping only the most recent files"""
    try:
        if not os.path.exists(directory):
            return
            
        # Get all files in the directory
        files = []
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath) and not filename.startswith('.'):
                # Get file creation/modification time
                file_time = os.path.getmtime(filepath)
                files.append((filepath, file_time))
        
        # Sort files by time (newest first)
        files.sort(key=lambda x: x[1], reverse=True)
        
        # Remove older files, keeping only max_files
        if len(files) > max_files:
            for filepath, _ in files[max_files:]:
                try:
                    os.remove(filepath)
                    logger.info(f"Deleted old download: {filepath}")
                except Exception as e:
                    logger.warning(f"Failed to delete file {filepath}: {str(e)}")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        # Don't raise the exception - cleanup is not critical

def get_video_info(url):
    """Get information about a video without downloading it"""
    if not is_supported_url(url):
        raise VideoDownloadError("This URL is not from a supported platform")
    
    # Configure yt-dlp options with better error handling
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'format': 'best',
        'noplaylist': True,
        'extract_flat': False,
        'check_formats': True,
        'socket_timeout': 30,
        'retries': 3,
        'fragment_retries': 3,
        'extractor_retries': 3,
        'http_chunk_size': 10485760,  # 10MB chunks
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Process formats to get available quality options
            formats = []
            seen_formats = set()  # Track unique format combinations (resolution+ext)
            
            # First, add the 'best' option for convenience
            formats.append({
                'format_id': 'best',
                'resolution': 'Best Quality',
                'ext': 'auto',
                'filesize': 0,
                'filesize_approx': 0,
                'format_note': 'Recommended',
            })
            
            # Add the format with best audio and video
            formats.append({
                'format_id': 'bv*+ba/b',
                'resolution': 'Best Quality',
                'ext': 'auto',
                'filesize': 0,
                'filesize_approx': 0,
                'format_note': 'Best video with best audio',
            })
            
            # Process individual formats
            if info and 'formats' in info:
                for f in info['formats']:
                    # Skip audio-only formats
                    if f.get('vcodec') == 'none' or f.get('resolution') == 'audio only':
                        continue
                    
                    # Get format details
                    resolution = f.get('height', 0)
                    format_id = f.get('format_id', '')
                    extension = f.get('ext', '')
                    filesize = f.get('filesize') or f.get('filesize_approx', 0)
                    fps = f.get('fps', 0)
                    format_note = f.get('format_note', '')
                    
                    # Create a unique identifier for this format
                    format_key = f"{resolution}p_{extension}"
                    
                    # Skip if we've already seen this exact format
                    if format_key in seen_formats:
                        continue
                    
                    # Only include formats with meaningful resolution info
                    if resolution and resolution > 0:
                        seen_formats.add(format_key)
                        formats.append({
                            'format_id': format_id,
                            'resolution': f"{resolution}p",
                            'ext': extension,
                            'filesize': filesize,
                            'filesize_approx': filesize,
                            'format_note': format_note,
                            'fps': fps
                        })
            
            # Sort formats by resolution (highest first) and then by fps
            if len(formats) > 2:
                formats[2:] = sorted(
                    formats[2:], 
                    key=lambda x: (int(x['resolution'].replace('p', '')), x.get('fps', 0)), 
                    reverse=True
                )
            
            # Create a response with essential information
            result = {
                'title': info.get('title', 'Unknown Title') if info else 'Unknown Title',
                'thumbnail': info.get('thumbnail', '') if info else '',
                'duration': info.get('duration', 0) if info else 0,
                'uploader': info.get('uploader', 'Unknown Uploader') if info else 'Unknown Uploader',
                'formats': formats,
                'description': info.get('description', '') if info else '',
                'url': url,  # Include the original URL
                'extractor': info.get('extractor', '') if info else '',  # Which platform extractor was used
            }
            
            return result
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e).lower()
        logger.error(f"yt-dlp download error: {str(e)}")
        
        # Provide more user-friendly error messages
        if 'ssl' in error_msg or 'certificate' in error_msg:
            raise VideoDownloadError("Network connection error. Please check your internet connection and try again.")
        elif 'timeout' in error_msg or 'timed out' in error_msg:
            raise VideoDownloadError("Connection timed out. Please try again in a moment.")
        elif 'private' in error_msg or 'unavailable' in error_msg:
            raise VideoDownloadError("This video is private or unavailable.")
        elif 'not found' in error_msg or '404' in error_msg:
            raise VideoDownloadError("Video not found. Please check the URL and try again.")
        else:
            raise VideoDownloadError(f"Could not fetch video info: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in get_video_info: {str(e)}")
        raise VideoDownloadError("An error occurred while fetching video info. Please try again.")

def download_video(url, format_id='best'):
    """Download a video and return the path to the downloaded file"""
    if not is_supported_url(url):
        raise VideoDownloadError("This URL is not from a supported platform")
    
    # Create a download directory in the static folder for better access
    download_dir = os.path.join('static', 'downloads')
    os.makedirs(download_dir, exist_ok=True)
    
    # Clean up old downloads - keep only the 5 most recent files
    try:
        cleanup_downloads(download_dir, max_files=5)
    except Exception as e:
        logger.warning(f"Failed to clean up old downloads: {str(e)}")
    
    # Create a unique filename based on timestamp
    timestamp = int(time.time())
    temp_filename = f"video_{timestamp}"
    output_template = os.path.join(download_dir, temp_filename)
    
    # Configure yt-dlp options with optimized settings and better error handling
    ydl_opts = {
        'format': format_id,
        'outtmpl': output_template + '.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,
        'continuedl': True,  # Continue partial downloads
        'retries': 5,       # Retry on errors
        'fragment_retries': 5,  # Retry fragments on errors
        'extractor_retries': 3,  # Retry on extractor errors
        'file_access_retries': 3,  # Retry on file access issues
        'buffersize': 1024,  # Optimize buffer size (in KB)
        'external_downloader': 'native',  # Use native downloader for better performance
        'socket_timeout': 30,  # Timeout for socket operations (seconds)
        'http_chunk_size': 10485760,  # 10MB chunks
        'prefer_insecure': False,  # Always use HTTPS when possible
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Download the file
            info = ydl.extract_info(url, download=True)
            
            # Get the actual filename
            if info and 'entries' in info:
                # Playlist (should be avoided with noplaylist option, but just in case)
                info = info['entries'][0]
            
            # Get the extension from the downloaded file
            ext = info.get('ext', 'mp4') if info else 'mp4'
            
            # Create the complete filepath
            filepath = f"{output_template}.{ext}"
            
            # Check if the file exists
            if not os.path.exists(filepath):
                # Try to find the actual file
                pattern = f"{output_template}.*"
                matching_files = glob.glob(pattern)
                if matching_files:
                    filepath = matching_files[0]
                else:
                    raise VideoDownloadError("Download failed: File not found")
            
            # Get a clean title for the download filename
            title = info.get('title', 'video') if info else 'video'
            title = re.sub(r'[^\w\s-]', '', title).strip().lower()
            title = re.sub(r'[-\s]+', '-', title)
            download_filename = f"{title}.{ext}"
            
            logger.info(f"Downloaded video to {filepath}")
            return filepath, download_filename
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e).lower()
        logger.error(f"yt-dlp download error: {str(e)}")
        
        # Provide more user-friendly error messages
        if 'ssl' in error_msg or 'certificate' in error_msg:
            raise VideoDownloadError("Network connection error during download. Please check your internet connection and try again.")
        elif 'timeout' in error_msg or 'timed out' in error_msg:
            raise VideoDownloadError("Download timed out. Please try again in a moment.")
        elif 'private' in error_msg or 'unavailable' in error_msg:
            raise VideoDownloadError("This video is private or no longer available for download.")
        elif 'not found' in error_msg or '404' in error_msg:
            raise VideoDownloadError("Video not found. The link may be broken or the video may have been removed.")
        elif 'format' in error_msg:
            raise VideoDownloadError("The selected quality is not available. Please try a different quality option.")
        else:
            raise VideoDownloadError(f"Download failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in download_video: {str(e)}")
        raise VideoDownloadError("An unexpected error occurred during download. Please try again.")