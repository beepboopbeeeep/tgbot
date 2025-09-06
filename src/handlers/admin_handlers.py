import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from typing import Optional, Dict, Any, List

from config.config import Config
from src.services.firebase import firebase_service
from src.utils.logger import Logger
from src.utils.language import language_manager, _

class AdminHandlers:
    """Admin handlers for the bot"""
    
    def __init__(self):
        self.logger = Logger("AdminHandlers")
        self.broadcast_states = {}  # user_id -> broadcast_data
        self.admin_conversations = {}  # user_id -> conversation_state
        
        # Conversation states
        self.BROADCAST_TYPE = 1
        self.BROADCAST_MESSAGE = 2
        self.BROADCAST_SCHEDULE = 3
        self.BROADCAST_CONFIRM = 4
    
    async def broadcast_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle broadcast to users only"""
        try:
            query = update.callback_query
            user = query.from_user
            
            # Get user data
            user_data = firebase_service.get_user(user.id)
            if not user_data or not user_data.get('is_admin', False):
                await query.answer("❌ Access denied", show_alert=True)
                return
            
            language = user_data.get('language', 'en')
            
            # Set broadcast state
            self.broadcast_states[user.id] = {
                'type': 'users',
                'message': None,
                'scheduled_time': None
            }
            
            # Ask for message
            keyboard = [[InlineKeyboardButton(_("BTN_CANCEL", language), callback_data='admin_broadcast')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                _("PLEASE_SEND_BROADCAST_MESSAGE", language),
                reply_markup=reply_markup
            )
            
            # Set conversation state
            self.admin_conversations[user.id] = self.BROADCAST_MESSAGE
            
        except Exception as e:
            self.logger.error(f"Error in broadcast_users: {e}")
    
    async def broadcast_users_groups(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle broadcast to users and groups"""
        try:
            query = update.callback_query
            user = query.from_user
            
            # Get user data
            user_data = firebase_service.get_user(user.id)
            if not user_data or not user_data.get('is_admin', False):
                await query.answer("❌ Access denied", show_alert=True)
                return
            
            language = user_data.get('language', 'en')
            
            # Set broadcast state
            self.broadcast_states[user.id] = {
                'type': 'users_and_groups',
                'message': None,
                'scheduled_time': None
            }
            
            # Ask for message
            keyboard = [[InlineKeyboardButton(_("BTN_CANCEL", language), callback_data='admin_broadcast')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                _("PLEASE_SEND_BROADCAST_MESSAGE", language),
                reply_markup=reply_markup
            )
            
            # Set conversation state
            self.admin_conversations[user.id] = self.BROADCAST_MESSAGE
            
        except Exception as e:
            self.logger.error(f"Error in broadcast_users_groups: {e}")
    
    async def broadcast_scheduled(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle scheduled broadcast"""
        try:
            query = update.callback_query
            user = query.from_user
            
            # Get user data
            user_data = firebase_service.get_user(user.id)
            if not user_data or not user_data.get('is_admin', False):
                await query.answer("❌ Access denied", show_alert=True)
                return
            
            language = user_data.get('language', 'en')
            
            # Set broadcast state
            self.broadcast_states[user.id] = {
                'type': 'scheduled',
                'message': None,
                'scheduled_time': None
            }
            
            # Ask for message
            keyboard = [[InlineKeyboardButton(_("BTN_CANCEL", language), callback_data='admin_broadcast')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                _("PLEASE_SEND_BROADCAST_MESSAGE", language),
                reply_markup=reply_markup
            )
            
            # Set conversation state
            self.admin_conversations[user.id] = self.BROADCAST_MESSAGE
            
        except Exception as e:
            self.logger.error(f"Error in broadcast_scheduled: {e}")
    
    async def broadcast_delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle broadcast deletion"""
        try:
            query = update.callback_query
            user = query.from_user
            
            # Get user data
            user_data = firebase_service.get_user(user.id)
            if not user_data or not user_data.get('is_admin', False):
                await query.answer("❌ Access denied", show_alert=True)
                return
            
            language = user_data.get('language', 'en')
            
            # Get pending broadcasts
            broadcasts = firebase_service.get_pending_broadcasts()
            
            if not broadcasts:
                await query.edit_message_text(
                    _("NO_PENDING_BROADCASTS", language),
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(_("BTN_BACK", language), callback_data='admin_broadcast')
                    ]])
                )
                return
            
            # Create broadcast list keyboard
            keyboard = []
            for broadcast in broadcasts:
                broadcast_id = broadcast.get('id', 'unknown')
                broadcast_type = broadcast.get('target_type', 'unknown')
                created_at = broadcast.get('created_at', datetime.now())
                
                # Format created time
                if isinstance(created_at, datetime):
                    time_str = created_at.strftime('%Y-%m-%d %H:%M')
                else:
                    time_str = str(created_at)
                
                keyboard.append([
                    InlineKeyboardButton(
                        f"{broadcast_type} - {time_str}",
                        callback_data=f'delete_broadcast_{broadcast_id}'
                    )
                ])
            
            keyboard.append([InlineKeyboardButton(_("BTN_BACK", language), callback_data='admin_broadcast')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                _("SELECT_BROADCAST_TO_DELETE", language),
                reply_markup=reply_markup
            )
            
        except Exception as e:
            self.logger.error(f"Error in broadcast_delete: {e}")
    
    async def delete_broadcast_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirm broadcast deletion"""
        try:
            query = update.callback_query
            user = query.from_user
            
            # Get user data
            user_data = firebase_service.get_user(user.id)
            if not user_data or not user_data.get('is_admin', False):
                await query.answer("❌ Access denied", show_alert=True)
                return
            
            language = user_data.get('language', 'en')
            
            # Get broadcast ID from callback data
            broadcast_id = query.data.split('_')[-1]
            
            # Delete broadcast
            success = firebase_service.delete_broadcast(broadcast_id)
            
            if success:
                await query.edit_message_text(
                    _("BROADCAST_DELETED", language),
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(_("BTN_BACK", language), callback_data='admin_broadcast')
                    ]])
                )
            else:
                await query.edit_message_text(
                    _("ERROR_DELETING_BROADCAST", language),
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(_("BTN_BACK", language), callback_data='admin_broadcast')
                    ]])
                )
            
        except Exception as e:
            self.logger.error(f"Error in delete_broadcast_confirm: {e}")
    
    async def handle_broadcast_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle broadcast message input"""
        try:
            message = update.message
            user = message.from_user
            
            # Check if user is in broadcast conversation
            if user.id not in self.admin_conversations:
                return
            
            # Get broadcast state
            broadcast_state = self.broadcast_states.get(user.id)
            if not broadcast_state:
                return
            
            # Get user data
            user_data = firebase_service.get_user(user.id)
            language = user_data.get('language', 'en')
            
            # Store message
            broadcast_state['message'] = message.text
            
            # If scheduled broadcast, ask for time
            if broadcast_state['type'] == 'scheduled':
                keyboard = [[InlineKeyboardButton(_("BTN_CANCEL", language), callback_data='admin_broadcast')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await message.reply_text(
                    _("PLEASE_SEND_SCHEDULE_TIME", language),
                    reply_markup=reply_markup
                )
                
                self.admin_conversations[user.id] = self.BROADCAST_SCHEDULE
            else:
                # Show confirmation
                await self.show_broadcast_confirmation(update, context)
            
        except Exception as e:
            self.logger.error(f"Error handling broadcast message: {e}")
    
    async def handle_broadcast_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle broadcast schedule input"""
        try:
            message = update.message
            user = message.from_user
            
            # Check if user is in broadcast conversation
            if user.id not in self.admin_conversations:
                return
            
            # Get broadcast state
            broadcast_state = self.broadcast_states.get(user.id)
            if not broadcast_state:
                return
            
            # Get user data
            user_data = firebase_service.get_user(user.id)
            language = user_data.get('language', 'en')
            
            # Parse schedule time
            try:
                # Try to parse different time formats
                time_text = message.text.strip()
                
                # Format: YYYY-MM-DD HH:MM
                if len(time_text) == 16 and time_text[4] == '-' and time_text[7] == '-' and time_text[10] == ' ' and time_text[13] == ':':
                    scheduled_time = datetime.strptime(time_text, '%Y-%m-%d %H:%M')
                # Format: HH:MM (today)
                elif len(time_text) == 5 and time_text[2] == ':':
                    today = datetime.now().date()
                    time_parts = time_text.split(':')
                    scheduled_time = datetime.combine(today, datetime.min.time().replace(
                        hour=int(time_parts[0]), minute=int(time_parts[1])
                    ))
                else:
                    raise ValueError("Invalid time format")
                
                # Check if time is in the future
                if scheduled_time <= datetime.now():
                    await message.reply_text(
                        _("SCHEDULE_TIME_MUST_BE_FUTURE", language),
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(_("BTN_CANCEL", language), callback_data='admin_broadcast')
                        ]])
                    )
                    return
                
                broadcast_state['scheduled_time'] = scheduled_time
                
                # Show confirmation
                await self.show_broadcast_confirmation(update, context)
                
            except ValueError:
                await message.reply_text(
                    _("INVALID_TIME_FORMAT", language),
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(_("BTN_CANCEL", language), callback_data='admin_broadcast')
                    ]])
                )
            
        except Exception as e:
            self.logger.error(f"Error handling broadcast schedule: {e}")
    
    async def show_broadcast_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show broadcast confirmation"""
        try:
            message = update.message
            user = message.from_user
            
            # Get broadcast state
            broadcast_state = self.broadcast_states.get(user.id)
            if not broadcast_state:
                return
            
            # Get user data
            user_data = firebase_service.get_user(user.id)
            language = user_data.get('language', 'en')
            
            # Create confirmation message
            confirmation_text = _("BROADCAST_CONFIRMATION", language)
            confirmation_text += f"\n\n{_('BROADCAST_TYPE', language)}: {broadcast_state['type']}"
            confirmation_text += f"\n{_('BROADCAST_MESSAGE', language)}:\n{broadcast_state['message']}"
            
            if broadcast_state['scheduled_time']:
                confirmation_text += f"\n{_('SCHEDULED_TIME', language)}: {broadcast_state['scheduled_time'].strftime('%Y-%m-%d %H:%M')}"
            
            # Create confirmation keyboard
            keyboard = [
                [InlineKeyboardButton(_("BTN_CONFIRM", language), callback_data='confirm_broadcast')],
                [InlineKeyboardButton(_("BTN_CANCEL", language), callback_data='admin_broadcast')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await message.reply_text(
                confirmation_text,
                reply_markup=reply_markup
            )
            
            self.admin_conversations[user.id] = self.BROADCAST_CONFIRM
            
        except Exception as e:
            self.logger.error(f"Error showing broadcast confirmation: {e}")
    
    async def confirm_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirm and execute broadcast"""
        try:
            query = update.callback_query
            user = query.from_user
            
            # Get broadcast state
            broadcast_state = self.broadcast_states.get(user.id)
            if not broadcast_state:
                return
            
            # Get user data
            user_data = firebase_service.get_user(user.id)
            language = user_data.get('language', 'en')
            
            # Create broadcast
            broadcast_id = firebase_service.create_broadcast(
                message=broadcast_state['message'],
                target_type=broadcast_state['type'],
                scheduled_time=broadcast_state['scheduled_time']
            )
            
            if broadcast_id:
                # Execute broadcast immediately if not scheduled
                if not broadcast_state['scheduled_time']:
                    await self.execute_broadcast(broadcast_id)
                
                await query.edit_message_text(
                    _("BROADCAST_CREATED", language),
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(_("BTN_BACK", language), callback_data='admin_broadcast')
                    ]])
                )
            else:
                await query.edit_message_text(
                    _("ERROR_CREATING_BROADCAST", language),
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(_("BTN_BACK", language), callback_data='admin_broadcast')
                    ]])
                )
            
            # Clear broadcast state
            if user.id in self.broadcast_states:
                del self.broadcast_states[user.id]
            
            if user.id in self.admin_conversations:
                del self.admin_conversations[user.id]
            
        except Exception as e:
            self.logger.error(f"Error confirming broadcast: {e}")
    
    async def execute_broadcast(self, broadcast_id: str):
        """Execute broadcast to recipients"""
        try:
            # Get broadcast data
            broadcast = firebase_service.get_broadcast(broadcast_id)
            if not broadcast:
                return
            
            message = broadcast.get('message', '')
            target_type = broadcast.get('target_type', 'users')
            
            recipients_count = 0
            sent_count = 0
            failed_count = 0
            
            # Get recipients based on type
            if target_type == 'users':
                users = firebase_service.get_all_users()
                recipients = users
            elif target_type == 'users_and_groups':
                users = firebase_service.get_all_users()
                groups = firebase_service.get_all_groups()
                recipients = users + groups
            else:
                return
            
            recipients_count = len(recipients)
            
            # Send message to each recipient
            for recipient in recipients:
                try:
                    chat_id = recipient.get('user_id') or recipient.get('group_id')
                    if chat_id:
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=message,
                            parse_mode='Markdown'
                        )
                        sent_count += 1
                except Exception as e:
                    self.logger.error(f"Error sending broadcast to {chat_id}: {e}")
                    failed_count += 1
            
            # Update broadcast status
            # Note: This would require updating the Firebase document
            # For now, we'll just log the results
            
            self.logger.info(f"Broadcast {broadcast_id} completed: {sent_count}/{recipients_count} sent, {failed_count} failed")
            
        except Exception as e:
            self.logger.error(f"Error executing broadcast {broadcast_id}: {e}")
    
    async def cancel_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel broadcast operation"""
        try:
            query = update.callback_query
            user = query.from_user
            
            # Clear broadcast state
            if user.id in self.broadcast_states:
                del self.broadcast_states[user.id]
            
            if user.id in self.admin_conversations:
                del self.admin_conversations[user.id]
            
            # Show broadcast menu
            from src.handlers.main_handlers import MainHandlers
            main_handlers = MainHandlers()
            await main_handlers.show_broadcast_menu(update, context)
            
        except Exception as e:
            self.logger.error(f"Error canceling broadcast: {e}")
    
    def get_conversation_handler(self):
        """Get conversation handler for admin operations"""
        return ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.broadcast_users, pattern='^broadcast_users$'),
                CallbackQueryHandler(self.broadcast_users_groups, pattern='^broadcast_users_groups$'),
                CallbackQueryHandler(self.broadcast_scheduled, pattern='^broadcast_scheduled$'),
            ],
            states={
                self.BROADCAST_MESSAGE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_broadcast_message)
                ],
                self.BROADCAST_SCHEDULE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_broadcast_schedule)
                ],
                self.BROADCAST_CONFIRM: [
                    CallbackQueryHandler(self.confirm_broadcast, pattern='^confirm_broadcast$'),
                    CallbackQueryHandler(self.cancel_broadcast, pattern='^admin_broadcast$')
                ]
            },
            fallbacks=[
                CallbackQueryHandler(self.cancel_broadcast, pattern='^admin_broadcast$')
            ],
            per_message=False
        )
    
    def get_callback_handlers(self):
        """Get callback handlers for admin operations"""
        return [
            CallbackQueryHandler(self.broadcast_delete, pattern='^broadcast_delete$'),
            CallbackQueryHandler(self.delete_broadcast_confirm, pattern='^delete_broadcast_'),
            CallbackQueryHandler(self.cancel_broadcast, pattern='^admin_broadcast$'),
        ]

# Add missing text constants
def _(key: str, language: str = 'en', **kwargs) -> str:
    """Shorthand function for getting text"""
    texts = {
        'PLEASE_SEND_BROADCAST_MESSAGE': {
            'en': 'Please send the broadcast message:',
            'fa': 'لطفاً پیام همگانی را ارسال کنید:'
        },
        'NO_PENDING_BROADCASTS': {
            'en': 'No pending broadcasts found.',
            'fa': 'هیچ پیام همگانی در انتظار پیدا نشد.'
        },
        'SELECT_BROADCAST_TO_DELETE': {
            'en': 'Select broadcast to delete:',
            'fa': 'پیام همگانی برای حذف را انتخاب کنید:'
        },
        'BROADCAST_DELETED': {
            'en': '✅ Broadcast deleted successfully!',
            'fa': '✅ پیام همگانی با موفقیت حذف شد!'
        },
        'ERROR_DELETING_BROADCAST': {
            'en': '❌ Error deleting broadcast.',
            'fa': '❌ خطا در حذف پیام همگانی.'
        },
        'PLEASE_SEND_SCHEDULE_TIME': {
            'en': 'Please send the schedule time (format: YYYY-MM-DD HH:MM or HH:MM):',
            'fa': 'لطفاً زمان زمان‌بندی را ارسال کنید (فرمت: YYYY-MM-DD HH:MM یا HH:MM):'
        },
        'SCHEDULE_TIME_MUST_BE_FUTURE': {
            'en': 'Schedule time must be in the future.',
            'fa': 'زمان زمان‌بندی باید در آینده باشد.'
        },
        'INVALID_TIME_FORMAT': {
            'en': 'Invalid time format. Please use YYYY-MM-DD HH:MM or HH:MM',
            'fa': 'فرمت زمان نامعتبر است. لطفاً از YYYY-MM-DD HH:MM یا HH:MM استفاده کنید'
        },
        'BROADCAST_CONFIRMATION': {
            'en': '📢 *Broadcast Confirmation*',
            'fa': '📢 *تأیید پیام همگانی*'
        },
        'BROADCAST_TYPE': {
            'en': 'Type',
            'fa': 'نوع'
        },
        'BROADCAST_MESSAGE': {
            'en': 'Message',
            'fa': 'پیام'
        },
        'SCHEDULED_TIME': {
            'en': 'Scheduled Time',
            'fa': 'زمان زمان‌بندی'
        },
        'BROADCAST_CREATED': {
            'en': '✅ Broadcast created successfully!',
            'fa': '✅ پیام همگانی با موفقیت ایجاد شد!'
        },
        'ERROR_CREATING_BROADCAST': {
            'en': '❌ Error creating broadcast.',
            'fa': '❌ خطا در ایجاد پیام همگانی.'
        }
    }
    
    text = texts.get(key, {}).get(language, key)
    try:
        return text.format(**kwargs)
    except (KeyError, ValueError):
        return text