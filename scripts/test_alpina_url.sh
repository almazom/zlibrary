#!/bin/bash

echo "Testing Alpina URL extraction..."
URL="https://alpinabook.ru/catalog/book-pishi-sokrashchay-2025/"

echo "1. Direct test with quotes:"
./scripts/book_search.sh "$URL" 2>&1 | jq '.input_format, .query_info.extracted_query'

echo ""
echo "2. Test with known Russian query:"
./scripts/book_search.sh "Пиши сокращай" 2>&1 | jq '.status, .result.book_info.title'

echo ""
echo "3. Testing URL detection:"
if [[ "$URL" =~ ^https?:// ]]; then
    echo "URL detected correctly"
else
    echo "URL NOT detected"
fi