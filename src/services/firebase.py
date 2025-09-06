import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
from config.config import Config
from src.utils.logger import Logger

class FirebaseService:
    """Service for handling Firebase operations"""
    
    def __init__(self):
        self.logger = Logger("FirebaseService")
        self.db = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase connection"""
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': Config.FIREBASE_DATABASE_URL
                })
            
            self.db = firestore.client()
            self.logger.info("Firebase initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Firebase: {e}")
            raise
    
    # User operations
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data"""
        try:
            doc_ref = self.db.collection('users').document(str(user_id))
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            self.logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    def create_user(self, user_id: int, username: str, first_name: str, language: str = 'en') -> bool:
        """Create new user"""
        try:
            user_data = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'language': language,
                'created_at': datetime.now(),
                'last_activity': datetime.now(),
                'is_admin': False,
                'downloads_count': 0,
                'successful_downloads': 0,
                'failed_downloads': 0
            }
            
            doc_ref = self.db.collection('users').document(str(user_id))
            doc_ref.set(user_data)
            self.logger.log_user_action(user_id, username, "User created")
            return True
        except Exception as e:
            self.logger.error(f"Error creating user {user_id}: {e}")
            return False
    
    def update_user(self, user_id: int, updates: Dict[str, Any]) -> bool:
        """Update user data"""
        try:
            doc_ref = self.db.collection('users').document(str(user_id))
            doc_ref.update(updates)
            self.logger.log_user_action(user_id, "unknown", "User updated", str(updates))
            return True
        except Exception as e:
            self.logger.error(f"Error updating user {user_id}: {e}")
            return False
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        try:
            users_ref = self.db.collection('users')
            docs = users_ref.stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            self.logger.error(f"Error getting all users: {e}")
            return []
    
    def get_users_count(self) -> int:
        """Get total users count"""
        try:
            users_ref = self.db.collection('users')
            return len(list(users_ref.stream()))
        except Exception as e:
            self.logger.error(f"Error getting users count: {e}")
            return 0
    
    # Group operations
    def get_group(self, group_id: int) -> Optional[Dict[str, Any]]:
        """Get group data"""
        try:
            doc_ref = self.db.collection('groups').document(str(group_id))
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            self.logger.error(f"Error getting group {group_id}: {e}")
            return None
    
    def create_group(self, group_id: int, title: str, language: str = 'en') -> bool:
        """Create new group"""
        try:
            group_data = {
                'group_id': group_id,
                'title': title,
                'language': language,
                'created_at': datetime.now(),
                'last_activity': datetime.now(),
                'settings': {
                    'welcome_message': Config.DEFAULT_WELCOME_MESSAGE,
                    'warn_limit': Config.DEFAULT_WARN_LIMIT,
                    'force_membership': False,
                    'force_channels': [],
                    'downloads_enabled': Config.ENABLE_DOWNLOAD_IN_GROUPS,
                    'auto_lock': False,
                    'auto_lock_duration': 0,
                    'group_locked': False
                },
                'locks': {
                    'links': False,
                    'hyperlinks': False,
                    'hashtags': False,
                    'usernames': False,
                    'inline': False,
                    'forwarded': False,
                    'emoji': False,
                    'games': False,
                    'edit': False,
                    'media_edit': False,
                    'videos': False,
                    'photos': False,
                    'files': False,
                    'music': False,
                    'stickers': False,
                    'gifs': False,
                    'location': False,
                    'voice': False,
                    'video_msg': False,
                    'polls': False
                },
                'lists': {
                    'admins': [],
                    'vip_members': [],
                    'filtered_words': [],
                    'muted_users': [],
                    'banned_users': [],
                    'warnings': {}
                }
            }
            
            doc_ref = self.db.collection('groups').document(str(group_id))
            doc_ref.set(group_data)
            self.logger.log_group_action(group_id, title, "Group created")
            return True
        except Exception as e:
            self.logger.error(f"Error creating group {group_id}: {e}")
            return False
    
    def update_group(self, group_id: int, updates: Dict[str, Any]) -> bool:
        """Update group data"""
        try:
            doc_ref = self.db.collection('groups').document(str(group_id))
            doc_ref.update(updates)
            self.logger.log_group_action(group_id, "unknown", "Group updated", str(updates))
            return True
        except Exception as e:
            self.logger.error(f"Error updating group {group_id}: {e}")
            return False
    
    def get_all_groups(self) -> List[Dict[str, Any]]:
        """Get all groups"""
        try:
            groups_ref = self.db.collection('groups')
            docs = groups_ref.stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            self.logger.error(f"Error getting all groups: {e}")
            return []
    
    def get_groups_count(self) -> int:
        """Get total groups count"""
        try:
            groups_ref = self.db.collection('groups')
            return len(list(groups_ref.stream()))
        except Exception as e:
            self.logger.error(f"Error getting groups count: {e}")
            return 0
    
    # Statistics operations
    def get_statistics(self) -> Dict[str, Any]:
        """Get bot statistics"""
        try:
            users_count = self.get_users_count()
            groups_count = self.get_groups_count()
            
            # Get download statistics
            stats_ref = self.db.collection('statistics').document('downloads')
            stats_doc = stats_ref.get()
            download_stats = stats_doc.to_dict() if stats_doc.exists else {
                'total_downloads': 0,
                'successful_downloads': 0,
                'failed_downloads': 0
            }
            
            return {
                'users_count': users_count,
                'groups_count': groups_count,
                'total_downloads': download_stats.get('total_downloads', 0),
                'successful_downloads': download_stats.get('successful_downloads', 0),
                'failed_downloads': download_stats.get('failed_downloads', 0)
            }
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {}
    
    def update_download_statistics(self, success: bool = True):
        """Update download statistics"""
        try:
            stats_ref = self.db.collection('statistics').document('downloads')
            
            if success:
                stats_ref.update({
                    'total_downloads': firestore.Increment(1),
                    'successful_downloads': firestore.Increment(1)
                })
            else:
                stats_ref.update({
                    'total_downloads': firestore.Increment(1),
                    'failed_downloads': firestore.Increment(1)
                })
        except Exception as e:
            self.logger.error(f"Error updating download statistics: {e}")
    
    # Broadcast operations
    def create_broadcast(self, message: str, target_type: str, scheduled_time: datetime = None) -> str:
        """Create broadcast message"""
        try:
            broadcast_data = {
                'message': message,
                'target_type': target_type,  # 'users', 'users_and_groups'
                'created_at': datetime.now(),
                'scheduled_time': scheduled_time,
                'status': 'pending',  # 'pending', 'sent', 'failed'
                'recipients_count': 0,
                'sent_count': 0,
                'failed_count': 0
            }
            
            doc_ref = self.db.collection('broadcasts').document()
            doc_ref.set(broadcast_data)
            self.logger.log_admin_action("system", "Broadcast created", f"Type: {target_type}")
            return doc_ref.id
        except Exception as e:
            self.logger.error(f"Error creating broadcast: {e}")
            return None
    
    def get_broadcast(self, broadcast_id: str) -> Optional[Dict[str, Any]]:
        """Get broadcast data"""
        try:
            doc_ref = self.db.collection('broadcasts').document(broadcast_id)
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            self.logger.error(f"Error getting broadcast {broadcast_id}: {e}")
            return None
    
    def delete_broadcast(self, broadcast_id: str) -> bool:
        """Delete broadcast"""
        try:
            doc_ref = self.db.collection('broadcasts').document(broadcast_id)
            doc_ref.delete()
            self.logger.log_admin_action("system", "Broadcast deleted", f"ID: {broadcast_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting broadcast {broadcast_id}: {e}")
            return False
    
    def get_pending_broadcasts(self) -> List[Dict[str, Any]]:
        """Get pending broadcasts"""
        try:
            broadcasts_ref = self.db.collection('broadcasts')
            query = broadcasts_ref.where('status', '==', 'pending')
            docs = query.stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            self.logger.error(f"Error getting pending broadcasts: {e}")
            return []
    
    # System operations
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        try:
            return {
                'firebase_connected': True,
                'last_update': datetime.now(),
                'version': '1.0.0'
            }
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {}

# Global Firebase service instance
firebase_service = FirebaseService()