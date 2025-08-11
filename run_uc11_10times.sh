#!/bin/bash
# Run UC11 exhaustion test 10 times and report results via Telegram

echo "=== Running UC11 Test 10 Times ==="
echo "Start time: $(date)"

# Results tracking
PASS_COUNT=0
FAIL_COUNT=0
RESULTS_LOG=""

# Run test 10 times
for i in {1..10}; do
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "RUN $i/10"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Run the simulation
    result=$(python3 tests/UC11_simulation.py 2>&1 | grep "UC11 TEST")
    
    if [[ "$result" == *"PASSED"* ]]; then
        echo "✅ Run $i: PASSED"
        PASS_COUNT=$((PASS_COUNT+1))
        RESULTS_LOG="${RESULTS_LOG}Run $i: ✅ PASS\n"
    else
        echo "❌ Run $i: FAILED"
        FAIL_COUNT=$((FAIL_COUNT+1))
        RESULTS_LOG="${RESULTS_LOG}Run $i: ❌ FAIL\n"
    fi
    
    # Small delay between runs
    sleep 0.5
done

# Calculate success rate
SUCCESS_RATE=$(echo "scale=1; $PASS_COUNT*100/10" | bc)

# Prepare report
REPORT="🤖 UC11 Test Report (10 Runs)
━━━━━━━━━━━━━━━━━━━━━━
📊 Results:
✅ Passed: $PASS_COUNT/10
❌ Failed: $FAIL_COUNT/10
📈 Success Rate: ${SUCCESS_RATE}%

📝 Test: Account Exhaustion & Switching
📚 Books: 25 from Podpisnie.ru/Ad Marginem
🔄 Expected: 22 downloads, 2 switches

💾 Individual Runs:
$RESULTS_LOG
⏰ Time: $(date '+%H:%M %Z')
📍 System: zlibrary_api_module

Status: $([ $PASS_COUNT -eq 10 ] && echo '✅ All tests passed!' || echo '⚠️ Some tests failed')"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "FINAL REPORT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$REPORT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Send via Telegram using fallback script
echo ""
echo "📤 Sending report to Telegram..."
/home/almaz/MCP/scripts/smart-telegram-healer.sh send "$REPORT" 2>&1 | tail -2

echo ""
echo "Test complete: $(date)"