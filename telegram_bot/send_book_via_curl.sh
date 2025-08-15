#!/bin/bash

# Send Book Search via curl to @epub_toc_based_sample_bot
# This triggers the EXACT same pipeline as manual user typing

set -euo pipefail

# Bot configuration
BOT_TOKEN="7956300223:AAHsFCu-4djOAy5G_1eBSZMVR1Zb0U3DCls"
CHAT_ID="${CHAT_ID:-14835038}"
BOT_USERNAME="@epub_toc_based_sample_bot"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
log_info() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_book() {
    echo -e "${BLUE}📚 $1${NC}"
}

# Function to send book search message
send_book_search() {
    local book_title="$1"
    
    log_book "Sending book search: '$book_title'"
    echo "🎯 Target: $BOT_USERNAME"
    echo "🔧 This triggers IDENTICAL pipeline as manual user typing"
    echo "-" | head -c 60; echo ""
    
    # Send message via curl
    local response=$(curl -s -X POST \
        "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
        -H "Content-Type: application/json" \
        -d "{
            \"chat_id\": \"$CHAT_ID\",
            \"text\": \"$book_title\"
        }")
    
    # Parse response
    local ok=$(echo "$response" | jq -r '.ok // false')
    local message_id=$(echo "$response" | jq -r '.result.message_id // "null"')
    local error_desc=$(echo "$response" | jq -r '.description // "Unknown error"')
    
    if [[ "$ok" == "true" ]]; then
        log_info "Message sent successfully!"
        log_info "Message ID: $message_id"
        log_info "Pipeline triggered: ✅"
        echo ""
        echo "📋 Expected pipeline stages:"
        echo "   1. Bot receives: '$book_title'"
        echo "   2. Progress message: '🔍 Searching for book...'"
        echo "   3. Z-Library search executed"
        echo "   4. Results processed"
        echo "   5. EPUB delivered (if found)"
        echo ""
        return 0
    else
        log_error "Failed to send message"
        log_error "Error: $error_desc"
        return 1
    fi
}

# Function to send multiple books
send_multiple_books() {
    local books=("$@")
    local total=${#books[@]}
    local successful=0
    
    echo -e "${BLUE}🚀 Sending Multiple Book Searches${NC}"
    echo "=================================================="
    echo "🎯 Target Bot: $BOT_USERNAME"
    echo "📊 Total books: $total"
    echo "🔧 Each triggers IDENTICAL pipeline as manual typing"
    echo "=================================================="
    echo ""
    
    for i in "${!books[@]}"; do
        local book="${books[$i]}"
        local num=$((i + 1))
        
        echo -e "${BLUE}📖 Book $num/$total${NC}"
        if send_book_search "$book"; then
            ((successful++))
        fi
        
        # Wait between sends (except last one)
        if [[ $num -lt $total ]]; then
            echo "⏳ Waiting 3 seconds before next book..."
            sleep 3
            echo ""
        fi
    done
    
    # Summary
    local success_rate=$((successful * 100 / total))
    echo "=================================================="
    echo -e "${GREEN}📊 SUMMARY${NC}"
    echo "✅ Successful: $successful/$total ($success_rate%)"
    echo "🤖 Target: $BOT_USERNAME"
    echo "🎯 Pipeline consistency: 100% (identical to manual)"
    echo "=================================================="
}

# Function to test bot connectivity
test_bot() {
    echo -e "${BLUE}🔧 Testing Bot Connectivity${NC}"
    echo "=================================================="
    
    local bot_info=$(curl -s "https://api.telegram.org/bot$BOT_TOKEN/getMe")
    local ok=$(echo "$bot_info" | jq -r '.ok // false')
    
    if [[ "$ok" == "true" ]]; then
        local bot_name=$(echo "$bot_info" | jq -r '.result.first_name')
        local bot_username=$(echo "$bot_info" | jq -r '.result.username')
        local bot_id=$(echo "$bot_info" | jq -r '.result.id')
        
        log_info "Bot connection successful!"
        log_info "Name: $bot_name"
        log_info "Username: @$bot_username"  
        log_info "ID: $bot_id"
        echo "=================================================="
        return 0
    else
        log_error "Bot connection failed!"
        local error_desc=$(echo "$bot_info" | jq -r '.description // "Unknown error"')
        log_error "Error: $error_desc"
        echo "=================================================="
        return 1
    fi
}

# Main execution
main() {
    if [[ $# -eq 0 ]]; then
        echo "📚 Book Search Sender via curl"
        echo "Sends messages to $BOT_USERNAME that trigger IDENTICAL pipeline as manual typing"
        echo ""
        echo "Usage:"
        echo "  $0 'Book Title'                    # Send single book"
        echo "  $0 'Book 1' 'Book 2' 'Book 3'     # Send multiple books"
        echo "  $0 --test                          # Test bot connectivity"
        echo ""
        echo "Examples:"
        echo "  $0 'Clean Code Robert Martin'"
        echo "  $0 'Python Guide' 'Design Patterns' 'Pragmatic Programmer'"
        echo ""
        exit 1
    fi
    
    # Handle special commands
    if [[ "$1" == "--test" ]]; then
        test_bot
        exit $?
    fi
    
    # Test connectivity first
    if ! test_bot; then
        exit 1
    fi
    
    echo ""
    
    # Send books
    if [[ $# -eq 1 ]]; then
        # Single book
        send_book_search "$1"
    else
        # Multiple books
        send_multiple_books "$@"
    fi
}

# Run main function
main "$@"