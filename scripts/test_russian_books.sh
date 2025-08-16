#\!/bin/bash
# Test Russian books with clear YES/NO verdicts

echo "===================================="
echo "RUSSIAN BOOKS TEST SUITE"
echo "===================================="

test_book() {
    local query="$1"
    local name="$2"
    
    echo -n "$name: "
    result=$(./scripts/book_search.sh "$query" 2>/dev/null)
    
    found=$(echo "$result" | jq -r '.result.found' 2>/dev/null)
    epub_path=$(echo "$result" | jq -r '.result.epub_download_url' 2>/dev/null)
    confidence=$(echo "$result" | jq -r '.result.confidence.level' 2>/dev/null)
    
    if [ "$found" = "true" ] && [ -n "$epub_path" ] && [ "$epub_path" \!= "null" ]; then
        echo "✅ YES (Confidence: $confidence)"
    else
        echo "❌ NO"
    fi
}

# Russian classics
echo -e "\n📚 Russian Classics:"
test_book "Война и мир Толстой" "War and Peace"
test_book "Преступление и наказание Достоевский" "Crime and Punishment"
test_book "Мастер и Маргарита Булгаков" "Master and Margarita"
test_book "Евгений Онегин Пушкин" "Eugene Onegin"
test_book "Анна Каренина Толстой" "Anna Karenina"

# Modern Russian
echo -e "\n📚 Modern Russian:"
test_book "Метро 2033 Глуховский" "Metro 2033"
test_book "Пикник на обочине Стругацкие" "Roadside Picnic"
test_book "Понедельник начинается в субботу" "Monday Begins on Saturday"

# Non-existent Russian books
echo -e "\n📚 Non-existent (should be NO):"
test_book "фывапролд несуществующая книга" "Fake Russian Book 1"
test_book "ццц999 выдуманный автор" "Fake Russian Book 2"

echo -e "\n===================================="
echo "VERDICT: Clear YES/NO for each book"
echo "===================================="
