#!/bin/bash

echo "📱 Telegram Bot Setup for Autopilot Notifications"
echo "================================================="
echo ""
echo "To receive test notifications in Telegram:"
echo ""
echo "1. Create a bot:"
echo "   - Open @BotFather in Telegram"
echo "   - Send /newbot"
echo "   - Choose a name and username"
echo "   - Copy the bot token"
echo ""
echo "2. Get your chat ID:"
echo "   - Start a chat with your bot"
echo "   - Send any message"
echo "   - Visit: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates"
echo "   - Find your chat_id in the response"
echo ""
echo "3. Add to .env file:"
echo "   TELEGRAM_BOT_TOKEN=your_bot_token_here"
echo "   TELEGRAM_CHAT_ID=your_chat_id_here"
echo ""
echo "================================================="
echo ""

# Check if user wants to add credentials now
read -p "Do you have Telegram credentials ready? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter Bot Token: " bot_token
    read -p "Enter Chat ID: " chat_id
    
    # Add to .env
    echo "" >> .env
    echo "# Telegram Bot Configuration" >> .env
    echo "TELEGRAM_BOT_TOKEN=$bot_token" >> .env
    echo "TELEGRAM_CHAT_ID=$chat_id" >> .env
    
    echo "✅ Telegram credentials added to .env"
    
    # Test the connection
    echo "Testing Telegram connection..."
    curl -s -X POST "https://api.telegram.org/bot$bot_token/sendMessage" \
        -d "chat_id=$chat_id" \
        -d "text=🚀 Autopilot Testing Bot Connected!" \
        -d "parse_mode=Markdown" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ Test message sent successfully!"
    else
        echo "⚠️ Could not send test message. Check your credentials."
    fi
else
    echo "ℹ️ You can add credentials later to .env file"
fi