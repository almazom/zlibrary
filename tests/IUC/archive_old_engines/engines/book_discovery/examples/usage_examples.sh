#!/bin/bash

# =============================================================================
# Book Discovery Engine - Usage Examples
# Demonstrates various ways to use the atomic book discovery engine
# =============================================================================

ENGINE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENGINE="$ENGINE_DIR/engine.sh"

echo "📚 Book Discovery Engine - Usage Examples"
echo "=========================================="

# Example 1: Basic Discovery
echo ""
echo "🎯 Example 1: Basic book discovery from eksmo.ru"
echo "Command: $ENGINE --store eksmo.ru"
echo "Output:"
$ENGINE --store eksmo.ru

# Example 2: Specific Category and Page
echo ""
echo "🎯 Example 2: Discover from specific category and page" 
echo "Command: $ENGINE --store alpinabook.ru --category business --page 2 --count 3"
echo "Output:"
$ENGINE --store alpinabook.ru --category business --page 2 --count 3

# Example 3: Verbose Mode for Debugging
echo ""
echo "🎯 Example 3: Verbose mode with detailed logging"
echo "Command: $ENGINE --store eksmo.ru --category fiction --verbose --count 2"
echo "Output:"
$ENGINE --store eksmo.ru --category fiction --verbose --count 2

# Example 4: Error Handling - Invalid Store
echo ""
echo "🎯 Example 4: Error handling with invalid store"
echo "Command: $ENGINE --store invalid_store"
echo "Output:"
$ENGINE --store invalid_store 2>/dev/null || echo "Exit code: $?"

# Example 5: Custom Timeout
echo ""
echo "🎯 Example 5: Custom timeout configuration"
echo "Command: $ENGINE --store eksmo.ru --timeout 30"
echo "Output:"
$ENGINE --store eksmo.ru --timeout 30

# Example 6: Pipeline Integration
echo ""
echo "🎯 Example 6: Pipeline integration with jq processing"
echo "Command: $ENGINE --store eksmo.ru --count 2 | jq '.result.books[0].title'"
echo "Output:"
FIRST_BOOK_TITLE=$($ENGINE --store eksmo.ru --count 2 | jq -r '.result.books[0].title' 2>/dev/null)
echo "First discovered book: $FIRST_BOOK_TITLE"

# Example 7: Multiple Store Testing
echo ""
echo "🎯 Example 7: Testing multiple stores"
for store in eksmo.ru alpinabook.ru; do
    echo "Testing store: $store"
    result=$($ENGINE --store $store --count 1 2>/dev/null)
    status=$(echo "$result" | jq -r '.status' 2>/dev/null)
    echo "Status: $status"
    if [[ "$status" == "success" ]]; then
        book_count=$(echo "$result" | jq -r '.result.discovered_count' 2>/dev/null)
        echo "Books discovered: $book_count"
    fi
    echo ""
done

# Example 8: Category Testing
echo ""
echo "🎯 Example 8: Testing different categories for eksmo.ru"
for category in books fiction novelties; do
    echo "Testing category: $category"
    result=$($ENGINE --store eksmo.ru --category $category --count 1 2>/dev/null)
    status=$(echo "$result" | jq -r '.status' 2>/dev/null)
    echo "Status: $status"
    echo ""
done

# Example 9: Performance Testing
echo ""
echo "🎯 Example 9: Performance measurement"
echo "Measuring discovery time..."
start_time=$(date +%s)
result=$($ENGINE --store eksmo.ru --count 3 2>/dev/null)
end_time=$(date +%s)
duration=$((end_time - start_time))
echo "Discovery completed in: ${duration}s"

status=$(echo "$result" | jq -r '.status' 2>/dev/null)
if [[ "$status" == "success" ]]; then
    book_count=$(echo "$result" | jq -r '.result.discovered_count' 2>/dev/null)
    echo "Books discovered: $book_count"
    echo "Average time per book: $((duration / book_count))s"
fi

# Example 10: JSON Processing and Extraction
echo ""
echo "🎯 Example 10: Advanced JSON processing"
echo "Extracting all book URLs:"
result=$($ENGINE --store eksmo.ru --count 2 2>/dev/null)
echo "$result" | jq -r '.result.books[].url' 2>/dev/null | while read -r url; do
    echo "  - $url"
done

# Example 11: Error Recovery Pattern  
echo ""
echo "🎯 Example 11: Error recovery pattern"
for attempt in 1 2 3; do
    echo "Attempt $attempt:"
    if result=$($ENGINE --store eksmo.ru --count 1 2>/dev/null); then
        echo "  Success!"
        echo "$result" | jq -r '.result.books[0].title' 2>/dev/null | head -1
        break
    else
        echo "  Failed, retrying..."
        sleep 2
    fi
done

# Example 12: Configuration Validation
echo ""
echo "🎯 Example 12: Help and configuration info"
echo "Engine help:"
$ENGINE --help | head -5

echo ""
echo "Engine manifest info:"
if [[ -f "$ENGINE_DIR/manifest.json" ]]; then
    echo "  Version: $(jq -r '.version' "$ENGINE_DIR/manifest.json")"
    echo "  Supported stores: $(jq -r '.configuration.supported_stores[].name' "$ENGINE_DIR/manifest.json" | tr '\n' ' ')"
fi

echo ""
echo "✅ Usage examples completed!"
echo "For more examples, see the README.md and docs/ directory."