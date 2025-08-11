#!/bin/bash

echo "🚀 Starting Autopilot Testing in Background"
echo "=========================================="

# Create logs directory
mkdir -p logs

# Get timestamp for this run
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="logs/autopilot_${TIMESTAMP}.log"

echo "📋 Test Configuration:"
echo "   • URL Tests: 5 marketplace URLs"  
echo "   • Query Tests: 5 direct searches"
echo "   • Error Tests: 3 edge cases"
echo "   • Log File: $LOG_FILE"
echo ""

echo "⏰ Starting tests at $(date '+%H:%M:%S')..."

# Run autopilot tests in background with logging
nohup python3 autopilot_test_url_epub.py > "$LOG_FILE" 2>&1 &
AUTOPILOT_PID=$!

echo "🔥 Autopilot PID: $AUTOPILOT_PID"
echo "📊 Monitor progress with: tail -f $LOG_FILE"
echo ""

# Show initial progress
echo "📡 Showing initial progress (10 seconds)..."
sleep 2
if kill -0 $AUTOPILOT_PID 2>/dev/null; then
    echo "✅ Autopilot is running"
    echo ""
    echo "📋 First few log lines:"
    head -20 "$LOG_FILE" 2>/dev/null || echo "   (Log file not created yet)"
    echo ""
    echo "🔍 To monitor:"
    echo "   tail -f $LOG_FILE"
    echo ""
    echo "🛑 To stop:"
    echo "   kill $AUTOPILOT_PID"
    echo ""
    echo "📊 Check results in ~5-10 minutes"
else
    echo "❌ Autopilot failed to start"
    cat "$LOG_FILE" 2>/dev/null
fi

# Save PID for later reference
echo $AUTOPILOT_PID > logs/autopilot.pid
echo "💾 PID saved to logs/autopilot.pid"