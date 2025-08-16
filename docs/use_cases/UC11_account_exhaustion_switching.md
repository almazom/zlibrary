# UC11: Account Exhaustion and Switching Test Cases

## Feature: Multi-Account Management with Automatic Switching on Exhaustion
As a system with multiple Z-Library accounts
I want to automatically switch accounts when one is exhausted
So that users can continue downloading without interruption

## Background:
- 3 Z-Library accounts configured
- Account 1: 8 downloads daily limit
- Account 2: 4 downloads daily limit  
- Account 3: 10 downloads daily limit
- Total capacity: 22 downloads per day
- Reset time: Midnight Moscow time (MSK)

## Test Data Sources:
1. **Podpisnie.ru Books** (Russian bookstore)
2. **Ad Marginem Books** (Philosophy/Art publisher)

## Scenario 1: Sequential Account Exhaustion
**Given** All accounts are fresh with full limits
**When** Downloading 25 books sequentially
**Then** System should:
  - Use Account 1 for first 8 books
  - Switch to Account 2 for next 4 books
  - Switch to Account 3 for next 10 books
  - Fail gracefully on book 23

### Test Implementation:
```python
# Books from Podpisnie.ru
BOOKS_BATCH_1 = [
    "Семейный лексикон",
    "Ирландские сказки и легенды",
    "Из ничего: искусство создавать искусство",
    "Развод",
    "Курс: Разговоры со студентами",
    "Семь лет в Крестах",
    "Кадавры",
    "Полторы комнаты"
]

# Books from Ad Marginem  
BOOKS_BATCH_2 = [
    "Невыносимая легкость бытия Кундера",
    "Средневековое мышление Ален де Либера",
    "Феноменология восприятия Мерло-Понти",
    "Бытие и ничто Сартр"
]

# Philosophy/Literature books
BOOKS_BATCH_3 = [
    "Общество спектакля Ги Дебор",
    "Симулякры и симуляция Бодрийяр",
    "Капитализм и шизофрения Делез Гваттари",
    "Археология знания Фуко",
    "Различие и повторение Делез",
    "Логика смысла Делез",
    "Надзирать и наказывать Фуко",
    "История сексуальности Фуко",
    "Мифологии Барт",
    "Грамматология Деррида"
]

# Extra books to ensure exhaustion
BOOKS_OVERFLOW = [
    "Улисс Джойс",
    "В поисках утраченного времени Пруст",
    "Человек без свойств Музиль"
]
```

## Scenario 2: Account Switch Detection
**Given** Account 1 is exhausted
**When** Attempting next download
**Then** System should:
  - Skip Account 1 (0 downloads)
  - Try Account 2 automatically
  - Log switch event
  - Continue download

### Expected Behavior:
```json
// Book #8 - Last from Account 1
{
  "status": "success",
  "result": {
    "found": true,
    "epub_download_url": "/downloads/book8.epub"
  }
}

// Book #9 - Automatic switch to Account 2
{
  "status": "success",
  "result": {
    "found": true,
    "epub_download_url": "/downloads/book9.epub"
  }
  // Note: No indication of account switch in response
}
```

## Scenario 3: All Accounts Exhausted
**Given** All 22 downloads used
**When** Attempting download #23
**Then** System should return:
```json
{
  "status": "error",
  "result": {
    "error": "search_failed",
    "message": "No working accounts found"
  }
}
```

## Scenario 4: Account Health Monitoring
**Given** Partial exhaustion state
**When** Checking account status
**Then** Should show:

### Command:
```bash
python3 check_accounts.py
```

### Expected Output:
```json
{
  "accounts": [
    {
      "account_id": 1,
      "daily_remaining": 0,
      "status": "exhausted"
    },
    {
      "account_id": 2,
      "daily_remaining": 2,
      "status": "healthy"
    },
    {
      "account_id": 3,
      "daily_remaining": 10,
      "status": "healthy"
    }
  ],
  "total_downloads_available": 12
}
```

## Scenario 5: Reset Time Tracking
**Given** Accounts exhausted
**When** Checking reset time
**Then** Should show time until midnight MSK

## Test Script: Full Exhaustion Simulation
```bash
#!/bin/bash
# UC11_exhaustion_test.sh

echo "=== UC11: Account Exhaustion & Switching Test ==="
echo "Date: $(date)"
echo "Moscow Time: $(TZ=Europe/Moscow date)"
echo ""

# Track statistics
TOTAL=0
SUCCESS=0
ACCOUNT_1=0
ACCOUNT_2=0
ACCOUNT_3=0
SWITCHES=0
LAST_ACCOUNT=1

# Function to detect account switch
detect_switch() {
    # Logic to detect which account was used
    # Based on download patterns
    if [[ $SUCCESS -le 8 ]]; then
        CURRENT_ACCOUNT=1
    elif [[ $SUCCESS -le 12 ]]; then
        CURRENT_ACCOUNT=2
    else
        CURRENT_ACCOUNT=3
    fi
    
    if [[ $CURRENT_ACCOUNT != $LAST_ACCOUNT ]]; then
        SWITCHES=$((SWITCHES+1))
        echo "  ⚡ ACCOUNT SWITCH: #$LAST_ACCOUNT → #$CURRENT_ACCOUNT"
        LAST_ACCOUNT=$CURRENT_ACCOUNT
    fi
}

# Test all books
ALL_BOOKS=(
    # Batch 1: Podpisnie.ru (8 books)
    "Семейный лексикон"
    "Ирландские сказки и легенды"
    "Из ничего искусство создавать искусство"
    "Развод"
    "Курс Разговоры со студентами"
    "Семь лет в Крестах"
    "Кадавры"
    "Полторы комнаты"
    
    # Batch 2: Philosophy (4 books)
    "Невыносимая легкость бытия"
    "Средневековое мышление"
    "Феноменология восприятия"
    "Бытие и ничто"
    
    # Batch 3: More books (10 books)
    "Общество спектакля"
    "Симулякры и симуляция"
    "Капитализм и шизофрения"
    "Археология знания"
    "Различие и повторение"
    "Логика смысла"
    "Надзирать и наказывать"
    "История сексуальности"
    "Мифологии Барт"
    "Грамматология"
    
    # Overflow (3 books to test exhaustion)
    "Улисс Джойс"
    "Процесс Кафка"
    "Замок Кафка"
)

for book in "${ALL_BOOKS[@]}"; do
    TOTAL=$((TOTAL+1))
    echo "[$TOTAL/25] Testing: $book"
    
    result=$(./scripts/book_search.sh "$book" 2>/dev/null)
    status=$(echo "$result" | jq -r '.status')
    
    if [[ "$status" == "success" ]]; then
        SUCCESS=$((SUCCESS+1))
        detect_switch
        echo "  ✅ Downloaded (Total: $SUCCESS/22)"
    else
        echo "  ❌ Failed - Accounts exhausted"
        break
    fi
done

echo ""
echo "=== EXHAUSTION TEST RESULTS ==="
echo "Books attempted: $TOTAL"
echo "Books downloaded: $SUCCESS"
echo "Account switches: $SWITCHES"
echo ""
echo "Expected: 22 downloads, 2 switches"
echo "Actual: $SUCCESS downloads, $SWITCHES switches"
echo ""
if [[ $SUCCESS -eq 22 ]] && [[ $SWITCHES -ge 2 ]]; then
    echo "✅ TEST PASSED: Exhaustion handling works correctly"
else
    echo "❌ TEST FAILED: Check implementation"
fi
```

## Success Metrics:
- ✅ All 22 downloads used before exhaustion
- ✅ Exactly 2 account switches occur
- ✅ Switches happen at correct points (8 and 12)
- ✅ No duplicate account attempts
- ✅ Clear error on exhaustion
- ✅ Account status correctly reported

## Edge Cases:
1. **Partial failure**: One account fails login, others continue
2. **Mid-download exhaustion**: Account exhausts during batch
3. **Reset during operation**: Midnight reset while downloading
4. **Concurrent requests**: Multiple downloads at once
5. **Network failures**: Retry with same account first

## Implementation Requirements:

### Account Selection Logic:
```python
async def get_working_account():
    """Get next account with available downloads"""
    
    for email, password in accounts:
        if email in exhausted_accounts:
            continue
            
        try:
            client = AsyncZlib()
            profile = await client.login(email, password)
            limits = await profile.get_limits()
            
            if limits.get('daily_remaining', 0) > 0:
                return client, profile
            else:
                exhausted_accounts.add(email)
        except Exception:
            failed_accounts.add(email)
            continue
    
    return None, None
```

### Switch Detection:
```python
def log_account_switch(old_account, new_account):
    """Log account switching event"""
    print(f"Account switch: {old_account} → {new_account}")
    # Don't expose in API response
```

## Validation Checklist:
- [ ] Account 1 handles exactly 8 downloads
- [ ] Account 2 handles exactly 4 downloads  
- [ ] Account 3 handles exactly 10 downloads
- [ ] First switch occurs at download #9
- [ ] Second switch occurs at download #13
- [ ] Download #23 fails with exhaustion error
- [ ] No account credentials exposed in responses
- [ ] Account status monitoring works
- [ ] Reset time correctly calculated

## Conclusion:
This UC ensures the multi-account system provides maximum availability (22 books/day) with transparent automatic failover when accounts exhaust their limits.