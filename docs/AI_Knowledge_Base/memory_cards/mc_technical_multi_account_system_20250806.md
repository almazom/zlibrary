# Memory Card: Multi-Account Pool System for Z-Library
---
id: mc_technical_multi_account_system_20250806
type: memory_card
category: technical
created: 2025-08-06
updated: 2025-08-07
status: active
priority: high
accounts_configured: 3
total_daily_capacity: 30
---

## System Overview
Intelligent multi-account management system that enables unlimited Z-Library accounts with automatic rotation when daily limits are reached. Multiplies download capacity linearly with number of accounts.

## Current Configuration (2025-08-07)
- **3 Active Accounts** configured and tested
- **30 downloads/day** total capacity (3 × 10)
- **All accounts verified** and working

### Configured Accounts
1. **Primary**: almazomam2@gmail.com (ZLOGIN/ZPASSW)
2. **Secondary**: almazomam@gmail.com (ZLOGIN1/ZPASSW1)  
3. **Tertiary**: almazomam3@gmail.com (ZLOGIN2/ZPASSW2)

## Core Components

### AccountPool Class
**Location**: `src/zlibrary/account_pool.py`
- Manages unlimited accounts
- Automatic failover on limit reached
- Persistent state in JSON config
- Health monitoring per account

### SmartDownloader Class
**Location**: `src/zlibrary/account_pool.py`
- Uses AccountPool for downloads
- Automatic account switching
- Rate limiting between requests
- Error recovery

### MultiAccountManager
**Location**: `multi_account_manager.py`
- High-level orchestration
- Telegram notifications
- Statistics tracking
- Multiple input methods

## Account Configuration Methods

### Method 1: Environment Variables (.env file)
```bash
# Primary account
ZLOGIN=almazomam2@gmail.com
ZPASSW=Alombk78!5

# Additional accounts
ZLOGIN1=almazomam@gmail.com
ZPASSW1=Alombk78!5

ZLOGIN2=almazomam3@gmail.com
ZPASSW2=Alombk78!5

# Add more as needed (up to ZLOGIN99/ZPASSW99)
ZLOGIN3=email3@example.com
ZPASSW3=password3
```

### Method 2: Text File
File: `accounts.txt`
```
email1@example.com:password1
email2@example.com:password2
email3@example.com:password3
```

### Method 3: Programmatic
```python
pool = AccountPool("accounts_config.json")
pool.add_account("email", "password", "notes")
```

## Key Features

### Automatic Rotation Logic
1. Check current account quota
2. If exhausted, rotate to next available
3. Round-robin through all accounts
4. Skip failed/inactive accounts
5. Notify when all exhausted

### Limit Multiplication
- **Formula**: Total = N accounts × 10 daily limit
- **Example**: 5 accounts = 50 downloads/day
- **Example**: 10 accounts = 100 downloads/day
- **No hardcoded upper limit**

### Account State Tracking
```json
{
  "email": "account@example.com",
  "daily_limit": 10,
  "daily_remaining": 7,
  "daily_used": 3,
  "reset_time": "5 hours",
  "is_active": true,
  "last_used": "2025-08-06T10:30:00"
}
```

## Usage Patterns

### Initialize Pool
```python
manager = MultiAccountManager()
await manager.add_accounts_from_env()
await manager.add_accounts_from_file("accounts.txt")
stats = await manager.initialize()
```

### Search with Rotation
```python
books = await manager.search_with_rotation(
    query="Python programming",
    max_results=50,
    extension="epub"
)
```

### Download with Failover
```python
results = await manager.download_with_rotation(
    books,
    output_dir="downloads"
)
# Automatically switches accounts when limits hit
```

## Error Handling

### Rate Limit Detection
- Monitors `daily_remaining` counter
- Detects "limit" in error messages
- Marks account as exhausted
- Rotates to next account

### Account Failures
- Tracks login failures per account
- Marks failed accounts as inactive
- Continues with remaining accounts
- Sends notification of failures

## Notifications System

### Telegram Alerts
- Account initialization status
- Low quota warnings (< 5 remaining)
- Account exhaustion notices
- Reset time information
- Download summaries

### Log File
- All notifications saved to `notifications.log`
- Timestamp for each message
- Useful for debugging

## Statistics Tracking

### Pool Statistics
```python
{
    'total_accounts': 5,
    'active_accounts': 4,
    'inactive_accounts': 1,
    'total_daily_limit': 40,
    'total_daily_remaining': 27,
    'total_daily_used': 13
}
```

### Download Statistics
- Total searches performed
- Total successful downloads
- Total failures
- Account usage distribution

## Configuration File

### Location
`accounts_config.json`

### Structure
```json
{
  "version": "1.0",
  "updated": "2025-08-06T12:00:00",
  "accounts": [
    {
      "email": "account1@example.com",
      "password": "password1",
      "daily_limit": 10,
      "daily_remaining": 7,
      "is_active": true,
      "notes": "Primary account"
    }
  ]
}
```

## Quick Start Commands

### Run Multi-Account Manager
```bash
python3 multi_account_manager.py
```

### Add Accounts via Environment
```bash
export ZLOGIN1="email1" ZPASSW1="pass1"
export ZLOGIN2="email2" ZPASSW2="pass2"
python3 multi_account_manager.py
```

### Monitor Limits
```python
await manager.monitor_limits()  # Runs every 5 minutes
```

## Advantages

1. **Linear Scaling**: Each account adds full daily limit
2. **No Downtime**: Automatic failover keeps downloads running
3. **Flexible Input**: Multiple ways to add accounts
4. **Persistent State**: Survives restarts
5. **Smart Rotation**: Uses accounts efficiently
6. **Real-time Monitoring**: Telegram notifications

## Limitations & Considerations

1. Each account needs valid Z-Library credentials
2. Accounts share same IP (consider proxy rotation)
3. Rate limiting (2 sec delay) between downloads
4. Account limits reset at different times
5. Failed logins may trigger security checks

## Future Enhancements

1. Proxy rotation per account
2. Account quality scoring
3. Predictive limit management
4. Web dashboard for monitoring
5. Automatic account creation
6. Integration with download queue