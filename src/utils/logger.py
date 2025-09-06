import logging
import os
from datetime import datetime
from pathlib import Path
from config.config import Config

class Logger:
    """Custom logger for the Telegram bot"""
    
    def __init__(self, name="TelegramBot"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, Config.LOG_LEVEL))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        log_file = Path(Config.LOGS_PATH) / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
    
    def error(self, message):
        """Log error message"""
        self.logger.error(message)
    
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
    
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
    
    def critical(self, message):
        """Log critical message"""
        self.logger.critical(message)
    
    def log_user_action(self, user_id, username, action, details=None):
        """Log user action"""
        message = f"User {user_id} (@{username}) - {action}"
        if details:
            message += f" - {details}"
        self.info(message)
    
    def log_group_action(self, group_id, group_title, action, details=None):
        """Log group action"""
        message = f"Group {group_id} ({group_title}) - {action}"
        if details:
            message += f" - {details}"
        self.info(message)
    
    def log_admin_action(self, admin_id, action, details=None):
        """Log admin action"""
        message = f"Admin {admin_id} - {action}"
        if details:
            message += f" - {details}"
        self.info(message)
    
    def log_download(self, user_id, url, success=True, error=None):
        """Log download attempt"""
        status = "SUCCESS" if success else "FAILED"
        message = f"Download {status} - User {user_id} - URL: {url}"
        if error:
            message += f" - Error: {error}"
        self.info(message)
    
    def log_error(self, error, context=None):
        """Log error with context"""
        message = f"Error: {str(error)}"
        if context:
            message += f" - Context: {context}"
        self.error(message)