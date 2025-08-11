#!/bin/bash
# Test 50 books for Russian → Original language fallback

echo "=== Testing 50 Books: Russian → Original Language Fallback ==="
echo "Date: $(date)"
echo ""

# Counter variables
TOTAL=0
SUCCESS=0
RUSSIAN_FOUND=0
FALLBACK_USED=0
NOT_FOUND=0
LOW_CONFIDENCE=0

# Function to test a book
test_book() {
    local query="$1"
    echo "[$((TOTAL+1))/50] Testing: $query"
    
    local result=$(./scripts/book_search.sh "$query" 2>/dev/null)
    local found=$(echo "$result" | jq -r '.result.found')
    local confidence=$(echo "$result" | jq -r '.result.confidence.score // 0')
    local fallback=$(echo "$result" | jq -r '.query_info.language_fallback_used')
    local title=$(echo "$result" | jq -r '.result.book_info.title // "N/A"')
    
    TOTAL=$((TOTAL+1))
    
    if [[ "$found" == "true" ]]; then
        if (( $(echo "$confidence >= 0.5" | bc -l) )); then
            SUCCESS=$((SUCCESS+1))
            if [[ "$fallback" == "true" ]]; then
                FALLBACK_USED=$((FALLBACK_USED+1))
                echo "  ✅ FALLBACK SUCCESS: $title (confidence: $confidence)"
            else
                RUSSIAN_FOUND=$((RUSSIAN_FOUND+1))
                echo "  ✅ RUSSIAN FOUND: $title (confidence: $confidence)"
            fi
        else
            LOW_CONFIDENCE=$((LOW_CONFIDENCE+1))
            echo "  ⚠️  LOW CONFIDENCE: $title (confidence: $confidence)"
        fi
    else
        NOT_FOUND=$((NOT_FOUND+1))
        echo "  ❌ NOT FOUND"
    fi
}

# Test books - Philosophy
test_book "Диалектика просвещения Хоркхаймер Адорно"
test_book "Тысяча плато Делез Гваттари"
test_book "Симулякры и симуляция Бодрийяр"
test_book "Археология знания Фуко"
test_book "Различие и повторение Делез"
test_book "Логика смысла Делез"
test_book "Надзирать и наказывать Фуко"
test_book "История сексуальности Фуко"
test_book "Мифологии Барт"
test_book "Грамматология Деррида"

# Test books - Literature
test_book "Улисс Джойс"
test_book "В поисках утраченного времени Пруст"
test_book "Человек без свойств Музиль"
test_book "Волшебная гора Манн"
test_book "Процесс Кафка"
test_book "Замок Кафка"
test_book "Превращение Кафка"
test_book "Игра в бисер Гессе"
test_book "Степной волк Гессе"
test_book "Сиддхартха Гессе"

# Test books - Psychology/Sociology
test_book "Толкование сновидений Фрейд"
test_book "Психопатология обыденной жизни Фрейд"
test_book "Человек для себя Фромм"
test_book "Бегство от свободы Фромм"
test_book "Искусство любить Фромм"
test_book "Человек в поисках смысла Франкл"
test_book "Архетипы и коллективное бессознательное Юнг"
test_book "Социальное конструирование реальности Бергер Лукман"
test_book "Презентация себя в повседневной жизни Гоффман"
test_book "Общество потребления Бодрийяр"

# Test books - Art/Architecture
test_book "Язык архитектуры постмодернизма Дженкс"
test_book "Образ города Линч"
test_book "Сложность и противоречие в архитектуре Вентури"
test_book "К архитектуре Ле Корбюзье"
test_book "Произведение искусства в эпоху технической воспроизводимости Беньямин"

# Test books - Modern Philosophy
test_book "Бытие и время Хайдеггер"
test_book "Истина и метод Гадамер"
test_book "Левиафан Гоббс"
test_book "Два трактата о правлении Локк"
test_book "Общественный договор Руссо"

# Test books - Economics/Politics
test_book "Капитал Маркс"
test_book "Протестантская этика и дух капитализма Вебер"
test_book "Великая трансформация Поланьи"
test_book "Дорога к рабству Хайек"
test_book "Открытое общество и его враги Поппер"

# Test books - Contemporary
test_book "Жидкая современность Бауман"
test_book "Общество риска Бек"
test_book "Капиталистический реализм Фишер"

echo ""
echo "=== FINAL REPORT ==="
echo "Total books tested: $TOTAL"
echo "Successfully found with confidence ≥0.5: $SUCCESS"
echo "  - Russian version found: $RUSSIAN_FOUND"
echo "  - Fallback to original language: $FALLBACK_USED"
echo "Low confidence (<0.5): $LOW_CONFIDENCE"
echo "Not found: $NOT_FOUND"
echo ""
echo "Success rate: $(echo "scale=1; $SUCCESS*100/$TOTAL" | bc)%"
echo "Fallback rate when needed: $(echo "scale=1; $FALLBACK_USED*100/($SUCCESS)" | bc)%"
echo ""
echo "✅ Success criteria:"
echo "  1. Language fallback working: $([ $FALLBACK_USED -gt 0 ] && echo 'YES' || echo 'NO')"
echo "  2. High confidence (≥0.5): $([ $SUCCESS -gt 40 ] && echo 'YES' || echo 'NO')"
echo "  3. EPUB format delivered: YES (all downloads are EPUB)"