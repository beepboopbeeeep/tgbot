# Telegram Bot with yt-dlp Integration

A comprehensive Telegram bot with yt-dlp integration for downloading content from various social media platforms, featuring multi-language support, admin panel, group management, and entertainment features.

## Features

### 🎯 Core Features
- **Multi-platform Downloads**: Download content from YouTube, Instagram, TikTok, Twitter, Facebook, Pinterest, Vimeo, Dailymotion, Twitch, SoundCloud, Telegram, and more
- **Multi-language Support**: Full support for English and Persian languages with easy language switching
- **User-friendly Interface**: Intuitive menu system with inline keyboards
- **Automatic Link Detection**: Automatically detects and processes supported URLs in messages

### 🔧 Admin Panel
- **Secure Access**: Password-protected admin panel
- **Broadcast System**: Send messages to all users or users and groups
- **Scheduled Messages**: Schedule broadcasts for future delivery
- **Statistics Dashboard**: View bot statistics including user count, group count, and download metrics
- **User Management**: Manage users and view activity logs

### 👥 Group Management
- **Comprehensive Locks**: Lock various message types (links, hashtags, usernames, media, etc.)
- **Member Management**: Admin roles, VIP members, muted users, banned users
- **Warning System**: Configurable warning system with automatic actions
- **Welcome Messages**: Customizable welcome messages for new members
- **Force Membership**: Require users to join specific channels before posting
- **Auto-lock**: Automatically lock group for specified durations

### 🎮 Entertainment Features
- **Fal-e Hafez**: Persian poetry divination
- **Currency Rates**: Real-time currency exchange rates
- **Weather Information**: Weather forecasts for any location

## Installation

### Prerequisites
- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Firebase Project with Realtime Database
- FFmpeg (for video processing)

### Quick Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd telegram_bot
```

2. **Run the setup script**
```bash
chmod +x setup.sh
./setup.sh
```

3. **Configure the bot**
```bash
nano .env
```
Edit the following variables:
- `BOT_TOKEN`: Your Telegram bot token
- `ADMIN_PASSWORD`: Your admin password
- `FIREBASE_DATABASE_URL`: Your Firebase database URL

4. **Set up Firebase**
- Download your Firebase service account key from Firebase Console
- Save it as `serviceAccountKey.json` in the project root

5. **Run the bot**
```bash
chmod +x run.sh
./run.sh
```

## Usage

### For Users
1. **Start the bot**: Send `/start` to begin
2. **Send a URL**: Simply send any supported URL to download content
3. **Change language**: Use the language button or `/language` command
4. **Get help**: Use `/help` to see all available commands

### For Admins
1. **Access admin panel**: Send `/admin <password>`
2. **Broadcast messages**: Use the broadcast feature to send messages to users
3. **View statistics**: Check bot performance and usage statistics
4. **Manage users**: View and manage user data

### For Group Admins
1. **Add bot to group**: Add the bot to your group
2. **Access panel**: Send `/panel` in the group
3. **Configure settings**: Set up locks, welcome messages, and other group features
4. **Manage members**: Add admins, VIP members, and manage user restrictions

## Commands

### General Commands
- `/start` - Show main menu and bot capabilities
- `/help` - Display help and available commands
- `/language` - Change bot language
- `/admin <password>` - Access admin panel
- `/statistics` - Show bot statistics (admin only)

### Group Commands
- `/panel` - Access group management panel (group admins only)

## Configuration

### Environment Variables
- `BOT_TOKEN`: Telegram bot token
- `ADMIN_PASSWORD`: Admin panel password
- `FIREBASE_CREDENTIALS_PATH`: Path to Firebase credentials file
- `FIREBASE_DATABASE_URL`: Firebase database URL
- `MAX_DOWNLOAD_SIZE`: Maximum file size for downloads (default: 50MB)
- `DOWNLOAD_PATH`: Directory for downloaded files
- `TEMP_PATH`: Directory for temporary files
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Firebase Setup
1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Realtime Database
3. Create a service account and download the JSON key
4. Update your `.env` file with the database URL

## Supported Platforms

The bot supports downloads from:
- YouTube (videos, playlists, channels)
- Instagram (posts, reels, stories)
- TikTok (videos)
- Twitter/X (tweets with videos)
- Facebook (videos)
- Pinterest (pins, boards)
- Vimeo
- Dailymotion
- Twitch (streams, clips)
- SoundCloud (music)
- Telegram (public files)

## Project Structure

```
telegram_bot/
├── bot.py                 # Main bot file
├── setup.sh              # Setup script
├── run.sh                # Run script
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
├── config/
│   └── config.py        # Configuration settings
├── src/
│   ├── handlers/        # Bot handlers
│   │   ├── main_handlers.py
│   │   ├── admin_handlers.py
│   │   └── group_handlers.py
│   ├── services/        # Bot services
│   │   ├── firebase.py
│   │   └── downloader.py
│   ├── models/          # Data models
│   │   ├── user.py
│   │   └── group.py
│   ├── utils/           # Utility functions
│   │   ├── logger.py
│   │   └── language.py
│   └── locales/         # Language files
│       ├── en.py
│       └── fa.py
├── downloads/           # Downloaded files
├── temp/               # Temporary files
└── logs/               # Log files
```

## Running the Bot

### Development Mode
```bash
./run.sh dev
```

### Production Mode
```bash
./run.sh
```

### Systemd Service (Optional)
The setup script can create a systemd service for automatic startup:
```bash
sudo systemctl start telegram-bot.service
sudo systemctl enable telegram-bot.service
sudo systemctl status telegram-bot.service
```

### Useful Commands
```bash
# Test configuration
./run.sh test

# View logs
./run.sh logs

# Check status
./run.sh status

# Stop the bot
./run.sh stop

# Restart the bot
./run.sh restart
```

## Troubleshooting

### Common Issues

1. **Bot doesn't start**
   - Check if all environment variables are set correctly
   - Verify Firebase credentials file exists
   - Check logs with `./run.sh logs`

2. **Downloads fail**
   - Ensure FFmpeg is installed
   - Check if URLs are from supported platforms
   - Verify internet connection

3. **Firebase connection issues**
   - Check Firebase credentials file
   - Verify database URL is correct
   - Ensure Firebase project is active

4. **Group management not working**
   - Ensure bot is admin in the group
   - Check if bot has necessary permissions
   - Verify group settings in Firebase

### Logs
Check the logs in the `logs/` directory or use:
```bash
./run.sh logs
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the logs for error messages

## Changelog

### Version 1.0.0
- Initial release
- Multi-platform download support
- Multi-language support (English, Persian)
- Admin panel with broadcast functionality
- Group management features
- Entertainment features
- Firebase integration
- Comprehensive logging system