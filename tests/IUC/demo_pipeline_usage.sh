#!/bin/bash

# demo_pipeline_usage.sh: Demonstration of using IUC05_atomic_book_extraction as a pipeline component
# Shows how the atomic book extraction can be used as a building block in other tests

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ATOMIC_EXTRACTOR="$SCRIPT_DIR/IUC05_atomic_book_extraction.sh"

echo "🔗 Pipeline Usage Demo: Using IUC05_atomic_book_extraction as a pipeline component"
echo "=============================================================================="

# Example 1: Extract book and use in search pipeline
echo ""
echo "📚 Example 1: Book Search Pipeline"
echo "-----------------------------------"

if [[ -x "$ATOMIC_EXTRACTOR" ]]; then
    echo "🔍 Step 1: Extract random book metadata..."
    
    if book_result=$(PATH="/home/almaz/.claude/local:$PATH" timeout 90 "$ATOMIC_EXTRACTOR" 2>/dev/null); then
        echo "✅ Book extracted successfully!"
        
        # Parse the result
        status=$(echo "$book_result" | jq -r '.status')
        
        if [[ "$status" == "success" ]]; then
            title=$(echo "$book_result" | jq -r '.extraction.title')
            author=$(echo "$book_result" | jq -r '.extraction.author')
            confidence=$(echo "$book_result" | jq -r '.extraction.confidence')
            source_url=$(echo "$book_result" | jq -r '.source.url')
            store_type=$(echo "$book_result" | jq -r '.source.store_type')
            
            echo "📖 Extracted: '$title' by '$author'"
            echo "🎯 Confidence: $confidence"
            echo "🏪 Source: $source_url ($store_type)"
            echo ""
            
            echo "🔍 Step 2: Format for book search..."
            search_query="$title $author"
            echo "📋 Search query: '$search_query'"
            echo ""
            
            echo "✅ Pipeline Step Complete - Book ready for search system"
            echo "   Next step would be: ./book_search.sh \"$search_query\""
            
        else
            echo "❌ Book extraction failed"
            exit 1
        fi
    else
        echo "❌ Failed to extract book"
        exit 1
    fi
else
    echo "❌ Atomic extractor not found: $ATOMIC_EXTRACTOR"
    exit 1
fi

echo ""
echo "📊 Example 2: Batch Processing Pipeline"
echo "----------------------------------------"

echo "🔄 Extracting 3 random books for batch processing..."
books_array="[]"

for i in {1..3}; do
    echo "📚 Extracting book $i/3..."
    
    if book_result=$(PATH="/home/almaz/.claude/local:$PATH" timeout 90 "$ATOMIC_EXTRACTOR" 2>/dev/null); then
        status=$(echo "$book_result" | jq -r '.status')
        
        if [[ "$status" == "success" ]]; then
            title=$(echo "$book_result" | jq -r '.extraction.title')
            author=$(echo "$book_result" | jq -r '.extraction.author')
            confidence=$(echo "$book_result" | jq -r '.extraction.confidence')
            
            echo "   ✅ '$title' by '$author' (confidence: $confidence)"
            
            # Add to batch array
            books_array=$(echo "$books_array" | jq --argjson book "$book_result" '. += [$book]')
        else
            echo "   ❌ Failed (attempt $i)"
        fi
    else
        echo "   ❌ Extraction timeout (attempt $i)"
    fi
    
    sleep 2  # Small delay between extractions
done

echo ""
echo "📋 Batch Results Summary:"
batch_count=$(echo "$books_array" | jq 'length')
echo "   Total books extracted: $batch_count"

if [[ $batch_count -gt 0 ]]; then
    echo "   📚 Books in batch:"
    echo "$books_array" | jq -r '.[] | "   - \(.extraction.title) by \(.extraction.author) (\(.source.store_type))"'
    
    echo ""
    echo "✅ Batch pipeline complete - Ready for bulk search processing"
    echo "   Next step would be: process each book through search system"
fi

echo ""
echo "🎯 Example 3: Confidence-Based Pipeline"
echo "----------------------------------------"

echo "🔍 Extracting books until we find one with high confidence (≥0.8)..."
attempts=0
max_attempts=5

while [[ $attempts -lt $max_attempts ]]; do
    ((attempts++))
    echo "🔄 Attempt $attempts/$max_attempts..."
    
    if book_result=$(PATH="/home/almaz/.claude/local:$PATH" timeout 90 "$ATOMIC_EXTRACTOR" 2>/dev/null); then
        status=$(echo "$book_result" | jq -r '.status')
        
        if [[ "$status" == "success" ]]; then
            confidence=$(echo "$book_result" | jq -r '.extraction.confidence')
            title=$(echo "$book_result" | jq -r '.extraction.title')
            author=$(echo "$book_result" | jq -r '.extraction.author')
            
            echo "   📖 Found: '$title' by '$author' (confidence: $confidence)"
            
            # Check confidence threshold
            if (( $(echo "$confidence >= 0.8" | bc -l 2>/dev/null || echo "0") )); then
                echo "   ✅ High confidence book found!"
                echo "   🎯 This book is suitable for automated processing"
                break
            else
                echo "   ⚠️ Low confidence, continuing search..."
            fi
        else
            echo "   ❌ Extraction failed"
        fi
    else
        echo "   ❌ Extraction timeout"
    fi
done

if [[ $attempts -eq $max_attempts ]]; then
    echo "⚠️ Reached maximum attempts without finding high-confidence book"
    echo "   Pipeline would fallback to manual review or lower threshold"
fi

echo ""
echo "🏁 Pipeline Demo Complete"
echo "========================="
echo ""
echo "🔧 Usage Summary:"
echo "   ✅ IUC05_atomic_book_extraction.sh can be used as a standalone component"
echo "   ✅ Produces structured JSON output for easy parsing"
echo "   ✅ Can be integrated into larger test pipelines"
echo "   ✅ Supports batch processing and conditional logic"
echo "   ✅ Provides randomness for varied test scenarios"
echo ""
echo "📝 Integration Examples:"
echo "   • Book search testing: Extract → Search → Validate"
echo "   • Performance testing: Batch extract → Bulk search"
echo "   • Quality testing: Filter by confidence → Test high-quality matches"
echo "   • Stress testing: Continuous extraction → Load testing"