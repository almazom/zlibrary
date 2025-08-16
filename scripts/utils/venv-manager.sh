#!/bin/bash

# Virtual Environment Manager for Z-Library Telegram Bot
# Manages single instance execution with live logging and process control

set -euo pipefail

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$PROJECT_ROOT/venv"
BOT_DIR="$PROJECT_ROOT/telegram_bot"
LOGS_DIR="$BOT_DIR/logs"
PID_FILE="$LOGS_DIR/bot.pid"
LOG_FILE="$LOGS_DIR/venv_bot.log"
REQUIREMENTS_FILE="$BOT_DIR/requirements.txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to display help
show_help() {
    cat << EOF
${CYAN}Z-Library Telegram Bot - Virtual Environment Manager${NC}

${YELLOW}DESCRIPTION:${NC}
    Manages the Z-Library Telegram Bot in a virtual environment with proper
    instance control, live logging, and process management. Prevents duplicate
    instances and provides comprehensive monitoring.

${YELLOW}USAGE:${NC}
    ./scripts/venv-manager.sh [COMMAND] [OPTIONS]

${YELLOW}COMMANDS:${NC}
    ${GREEN}setup${NC}           Create and configure virtual environment
    ${GREEN}start${NC}           Start the bot (kills existing instance first)
    ${GREEN}stop${NC}            Stop the bot gracefully
    ${GREEN}restart${NC}         Restart the bot (stop + start)
    ${GREEN}status${NC}          Show bot status and process information
    ${GREEN}logs${NC}            Show recent logs (default: last 50 lines)
    ${GREEN}watch${NC}           Watch live logs in real-time
    ${GREEN}kill${NC}            Force kill all bot processes
    ${GREEN}clean${NC}           Clean logs and temporary files
    ${GREEN}test${NC}            Test bot functionality
    ${GREEN}deps${NC}            Install/update dependencies

${YELLOW}OPTIONS:${NC}
    --help, -h       Show this help message
    --verbose, -v    Enable verbose output
    --quiet, -q      Suppress non-essential output
    --lines N        Number of log lines to show (default: 50)
    --follow, -f     Follow logs (like tail -f)
    --debug          Enable debug mode
    --force          Force operations without confirmation

${YELLOW}EXAMPLES:${NC}
    ./scripts/venv-manager.sh setup               # Initial setup
    ./scripts/venv-manager.sh start --verbose     # Start with verbose output
    ./scripts/venv-manager.sh watch              # Watch live logs
    ./scripts/venv-manager.sh logs --lines 100   # Show last 100 log lines
    ./scripts/venv-manager.sh restart --debug    # Restart in debug mode
    ./scripts/venv-manager.sh status             # Check current status

${YELLOW}ENVIRONMENT VARIABLES:${NC}
    BOT_DEBUG=1         Enable debug logging
    BOT_PORT=8443       Set custom port (default: 8443)
    LOG_LEVEL=DEBUG     Set log level (DEBUG, INFO, WARNING, ERROR)

${YELLOW}FILES:${NC}
    PID File:       $PID_FILE
    Log File:       $LOG_FILE
    Virtual Env:    $VENV_DIR
    Requirements:   $REQUIREMENTS_FILE

${YELLOW}PROCESS MANAGEMENT:${NC}
    - Automatically kills existing bot instances before starting new ones
    - Uses PID file for reliable process tracking
    - Graceful shutdown with SIGTERM, force kill with SIGKILL if needed
    - Prevents multiple instances running simultaneously

${YELLOW}LOGGING:${NC}
    - Live log monitoring with colored output
    - Separate log files for debugging
    - Configurable log levels and verbosity
    - Automatic log rotation and cleanup

${YELLOW}EXIT CODES:${NC}
    0    Success
    1    General error
    2    Invalid arguments
    3    Bot not running
    4    Bot already running
    5    Environment setup failed

${YELLOW}AUTHOR:${NC}
    Z-Library Telegram Bot Project
    Generated: $(TZ=Europe/Moscow date '+%Y-%m-%d %H:%M:%S %Z')
EOF
}

# Logging functions
log_info() {
    if [[ "${QUIET:-false}" != "true" ]]; then
        echo -e "${BLUE}[INFO]${NC} $1" >&2
    fi
}

log_success() {
    if [[ "${QUIET:-false}" != "true" ]]; then
        echo -e "${GREEN}[SUCCESS]${NC} $1" >&2
    fi
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_warn() {
    if [[ "${QUIET:-false}" != "true" ]]; then
        echo -e "${YELLOW}[WARNING]${NC} $1" >&2
    fi
}

log_verbose() {
    if [[ "${VERBOSE:-false}" == "true" ]]; then
        echo -e "${CYAN}[VERBOSE]${NC} $1" >&2
    fi
}

log_debug() {
    if [[ "${DEBUG:-false}" == "true" ]]; then
        echo -e "${YELLOW}[DEBUG]${NC} $1" >&2
    fi
}

# Check if bot is running
is_bot_running() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo "$pid"
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Kill all bot processes
kill_bot_processes() {
    local force=${1:-false}
    
    log_verbose "Searching for bot processes..."
    
    # Kill by PID file first
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log_info "Stopping bot process (PID: $pid)..."
            if [[ "$force" == "true" ]]; then
                kill -KILL "$pid" 2>/dev/null || true
            else
                kill -TERM "$pid" 2>/dev/null || true
                sleep 3
                if kill -0 "$pid" 2>/dev/null; then
                    log_warn "Process still running, force killing..."
                    kill -KILL "$pid" 2>/dev/null || true
                fi
            fi
        fi
        rm -f "$PID_FILE"
    fi
    
    # Kill by process name pattern
    local bot_pids=$(pgrep -f "python.*bot_app.py" || true)
    if [[ -n "$bot_pids" ]]; then
        log_info "Found additional bot processes: $bot_pids"
        echo "$bot_pids" | while read -r pid; do
            if [[ -n "$pid" ]]; then
                log_verbose "Killing process $pid..."
                if [[ "$force" == "true" ]]; then
                    kill -KILL "$pid" 2>/dev/null || true
                else
                    kill -TERM "$pid" 2>/dev/null || true
                fi
            fi
        done
    fi
    
    # Kill processes using the log file (in case of orphaned processes)
    local log_pids=$(lsof "$LOG_FILE" 2>/dev/null | awk 'NR>1 {print $2}' || true)
    if [[ -n "$log_pids" ]]; then
        log_verbose "Killing processes using log file: $log_pids"
        echo "$log_pids" | while read -r pid; do
            if [[ -n "$pid" ]] && [[ "$pid" != "PID" ]]; then
                kill -TERM "$pid" 2>/dev/null || true
            fi
        done
    fi
}

# Setup virtual environment
setup_venv() {
    log_info "Setting up virtual environment..."
    
    # Create directories
    mkdir -p "$LOGS_DIR"
    
    # Remove existing venv if it exists
    if [[ -d "$VENV_DIR" ]]; then
        log_warn "Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
    fi
    
    # Create new virtual environment
    log_verbose "Creating virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
    
    # Activate and install requirements
    source "$VENV_DIR/bin/activate"
    
    log_verbose "Upgrading pip..."
    pip install --upgrade pip
    
    if [[ -f "$REQUIREMENTS_FILE" ]]; then
        log_info "Installing requirements from $REQUIREMENTS_FILE..."
        pip install -r "$REQUIREMENTS_FILE"
    else
        log_error "Requirements file not found: $REQUIREMENTS_FILE"
        return 5
    fi
    
    log_success "Virtual environment setup completed!"
    
    # Show installed packages
    if [[ "${VERBOSE:-false}" == "true" ]]; then
        log_verbose "Installed packages:"
        pip list
    fi
}

# Start the bot
start_bot() {
    log_info "Starting Z-Library Telegram Bot..."
    
    # Check if already running
    if pid=$(is_bot_running); then
        if [[ "${FORCE:-false}" == "true" ]]; then
            log_warn "Bot is running (PID: $pid), force stopping..."
            kill_bot_processes true
        else
            log_error "Bot is already running (PID: $pid)"
            log_info "Use 'restart' command or --force flag to override"
            return 4
        fi
    fi
    
    # Kill any remaining processes
    kill_bot_processes
    
    # Check virtual environment
    if [[ ! -d "$VENV_DIR" ]]; then
        log_warn "Virtual environment not found, setting up..."
        setup_venv
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Set environment variables
    cd "$BOT_DIR"
    export PYTHONPATH="$BOT_DIR:$PROJECT_ROOT"
    
    # Clear any conflicting system environment variables
    unset TELEGRAM_BOT_TOKEN
    
    # Load .env file to get correct token
    if [[ -f "$BOT_DIR/.env" ]]; then
        source "$BOT_DIR/.env"
        log_verbose "Loaded environment from .env file"
        log_verbose "Token loaded: ${TELEGRAM_BOT_TOKEN:0:20}..."
    fi
    
    if [[ "${DEBUG:-false}" == "true" ]]; then
        export LOG_LEVEL=DEBUG
        export BOT_DEBUG=1
    fi
    
    # Create log file
    touch "$LOG_FILE"
    
    # Start bot in background
    log_verbose "Starting bot process..."
    nohup python bot_app.py > "$LOG_FILE" 2>&1 &
    local bot_pid=$!
    
    # Save PID
    echo "$bot_pid" > "$PID_FILE"
    
    # Wait a moment and check if process is still running
    sleep 2
    if kill -0 "$bot_pid" 2>/dev/null; then
        log_success "Bot started successfully (PID: $bot_pid)"
        log_info "Log file: $LOG_FILE"
        log_info "Use 'watch' command to monitor logs"
    else
        log_error "Bot failed to start"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Stop the bot
stop_bot() {
    log_info "Stopping Z-Library Telegram Bot..."
    
    if pid=$(is_bot_running); then
        log_info "Stopping bot process (PID: $pid)..."
        kill_bot_processes
        log_success "Bot stopped successfully"
    else
        log_warn "Bot is not running"
        return 3
    fi
}

# Show bot status
show_status() {
    log_info "Z-Library Telegram Bot Status"
    echo "================================"
    
    if pid=$(is_bot_running); then
        echo -e "Status: ${GREEN}RUNNING${NC}"
        echo "PID: $pid"
        
        # Show process info
        if ps -p "$pid" -o pid,ppid,user,start,time,cmd --no-headers 2>/dev/null; then
            echo ""
        fi
        
        # Show memory usage
        if command -v pstree >/dev/null; then
            echo "Process tree:"
            pstree -p "$pid" 2>/dev/null || true
        fi
        
        # Show log file info
        if [[ -f "$LOG_FILE" ]]; then
            echo "Log file: $LOG_FILE"
            echo "Log size: $(du -h "$LOG_FILE" | cut -f1)"
            echo "Last modified: $(stat -c %y "$LOG_FILE")"
        fi
        
        # Show recent log entries
        if [[ -f "$LOG_FILE" ]] && [[ -s "$LOG_FILE" ]]; then
            echo ""
            echo "Recent log entries (last 5 lines):"
            tail -5 "$LOG_FILE" | sed 's/^/  /'
        fi
        
    else
        echo -e "Status: ${RED}STOPPED${NC}"
        
        # Check for orphaned processes
        local orphaned=$(pgrep -f "python.*bot_app.py" || true)
        if [[ -n "$orphaned" ]]; then
            echo -e "Warning: ${YELLOW}Orphaned processes found${NC}: $orphaned"
        fi
    fi
    
    echo ""
    echo "Environment:"
    echo "  Project root: $PROJECT_ROOT"
    echo "  Virtual env: $VENV_DIR"
    echo "  Logs directory: $LOGS_DIR"
    echo "  PID file: $PID_FILE"
    
    # Check virtual environment
    if [[ -d "$VENV_DIR" ]]; then
        echo -e "  Virtual env: ${GREEN}EXISTS${NC}"
    else
        echo -e "  Virtual env: ${RED}NOT FOUND${NC}"
    fi
}

# Show logs
show_logs() {
    local lines=${LINES:-50}
    local follow=${FOLLOW:-false}
    
    if [[ ! -f "$LOG_FILE" ]]; then
        log_warn "Log file not found: $LOG_FILE"
        return 1
    fi
    
    log_info "Showing bot logs (last $lines lines)..."
    echo "=========================================="
    
    if [[ "$follow" == "true" ]]; then
        tail -f -n "$lines" "$LOG_FILE"
    else
        tail -n "$lines" "$LOG_FILE"
    fi
}

# Watch live logs
watch_logs() {
    log_info "Watching live logs (Ctrl+C to stop)..."
    echo "========================================"
    
    if [[ ! -f "$LOG_FILE" ]]; then
        touch "$LOG_FILE"
    fi
    
    # Use tail -f with color highlighting
    tail -f "$LOG_FILE" | while IFS= read -r line; do
        case "$line" in
            *ERROR*)
                echo -e "${RED}$line${NC}"
                ;;
            *WARNING*)
                echo -e "${YELLOW}$line${NC}"
                ;;
            *SUCCESS*)
                echo -e "${GREEN}$line${NC}"
                ;;
            *INFO*)
                echo -e "${BLUE}$line${NC}"
                ;;
            *DEBUG*)
                echo -e "${CYAN}$line${NC}"
                ;;
            *)
                echo "$line"
                ;;
        esac
    done
}

# Clean logs and temp files
clean_files() {
    log_info "Cleaning logs and temporary files..."
    
    # Stop bot first if running
    if is_bot_running >/dev/null; then
        log_warn "Stopping bot before cleanup..."
        stop_bot
    fi
    
    # Clean log files
    if [[ -f "$LOG_FILE" ]]; then
        log_verbose "Removing log file: $LOG_FILE"
        rm -f "$LOG_FILE"
    fi
    
    # Clean PID file
    if [[ -f "$PID_FILE" ]]; then
        log_verbose "Removing PID file: $PID_FILE"
        rm -f "$PID_FILE"
    fi
    
    # Clean other temporary files
    find "$LOGS_DIR" -name "*.log.*" -delete 2>/dev/null || true
    find "$BOT_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$BOT_DIR" -name "*.pyc" -delete 2>/dev/null || true
    
    log_success "Cleanup completed"
}

# Test bot functionality
test_bot() {
    log_info "Testing bot functionality..."
    
    if ! is_bot_running >/dev/null; then
        log_error "Bot is not running"
        return 3
    fi
    
    # Test bot API
    source "$BOT_DIR/.env" 2>/dev/null || true
    if [[ -n "${TELEGRAM_BOT_TOKEN:-}" ]]; then
        log_verbose "Testing bot API connection..."
        if command -v curl >/dev/null; then
            local response=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe")
            if echo "$response" | grep -q '"ok":true'; then
                log_success "Bot API connection successful"
                local bot_name=$(echo "$response" | grep -o '"first_name":"[^"]*"' | cut -d'"' -f4)
                log_info "Bot name: $bot_name"
            else
                log_error "Bot API connection failed"
                log_debug "Response: $response"
            fi
        else
            log_warn "curl not found, skipping API test"
        fi
    else
        log_warn "TELEGRAM_BOT_TOKEN not found, skipping API test"
    fi
    
    # Check log activity
    if [[ -f "$LOG_FILE" ]]; then
        local recent_logs=$(tail -10 "$LOG_FILE" | wc -l)
        log_info "Recent log entries: $recent_logs"
    fi
}

# Install/update dependencies
update_deps() {
    log_info "Updating dependencies..."
    
    if [[ ! -d "$VENV_DIR" ]]; then
        log_warn "Virtual environment not found, setting up..."
        setup_venv
        return
    fi
    
    source "$VENV_DIR/bin/activate"
    
    log_verbose "Upgrading pip..."
    pip install --upgrade pip
    
    if [[ -f "$REQUIREMENTS_FILE" ]]; then
        log_info "Installing/updating requirements..."
        pip install --upgrade -r "$REQUIREMENTS_FILE"
        log_success "Dependencies updated successfully"
    else
        log_error "Requirements file not found: $REQUIREMENTS_FILE"
        return 1
    fi
}

# Parse command line arguments
COMMAND=""
VERBOSE=false
QUIET=false
DEBUG=false
FORCE=false
LINES=50
FOLLOW=false

while [[ $# -gt 0 ]]; do
    case $1 in
        setup|start|stop|restart|status|logs|watch|kill|clean|test|deps)
            if [[ -n "$COMMAND" ]]; then
                log_error "Multiple commands specified. Use --help for usage."
                exit 2
            fi
            COMMAND="$1"
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --quiet|-q)
            QUIET=true
            shift
            ;;
        --debug)
            DEBUG=true
            VERBOSE=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --lines)
            if [[ -n "${2-}" ]] && [[ "$2" =~ ^[0-9]+$ ]]; then
                LINES="$2"
                shift 2
            else
                log_error "--lines requires a numeric value"
                exit 2
            fi
            ;;
        --follow|-f)
            FOLLOW=true
            shift
            ;;
        *)
            log_error "Unknown option: $1. Use --help for usage."
            exit 2
            ;;
    esac
done

# Set default command if none provided
if [[ -z "$COMMAND" ]]; then
    COMMAND="status"
fi

# Export variables for use in functions
export VERBOSE QUIET DEBUG FORCE LINES FOLLOW

# Execute command
case "$COMMAND" in
    setup)
        setup_venv
        ;;
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        stop_bot
        start_bot
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    watch)
        watch_logs
        ;;
    kill)
        log_info "Force killing all bot processes..."
        kill_bot_processes true
        log_success "All processes killed"
        ;;
    clean)
        clean_files
        ;;
    test)
        test_bot
        ;;
    deps)
        update_deps
        ;;
    *)
        log_error "Unknown command: $COMMAND"
        show_help
        exit 2
        ;;
esac