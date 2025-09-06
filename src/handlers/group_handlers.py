import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message, Chat, ChatMemberAdministrator
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.error import TelegramError
from typing import Optional, Dict, Any, List

from config.config import Config
from src.services.firebase import firebase_service
from src.models.group import Group
from src.utils.logger import Logger
from src.utils.language import language_manager, _

class GroupHandlers:
    """Group management handlers"""
    
    def __init__(self):
        self.logger = Logger("GroupHandlers")
        self.group_conversations = {}  # (group_id, user_id) -> conversation_state
        self.temp_data = {}  # (group_id, user_id) -> temporary_data
        
        # Conversation states
        self.SETTINGS_WELCOME = 1
        self.SETTINGS_FORCE_CHANNELS = 2
        self.SETTINGS_WARNINGS = 3
        self.SETTINGS_AUTO_LOCK = 4
        self.LIST_MANAGEMENT = 5
        self.FILTER_WORDS = 6
    
    async def panel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /panel command in groups"""
        try:
            message = update.message
            chat = message.chat
            user = message.from_user
            
            # Check if it's a group
            if chat.type not in ['group', 'supergroup']:
                await message.reply_text("❌ This command is only available in groups")
                return
            
            # Check if user is admin
            chat_member = await context.bot.get_chat_member(chat.id, user.id)
            if not isinstance(chat_member, ChatMemberAdministrator) and not chat_member.status == 'creator':
                await message.reply_text("❌ Only group admins can use this command")
                return
            
            # Get or create group data
            group_data = firebase_service.get_group(chat.id)
            if not group_data:
                success = firebase_service.create_group(
                    group_id=chat.id,
                    title=chat.title or "Unknown Group"
                )
                if not success:
                    await message.reply_text("❌ Error creating group profile")
                    return
                
                group_data = firebase_service.get_group(chat.id)
            
            # Convert to Group model
            group = Group.from_dict(group_data)
            
            # Add user as admin if not already
            if not group.is_admin(user.id):
                group.add_admin(user.id)
                firebase_service.update_group(chat.id, {'lists': group.lists.to_dict()})
            
            # Show group panel
            await self.show_group_panel(update, context, group)
            
        except Exception as e:
            self.logger.error(f"Error in panel command: {e}")
            await message.reply_text("❌ An error occurred")
    
    async def show_group_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE, group: Group):
        """Show group management panel"""
        try:
            message = update.message or update.callback_query.message
            user = message.from_user
            
            # Get user language
            user_data = firebase_service.get_user(user.id)
            language = user_data.get('language', 'en') if user_data else 'en'
            
            # Create panel keyboard
            keyboard = [
                [InlineKeyboardButton(_("BTN_LOCKS", language), callback_data='group_locks')],
                [InlineKeyboardButton(_("BTN_LISTS", language), callback_data='group_lists')],
                [InlineKeyboardButton(_("BTN_SETTINGS", language), callback_data='group_settings')],
                [InlineKeyboardButton(_("BTN_ENTERTAINMENT", language), callback_data='group_entertainment')],
                [InlineKeyboardButton(_("BTN_BACK", language), callback_data='main_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Edit or send message
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    _("GROUP_PANEL", language),
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            else:
                await message.reply_text(
                    _("GROUP_PANEL", language),
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            
        except Exception as e:
            self.logger.error(f"Error showing group panel: {e}")
    
    async def show_locks_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show locks menu"""
        try:
            query = update.callback_query
            chat = query.message.chat
            user = query.from_user
            
            # Get group data
            group_data = firebase_service.get_group(chat.id)
            if not group_data:
                await query.answer("❌ Group not found", show_alert=True)
                return
            
            group = Group.from_dict(group_data)
            
            # Check if user is admin
            if not group.is_admin(user.id):
                await query.answer("❌ Access denied", show_alert=True)
                return
            
            # Get user language
            user_data = firebase_service.get_user(user.id)
            language = user_data.get('language', 'en') if user_data else 'en'
            
            # Create locks keyboard
            keyboard = [
                [InlineKeyboardButton(
                    f"{'🔒' if group.locks.links else '🔓'} " + _("BTN_LOCK_LINKS", language),
                    callback_data='toggle_lock_links'
                )],
                [InlineKeyboardButton(
                    f"{'🔒' if group.locks.hyperlinks else '🔓'} " + _("BTN_LOCK_HYPERLINKS", language),
                    callback_data='toggle_lock_hyperlinks'
                )],
                [InlineKeyboardButton(
                    f"{'🔒' if group.locks.hashtags else '🔓'} " + _("BTN_LOCK_HASHTAGS", language),
                    callback_data='toggle_lock_hashtags'
                )],
                [InlineKeyboardButton(
                    f"{'🔒' if group.locks.usernames else '🔓'} " + _("BTN_LOCK_USERNAMES", language),
                    callback_data='toggle_lock_usernames'
                )],
                [InlineKeyboardButton(
                    f"{'🔒' if group.locks.forwarded else '🔓'} " + _("BTN_LOCK_FORWARDED", language),
                    callback_data='toggle_lock_forwarded'
                )],
                [InlineKeyboardButton(
                    f"{'🔒' if group.locks.videos else '🔓'} " + _("BTN_LOCK_VIDEOS", language),
                    callback_data='toggle_lock_videos'
                )],
                [InlineKeyboardButton(
                    f"{'🔒' if group.locks.photos else '🔓'} " + _("BTN_LOCK_PHOTOS", language),
                    callback_data='toggle_lock_photos'
                )],
                [InlineKeyboardButton(
                    f"{'🔒' if group.locks.files else '🔓'} " + _("BTN_LOCK_FILES", language),
                    callback_data='toggle_lock_files'
                )],
                [InlineKeyboardButton(
                    f"{'🔒' if group.locks.music else '🔓'} " + _("BTN_LOCK_MUSIC", language),
                    callback_data='toggle_lock_music'
                )],
                [InlineKeyboardButton(_("BTN_BACK", language), callback_data='group_panel')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                _("GROUP_LOCKS_MENU", language),
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing locks menu: {e}")
    
    async def toggle_lock(self, update: Update, context: ContextTypes.DEFAULT_TYPE, lock_type: str):
        """Toggle a specific lock"""
        try:
            query = update.callback_query
            chat = query.message.chat
            user = query.from_user
            
            # Get group data
            group_data = firebase_service.get_group(chat.id)
            if not group_data:
                await query.answer("❌ Group not found", show_alert=True)
                return
            
            group = Group.from_dict(group_data)
            
            # Check if user is admin
            if not group.is_admin(user.id):
                await query.answer("❌ Access denied", show_alert=True)
                return
            
            # Toggle lock
            current_state = group.is_feature_locked(lock_type)
            if current_state:
                group.unlock_feature(lock_type)
            else:
                group.lock_feature(lock_type)
            
            # Update group
            firebase_service.update_group(chat.id, {'locks': group.locks.to_dict()})
            
            # Show updated locks menu
            await self.show_locks_menu(update, context)
            
            # Log action
            action = f"{'Unlocked' if not current_state else 'Locked'} {lock_type}"
            self.logger.log_group_action(chat.id, chat.title, action, f"by {user.id}")
            
        except Exception as e:
            self.logger.error(f"Error toggling lock {lock_type}: {e}")
    
    async def show_lists_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show lists management menu"""
        try:
            query = update.callback_query
            chat = query.message.chat
            user = query.from_user
            
            # Get group data
            group_data = firebase_service.get_group(chat.id)
            if not group_data:
                await query.answer("❌ Group not found", show_alert=True)
                return
            
            group = Group.from_dict(group_data)
            
            # Check if user is admin
            if not group.is_admin(user.id):
                await query.answer("❌ Access denied", show_alert=True)
                return
            
            # Get user language
            user_data = firebase_service.get_user(user.id)
            language = user_data.get('language', 'en') if user_data else 'en'
            
            # Create lists keyboard
            keyboard = [
                [InlineKeyboardButton(_("BTN_LIST_ADMINS", language), callback_data='list_admins')],
                [InlineKeyboardButton(_("BTN_LIST_VIP", language), callback_data='list_vip')],
                [InlineKeyboardButton(_("BTN_LIST_FILTERED", language), callback_data='list_filtered')],
                [InlineKeyboardButton(_("BTN_LIST_MUTED", language), callback_data='list_muted')],
                [InlineKeyboardButton(_("BTN_LIST_BANNED", language), callback_data='list_banned')],
                [InlineKeyboardButton(_("BTN_LIST_WARNINGS", language), callback_data='list_warnings')],
                [InlineKeyboardButton(_("BTN_BACK", language), callback_data='group_panel')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                _("GROUP_LISTS_MENU", language),
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing lists menu: {e}")
    
    async def show_settings_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show settings menu"""
        try:
            query = update.callback_query
            chat = query.message.chat
            user = query.from_user
            
            # Get group data
            group_data = firebase_service.get_group(chat.id)
            if not group_data:
                await query.answer("❌ Group not found", show_alert=True)
                return
            
            group = Group.from_dict(group_data)
            
            # Check if user is admin
            if not group.is_admin(user.id):
                await query.answer("❌ Access denied", show_alert=True)
                return
            
            # Get user language
            user_data = firebase_service.get_user(user.id)
            language = user_data.get('language', 'en') if user_data else 'en'
            
            # Create settings keyboard
            keyboard = [
                [InlineKeyboardButton(_("BTN_SET_FORCE_MEMBER", language), callback_data='set_force_member')],
                [InlineKeyboardButton(_("BTN_SET_WELCOME", language), callback_data='set_welcome')],
                [InlineKeyboardButton(_("BTN_SET_WARNINGS", language), callback_data='set_warnings')],
                [InlineKeyboardButton(_("BTN_SET_AUTO_LOCK", language), callback_data='set_auto_lock')],
                [InlineKeyboardButton(_("BTN_SET_GROUP_LOCK", language), callback_data='set_group_lock')],
                [InlineKeyboardButton(_("BTN_SET_DOWNLOADS", language), callback_data='set_downloads')],
                [InlineKeyboardButton(_("BTN_BACK", language), callback_data='group_panel')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                _("GROUP_SETTINGS_MENU", language),
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing settings menu: {e}")
    
    async def show_entertainment_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show entertainment menu"""
        try:
            query = update.callback_query
            chat = query.message.chat
            user = query.from_user
            
            # Get group data
            group_data = firebase_service.get_group(chat.id)
            if not group_data:
                await query.answer("❌ Group not found", show_alert=True)
                return
            
            group = Group.from_dict(group_data)
            
            # Check if user is admin
            if not group.is_admin(user.id):
                await query.answer("❌ Access denied", show_alert=True)
                return
            
            # Get user language
            user_data = firebase_service.get_user(user.id)
            language = user_data.get('language', 'en') if user_data else 'en'
            
            # Create entertainment keyboard
            keyboard = [
                [InlineKeyboardButton(_("BTN_FAL_HAFEZ", language), callback_data='fal_hafez')],
                [InlineKeyboardButton(_("BTN_CURRENCY", language), callback_data='currency_rates')],
                [InlineKeyboardButton(_("BTN_WEATHER", language), callback_data='weather_info')],
                [InlineKeyboardButton(_("BTN_BACK", language), callback_data='group_panel')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                _("GROUP_ENTERTAINMENT_MENU", language),
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing entertainment menu: {e}")
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries for group management"""
        try:
            query = update.callback_query
            data = query.data
            
            # Handle different callback data
            if data == 'group_panel':
                await self.show_group_panel_from_callback(update, context)
            
            elif data == 'group_locks':
                await self.show_locks_menu(update, context)
            
            elif data == 'group_lists':
                await self.show_lists_menu(update, context)
            
            elif data == 'group_settings':
                await self.show_settings_menu(update, context)
            
            elif data == 'group_entertainment':
                await self.show_entertainment_menu(update, context)
            
            elif data.startswith('toggle_lock_'):
                lock_type = data.replace('toggle_lock_', '')
                await self.toggle_lock(update, context, lock_type)
            
            elif data == 'set_force_member':
                await self.set_force_member(update, context)
            
            elif data == 'set_welcome':
                await self.set_welcome_message(update, context)
            
            elif data == 'set_warnings':
                await self.set_warning_settings(update, context)
            
            elif data == 'set_auto_lock':
                await self.set_auto_lock(update, context)
            
            elif data == 'set_group_lock':
                await self.set_group_lock(update, context)
            
            elif data == 'set_downloads':
                await self.set_downloads_enabled(update, context)
            
            elif data == 'fal_hafez':
                await self.fal_hafez(update, context)
            
            elif data == 'currency_rates':
                await self.currency_rates(update, context)
            
            elif data == 'weather_info':
                await self.weather_info(update, context)
            
            # Answer callback query
            await query.answer()
            
        except Exception as e:
            self.logger.error(f"Error handling callback query: {e}")
    
    async def show_group_panel_from_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show group panel from callback query"""
        try:
            query = update.callback_query
            chat = query.message.chat
            
            # Get group data
            group_data = firebase_service.get_group(chat.id)
            if not group_data:
                await query.answer("❌ Group not found", show_alert=True)
                return
            
            group = Group.from_dict(group_data)
            
            # Show group panel
            await self.show_group_panel(update, context, group)
            
        except Exception as e:
            self.logger.error(f"Error showing group panel from callback: {e}")
    
    async def set_force_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set force membership settings"""
        try:
            query = update.callback_query
            chat = query.message.chat
            user = query.from_user
            
            # Get group data
            group_data = firebase_service.get_group(chat.id)
            if not group_data:
                await query.answer("❌ Group not found", show_alert=True)
                return
            
            group = Group.from_dict(group_data)
            
            # Check if user is admin
            if not group.is_admin(user.id):
                await query.answer("❌ Access denied", show_alert=True)
                return
            
            # Get user language
            user_data = firebase_service.get_user(user.id)
            language = user_data.get('language', 'en') if user_data else 'en'
            
            # Toggle force membership
            group.settings.force_membership = not group.settings.force_membership
            
            # Update group
            firebase_service.update_group(chat.id, {'settings': group.settings.to_dict()})
            
            # If enabling, ask for channels
            if group.settings.force_membership:
                keyboard = [[InlineKeyboardButton(_("BTN_CANCEL", language), callback_data='group_settings')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    _("PLEASE_SEND_FORCE_CHANNELS", language),
                    reply_markup=reply_markup
                )
                
                # Set conversation state
                self.group_conversations[(chat.id, user.id)] = self.SETTINGS_FORCE_CHANNELS
            else:
                # Clear channels and show settings menu
                group.settings.force_channels = []
                firebase_service.update_group(chat.id, {'settings': group.settings.to_dict()})
                
                await self.show_settings_menu(update, context)
            
        except Exception as e:
            self.logger.error(f"Error setting force membership: {e}")
    
    async def set_welcome_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set welcome message"""
        try:
            query = update.callback_query
            chat = query.message.chat
            user = query.from_user
            
            # Get group data
            group_data = firebase_service.get_group(chat.id)
            if not group_data:
                await query.answer("❌ Group not found", show_alert=True)
                return
            
            group = Group.from_dict(group_data)
            
            # Check if user is admin
            if not group.is_admin(user.id):
                await query.answer("❌ Access denied", show_alert=True)
                return
            
            # Get user language
            user_data = firebase_service.get_user(user.id)
            language = user_data.get('language', 'en') if user_data else 'en'
            
            # Show current welcome message and ask for new one
            keyboard = [[InlineKeyboardButton(_("BTN_CANCEL", language), callback_data='group_settings')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            current_message = group.settings.welcome_message
            await query.edit_message_text(
                _("CURRENT_WELCOME_MESSAGE", language, message=current_message) + "\n\n" + 
                _("PLEASE_SEND_NEW_WELCOME", language),
                reply_markup=reply_markup
            )
            
            # Set conversation state
            self.group_conversations[(chat.id, user.id)] = self.SETTINGS_WELCOME
            
        except Exception as e:
            self.logger.error(f"Error setting welcome message: {e}")
    
    async def set_warning_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set warning settings"""
        try:
            query = update.callback_query
            chat = query.message.chat
            user = query.from_user
            
            # Get group data
            group_data = firebase_service.get_group(chat.id)
            if not group_data:
                await query.answer("❌ Group not found", show_alert=True)
                return
            
            group = Group.from_dict(group_data)
            
            # Check if user is admin
            if not group.is_admin(user.id):
                await query.answer("❌ Access denied", show_alert=True)
                return
            
            # Get user language
            user_data = firebase_service.get_user(user.id)
            language = user_data.get('language', 'en') if user_data else 'en'
            
            # Show current warning limit and ask for new one
            keyboard = [[InlineKeyboardButton(_("BTN_CANCEL", language), callback_data='group_settings')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            current_limit = group.settings.warn_limit
            await query.edit_message_text(
                _("CURRENT_WARNING_LIMIT", language, limit=current_limit) + "\n\n" + 
                _("PLEASE_SEND_NEW_WARNING_LIMIT", language),
                reply_markup=reply_markup
            )
            
            # Set conversation state
            self.group_conversations[(chat.id, user.id)] = self.SETTINGS_WARNINGS
            
        except Exception as e:
            self.logger.error(f"Error setting warning settings: {e}")
    
    async def set_auto_lock(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set auto lock settings"""
        try:
            query = update.callback_query
            chat = query.message.chat
            user = query.from_user
            
            # Get group data
            group_data = firebase_service.get_group(chat.id)
            if not group_data:
                await query.answer("❌ Group not found", show_alert=True)
                return
            
            group = Group.from_dict(group_data)
            
            # Check if user is admin
            if not group.is_admin(user.id):
                await query.answer("❌ Access denied", show_alert=True)
                return
            
            # Get user language
            user_data = firebase_service.get_user(user.id)
            language = user_data.get('language', 'en') if user_data else 'en'
            
            # Toggle auto lock
            group.settings.auto_lock = not group.settings.auto_lock
            
            # Update group
            firebase_service.update_group(chat.id, {'settings': group.settings.to_dict()})
            
            # If enabling, ask for duration
            if group.settings.auto_lock:
                keyboard = [[InlineKeyboardButton(_("BTN_CANCEL", language), callback_data='group_settings')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    _("PLEASE_SEND_AUTO_LOCK_DURATION", language),
                    reply_markup=reply_markup
                )
                
                # Set conversation state
                self.group_conversations[(chat.id, user.id)] = self.SETTINGS_AUTO_LOCK
            else:
                await self.show_settings_menu(update, context)
            
        except Exception as e:
            self.logger.error(f"Error setting auto lock: {e}")
    
    async def set_group_lock(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set group lock"""
        try:
            query = update.callback_query
            chat = query.message.chat
            user = query.from_user
            
            # Get group data
            group_data = firebase_service.get_group(chat.id)
            if not group_data:
                await query.answer("❌ Group not found", show_alert=True)
                return
            
            group = Group.from_dict(group_data)
            
            # Check if user is admin
            if not group.is_admin(user.id):
                await query.answer("❌ Access denied", show_alert=True)
                return
            
            # Toggle group lock
            group.settings.group_locked = not group.settings.group_locked
            
            # Update group
            firebase_service.update_group(chat.id, {'settings': group.settings.to_dict()})
            
            # Show settings menu
            await self.show_settings_menu(update, context)
            
            # Log action
            action = f"Group {'locked' if group.settings.group_locked else 'unlocked'}"
            self.logger.log_group_action(chat.id, chat.title, action, f"by {user.id}")
            
        except Exception as e:
            self.logger.error(f"Error setting group lock: {e}")
    
    async def set_downloads_enabled(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set downloads enabled"""
        try:
            query = update.callback_query
            chat = query.message.chat
            user = query.from_user
            
            # Get group data
            group_data = firebase_service.get_group(chat.id)
            if not group_data:
                await query.answer("❌ Group not found", show_alert=True)
                return
            
            group = Group.from_dict(group_data)
            
            # Check if user is admin
            if not group.is_admin(user.id):
                await query.answer("❌ Access denied", show_alert=True)
                return
            
            # Toggle downloads
            group.settings.downloads_enabled = not group.settings.downloads_enabled
            
            # Update group
            firebase_service.update_group(chat.id, {'settings': group.settings.to_dict()})
            
            # Show settings menu
            await self.show_settings_menu(update, context)
            
            # Log action
            action = f"Downloads {'enabled' if group.settings.downloads_enabled else 'disabled'}"
            self.logger.log_group_action(chat.id, chat.title, action, f"by {user.id}")
            
        except Exception as e:
            self.logger.error(f"Error setting downloads enabled: {e}")
    
    async def handle_conversation_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle conversation messages"""
        try:
            message = update.message
            chat = message.chat
            user = message.from_user
            
            # Check if user is in conversation
            conversation_key = (chat.id, user.id)
            if conversation_key not in self.group_conversations:
                return
            
            state = self.group_conversations[conversation_key]
            
            # Get group data
            group_data = firebase_service.get_group(chat.id)
            if not group_data:
                return
            
            group = Group.from_dict(group_data)
            
            # Get user language
            user_data = firebase_service.get_user(user.id)
            language = user_data.get('language', 'en') if user_data else 'en'
            
            # Handle different states
            if state == self.SETTINGS_WELCOME:
                # Handle welcome message
                group.settings.welcome_message = message.text
                firebase_service.update_group(chat.id, {'settings': group.settings.to_dict()})
                
                await message.reply_text(
                    _("WELCOME_MESSAGE_UPDATED", language),
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(_("BTN_BACK", language), callback_data='group_settings')
                    ]])
                )
                
                del self.group_conversations[conversation_key]
            
            elif state == self.SETTINGS_FORCE_CHANNELS:
                # Handle force membership channels
                channels = [ch.strip() for ch in message.text.split('\n') if ch.strip()]
                group.settings.force_channels = channels
                firebase_service.update_group(chat.id, {'settings': group.settings.to_dict()})
                
                await message.reply_text(
                    _("FORCE_CHANNELS_UPDATED", language),
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(_("BTN_BACK", language), callback_data='group_settings')
                    ]])
                )
                
                del self.group_conversations[conversation_key]
            
            elif state == self.SETTINGS_WARNINGS:
                # Handle warning limit
                try:
                    limit = int(message.text)
                    if limit < 1 or limit > 10:
                        await message.reply_text(_("INVALID_WARNING_LIMIT", language))
                        return
                    
                    group.settings.warn_limit = limit
                    firebase_service.update_group(chat.id, {'settings': group.settings.to_dict()})
                    
                    await message.reply_text(
                        _("WARNING_LIMIT_UPDATED", language),
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(_("BTN_BACK", language), callback_data='group_settings')
                        ]])
                    )
                    
                    del self.group_conversations[conversation_key]
                except ValueError:
                    await message.reply_text(_("INVALID_WARNING_LIMIT", language))
            
            elif state == self.SETTINGS_AUTO_LOCK:
                # Handle auto lock duration
                try:
                    duration = int(message.text)
                    if duration < 1 or duration > 1440:  # Max 24 hours
                        await message.reply_text(_("INVALID_AUTO_LOCK_DURATION", language))
                        return
                    
                    group.settings.auto_lock_duration = duration
                    firebase_service.update_group(chat.id, {'settings': group.settings.to_dict()})
                    
                    await message.reply_text(
                        _("AUTO_LOCK_DURATION_UPDATED", language),
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(_("BTN_BACK", language), callback_data='group_settings')
                        ]])
                    )
                    
                    del self.group_conversations[conversation_key]
                except ValueError:
                    await message.reply_text(_("INVALID_AUTO_LOCK_DURATION", language))
            
        except Exception as e:
            self.logger.error(f"Error handling conversation message: {e}")
    
    async def fal_hafez(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show Fal-e Hafez"""
        try:
            query = update.callback_query
            chat = query.message.chat
            
            # Get user language
            user_data = firebase_service.get_user(query.from_user.id)
            language = user_data.get('language', 'en') if user_data else 'en'
            
            # Get random Fal-e Hafez (placeholder implementation)
            poem = "غزل حافظ (متن نمونه)"
            interpretation = "تفسیر فال (متن نمونه)"
            
            fal_text = _("FAL_HAFEZ", language, poem=poem, interpretation=interpretation)
            
            keyboard = [[InlineKeyboardButton(_("BTN_BACK", language), callback_data='group_entertainment')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                fal_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error in fal_hafez: {e}")
    
    async def currency_rates(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show currency rates"""
        try:
            query = update.callback_query
            chat = query.message.chat
            
            # Get user language
            user_data = firebase_service.get_user(query.from_user.id)
            language = user_data.get('language', 'en') if user_data else 'en'
            
            # Get currency rates (placeholder implementation)
            rates = "USD: 42,000\nEUR: 45,000\nGBP: 52,000"
            
            currency_text = _("CURRENCY_RATES", language, rates=rates)
            
            keyboard = [[InlineKeyboardButton(_("BTN_BACK", language), callback_data='group_entertainment')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                currency_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error in currency_rates: {e}")
    
    async def weather_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show weather information"""
        try:
            query = update.callback_query
            chat = query.message.chat
            
            # Get user language
            user_data = firebase_service.get_user(query.from_user.id)
            language = user_data.get('language', 'en') if user_data else 'en'
            
            # Get weather info (placeholder implementation)
            weather = "Temperature: 25°C\nCondition: Sunny\nHumidity: 60%"
            
            weather_text = _("WEATHER_INFO", language, city="Tehran", weather=weather)
            
            keyboard = [[InlineKeyboardButton(_("BTN_BACK", language), callback_data='group_entertainment')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                weather_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error in weather_info: {e}")
    
    def get_handlers(self):
        """Get all handlers for group management"""
        return [
            CommandHandler("panel", self.panel_command),
            CallbackQueryHandler(self.handle_callback_query),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_conversation_message)
        ]

# Add missing text constants
def _(key: str, language: str = 'en', **kwargs) -> str:
    """Shorthand function for getting text"""
    texts = {
        'GROUP_LOCKS_MENU': {
            'en': '🔒 *Group Locks*\n\nToggle locks to restrict message types in the group.',
            'fa': '🔒 *قفل‌های گروه*\n\nقفل‌ها را برای محدود کردن انواع پیام‌ها در گروه فعال/غیرفعال کنید.'
        },
        'GROUP_LISTS_MENU': {
            'en': '📋 *Group Lists*\n\nManage various lists for group members.',
            'fa': '📋 *لیست‌های گروه*\n\nلیست‌های مختلف اعضای گروه را مدیریت کنید.'
        },
        'GROUP_SETTINGS_MENU': {
            'en': '⚙️ *Group Settings*\n\nConfigure group settings and preferences.',
            'fa': '⚙️ *تنظیمات گروه*\n\nتنظیمات و ترجیحات گروه را پیکربندی کنید.'
        },
        'GROUP_ENTERTAINMENT_MENU': {
            'en': '🎮 *Entertainment*\n\nFun features for group members.',
            'fa': '🎮 *سرگرمی*\n\nقابلیت‌های سرگرم‌کننده برای اعضای گروه.'
        },
        'PLEASE_SEND_FORCE_CHANNELS': {
            'en': 'Please send the list of channels (one per line) that users must join:',
            'fa': 'لطفاً لیست کانال‌هایی که کاربران باید عضو شوند را ارسال کنید (هر کانال در یک خط):'
        },
        'CURRENT_WELCOME_MESSAGE': {
            'en': 'Current welcome message:\n{message}',
            'fa': 'پیام خوش آمد فعلی:\n{message}'
        },
        'PLEASE_SEND_NEW_WELCOME': {
            'en': 'Please send the new welcome message (use {user} for username, {group} for group name):',
            'fa': 'لطفاً پیام خوش آمد جدید را ارسال کنید (از {user} برای نام کاربری و {group} برای نام گروه استفاده کنید):'
        },
        'CURRENT_WARNING_LIMIT': {
            'en': 'Current warning limit: {limit}',
            'fa': 'محدودیت اخطار فعلی: {limit}'
        },
        'PLEASE_SEND_NEW_WARNING_LIMIT': {
            'en': 'Please send the new warning limit (1-10):',
            'fa': 'لطفاً محدودیت اخطار جدید را ارسال کنید (۱-۱۰):'
        },
        'PLEASE_SEND_AUTO_LOCK_DURATION': {
            'en': 'Please send the auto lock duration in minutes (1-1440):',
            'fa': 'لطفاً مدت قفل خودکار را به دقیقه ارسال کنید (۱-۱۴۴۰):'
        },
        'WELCOME_MESSAGE_UPDATED': {
            'en': '✅ Welcome message updated successfully!',
            'fa': '✅ پیام خوش آمد با موفقیت به‌روزرسانی شد!'
        },
        'FORCE_CHANNELS_UPDATED': {
            'en': '✅ Force membership channels updated successfully!',
            'fa': '✅ کانال‌های عضویت اجباری با موفقیت به‌روزرسانی شد!'
        },
        'WARNING_LIMIT_UPDATED': {
            'en': '✅ Warning limit updated successfully!',
            'fa': '✅ محدودیت اخطار با موفقیت به‌روزرسانی شد!'
        },
        'AUTO_LOCK_DURATION_UPDATED': {
            'en': '✅ Auto lock duration updated successfully!',
            'fa': '✅ مدت قفل خودکار با موفقیت به‌روزرسانی شد!'
        },
        'INVALID_WARNING_LIMIT': {
            'en': '❌ Invalid warning limit. Please enter a number between 1 and 10.',
            'fa': '❌ محدودیت اخطار نامعتبر است. لطفاً عددی بین ۱ تا ۱۰ وارد کنید.'
        },
        'INVALID_AUTO_LOCK_DURATION': {
            'en': '❌ Invalid duration. Please enter a number between 1 and 1440 minutes.',
            'fa': '❌ مدت زمان نامعتبر است. لطفاً عددی بین ۱ تا ۱۴۴۰ دقیقه وارد کنید.'
        }
    }
    
    text = texts.get(key, {}).get(language, key)
    try:
        return text.format(**kwargs)
    except (KeyError, ValueError):
        return text