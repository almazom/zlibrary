# UC9: Account Health Monitoring Test Cases

## Feature: Monitor and Report Account Status with Smart Fallback
As a system managing multiple accounts
I want to monitor account health and switch intelligently
So that downloads continue even when accounts are exhausted

## Scenario 1: Account Status Check
**Given** 3 Z-Library accounts configured
**When** I check account status
**Then** System should report:
  - Downloads remaining per account
  - Total downloads available
  - Reset time for each account
  - Account health status

### Test Cases:
```bash
# Test 1.1: Check all accounts
./scripts/book_search.sh --check-accounts
# Expected: JSON with all account statuses

# Test 1.2: Check specific account
./scripts/book_search.sh --check-account 1
# Expected: Status for account #1

# Test 1.3: Summary view
./scripts/book_search.sh --account-summary
# Expected: "Total: 22 downloads (8+4+10)"
```

## Scenario 2: Automatic Account Switching
**Given** First account exhausted
**When** Searching for a book
**Then** System should:
  - Detect account has 0 downloads
  - Switch to next account automatically
  - Log which account was used
  - Continue until all exhausted

### Test Cases:
```bash
# Test 2.1: Exhaust first account
# Download 8 books with account 1
for i in {1..8}; do
    ./scripts/book_search.sh "Book $i"
done
# 9th download should use account 2

# Test 2.2: Track account usage
./scripts/book_search.sh "Test Book" --verbose
# Expected: Shows "Using account 2 (4 downloads remaining)"
```

## Scenario 3: All Accounts Exhausted
**Given** All accounts have 0 downloads
**When** Trying to download
**Then** System should:
  - Report all accounts exhausted
  - Show when limits reset (timezone aware)
  - Suggest waiting or manual download
  - NOT fail silently

### Test Cases:
```bash
# Test 3.1: Exhausted state
./scripts/book_search.sh "Book"
# Expected: {
#   "status": "exhausted",
#   "message": "All accounts exhausted",
#   "reset_times": {
#     "account1": "2025-08-09 00:00 MSK",
#     "account2": "2025-08-09 00:00 MSK",
#     "account3": "2025-08-09 00:00 MSK"
#   }
# }
```

## Implementation:

### 1. Account Health Check Script
```python
async def check_all_accounts():
    accounts_status = []
    total_available = 0
    
    for i, (email, password) in enumerate(accounts):
        try:
            client = AsyncZlib()
            profile = await client.login(email, password)
            limits = await profile.get_limits()
            
            status = {
                "account_id": i + 1,
                "email": email.split('@')[0] + "@...",  # Privacy
                "daily_remaining": limits.get('daily_remaining', 0),
                "daily_limit": limits.get('daily_allowed', 0),
                "reset_time": limits.get('daily_reset', 'unknown'),
                "status": "healthy" if limits.get('daily_remaining', 0) > 0 else "exhausted"
            }
            
            total_available += status['daily_remaining']
            accounts_status.append(status)
            
            await client.logout()
        except Exception as e:
            accounts_status.append({
                "account_id": i + 1,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "total_downloads": total_available,
        "accounts": accounts_status,
        "timestamp": datetime.now().isoformat()
    }
```

### 2. Smart Account Selection
```python
async def get_best_account():
    """Select account with most downloads remaining"""
    best_account = None
    max_downloads = 0
    
    for email, password in accounts:
        try:
            client = AsyncZlib()
            profile = await client.login(email, password)
            limits = await profile.get_limits()
            remaining = limits.get('daily_remaining', 0)
            
            if remaining > max_downloads:
                max_downloads = remaining
                best_account = (email, password, remaining)
            
            await client.logout()
        except:
            continue
    
    return best_account
```

### 3. Account Rotation Strategy
```python
ACCOUNT_USAGE = {
    'almazomam@gmail.com': {'used': 0, 'limit': 8},
    'almazomam2@gmail.com': {'used': 0, 'limit': 4},
    'almazomam3@gmail.com': {'used': 0, 'limit': 10}
}

def select_next_account():
    # Round-robin with weights based on limits
    for email, stats in ACCOUNT_USAGE.items():
        if stats['used'] < stats['limit']:
            return email
    return None
```

## Scenario 4: Reset Time Tracking
**Given** Accounts reset at midnight Moscow time
**When** Approaching reset time
**Then** System should:
  - Calculate time until reset
  - Show countdown
  - Auto-retry after reset

### Test Cases:
```bash
# Test 4.1: Time until reset
./scripts/book_search.sh --time-to-reset
# Expected: "Resets in 5h 23m (00:00 MSK)"

# Test 4.2: Timezone handling
TZ=UTC ./scripts/book_search.sh --check-accounts
# Expected: Shows times in UTC

# Test 4.3: Auto-wait for reset
./scripts/book_search.sh --wait-for-reset "Book"
# Expected: Waits until 00:00 MSK, then downloads
```

## Scenario 5: Account Failure Handling
**Given** Account login fails
**When** During search
**Then** System should:
  - Mark account as failed
  - Try next account
  - Report which accounts work
  - Continue with working accounts

### Test Cases:
```bash
# Test 5.1: One account fails
# Simulate by changing password
./scripts/book_search.sh "Book" --verbose
# Expected: "Account 1 failed, using account 2"

# Test 5.2: Multiple failures
# Expected: Uses last working account
```

## Monitoring Dashboard:
```bash
#!/bin/bash
# account_monitor.sh - Real-time account status

while true; do
    clear
    echo "=== Z-Library Account Status ==="
    echo "Time: $(date '+%Y-%m-%d %H:%M:%S MSK')"
    echo ""
    
    result=$(./scripts/book_search.sh --check-accounts)
    
    echo "Total Available: $(echo "$result" | jq -r '.total_downloads')"
    echo ""
    echo "Accounts:"
    echo "$result" | jq -r '.accounts[] | 
        "[\(.account_id)] \(.email): \(.daily_remaining)/\(.daily_limit) - \(.status)"'
    
    echo ""
    echo "Next reset: $(echo "$result" | jq -r '.accounts[0].reset_time')"
    
    sleep 60
done
```

## Success Metrics:
- ✅ Zero failed downloads due to account issues
- ✅ Automatic failover < 2 seconds
- ✅ Clear status reporting
- ✅ Timezone-aware reset tracking
- ✅ Graceful degradation when accounts fail

## Configuration:
```yaml
# ~/.zlibrary/accounts.yaml
accounts:
  - email: almazomam@gmail.com
    password: encrypted_pass
    priority: 1
    
  - email: almazomam2@gmail.com
    password: encrypted_pass
    priority: 2
    
  - email: almazomam3@gmail.com
    password: encrypted_pass
    priority: 3

settings:
  rotation_strategy: round_robin  # or 'least_used', 'most_available'
  retry_failed: true
  reset_timezone: Europe/Moscow
```