from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class User:
    """User model"""
    user_id: int
    username: str
    first_name: str
    language: str = 'en'
    created_at: datetime = None
    last_activity: datetime = None
    is_admin: bool = False
    downloads_count: int = 0
    successful_downloads: int = 0
    failed_downloads: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_activity is None:
            self.last_activity = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create from dictionary"""
        return cls(**data)
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
    
    def increment_downloads(self, success: bool = True):
        """Increment download counters"""
        self.downloads_count += 1
        if success:
            self.successful_downloads += 1
        else:
            self.failed_downloads += 1
    
    def get_download_success_rate(self) -> float:
        """Get download success rate"""
        if self.downloads_count == 0:
            return 0.0
        return (self.successful_downloads / self.downloads_count) * 100