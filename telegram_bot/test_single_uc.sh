#\!/bin/bash
set -euo pipefail
source .env 2>/dev/null || true
BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-7956300223:AAHsFCu-4djOAy5G_1eBSZMVR1Zb0U3DCls}"
CHAT_ID="14835038"

# Colors
GREEN="[0;32m"
BLUE="[0;34m" 
NC="[0m"

# Send message
BOOK="Design Patterns Gang of Four"
echo -e "${BLUE}📚 Testing: $BOOK${NC}"

curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
     -H "Content-Type: application/json" \
     -d "{\"chat_id\": \"$CHAT_ID\", \"text\": \"$BOOK\"}" > /dev/null

echo -e "${GREEN}✅ Message sent${NC}"

# Monitor logs for 2 minutes
echo -e "${BLUE}👁️ Monitoring bot logs for 120s...${NC}"
start_time=$(date +%s)
initial_lines=$(wc -l < bot_tdd.log 2>/dev/null || echo "0")

while [[ $(date +%s) -lt $((start_time + 120)) ]]; do
    current_lines=$(wc -l < bot_tdd.log 2>/dev/null || echo "$initial_lines")
    if [[ $current_lines -gt $initial_lines ]]; then
        new_content=$(tail -n +$((initial_lines + 1)) bot_tdd.log)
        if [[ "$new_content" == *"$BOOK"* ]]; then
            echo -e "${GREEN}📨 Message received by bot${NC}"
        fi
        if [[ "$new_content" == *"EPUB file sent successfully"* ]]; then
            echo -e "${GREEN}📖 EPUB DELIVERED SUCCESS\!${NC}"
            exit 0
        fi
        if [[ "$new_content" == *"Sending EPUB file:"* ]]; then
            echo -e "${BLUE}📤 EPUB sending in progress...${NC}"
        fi
        initial_lines=$current_lines
    fi
    sleep 2
done

echo -e "${GREEN}⏰ Monitoring complete${NC}"

