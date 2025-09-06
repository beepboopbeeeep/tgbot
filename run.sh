#!/bin/bash

# Telegram Bot Run Script
# This script will run the Telegram bot

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if virtual environment exists
check_venv() {
    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found. Please run setup.sh first."
        exit 1
    fi
}

# Check if environment file exists
check_env() {
    if [ ! -f ".env" ]; then
        print_error "Environment file not found. Please run setup.sh first."
        exit 1
    fi
}

# Check if Firebase credentials exist
check_firebase() {
    if [ ! -f "serviceAccountKey.json" ]; then
        print_error "Firebase service account key not found. Please run setup.sh first."
        exit 1
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Check configuration
check_config() {
    print_status "Checking configuration..."
    
    # Check if required environment variables are set
    source .env
    
    if [ -z "$BOT_TOKEN" ]; then
        print_error "BOT_TOKEN is not set in .env file"
        exit 1
    fi
    
    if [ -z "$ADMIN_PASSWORD" ]; then
        print_error "ADMIN_PASSWORD is not set in .env file"
        exit 1
    fi
    
    if [ -z "$FIREBASE_DATABASE_URL" ]; then
        print_error "FIREBASE_DATABASE_URL is not set in .env file"
        exit 1
    fi
    
    print_success "Configuration check passed"
}

# Create log directory
setup_logs() {
    mkdir -p logs
}

# Function to cleanup on exit
cleanup() {
    print_status "Cleaning up..."
    # Kill any background processes
    jobs -p | xargs -r kill
    print_success "Cleanup completed"
}

# Set up signal handlers
trap cleanup EXIT INT TERM

# Main run function
main() {
    echo ""
    echo "=========================================="
    echo "  Starting Telegram Bot"
    echo "=========================================="
    echo ""
    
    # Run checks
    check_venv
    check_env
    check_firebase
    activate_venv
    check_config
    setup_logs
    
    # Run the bot
    print_status "Starting bot..."
    python bot.py
}

# Check command line arguments
case "${1:-run}" in
    "run")
        main
        ;;
    "dev")
        print_status "Running in development mode..."
        export LOG_LEVEL=DEBUG
        main
        ;;
    "test")
        print_status "Running configuration test..."
        check_venv
        check_env
        check_firebase
        activate_venv
        check_config
        print_success "All checks passed!"
        ;;
    "logs")
        print_status "Showing logs..."
        if [ -f "logs/TelegramBot_$(date +%Y%m%d).log" ]; then
            tail -f logs/TelegramBot_$(date +%Y%m%d).log
        else
            print_warning "No log file found for today"
        fi
        ;;
    "status")
        print_status "Checking bot status..."
        if pgrep -f "python bot.py" > /dev/null; then
            print_success "Bot is running"
            ps aux | grep "python bot.py" | grep -v grep
        else
            print_warning "Bot is not running"
        fi
        ;;
    "stop")
        print_status "Stopping bot..."
        pkill -f "python bot.py"
        print_success "Bot stopped"
        ;;
    "restart")
        print_status "Restarting bot..."
        pkill -f "python bot.py"
        sleep 2
        main
        ;;
    "help"|"-h"|"--help")
        echo "Telegram Bot Run Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  run     - Run the bot (default)"
        echo "  dev     - Run in development mode with debug logging"
        echo "  test    - Test configuration"
        echo "  logs    - Show logs"
        echo "  status  - Check bot status"
        echo "  stop    - Stop the bot"
        echo "  restart - Restart the bot"
        echo "  help    - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0              # Run bot"
        echo "  $0 dev          # Run in development mode"
        echo "  $0 status       # Check status"
        echo "  $0 logs         # View logs"
        ;;
    *)
        print_error "Unknown command: $1"
        print_error "Use '$0 help' to see available commands"
        exit 1
        ;;
esac