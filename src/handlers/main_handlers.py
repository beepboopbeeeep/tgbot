import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from typing import Optional, Dict, Any

from config.config import Config
from src.services.firebase import firebase_service
from src.services.downloader import download_service
from src.models.user import User
from src.models.group import Group
from src.utils.logger import Logger
from src.utils.language import language_manager, _

class MainHandlers:
    """Main handlers for the bot"""
    
    def __init__(self):
        self.logger = Logger("MainHandlers")
        self.admin_sessions = {}  # user_id -> session_data
        self.user_states = {}  # user_id -> current_state
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        try:
            user = update.effective_user
            chat = update.effective_chat
            
            # Log user action
            self.logger.log_user_action(user.id, user.username, "Started bot")
            
            # Get or create user
            user_data = firebase_service.get_user(user.id)
            if not user_data:
                # Create new user
                success = firebase_service.create_user(
                    user_id=user.id,
                    username=user.username or "",
                    first_name=user.first_name or "",
                    language='en'  # Default language
                )
                if not success:
                    await update.message.reply_text("❌ Error creating user profile")
                    return
                
                user_data = firebase_service.get_user(user.id)
            
            # Update user activity
            firebase_service.update_user(user.id, {'last_activity': datetime.now()})
            
            # Get user language
            language = user_data.get('language', 'en')
            
            # Create main menu keyboard
            keyboard = [
                [InlineKeyboardButton(_("DOWNLOAD_FEATURE", language), callback_data='download')],
                [InlineKeyboardButton(_("CHANGE_LANGUAGE", language), callback_data='change_language')],
                [InlineKeyboardButton(_("BTN_HELP", language), callback_data='help')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send welcome message
            welcome_text = _("BOT_CAPABILITIES", language)
            await update.message.reply_text(
                welcome_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error in start command: {e}")
            await update.message.reply_text("❌ An error occurred")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        try:
            user = update.effective_user
            
            # Get user data
            user_data = firebase_service.get_user(user.id)
            language = user_data.get('language', 'en') if user_data else 'en'
            
            # Create help keyboard
            keyboard = [
                [InlineKeyboardButton(_("BTN_BACK", language), callback_data='main_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send help message
            help_text = _("HELP_TEXT", language)
            await update.message.reply_text(
                help_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error in help command: {e}")
            await update.message.reply_text("❌ An error occurred")
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command"""
        try:
            user = update.effective_user
            args = context.args
            
            if not args:
                await update.message.reply_text("❌ Please provide admin password")
                return
            
            password = args[0]
            
            # Check password
            if password != Config.ADMIN_PASSWORD:
                self.logger.log_user_action(user.id, user.username, "Failed admin login")
                await update.message.reply_text("❌ Invalid admin password")
                return
            
            # Log successful admin login
            self.logger.log_admin_action(user.id, "Admin login successful")
            
            # Get user data
            user_data = firebase_service.get_user(user.id)
            language = user_data.get('language', 'en') if user_data else 'en'
            
            # Create admin panel keyboard
            keyboard = [
                [InlineKeyboardButton(_("BTN_STATS", language), callback_data='admin_stats')],
                [InlineKeyboardButton(_("BTN_BROADCAST", language), callback_data='admin_broadcast')],
                [InlineKeyboardButton(_("BTN_SETTINGS", language), callback_data='admin_settings')],
                [InlineKeyboardButton(_("BTN_BACK", language), callback_data='main_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send admin panel
            admin_text = _("ADMIN_PANEL", language)
            await update.message.reply_text(
                admin_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error in admin command: {e}")
            await update.message.reply_text("❌ An error occurred")
    
    async def statistics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /statistics command"""
        try:
            user = update.effective_user
            
            # Get user data
            user_data = firebase_service.get_user(user.id)
            if not user_data or not user_data.get('is_admin', False):
                await update.message.reply_text("❌ Access denied")
                return
            
            # Get statistics
            stats = firebase_service.get_statistics()
            
            # Get user language
            language = user_data.get('language', 'en')
            
            # Format statistics
            stats_text = _("STATISTICS", language, **stats)
            
            # Create back button
            keyboard = [[InlineKeyboardButton(_("BTN_BACK", language), callback_data='admin_panel')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                stats_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error in statistics command: {e}")
            await update.message.reply_text("❌ An error occurred")
    
    async def language_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /language command"""
        try:
            user = update.effective_user
            
            # Get user data
            user_data = firebase_service.get_user(user.id)
            language = user_data.get('language', 'en') if user_data else 'en'
            
            # Create language selection keyboard
            keyboard = []
            for lang_code, lang_name in language_manager.get_supported_languages().items():
                keyboard.append([InlineKeyboardButton(lang_name, callback_data=f'lang_{lang_code}')])
            
            keyboard.append([InlineKeyboardButton(_("BTN_BACK", language), callback_data='main_menu')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                _("PLEASE_WAIT", language),
                reply_markup=reply_markup
            )
            
        except Exception as e:
            self.logger.error(f"Error in language command: {e}")
            await update.message.reply_text("❌ An error occurred")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        try:
            message = update.message
            user = message.from_user
            chat = message.chat
            
            # Get user data
            user_data = firebase_service.get_user(user.id)
            if not user_data:
                # Create new user
                success = firebase_service.create_user(
                    user_id=user.id,
                    username=user.username or "",
                    first_name=user.first_name or "",
                    language='en'
                )
                if not success:
                    await message.reply_text("❌ Error creating user profile")
                    return
                
                user_data = firebase_service.get_user(user.id)
            
            # Update user activity
            firebase_service.update_user(user.id, {'last_activity': datetime.now()})
            
            # Get user language
            language = user_data.get('language', 'en')
            
            # Check if message contains URL
            if message.entities:
                for entity in message.entities:
                    if entity.type == 'url':
                        url = message.text[entity.offset:entity.offset + entity.length]
                        await self.handle_download_request(update, context, url)
                        return
            
            # Handle group messages
            if chat.type in ['group', 'supergroup']:
                await self.handle_group_message(update, context)
            
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
    
    async def handle_download_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
        """Handle download request"""
        try:
            message = update.message
            user = message.from_user
            
            # Check if URL is supported
            if not download_service.is_supported_url(url):
                await message.reply_text(_("UNSUPPORTED_PLATFORM", user_data.get('language', 'en')))
                return
            
            # Send downloading message
            user_data = firebase_service.get_user(user.id)
            language = user_data.get('language', 'en')
            
            downloading_msg = await message.reply_text(_("DOWNLOAD_STARTING", language))
            
            # Download file
            file_path = await download_service.download_async(url, user.id)
            
            # Delete downloading message
            await downloading_msg.delete()
            
            if file_path:
                # Send file
                with open(file_path, 'rb') as file:
                    await message.reply_document(file)
                
                # Update statistics
                firebase_service.update_download_statistics(True)
                firebase_service.update_user(user.id, {
                    'downloads_count': user_data.get('downloads_count', 0) + 1,
                    'successful_downloads': user_data.get('successful_downloads', 0) + 1
                })
                
                self.logger.log_download(user.id, url, success=True)
                
                # Send success message with back button
                keyboard = [[InlineKeyboardButton(_("BTN_BACK", language), callback_data='main_menu')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await message.reply_text(
                    _("DOWNLOAD_SUCCESS", language),
                    reply_markup=reply_markup
                )
            else:
                # Update statistics
                firebase_service.update_download_statistics(False)
                firebase_service.update_user(user.id, {
                    'downloads_count': user_data.get('downloads_count', 0) + 1,
                    'failed_downloads': user_data.get('failed_downloads', 0) + 1
                })
                
                self.logger.log_download(user.id, url, success=False)
                
                await message.reply_text(_("DOWNLOAD_FAILED", language))
            
            # Clean up temporary files
            download_service.cleanup_temp_files(user.id)
            
        except Exception as e:
            self.logger.error(f"Error handling download request: {e}")
            await message.reply_text(_("ERROR_OCCURRED", language, error=str(e)))
    
    async def handle_group_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle group messages"""
        try:
            message = update.message
            chat = message.chat
            user = message.from_user
            
            # Get group data
            group_data = firebase_service.get_group(chat.id)
            if not group_data:
                # Create new group
                success = firebase_service.create_group(
                    group_id=chat.id,
                    title=chat.title or "Unknown Group"
                )
                if not success:
                    return
                
                group_data = firebase_service.get_group(chat.id)
            
            # Update group activity
            firebase_service.update_group(chat.id, {'last_activity': datetime.now()})
            
            # Convert to Group model
            group = Group.from_dict(group_data)
            
            # Check if user can send message
            if not group.can_send_message(user.id):
                await message.delete()
                return
            
            # Check group locks
            await self.check_group_locks(update, context, group)
            
            # Check for URLs in group if downloads are enabled
            if group.settings.downloads_enabled and message.entities:
                for entity in message.entities:
                    if entity.type == 'url':
                        url = message.text[entity.offset:entity.offset + entity.length]
                        if download_service.is_supported_url(url):
                            await self.handle_download_request(update, context, url)
                            return
            
        except Exception as e:
            self.logger.error(f"Error handling group message: {e}")
    
    async def check_group_locks(self, update: Update, context: ContextTypes.DEFAULT_TYPE, group: Group):
        """Check group locks and handle accordingly"""
        try:
            message = update.message
            user = message.from_user
            
            # Skip checks for admins and VIP members
            if group.is_admin(user.id) or group.is_vip(user.id):
                return
            
            # Check various locks
            if message.entities:
                for entity in message.entities:
                    if entity.type == 'url' and group.locks.links:
                        await message.delete()
                        return
                    
                    if entity.type == 'text_link' and group.locks.hyperlinks:
                        await message.delete()
                        return
                    
                    if entity.type == 'hashtag' and group.locks.hashtags:
                        await message.delete()
                        return
                    
                    if entity.type == 'mention' and group.locks.usernames:
                        await message.delete()
                        return
            
            # Check message content
            if message.text:
                # Check for filtered words
                for word in group.lists.filtered_words:
                    if word.lower() in message.text.lower():
                        await message.delete()
                        return
            
            # Check message type locks
            if message.forward_from and group.locks.forwarded:
                await message.delete()
                return
            
            if message.photo and group.locks.photos:
                await message.delete()
                return
            
            if message.video and group.locks.videos:
                await message.delete()
                return
            
            if message.audio and group.locks.music:
                await message.delete()
                return
            
            if message.document and group.locks.files:
                await message.delete()
                return
            
            if message.sticker and group.locks.stickers:
                await message.delete()
                return
            
            if message.animation and group.locks.gifs:
                await message.delete()
                return
            
            if message.location and group.locks.location:
                await message.delete()
                return
            
            if message.voice and group.locks.voice:
                await message.delete()
                return
            
            if message.video_note and group.locks.video_msg:
                await message.delete()
                return
            
            if message.poll and group.locks.polls:
                await message.delete()
                return
            
        except Exception as e:
            self.logger.error(f"Error checking group locks: {e}")
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries"""
        try:
            query = update.callback_query
            user = query.from_user
            
            # Get user data
            user_data = firebase_service.get_user(user.id)
            language = user_data.get('language', 'en') if user_data else 'en'
            
            # Handle different callback data
            data = query.data
            
            if data == 'main_menu':
                await self.show_main_menu(update, context)
            
            elif data == 'download':
                await self.show_download_info(update, context)
            
            elif data == 'change_language':
                await self.show_language_selection(update, context)
            
            elif data == 'help':
                await self.show_help(update, context)
            
            elif data.startswith('lang_'):
                lang_code = data.split('_')[1]
                await self.change_language(update, context, lang_code)
            
            elif data == 'admin_panel':
                await self.show_admin_panel(update, context)
            
            elif data == 'admin_stats':
                await self.show_admin_statistics(update, context)
            
            elif data == 'admin_broadcast':
                await self.show_broadcast_menu(update, context)
            
            # Answer callback query
            await query.answer()
            
        except Exception as e:
            self.logger.error(f"Error handling callback query: {e}")
    
    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main menu"""
        try:
            query = update.callback_query
            user = query.from_user
            
            # Get user data
            user_data = firebase_service.get_user(user.id)
            language = user_data.get('language', 'en')
            
            # Create main menu keyboard
            keyboard = [
                [InlineKeyboardButton(_("DOWNLOAD_FEATURE", language), callback_data='download')],
                [InlineKeyboardButton(_("CHANGE_LANGUAGE", language), callback_data='change_language')],
                [InlineKeyboardButton(_("BTN_HELP", language), callback_data='help')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Edit message
            await query.edit_message_text(
                _("BOT_CAPABILITIES", language),
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing main menu: {e}")
    
    async def show_download_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show download information"""
        try:
            query = update.callback_query
            user = query.from_user
            
            # Get user data
            user_data = firebase_service.get_user(user.id)
            language = user_data.get('language', 'en')
            
            # Create keyboard
            keyboard = [[InlineKeyboardButton(_("BTN_BACK", language), callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Edit message
            download_info = _("PLEASE_WAIT", language) + "\n\n" + _("SEND_URL", language)
            await query.edit_message_text(
                download_info,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            self.logger.error(f"Error showing download info: {e}")
    
    async def show_language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show language selection"""
        try:
            query = update.callback_query
            user = query.from_user
            
            # Get user data
            user_data = firebase_service.get_user(user.id)
            language = user_data.get('language', 'en')
            
            # Create language selection keyboard
            keyboard = []
            for lang_code, lang_name in language_manager.get_supported_languages().items():
                keyboard.append([InlineKeyboardButton(lang_name, callback_data=f'lang_{lang_code}')])
            
            keyboard.append([InlineKeyboardButton(_("BTN_BACK", language), callback_data='main_menu')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                _("PLEASE_WAIT", language),
                reply_markup=reply_markup
            )
            
        except Exception as e:
            self.logger.error(f"Error showing language selection: {e}")
    
    async def change_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE, lang_code: str):
        """Change user language"""
        try:
            query = update.callback_query
            user = query.from_user
            
            # Check if language is supported
            if not language_manager.is_supported(lang_code):
                await query.answer("❌ Language not supported", show_alert=True)
                return
            
            # Update user language
            firebase_service.update_user(user.id, {'language': lang_code})
            
            # Show success message
            language_name = language_manager.get_language_name(lang_code)
            await query.answer(f"✅ Language changed to {language_name}")
            
            # Show main menu
            await self.show_main_menu(update, context)
            
        except Exception as e:
            self.logger.error(f"Error changing language: {e}")
    
    async def show_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help"""
        try:
            query = update.callback_query
            user = query.from_user
            
            # Get user data
            user_data = firebase_service.get_user(user.id)
            language = user_data.get('language', 'en')
            
            # Create keyboard
            keyboard = [[InlineKeyboardButton(_("BTN_BACK", language), callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Edit message
            await query.edit_message_text(
                _("HELP_TEXT", language),
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing help: {e}")
    
    async def show_admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show admin panel"""
        try:
            query = update.callback_query
            user = query.from_user
            
            # Get user data
            user_data = firebase_service.get_user(user.id)
            if not user_data or not user_data.get('is_admin', False):
                await query.answer("❌ Access denied", show_alert=True)
                return
            
            language = user_data.get('language', 'en')
            
            # Create admin panel keyboard
            keyboard = [
                [InlineKeyboardButton(_("BTN_STATS", language), callback_data='admin_stats')],
                [InlineKeyboardButton(_("BTN_BROADCAST", language), callback_data='admin_broadcast')],
                [InlineKeyboardButton(_("BTN_SETTINGS", language), callback_data='admin_settings')],
                [InlineKeyboardButton(_("BTN_BACK", language), callback_data='main_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Edit message
            await query.edit_message_text(
                _("ADMIN_PANEL", language),
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing admin panel: {e}")
    
    async def show_admin_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show admin statistics"""
        try:
            query = update.callback_query
            user = query.from_user
            
            # Get user data
            user_data = firebase_service.get_user(user.id)
            if not user_data or not user_data.get('is_admin', False):
                await query.answer("❌ Access denied", show_alert=True)
                return
            
            # Get statistics
            stats = firebase_service.get_statistics()
            
            # Get user language
            language = user_data.get('language', 'en')
            
            # Format statistics
            stats_text = _("STATISTICS", language, **stats)
            
            # Create back button
            keyboard = [[InlineKeyboardButton(_("BTN_BACK", language), callback_data='admin_panel')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                stats_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing admin statistics: {e}")
    
    async def show_broadcast_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show broadcast menu"""
        try:
            query = update.callback_query
            user = query.from_user
            
            # Get user data
            user_data = firebase_service.get_user(user.id)
            if not user_data or not user_data.get('is_admin', False):
                await query.answer("❌ Access denied", show_alert=True)
                return
            
            language = user_data.get('language', 'en')
            
            # Create broadcast menu keyboard
            keyboard = [
                [InlineKeyboardButton("👤 " + _("BROADCAST_USERS", language), callback_data='broadcast_users')],
                [InlineKeyboardButton("👥 " + _("BROADCAST_USERS_GROUPS", language), callback_data='broadcast_users_groups')],
                [InlineKeyboardButton("⏰ " + _("BROADCAST_SCHEDULED", language), callback_data='broadcast_scheduled')],
                [InlineKeyboardButton("🗑️ " + _("BROADCAST_DELETE", language), callback_data='broadcast_delete')],
                [InlineKeyboardButton(_("BTN_BACK", language), callback_data='admin_panel')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Edit message
            await query.edit_message_text(
                _("BROADCAST_MENU", language),
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing broadcast menu: {e}")

# Add missing text constants
def _(key: str, language: str = 'en', **kwargs) -> str:
    """Shorthand function for getting text"""
    texts = {
        'SEND_URL': {
            'en': 'Please send me a URL to download',
            'fa': 'لطفاً یک URL برای دانلود ارسال کنید'
        },
        'BROADCAST_USERS': {
            'en': 'Broadcast to Users',
            'fa': 'پیام همگانی به کاربران'
        },
        'BROADCAST_USERS_GROUPS': {
            'en': 'Broadcast to Users & Groups',
            'fa': 'پیام همگانی به کاربران و گروه‌ها'
        },
        'BROADCAST_SCHEDULED': {
            'en': 'Scheduled Broadcast',
            'fa': 'پیام همگانی زمان‌بندی شده'
        },
        'BROADCAST_DELETE': {
            'en': 'Delete Broadcast',
            'fa': 'حذف پیام همگانی'
        }
    }
    
    text = texts.get(key, {}).get(language, key)
    try:
        return text.format(**kwargs)
    except (KeyError, ValueError):
        return text