# English language strings

# Main menu
MAIN_MENU = "🏠 Main Menu"
DOWNLOAD_FEATURE = "📥 Download Feature"
CHANGE_LANGUAGE = "🌐 Change Language"
BACK_TO_MAIN = "🔙 Back to Main Menu"

# Bot info
BOT_CAPABILITIES = """
🤖 *Bot Capabilities*

I can download content from various social media platforms:

📥 *Download Features:*
• YouTube videos, playlists, and channels
• Instagram posts, reels, and stories
• TikTok videos
• Twitter/X tweets with videos
• Facebook videos
• Pinterest pins and boards
• Vimeo videos
• Dailymotion videos
• Twitch streams and clips
• SoundCloud music
• Telegram public files
• And many more platforms!

🎯 *How to use:*
1. Send me a link from supported platforms
2. I'll download and send the content to you
3. Enjoy! 🎉

📋 *Available Commands:*
• /start - Show main menu
• /help - Show help and commands
• /admin <password> - Admin panel
• /panel - Group management panel
• /statistics - Show bot statistics
• /language - Change language

Choose an option below to get started!
"""

# Help
HELP_TEXT = """
📚 *Help & Commands*

🤖 *Bot Commands:*
• /start - Show main menu
• /help - Show this help message
• /admin <password> - Access admin panel
• /panel - Group management panel (admins only)
• /statistics - Show bot statistics (admin only)
• /language - Change bot language

📥 *Download Feature:*
Simply send any supported link and I'll download it for you!

Supported platforms:
• YouTube, Instagram, TikTok
• Twitter/X, Facebook, Pinterest
• Vimeo, Dailymotion, Twitch
• SoundCloud, Telegram, and more

👥 *Group Management:*
The bot can be added to groups with management features:
• Lock/unlock various message types
• Welcome messages
• Warning system
• And much more!

Use /panel in groups to access management features.
"""

# Admin
ADMIN_LOGIN_SUCCESS = "✅ Successfully logged in as admin!"
ADMIN_LOGIN_FAILED = "❌ Invalid admin password!"
ADMIN_PANEL = """
🔧 *Admin Panel*

Choose an option:

📊 *Statistics:*
• View bot statistics
• User count
• Group count
• System status

📢 *Broadcast:*
• Send message to all users
• Send message to users and groups
• Schedule messages
• Delete messages

⚙️ *Settings:*
• Bot configuration
• Manage users
• Manage groups

🔙 Back to main menu
"""

STATISTICS = """
📊 *Bot Statistics*

👥 *Users:* {user_count}
👥 *Groups:* {group_count}
📈 *Total Downloads:* {total_downloads}
✅ *Successful Downloads:* {successful_downloads}
❌ *Failed Downloads:* {failed_downloads}
🏓 *Bot Ping:* {ping_time}ms
⏰ *Uptime:* {uptime}

🔄 *Last Update:* {last_update}
"""

BROADCAST_MENU = """
📢 *Broadcast Menu*

Choose broadcast type:

👤 *Broadcast to Users Only*
Send message to all bot users

👥 *Broadcast to Users & Groups*
Send message to bot users and groups where bot is added

⏰ *Scheduled Broadcast*
Schedule a message for later

🗑️ *Delete Broadcast*
Delete a scheduled or active broadcast

🔙 Back to admin panel
"""

BROADCAST_SUCCESS = "✅ Message broadcasted successfully to {count} recipients!"
BROADCAST_FAILED = "❌ Failed to broadcast message: {error}"
BROADCAST_SCHEDULED = "✅ Message scheduled for {time}"
BROADCAST_DELETED = "✅ Broadcast deleted successfully!"

# Download
DOWNLOAD_STARTING = "⏳ Starting download..."
DOWNLOAD_PROGRESS = "📥 Downloading: {progress}%"
DOWNLOAD_SUCCESS = "✅ Download completed!"
DOWNLOAD_FAILED = "❌ Download failed: {error}"
FILE_TOO_LARGE = "❌ File is too large (max {max_size}MB)"
UNSUPPORTED_PLATFORM = "❌ This platform is not supported!"
INVALID_URL = "❌ Invalid URL format!"

# Group Management
GROUP_PANEL = """
🔧 *Group Management Panel*

🔒 *Locks:*
• Lock links
• Lock hyperlinks
• Lock hashtags
• Lock usernames
• Lock inline
• Lock forwarded messages
• Lock emoji
• Lock games
• Lock message editing
• Lock media editing
• Lock videos
• Lock photos
• Lock files
• Lock music
• Lock stickers
• Lock GIFs
• Lock location
• Lock voice
• Lock video messages
• Lock polls

📋 *Lists:*
• Admins list
• VIP members list
• Filtered words list
• Muted users list
• Banned users list
• Warnings list

⚙️ *Settings:*
• Force membership
• Welcome message
• Warning settings
• Auto lock
• Lock group
• Enable/disable downloads

🎮 *Entertainment:*
• Fal-e Hafez
• Currency rates
• Weather info

🔙 Back to main menu
"""

WELCOME_MESSAGE = "👋 Welcome {user} to {group}!"
FORCE_MEMBERSHIP = "⚠️ You must join the following channels to send messages:\n{channels}"
USER_WARNED = "⚠️ User {user} has been warned! ({current}/{max} warnings)"
USER_MUTED = "🔇 User {user} has been muted for {reason}!"
USER_BANNED = "🚫 User {user} has been banned for {reason}!"
USER_UNMUTED = "🔊 User {user} has been unmuted!"
USER_UNBANNED = "✅ User {user} has been unbanned!"
WORD_FILTERED = "🚫 Message contains filtered word: {word}"
LOCKED_FEATURE = "🔒 This feature is locked in this group!"
GROUP_LOCKED = "🔒 Group is locked! Only admins can send messages."
GROUP_UNLOCKED = "🔓 Group is unlocked! Everyone can send messages."

# Entertainment
FAL_HAFEZ = "📜 *Fal-e Hafez*\n\n{poem}\n\n{interpretation}"
CURRENCY_RATES = "💱 *Currency Rates*\n\n{rates}"
WEATHER_INFO = "🌤️ *Weather in {city}*\n\n{weather}"

# Common
YES = "✅ Yes"
NO = "❌ No"
CANCEL = "❌ Cancel"
CONFIRM = "✅ Confirm"
BACK = "🔙 Back"
NEXT = "➡️ Next"
PREVIOUS = "⬅️ Previous"
LOADING = "⏳ Loading..."
ERROR_OCCURRED = "❌ An error occurred: {error}"
PLEASE_WAIT = "⏳ Please wait..."
OPERATION_SUCCESS = "✅ Operation completed successfully!"
OPERATION_FAILED = "❌ Operation failed: {error}"

# Buttons
BTN_DOWNLOAD = "📥 Download"
BTN_LANGUAGE = "🌐 Language"
BTN_HELP = "❓ Help"
BTN_ADMIN = "🔧 Admin"
BTN_PANEL = "🔧 Panel"
BTN_STATS = "📊 Statistics"
BTN_BROADCAST = "📢 Broadcast"
BTN_SETTINGS = "⚙️ Settings"
BTN_BACK = "🔙 Back"
BTN_CANCEL = "❌ Cancel"
BTN_CONFIRM = "✅ Confirm"

# Group Management Buttons
BTN_LOCKS = "🔒 Locks"
BTN_LISTS = "📋 Lists"
BTN_SETTINGS = "⚙️ Settings"
BTN_ENTERTAINMENT = "🎮 Entertainment"
BTN_LOCK_LINKS = "🔒 Lock Links"
BTN_LOCK_HYPERLINKS = "🔒 Lock Hyperlinks"
BTN_LOCK_HASHTAGS = "🔒 Lock Hashtags"
BTN_LOCK_USERNAMES = "🔒 Lock Usernames"
BTN_LOCK_INLINE = "🔒 Lock Inline"
BTN_LOCK_FORWARDED = "🔒 Lock Forwarded"
BTN_LOCK_EMOJI = "🔒 Lock Emoji"
BTN_LOCK_GAMES = "🔒 Lock Games"
BTN_LOCK_EDIT = "🔒 Lock Edit"
BTN_LOCK_MEDIA_EDIT = "🔒 Lock Media Edit"
BTN_LOCK_VIDEOS = "🔒 Lock Videos"
BTN_LOCK_PHOTOS = "🔒 Lock Photos"
BTN_LOCK_FILES = "🔒 Lock Files"
BTN_LOCK_MUSIC = "🔒 Lock Music"
BTN_LOCK_STICKERS = "🔒 Lock Stickers"
BTN_LOCK_GIFS = "🔒 Lock GIFs"
BTN_LOCK_LOCATION = "🔒 Lock Location"
BTN_LOCK_VOICE = "🔒 Lock Voice"
BTN_LOCK_VIDEO_MSG = "🔒 Lock Video Msg"
BTN_LOCK_POLLS = "🔒 Lock Polls"

BTN_LIST_ADMINS = "👥 Admins"
BTN_LIST_VIP = "⭐ VIP Members"
BTN_LIST_FILTERED = "🚫 Filtered Words"
BTN_LIST_MUTED = "🔇 Muted Users"
BTN_LIST_BANNED = "🚫 Banned Users"
BTN_LIST_WARNINGS = "⚠️ Warnings"

BTN_SET_FORCE_MEMBER = "⚡ Force Membership"
BTN_SET_WELCOME = "👋 Welcome Message"
BTN_SET_WARNINGS = "⚠️ Warning Settings"
BTN_SET_AUTO_LOCK = "🔒 Auto Lock"
BTN_SET_GROUP_LOCK = "🔒 Lock Group"
BTN_SET_DOWNLOADS = "📥 Enable Downloads"

BTN_FAL_HAFEZ = "📜 Fal-e Hafez"
BTN_CURRENCY = "💱 Currency Rates"
BTN_WEATHER = "🌤️ Weather"