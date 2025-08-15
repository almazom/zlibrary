#!/bin/bash

# Unified System Startup Script
# Starts the unified message processor to eliminate polling conflicts

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🚀 Unified Message Processor System${NC}"
echo -e "${BLUE}====================================${NC}"
echo "📁 Project: $PROJECT_ROOT"
echo "🔧 Script: $SCRIPT_DIR"
echo ""

# Function to print colored output
log_info() {
    echo -e "${GREEN}ℹ️  $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if .env exists
if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
    log_error ".env file not found in $PROJECT_ROOT"
    log_error "Please create .env file with:"
    echo "TELEGRAM_BOT_TOKEN=your_bot_token"
    echo "CHAT_ID=your_chat_id"
    echo "SCRIPT_PATH=/path/to/book_search.sh"
    echo "UNIFIED_API_PORT=8765"
    exit 1
fi

# Source environment variables
source "$PROJECT_ROOT/.env"

# Validate required environment variables
if [[ -z "${TELEGRAM_BOT_TOKEN:-}" ]]; then
    log_error "TELEGRAM_BOT_TOKEN not set in .env"
    exit 1
fi

if [[ -z "${CHAT_ID:-}" ]]; then
    log_error "CHAT_ID not set in .env"
    exit 1
fi

# Set defaults
export SCRIPT_PATH="${SCRIPT_PATH:-$PROJECT_ROOT/scripts/book_search.sh}"
export UNIFIED_API_PORT="${UNIFIED_API_PORT:-8765}"

log_info "Environment validated"
log_info "Bot Token: ${TELEGRAM_BOT_TOKEN:0:10}..."
log_info "Chat ID: $CHAT_ID"
log_info "Script Path: $SCRIPT_PATH"
log_info "API Port: $UNIFIED_API_PORT"

# Check if script path exists
if [[ ! -f "$SCRIPT_PATH" ]]; then
    log_warn "Script path $SCRIPT_PATH not found"
    log_warn "Please update SCRIPT_PATH in .env"
fi

# Check if port is available
if command -v lsof &> /dev/null; then
    if lsof -Pi :$UNIFIED_API_PORT -sTCP:LISTEN -t >/dev/null; then
        log_warn "Port $UNIFIED_API_PORT is already in use"
        log_warn "Stopping existing process..."
        
        # Kill existing process on port
        PID=$(lsof -Pi :$UNIFIED_API_PORT -sTCP:LISTEN -t)
        if [[ -n "$PID" ]]; then
            kill -TERM "$PID" 2>/dev/null || true
            sleep 2
            
            # Force kill if still running
            if kill -0 "$PID" 2>/dev/null; then
                kill -KILL "$PID" 2>/dev/null || true
            fi
            
            log_info "Existing process stopped"
        fi
    fi
fi

echo ""
log_info "Starting Unified Message Processor..."
echo -e "${BLUE}📋 Features:${NC}"
echo "  ✅ Single polling instance (no conflicts)"
echo "  ✅ Unified pipeline for manual & automated messages"
echo "  ✅ External API for UC tests"
echo "  ✅ 100% identical processing guarantee"
echo ""

# Start the unified processor
cd "$SCRIPT_DIR"

log_info "Launching unified_message_processor.py..."
echo -e "${YELLOW}🔄 Starting system (Ctrl+C to stop)...${NC}"
echo ""

# Start with proper error handling
if command -v python3 &> /dev/null; then
    python3 unified_message_processor.py
elif command -v python &> /dev/null; then
    python unified_message_processor.py
else
    log_error "Python not found. Please install Python 3.8+"
    exit 1
fi