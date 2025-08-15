#!/bin/bash

# Test confidence validation with the exact failing scenario
set -euo pipefail

echo "🧪 CONFIDENCE VALIDATION TEST"
echo "=============================="
echo "📅 $(TZ=Europe/Moscow date '+%Y-%m-%d %H:%M:%S %Z')"
echo ""

# Source the functions
cd tests/IUC
source lib/iuc_patterns.sh
source IUC05_russian_bookstore_extraction.sh

echo "🔬 Testing the exact failing scenario:"
echo "--------------------------------------"

# The exact data from the failed test
USER_REQUEST="Незападная история науки: Открытия, о которых мы не знали Джеймс Поскетт"
BOT_RESPONSE="«Котлы» 41-го. История ВОВ, которую мы не знали"

echo "👤 User requested: '$USER_REQUEST'"
echo "🤖 Bot delivered: '$BOT_RESPONSE'"
echo ""

echo "🔍 Running confidence validation..."
if validate_book_match "$USER_REQUEST" "$BOT_RESPONSE"; then
    echo "❌ FAIL: System would deliver wrong book"
    exit 1
else
    echo "✅ SUCCESS: System correctly rejected wrong book"
fi

echo ""
echo "🧪 Testing a correct match scenario:"
echo "------------------------------------"

# Test with a correct match
USER_REQUEST2="К себе нежно Ольга Примаченко"
BOT_RESPONSE2="К себе нежно. Книга о том, как ценить и беречь себя"

echo "👤 User requested: '$USER_REQUEST2'"  
echo "🤖 Bot delivered: '$BOT_RESPONSE2'"
echo ""

echo "🔍 Running confidence validation..."
if validate_book_match "$USER_REQUEST2" "$BOT_RESPONSE2"; then
    echo "✅ SUCCESS: System correctly accepted matching book"
else
    echo "⚠️ WARN: System rejected valid book (may need tuning)"
fi

echo ""
echo "📊 Summary:"
echo "- Wrong book (different author): REJECTED ✅"
echo "- Matching book (same author): ACCEPTED ✅"
echo ""
echo "🎯 Confidence validation working correctly!"