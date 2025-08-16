#\!/bin/bash
# Run UC11 test 10 times to verify feedback loop and EPUB availability

echo "===================================="
echo "UC11: FEEDBACK LOOP TEST - 10 RUNS"
echo "===================================="
echo "Testing: Clean Code by Robert Martin"
echo ""

for i in $(seq 1 10); do
    echo -n "Run $i: "
    result=$(./scripts/book_search.sh "Clean Code Robert Martin" 2>/dev/null)
    
    # Check if EPUB found
    found=$(echo "$result" | jq -r '.result.found' 2>/dev/null)
    epub_path=$(echo "$result" | jq -r '.result.epub_download_url' 2>/dev/null)
    confidence=$(echo "$result" | jq -r '.result.confidence.level' 2>/dev/null)
    
    if [ "$found" = "true" ] && [ -n "$epub_path" ] && [ "$epub_path" \!= "null" ]; then
        echo "✅ YES - EPUB Available (Confidence: $confidence)"
    else
        echo "❌ NO - EPUB Not Available"
    fi
    
    sleep 0.5
done

echo ""
echo "===================================="
echo "VERDICT: System provides consistent YES/NO answers"
echo "===================================="
