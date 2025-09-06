#!/bin/bash

# Telegram Bot Setup Script
# This script will set up the Telegram bot with all dependencies

set -e  # Exit on any error

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

# Check if Python 3.8+ is installed
check_python() {
    print_status "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        REQUIRED_VERSION="3.8"
        
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python $PYTHON_VERSION is installed"
            PYTHON_CMD="python3"
        else
            print_error "Python 3.8+ is required. Found version: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 is not installed"
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    print_status "Checking pip installation..."
    
    if command -v pip3 &> /dev/null; then
        print_success "pip3 is installed"
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        print_success "pip is installed"
        PIP_CMD="pip"
    else
        print_error "pip is not installed"
        exit 1
    fi
}

# Check if ffmpeg is installed
check_ffmpeg() {
    print_status "Checking ffmpeg installation..."
    
    if command -v ffmpeg &> /dev/null; then
        print_success "ffmpeg is installed"
    else
        print_warning "ffmpeg is not installed. Installing..."
        
        # Try to install ffmpeg based on OS
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y ffmpeg
        elif command -v yum &> /dev/null; then
            sudo yum install -y ffmpeg
        elif command -v brew &> /dev/null; then
            brew install ffmpeg
        else
            print_error "Please install ffmpeg manually"
            exit 1
        fi
        
        print_success "ffmpeg has been installed"
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Upgrade pip
    $PIP_CMD install --upgrade pip
    
    # Install requirements
    $PIP_CMD install -r requirements.txt
    
    print_success "Dependencies installed successfully"
}

# Setup environment file
setup_env() {
    print_status "Setting up environment file..."
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_warning "Environment file created from template"
        print_warning "Please edit .env file with your configuration:"
        print_warning "- BOT_TOKEN: Your Telegram bot token"
        print_warning "- ADMIN_PASSWORD: Your admin password"
        print_warning "- FIREBASE_CREDENTIALS_PATH: Path to Firebase credentials"
        print_warning "- FIREBASE_DATABASE_URL: Your Firebase database URL"
        echo ""
        print_warning "After configuring, run: nano .env"
    else
        print_success "Environment file already exists"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p downloads
    mkdir -p temp
    mkdir -p logs
    
    print_success "Directories created"
}

# Setup Firebase service account
setup_firebase() {
    print_status "Firebase setup..."
    
    if [ ! -f "serviceAccountKey.json" ]; then
        print_warning "Firebase service account key not found"
        print_warning "Please download your Firebase service account key from Firebase Console"
        print_warning "and save it as 'serviceAccountKey.json' in the project root"
        print_warning "Firebase Console -> Project Settings -> Service Accounts -> Generate new private key"
    else
        print_success "Firebase service account key found"
    fi
}

# Set up systemd service (optional)
setup_systemd() {
    print_status "Setting up systemd service..."
    
    SERVICE_FILE="/etc/systemd/system/telegram-bot.service"
    
    if [ "$EUID" -eq 0 ]; then
        cat > $SERVICE_FILE << EOF
[Unit]
Description=Telegram Bot with yt-dlp
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        systemctl daemon-reload
        systemctl enable telegram-bot.service
        
        print_success "Systemd service created and enabled"
        print_warning "To start the service: sudo systemctl start telegram-bot.service"
        print_warning "To check status: sudo systemctl status telegram-bot.service"
    else
        print_warning "Run as root to setup systemd service"
    fi
}

# Main setup function
main() {
    echo ""
    echo "=========================================="
    echo "  Telegram Bot Setup Script"
    echo "=========================================="
    echo ""
    
    # Run checks
    check_python
    check_pip
    check_ffmpeg
    
    # Setup environment
    create_venv
    install_dependencies
    setup_env
    create_directories
    setup_firebase
    
    # Optional systemd setup
    echo ""
    read -p "Do you want to set up systemd service? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_systemd
    fi
    
    echo ""
    print_success "Setup completed successfully!"
    echo ""
    print_status "Next steps:"
    echo "1. Edit .env file with your configuration"
    echo "2. Place your Firebase service account key as serviceAccountKey.json"
    echo "3. Run the bot: ./run.sh"
    echo ""
    print_warning "Make sure to configure your bot token and Firebase settings before running!"
}

# Run main function
main "$@"