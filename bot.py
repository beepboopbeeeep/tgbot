#!/usr/bin/env python3
"""
Telegram Bot with yt-dlp integration
Features:
- Download content from various platforms
- Multi-language support (English, Persian)
- Admin panel with broadcast functionality
- Group management features
- Entertainment features
"""

import asyncio
import signal
import sys
from datetime import datetime
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.error import TelegramError

from config.config import Config
from src.handlers.main_handlers import MainHandlers
from src.handlers.admin_handlers import AdminHandlers
from src.handlers.group_handlers import GroupHandlers
from src.utils.logger import Logger
from src.services.firebase import firebase_service

class TelegramBot:
    """Main Telegram Bot class"""
    
    def __init__(self):
        self.logger = Logger("TelegramBot")
        self.main_handlers = MainHandlers()
        self.admin_handlers = AdminHandlers()
        self.group_handlers = GroupHandlers()
        self.application = None
        self.running = False
        
        # Validate configuration
        try:
            Config.validate()
            self.logger.info("Configuration validated successfully")
        except ValueError as e:
            self.logger.error(f"Configuration error: {e}")
            sys.exit(1)
    
    async def setup_handlers(self):
        """Setup all handlers"""
        if not self.application:
            return
        
        # Main handlers
        self.application.add_handler(CommandHandler("start", self.main_handlers.start_command))
        self.application.add_handler(CommandHandler("help", self.main_handlers.help_command))
        self.application.add_handler(CommandHandler("admin", self.main_handlers.admin_command))
        self.application.add_handler(CommandHandler("statistics", self.main_handlers.statistics_command))
        self.application.add_handler(CommandHandler("language", self.main_handlers.language_command))
        
        # Group handlers
        for handler in self.group_handlers.get_handlers():
            self.application.add_handler(handler)
        
        # Admin conversation handler
        self.application.add_handler(self.admin_handlers.get_conversation_handler())
        
        # Admin callback handlers
        for handler in self.admin_handlers.get_callback_handlers():
            self.application.add_handler(handler)
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, self.main_handlers.handle_message))
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(self.main_handlers.handle_callback_query))
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
        
        self.logger.info("Handlers setup completed")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        self.logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❌ An error occurred. Please try again later."
                )
            except Exception:
                pass
    
    async def start_bot(self):
        """Start the bot"""
        try:
            # Create application
            self.application = Application.builder().token(Config.BOT_TOKEN).build()
            
            # Setup handlers
            await self.setup_handlers()
            
            # Start bot
            self.running = True
            self.logger.info("Starting bot...")
            
            # Start polling
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(drop_pending_updates=True)
            
            self.logger.info("Bot started successfully")
            
            # Send startup notification to admin (if configured)
            await self.send_startup_notification()
            
        except Exception as e:
            self.logger.error(f"Error starting bot: {e}")
            raise
    
    async def send_startup_notification(self):
        """Send startup notification to admin"""
        try:
            # Get system status
            status = firebase_service.get_system_status()
            
            # Create startup message
            startup_message = f"""
🤖 *Bot Started Successfully*

📅 *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔧 *Version:* {status.get('version', '1.0.0')}
📊 *Users:* {firebase_service.get_users_count()}
👥 *Groups:* {firebase_service.get_groups_count()}
🔗 *Firebase:* {'Connected' if status.get('firebase_connected') else 'Disconnected'}

Bot is now online and ready to serve! 🚀
            """
            
            # Here you would send the message to admin chat
            # For now, just log it
            self.logger.info("Bot startup notification would be sent to admin")
            
        except Exception as e:
            self.logger.error(f"Error sending startup notification: {e}")
    
    async def stop_bot(self, signal=None, frame=None):
        """Stop the bot"""
        try:
            self.logger.info("Stopping bot...")
            self.running = False
            
            if self.application:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
            
            self.logger.info("Bot stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping bot: {e}")
    
    def run(self):
        """Run the bot"""
        try:
            # Setup signal handlers
            signal.signal(signal.SIGINT, self.stop_bot)
            signal.signal(signal.SIGTERM, self.stop_bot)
            
            # Start bot
            asyncio.run(self.start_bot())
            
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
        finally:
            asyncio.run(self.stop_bot())

def main():
    """Main function"""
    try:
        # Create and run bot
        bot = TelegramBot()
        bot.run()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()