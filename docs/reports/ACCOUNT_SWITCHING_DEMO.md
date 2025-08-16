# Account Switching Strategy - Demonstration

## How Account Switching Works on Exhaustion

### Initial State
```
Account 1: 8 downloads remaining  ✅
Account 2: 4 downloads remaining  ✅  
Account 3: 10 downloads remaining ✅
Total: 22 downloads available
```

### Book Search Sequence (20 books from Podpisnie.ru)

#### Books 1-8: Using Account 1
```
[1] "Семейный лексикон" → Account 1 (7 left)
[2] "Ирландские сказки" → Account 1 (6 left)
[3] "Из ничего" → Account 1 (5 left)
[4] "Развод" → Account 1 (4 left)
[5] "Курс" → Account 1 (3 left)
[6] "Семь лет в Крестах" → Account 1 (2 left)
[7] "Кадавры" → Account 1 (1 left)
[8] "Полторы комнаты" → Account 1 (0 left) ⚠️ EXHAUSTED
```

#### Book 9: AUTOMATIC SWITCH to Account 2
```
[9] "Невыносимая легкость бытия" 
    ❌ Account 1: 0 downloads (skip)
    ✅ Account 2: 4 downloads → SWITCH!
    Downloaded using Account 2 (3 left)
```

#### Books 10-12: Continue with Account 2
```
[10] "The Book" → Account 2 (2 left)
[11] "Мир образов" → Account 2 (1 left)
[12] "Тайна Моря" → Account 2 (0 left) ⚠️ EXHAUSTED
```

#### Book 13: AUTOMATIC SWITCH to Account 3
```
[13] "История одного немца"
    ❌ Account 1: 0 downloads (skip)
    ❌ Account 2: 0 downloads (skip)
    ✅ Account 3: 10 downloads → SWITCH!
    Downloaded using Account 3 (9 left)
```

#### Books 14-20: Continue with Account 3
```
[14] "Лисьи Броды" → Account 3 (8 left)
[15] "Дочь самурая" → Account 3 (7 left)
[16] "Другой дом" → Account 3 (6 left)
[17] "Истории книжных магазинов" → Account 3 (5 left)
[18] "Роза" → Account 3 (4 left)
[19] "У Плыли-Две-Птицы" → Account 3 (3 left)
[20] "Любовь в эпоху ненависти" → Account 3 (2 left)
```

### Final State
```
Account 1: 0 downloads (EXHAUSTED) ❌
Account 2: 0 downloads (EXHAUSTED) ❌
Account 3: 2 downloads remaining ✅
Total: 20/22 downloads used
Account switches: 2
```

## Implementation in Code

### Account Selection Logic
```python
# simple_book_search.py
for email, password in accounts:
    try:
        client = AsyncZlib()
        profile = await client.login(email, password)
        limits = await profile.get_limits()
        
        if limits.get('daily_remaining', 0) > 0:
            # Use this account
            search_results = await client.search(query)
            break
    except:
        # Try next account
        continue
```

### Key Features

1. **Transparent Switching**: User doesn't see which account is used
2. **Automatic Fallback**: When one exhausted, automatically tries next
3. **No Duplicate Attempts**: Skips already-exhausted accounts
4. **Graceful Degradation**: Works until all accounts exhausted

## Success Metrics

✅ **Account Switching**: Automatically switches when exhausted
✅ **Efficiency**: Uses accounts in order, maximizing downloads
✅ **Transparency**: API response doesn't expose account details
✅ **Resilience**: Continues working as long as any account has downloads

## API Response Example

```json
{
  "status": "success",
  "result": {
    "found": true,
    "epub_download_url": "/downloads/book.epub"
  },
  "service_used": "zlibrary"
  // Note: No indication of which account was used
}
```

## Error Handling

When all accounts exhausted:
```json
{
  "status": "error",
  "result": {
    "error": "search_failed",
    "message": "No working accounts found"
  }
}
```

## Account Reset

All accounts reset at midnight Moscow time (MSK):
- Account 1: 0:00 MSK → 8 downloads restored
- Account 2: 0:00 MSK → 4 downloads restored  
- Account 3: 0:00 MSK → 10 downloads restored

## Conclusion

The account switching strategy ensures:
1. **Maximum availability**: 22 books can be downloaded daily
2. **Automatic failover**: No manual intervention needed
3. **Clean API**: Users don't need to manage accounts
4. **Efficient usage**: Exhausts accounts sequentially