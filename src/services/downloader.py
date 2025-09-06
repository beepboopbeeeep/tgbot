import yt_dlp
import os
import asyncio
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
import re
from config.config import Config
from src.utils.logger import Logger

class DownloadService:
    """Service for handling downloads with yt-dlp"""
    
    def __init__(self):
        self.logger = Logger("DownloadService")
        self.temp_dir = Path(Config.TEMP_PATH)
        self.download_dir = Path(Config.DOWNLOAD_PATH)
        self.max_size = Config.MAX_DOWNLOAD_SIZE
        self.timeout = Config.DOWNLOAD_TIMEOUT
        
        # Create directories if they don't exist
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Supported platforms
        self.supported_platforms = [
            'youtube.com', 'youtu.be', 'instagram.com', 'tiktok.com',
            'twitter.com', 'x.com', 'facebook.com', 'pinterest.com',
            'vimeo.com', 'dailymotion.com', 'twitch.tv', 'soundcloud.com',
            't.me'
        ]
    
    def is_supported_url(self, url: str) -> bool:
        """Check if URL is supported"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return any(platform in domain for platform in self.supported_platforms)
        except Exception:
            return False
    
    def extract_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract information from URL"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'format': 'best',
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            self.logger.error(f"Error extracting info from {url}: {e}")
            return None
    
    def get_file_size(self, info: Dict[str, Any]) -> int:
        """Get file size from info"""
        try:
            if 'filesize' in info:
                return info['filesize']
            elif 'filesize_approx' in info:
                return info['filesize_approx']
            elif 'requested_formats' in info:
                # For videos with separate audio and video
                total_size = sum(f.get('filesize', 0) for f in info['requested_formats'])
                return total_size
            return 0
        except Exception:
            return 0
    
    def download_file(self, url: str, user_id: int) -> Optional[str]:
        """Download file from URL"""
        try:
            # Extract info first
            info = self.extract_info(url)
            if not info:
                return None
            
            # Check file size
            file_size = self.get_file_size(info)
            if file_size > self.max_size:
                self.logger.warning(f"File too large: {file_size} bytes for user {user_id}")
                return None
            
            # Generate output filename
            title = info.get('title', 'download')
            title = re.sub(r'[^\w\s-]', '', title)
            title = re.sub(r'[-\s]+', '-', title)
            
            output_template = str(self.temp_dir / f"{user_id}_{title}.%(ext)s")
            
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'best',
                'outtmpl': output_template,
                'quiet': False,
                'no_warnings': False,
                'progress_hooks': [self._progress_hook],
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }] if info.get('vcodec') != 'none' else [],
                'writethumbnail': False,
                'writeinfojson': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
            }
            
            # Download the file
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Find the downloaded file
            downloaded_files = list(self.temp_dir.glob(f"{user_id}_{title}.*"))
            if downloaded_files:
                return str(downloaded_files[0])
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error downloading {url} for user {user_id}: {e}")
            return None
    
    def _progress_hook(self, d):
        """Progress hook for yt-dlp"""
        if d['status'] == 'downloading':
            percent_str = d.get('_percent_str', '0%')
            percent = percent_str.strip().replace('%', '')
            try:
                percent_float = float(percent)
                self.logger.debug(f"Download progress: {percent_float}%")
            except ValueError:
                pass
    
    async def download_async(self, url: str, user_id: int) -> Optional[str]:
        """Download file asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.download_file, url, user_id)
        except Exception as e:
            self.logger.error(f"Error in async download {url} for user {user_id}: {e}")
            return None
    
    def cleanup_temp_files(self, user_id: int):
        """Clean up temporary files for user"""
        try:
            pattern = f"{user_id}_*"
            for file_path in self.temp_dir.glob(pattern):
                try:
                    file_path.unlink()
                    self.logger.debug(f"Cleaned up temporary file: {file_path}")
                except Exception as e:
                    self.logger.warning(f"Error cleaning up {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Error cleaning up temp files for user {user_id}: {e}")
    
    def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Get detailed video information"""
        try:
            info = self.extract_info(url)
            if not info:
                return None
            
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'upload_date': info.get('upload_date', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'like_count': info.get('like_count', 0),
                'description': info.get('description', ''),
                'thumbnail': info.get('thumbnail', ''),
                'extractor': info.get('extractor', 'Unknown'),
                'webpage_url': info.get('webpage_url', url),
                'formats': info.get('formats', []),
                'filesize': self.get_file_size(info)
            }
        except Exception as e:
            self.logger.error(f"Error getting video info for {url}: {e}")
            return None
    
    def is_audio_only(self, url: str) -> bool:
        """Check if URL is audio only"""
        try:
            info = self.extract_info(url)
            if not info:
                return False
            
            return info.get('vcodec') == 'none' or info.get('acodec') == 'none'
        except Exception:
            return False
    
    def get_available_formats(self, url: str) -> List[Dict[str, Any]]:
        """Get available formats for URL"""
        try:
            info = self.extract_info(url)
            if not info:
                return []
            
            formats = []
            for fmt in info.get('formats', []):
                if fmt.get('vcodec') != 'none' or fmt.get('acodec') != 'none':
                    formats.append({
                        'format_id': fmt.get('format_id'),
                        'format_note': fmt.get('format_note', ''),
                        'ext': fmt.get('ext'),
                        'filesize': fmt.get('filesize', 0),
                        'fps': fmt.get('fps', 0),
                        'height': fmt.get('height', 0),
                        'width': fmt.get('width', 0),
                        'vcodec': fmt.get('vcodec', ''),
                        'acodec': fmt.get('acodec', ''),
                        'format': fmt.get('format', '')
                    })
            
            return formats
        except Exception as e:
            self.logger.error(f"Error getting formats for {url}: {e}")
            return []

# Global download service instance
download_service = DownloadService()