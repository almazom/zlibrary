#!/bin/bash

# Feedback Loop Runner - Starts unified system and runs continuous tests
# One-click solution to start the complete feedback testing environment

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${MAGENTA}🚀 Feedback Loop System Launcher${NC}"
echo -e "${MAGENTA}=================================${NC}"
echo "🎯 Complete solution for conflict-free message processing"
echo "🔄 Will start unified system + continuous testing"
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

# Function to check if port is in use
check_port() {
    local port="$1"
    if command -v lsof &> /dev/null; then
        lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1
    else
        netstat -tuln | grep ":$port " >/dev/null 2>&1
    fi
}

# Function to kill process on port
kill_port_process() {
    local port="$1"
    if command -v lsof &> /dev/null; then
        local pids=$(lsof -Pi :$port -sTCP:LISTEN -t 2>/dev/null || true)
        if [[ -n "$pids" ]]; then
            echo "$pids" | xargs kill -TERM 2>/dev/null || true
            sleep 2
            # Force kill if still running
            echo "$pids" | xargs kill -KILL 2>/dev/null || true
        fi
    fi
}

# Configuration
UNIFIED_PORT=${UNIFIED_API_PORT:-8765}
LOOP_DELAY=${LOOP_DELAY:-15}  # Faster for feedback loop
MAX_CYCLES=${MAX_CYCLES:-0}   # Infinite by default

log_info "Configuration:"
log_info "  Unified API Port: $UNIFIED_PORT"
log_info "  Loop Delay: ${LOOP_DELAY}s"
log_info "  Max Cycles: ${MAX_CYCLES} (0 = infinite)"
log_info ""

# Check if .env exists
if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
    log_error ".env file not found!"
    log_error "Please create .env with:"
    echo "TELEGRAM_BOT_TOKEN=your_bot_token"
    echo "CHAT_ID=your_chat_id" 
    echo "SCRIPT_PATH=/path/to/book_search.sh"
    exit 1
fi

# Source environment
source "$PROJECT_ROOT/.env"

if [[ -z "${TELEGRAM_BOT_TOKEN:-}" ]] || [[ -z "${CHAT_ID:-}" ]]; then
    log_error "Missing required environment variables in .env"
    log_error "Required: TELEGRAM_BOT_TOKEN, CHAT_ID"
    exit 1
fi

log_info "✅ Environment validated"

# Step 1: Clean up any existing processes
log_info "🧹 Cleaning up existing processes..."

if check_port "$UNIFIED_PORT"; then
    log_warn "Port $UNIFIED_PORT is in use - stopping existing process"
    kill_port_process "$UNIFIED_PORT"
    sleep 3
fi

# Kill any existing Python processes related to our scripts
pkill -f "unified_message_processor.py" 2>/dev/null || true
pkill -f "feedback_loop_test.sh" 2>/dev/null || true
sleep 2

log_info "✅ Cleanup complete"

# Step 2: Start unified system in background
log_info "🚀 Starting unified message processor..."

cd "$SCRIPT_DIR"

# Start unified processor in background with logging
nohup python3 unified_message_processor.py > unified_system.log 2>&1 &
UNIFIED_PID=$!

log_info "📋 Unified processor started (PID: $UNIFIED_PID)"

# Step 3: Wait for system to be ready
log_info "⏳ Waiting for unified system to initialize..."

for i in {1..30}; do
    if curl -s -f http://localhost:$UNIFIED_PORT/health >/dev/null 2>&1; then
        log_info "✅ Unified system is ready!"
        break
    fi
    
    if ! kill -0 $UNIFIED_PID 2>/dev/null; then
        log_error "Unified processor died during startup!"
        log_error "Check unified_system.log for details"
        exit 1
    fi
    
    echo -ne "\r${YELLOW}⏳ Waiting... ${i}/30${NC}"
    sleep 2
done

echo ""

# Check if system is actually ready
if ! curl -s -f http://localhost:$UNIFIED_PORT/health >/dev/null 2>&1; then
    log_error "Unified system failed to start properly"
    log_error "Check unified_system.log for details:"
    tail -10 unified_system.log 2>/dev/null || echo "No log file found"
    kill $UNIFIED_PID 2>/dev/null || true
    exit 1
fi

# Step 4: Show system status
echo ""
log_info "📊 System Status:"
if command -v curl &> /dev/null; then
    stats=$(curl -s http://localhost:$UNIFIED_PORT/stats 2>/dev/null || echo '{}')
    echo "  Queue size: $(echo "$stats" | jq -r '.queue_size // "unknown"' 2>/dev/null || echo "unknown")"
    echo "  Success rate: $(echo "$stats" | jq -r '.success_rate // "unknown"' 2>/dev/null || echo "unknown")%"
fi

echo ""
log_info "🔄 Starting feedback loop testing..."
echo -e "${CYAN}Press Ctrl+C to stop the feedback loop${NC}"
echo ""

# Cleanup function
cleanup() {
    echo ""
    log_warn "Shutting down feedback loop system..."
    
    # Kill unified processor
    if kill -0 $UNIFIED_PID 2>/dev/null; then
        log_info "Stopping unified processor (PID: $UNIFIED_PID)"
        kill -TERM $UNIFIED_PID 2>/dev/null || true
        sleep 3
        kill -KILL $UNIFIED_PID 2>/dev/null || true
    fi
    
    # Clean up port
    kill_port_process "$UNIFIED_PORT"
    
    log_info "✅ Shutdown complete"
    log_info "📁 Logs available in:"
    log_info "  - unified_system.log"
    log_info "  - feedback_results/"
    
    exit 0
}

# Set up signal handling
trap cleanup SIGINT SIGTERM

# Step 5: Start feedback loop
export LOOP_DELAY
export MAX_CYCLES

# Run feedback loop test with our configuration
exec ./feedback_loop_test.sh