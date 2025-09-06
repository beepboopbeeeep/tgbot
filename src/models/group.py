from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Dict, Any, List, Optional

@dataclass
class GroupSettings:
    """Group settings model"""
    welcome_message: str = "Welcome {user} to {group}!"
    warn_limit: int = 3
    force_membership: bool = False
    force_channels: List[str] = field(default_factory=list)
    downloads_enabled: bool = True
    auto_lock: bool = False
    auto_lock_duration: int = 0  # in minutes
    group_locked: bool = False

@dataclass
class GroupLocks:
    """Group locks model"""
    links: bool = False
    hyperlinks: bool = False
    hashtags: bool = False
    usernames: bool = False
    inline: bool = False
    forwarded: bool = False
    emoji: bool = False
    games: bool = False
    edit: bool = False
    media_edit: bool = False
    videos: bool = False
    photos: bool = False
    files: bool = False
    music: bool = False
    stickers: bool = False
    gifs: bool = False
    location: bool = False
    voice: bool = False
    video_msg: bool = False
    polls: bool = False

@dataclass
class GroupLists:
    """Group lists model"""
    admins: List[int] = field(default_factory=list)
    vip_members: List[int] = field(default_factory=list)
    filtered_words: List[str] = field(default_factory=list)
    muted_users: List[int] = field(default_factory=list)
    banned_users: List[int] = field(default_factory=list)
    warnings: Dict[int, int] = field(default_factory=dict)  # user_id -> warning_count

@dataclass
class Group:
    """Group model"""
    group_id: int
    title: str
    language: str = 'en'
    created_at: datetime = None
    last_activity: datetime = None
    settings: GroupSettings = field(default_factory=GroupSettings)
    locks: GroupLocks = field(default_factory=GroupLocks)
    lists: GroupLists = field(default_factory=GroupLists)
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_activity is None:
            self.last_activity = datetime.now()
        
        # Ensure settings, locks, and lists are proper instances
        if not isinstance(self.settings, GroupSettings):
            self.settings = GroupSettings(**self.settings) if isinstance(self.settings, dict) else GroupSettings()
        if not isinstance(self.locks, GroupLocks):
            self.locks = GroupLocks(**self.locks) if isinstance(self.locks, dict) else GroupLocks()
        if not isinstance(self.lists, GroupLists):
            self.lists = GroupLists(**self.lists) if isinstance(self.lists, dict) else GroupLists()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Group':
        """Create from dictionary"""
        return cls(**data)
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in self.lists.admins
    
    def is_vip(self, user_id: int) -> bool:
        """Check if user is VIP member"""
        return user_id in self.lists.vip_members
    
    def is_muted(self, user_id: int) -> bool:
        """Check if user is muted"""
        return user_id in self.lists.muted_users
    
    def is_banned(self, user_id: int) -> bool:
        """Check if user is banned"""
        return user_id in self.lists.banned_users
    
    def add_admin(self, user_id: int) -> bool:
        """Add admin"""
        if user_id not in self.lists.admins:
            self.lists.admins.append(user_id)
            return True
        return False
    
    def remove_admin(self, user_id: int) -> bool:
        """Remove admin"""
        if user_id in self.lists.admins:
            self.lists.admins.remove(user_id)
            return True
        return False
    
    def add_vip(self, user_id: int) -> bool:
        """Add VIP member"""
        if user_id not in self.lists.vip_members:
            self.lists.vip_members.append(user_id)
            return True
        return False
    
    def remove_vip(self, user_id: int) -> bool:
        """Remove VIP member"""
        if user_id in self.lists.vip_members:
            self.lists.vip_members.remove(user_id)
            return True
        return False
    
    def mute_user(self, user_id: int) -> bool:
        """Mute user"""
        if user_id not in self.lists.muted_users:
            self.lists.muted_users.append(user_id)
            return True
        return False
    
    def unmute_user(self, user_id: int) -> bool:
        """Unmute user"""
        if user_id in self.lists.muted_users:
            self.lists.muted_users.remove(user_id)
            return True
        return False
    
    def ban_user(self, user_id: int) -> bool:
        """Ban user"""
        if user_id not in self.lists.banned_users:
            self.lists.banned_users.append(user_id)
            return True
        return False
    
    def unban_user(self, user_id: int) -> bool:
        """Unban user"""
        if user_id in self.lists.banned_users:
            self.lists.banned_users.remove(user_id)
            return True
        return False
    
    def add_warning(self, user_id: int) -> int:
        """Add warning to user"""
        current_warnings = self.lists.warnings.get(user_id, 0)
        current_warnings += 1
        self.lists.warnings[user_id] = current_warnings
        return current_warnings
    
    def remove_warning(self, user_id: int) -> int:
        """Remove warning from user"""
        current_warnings = self.lists.warnings.get(user_id, 0)
        if current_warnings > 0:
            current_warnings -= 1
            self.lists.warnings[user_id] = current_warnings
        return current_warnings
    
    def get_warnings(self, user_id: int) -> int:
        """Get warning count for user"""
        return self.lists.warnings.get(user_id, 0)
    
    def clear_warnings(self, user_id: int) -> bool:
        """Clear all warnings for user"""
        if user_id in self.lists.warnings:
            del self.lists.warnings[user_id]
            return True
        return False
    
    def add_filtered_word(self, word: str) -> bool:
        """Add filtered word"""
        if word.lower() not in [w.lower() for w in self.lists.filtered_words]:
            self.lists.filtered_words.append(word.lower())
            return True
        return False
    
    def remove_filtered_word(self, word: str) -> bool:
        """Remove filtered word"""
        word_lower = word.lower()
        if word_lower in [w.lower() for w in self.lists.filtered_words]:
            self.lists.filtered_words = [w for w in self.lists.filtered_words if w.lower() != word_lower]
            return True
        return False
    
    def is_word_filtered(self, word: str) -> bool:
        """Check if word is filtered"""
        return word.lower() in [w.lower() for w in self.lists.filtered_words]
    
    def lock_feature(self, feature: str) -> bool:
        """Lock a feature"""
        if hasattr(self.locks, feature):
            setattr(self.locks, feature, True)
            return True
        return False
    
    def unlock_feature(self, feature: str) -> bool:
        """Unlock a feature"""
        if hasattr(self.locks, feature):
            setattr(self.locks, feature, False)
            return True
        return False
    
    def is_feature_locked(self, feature: str) -> bool:
        """Check if feature is locked"""
        return getattr(self.locks, feature, False)
    
    def can_send_message(self, user_id: int) -> bool:
        """Check if user can send message"""
        # Check if group is locked
        if self.settings.group_locked:
            return self.is_admin(user_id) or self.is_vip(user_id)
        
        # Check if user is banned
        if self.is_banned(user_id):
            return False
        
        # Check if user is muted
        if self.is_muted(user_id):
            return False
        
        return True