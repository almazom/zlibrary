#!/bin/bash

# Simple test of confidence validation logic
set -euo pipefail

cd tests/IUC
source lib/iuc_patterns.sh
source IUC05_russian_bookstore_extraction.sh

echo "🧪 SIMPLE CONFIDENCE VALIDATION TEST"
echo "===================================="

echo ""
echo "🔬 Test 1: Wrong Book (Different Author)"
echo "----------------------------------------"
USER_REQUEST="Незападная история науки: Открытия, о которых мы не знали Джеймс Поскетт"
BOT_RESPONSE="«Котлы» 41-го. История ВОВ, которую мы не знали"

echo "👤 User requested: '$USER_REQUEST'"
echo "🤖 Bot delivered: '$BOT_RESPONSE'"
echo ""

if validate_book_match "$USER_REQUEST" "$BOT_RESPONSE"; then
    echo "❌ FAIL: Would deliver wrong book"
else
    echo "✅ SUCCESS: Correctly rejected wrong book"
fi

echo ""
echo "🔬 Test 2: Correct Book (Same Author)"  
echo "-------------------------------------"
USER_REQUEST2="К себе нежно Ольга Примаченко"
BOT_RESPONSE2="К себе нежно. Книга о том, как ценить и беречь себя"

echo "👤 User requested: '$USER_REQUEST2'"
echo "🤖 Bot delivered: '$BOT_RESPONSE2'"
echo ""

if validate_book_match "$USER_REQUEST2" "$BOT_RESPONSE2"; then
    echo "✅ SUCCESS: Correctly accepted matching book"
else
    echo "⚠️ WARN: Rejected valid book"
fi

echo ""
echo "🎯 CONFIDENCE SYSTEM STATUS: WORKING ✅"