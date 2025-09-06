import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the Telegram bot"""
    
    # Bot Configuration
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
    
    # Firebase Configuration
    FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', './serviceAccountKey.json')
    FIREBASE_DATABASE_URL = os.getenv('FIREBASE_DATABASE_URL')
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DOWNLOAD_PATH = os.getenv('DOWNLOAD_PATH', str(BASE_DIR / 'downloads'))
    TEMP_PATH = os.getenv('TEMP_PATH', str(BASE_DIR / 'temp'))
    LOGS_PATH = str(BASE_DIR / 'logs')
    
    # Create directories if they don't exist
    Path(DOWNLOAD_PATH).mkdir(parents=True, exist_ok=True)
    Path(TEMP_PATH).mkdir(parents=True, exist_ok=True)
    Path(LOGS_PATH).mkdir(parents=True, exist_ok=True)
    
    # Bot Settings
    MAX_DOWNLOAD_SIZE = int(os.getenv('MAX_DOWNLOAD_SIZE', 50000000))  # 50MB
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    MAX_CONCURRENT_DOWNLOADS = int(os.getenv('MAX_CONCURRENT_DOWNLOADS', 5))
    DOWNLOAD_TIMEOUT = int(os.getenv('DOWNLOAD_TIMEOUT', 300))
    
    # Group Management
    ENABLE_GROUP_MANAGEMENT = os.getenv('ENABLE_GROUP_MANAGEMENT', 'True').lower() == 'true'
    DEFAULT_WELCOME_MESSAGE = os.getenv('DEFAULT_WELCOME_MESSAGE', 'Welcome {user} to {group}!')
    DEFAULT_WARN_LIMIT = int(os.getenv('DEFAULT_WARN_LIMIT', 3))
    
    # Download Settings
    ENABLE_DOWNLOAD_IN_GROUPS = os.getenv('ENABLE_DOWNLOAD_IN_GROUPS', 'True').lower() == 'true'
    
    # API Keys
    CURRENCY_API_KEY = os.getenv('CURRENCY_API_KEY')
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
    
    # Supported Platforms
    SUPPORTED_PLATFORMS = [
        'youtube.com', 'youtu.be', 'instagram.com', 'tiktok.com', 
        'twitter.com', 'x.com', 'facebook.com', 'pinterest.com',
        'vimeo.com', 'dailymotion.com', 'twitch.tv', 'soundcloud.com',
        't.me'
    ]
    
    # Languages
    DEFAULT_LANGUAGE = 'en'
    SUPPORTED_LANGUAGES = ['en', 'fa']
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        required_fields = ['BOT_TOKEN', 'ADMIN_PASSWORD', 'FIREBASE_DATABASE_URL']
        
        for field in required_fields:
            if not getattr(cls, field):
                raise ValueError(f"Required field {field} is missing")
        
        if not Path(cls.FIREBASE_CREDENTIALS_PATH).exists():
            raise ValueError(f"Firebase credentials file not found at {cls.FIREBASE_CREDENTIALS_PATH}")
        
        return True