import aiohttp
import aiofiles
import os
import tempfile
import logging
from urllib.parse import urlparse
from typing import Tuple

logger = logging.getLogger(__name__)

class DocumentDownloader:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        
    async def download_document(self, url: str) -> Tuple[str, str]:
        """
        Download document from URL and return (file_path, file_type)
        Returns: (local_file_path, detected_file_type)
        """
        try:
            logger.info(f"📥 Starting download from: {url}")
            
            # Parse URL to get filename hint
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path) or "downloaded_document"
            
            # Detect file type from URL
            file_type = self._detect_file_type_from_url(url, filename)
            
            # Create temporary file path
            temp_filename = f"hackrx_{hash(url)}_{filename}"
            file_path = os.path.join(self.temp_dir, temp_filename)
            
            # Download the file
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to download: HTTP {response.status}")
                    
                    # Get content type from headers if available
                    content_type = response.headers.get('content-type', '').lower()
                    if not file_type:
                        file_type = self._detect_file_type_from_content_type(content_type)
                    
                    # Save file
                    async with aiofiles.open(file_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
            
            file_size = os.path.getsize(file_path)
            logger.info(f"✅ Downloaded {file_size} bytes to: {file_path}")
            logger.info(f"🔍 Detected file type: {file_type}")
            
            return file_path, file_type
            
        except Exception as e:
            logger.error(f"❌ Download failed: {str(e)}")
            raise
    
    def _detect_file_type_from_url(self, url: str, filename: str) -> str:
        """Detect file type from URL or filename"""
        url_lower = url.lower()
        filename_lower = filename.lower()
        
        if '.pdf' in url_lower or filename_lower.endswith('.pdf'):
            return 'pdf'
        elif '.docx' in url_lower or filename_lower.endswith('.docx'):
            return 'docx'
        elif '.doc' in url_lower or filename_lower.endswith('.doc'):
            return 'doc'
        elif '.eml' in url_lower or filename_lower.endswith('.eml'):
            return 'email'
        elif 'email' in url_lower or 'mail' in url_lower:
            return 'email'
        
        return None
    
    def _detect_file_type_from_content_type(self, content_type: str) -> str:
        """Detect file type from HTTP content-type header"""
        if 'pdf' in content_type:
            return 'pdf'
        elif 'wordprocessingml' in content_type or 'docx' in content_type:
            return 'docx'
        elif 'msword' in content_type:
            return 'doc'
        elif 'email' in content_type or 'message' in content_type:
            return 'email'
        
        return 'unknown'
    
    def cleanup_file(self, file_path: str):
        """Clean up temporary file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"🗑️ Cleaned up: {file_path}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to cleanup {file_path}: {str(e)}")