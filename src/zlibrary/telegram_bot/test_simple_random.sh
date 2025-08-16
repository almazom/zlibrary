#!/bin/bash

# Simple random book test without AI - just to demonstrate clean output
source .env 2>/dev/null || true
BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-7956300223:AAHsFCu-4djOAy5G_1eBSZMVR1Zb0U3DCls}"
CHAT_ID="14835038"

# Simple book arrays
BOOKS=(
    "Design Patterns Gang of Four"
    "Refactoring Martin Fowler"
    "The Pragmatic Programmer"
    "Effective Java Joshua Bloch"
    "Code Complete Steve McConnell"
)

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Pick random book
RANDOM_INDEX=$((RANDOM % ${#BOOKS[@]}))
BOOK="${BOOKS[$RANDOM_INDEX]}"

echo -e "${BLUE}📚 Selected book: $BOOK${NC}"

# Send to bot
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
     -H "Content-Type: application/json" \
     -d "{\"chat_id\": \"$CHAT_ID\", \"text\": \"$BOOK\"}" > /dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Message sent to @epub_toc_based_sample_bot${NC}"
    echo -e "${BLUE}📖 Expected: Bot will search for '$BOOK' and send EPUB${NC}"
else
    echo -e "❌ Failed to send message"
fi