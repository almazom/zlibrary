#!/bin/bash

echo "📊 AUTOPILOT MONITORING DASHBOARD"
echo "================================="

# Check if autopilot is running
if [ -f "logs/autopilot.pid" ]; then
    PID=$(cat logs/autopilot.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "✅ Autopilot Status: RUNNING (PID: $PID)"
    else
        echo "❌ Autopilot Status: STOPPED"
        rm -f logs/autopilot.pid
    fi
else
    echo "⚪ Autopilot Status: NOT STARTED"
fi

echo ""

# Show recent logs if available
LATEST_LOG=$(ls -t logs/autopilot_*.log 2>/dev/null | head -1)
if [ -n "$LATEST_LOG" ]; then
    echo "📋 Latest Log: $LATEST_LOG"
    echo "─────────────────────────────"
    echo ""
    
    # Show progress
    if grep -q "AUTOPILOT TESTING STARTED" "$LATEST_LOG" 2>/dev/null; then
        echo "🚀 Testing started!"
    fi
    
    if grep -q "Phase 1:" "$LATEST_LOG" 2>/dev/null; then
        echo "📌 Phase 1: URL Tests - In Progress"
    fi
    
    if grep -q "Phase 2:" "$LATEST_LOG" 2>/dev/null; then
        echo "📌 Phase 2: Query Tests - In Progress" 
    fi
    
    if grep -q "Phase 3:" "$LATEST_LOG" 2>/dev/null; then
        echo "📌 Phase 3: Error Tests - In Progress"
    fi
    
    if grep -q "AUTOPILOT TESTING COMPLETE" "$LATEST_LOG" 2>/dev/null; then
        echo "✅ All tests completed!"
        echo ""
        echo "📊 Final Results:"
        grep -E "(Success Rate|Duration)" "$LATEST_LOG" 2>/dev/null || echo "   (Processing results...)"
    fi
    
    echo ""
    echo "📺 Live Monitoring:"
    echo "   tail -f $LATEST_LOG"
    echo ""
    echo "🔍 Recent Activity (last 10 lines):"
    echo "─────────────────────────────────"
    tail -10 "$LATEST_LOG" 2>/dev/null || echo "   (No activity yet)"
    
else
    echo "📋 No log files found in logs/"
    echo ""
    echo "🚀 To start autopilot testing:"
    echo "   ./run_autopilot_background.sh"
fi

echo ""
echo "🎮 Available Commands:"
echo "   ./run_autopilot_background.sh    # Start autopilot testing"
echo "   ./monitor_autopilot.sh           # This monitoring script"
echo "   ./setup_telegram.sh              # Configure Telegram notifications"
echo "   python3 quick_autopilot_demo.py  # Quick demo test"
echo ""

# Show results files if any
RESULTS=$(ls -t autopilot_results_*.json 2>/dev/null | head -3)
if [ -n "$RESULTS" ]; then
    echo "📁 Recent Result Files:"
    echo "$RESULTS" | while read -r file; do
        SIZE=$(du -h "$file" 2>/dev/null | cut -f1)
        TIMESTAMP=$(echo "$file" | grep -o '[0-9]\{8\}_[0-9]\{6\}' | sed 's/_/ /')
        echo "   $file ($SIZE) - $TIMESTAMP"
    done
    echo ""
fi