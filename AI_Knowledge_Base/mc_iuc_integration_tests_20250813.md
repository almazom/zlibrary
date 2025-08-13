# Memory Card: IUC Integration Tests Architecture

**Created**: 2025-08-13  
**Category**: Integration Testing  
**Status**: Active  
**Author**: Claude Code Assistant  

## Overview

IUC (Integration User Cases) represent a new testing paradigm that implements complete feedback loops for Telegram bot interactions. Unlike traditional unit tests, IUC tests simulate real user behavior and validate actual bot responses.

## Core Concept

### Traditional Testing vs IUC Testing

**Traditional Approach:**
- Send API requests to bot
- Mock responses
- No real feedback validation

**IUC Approach:**
- Use authenticated user session (identical to manual typing)
- Send messages to bot via Telegram
- Read actual bot responses using telegram tools
- Validate complete feedback loop

## Architecture Components

### 1. User Session Integration
- **File**: `telegram_bot/stable_unified_session.py`
- **Purpose**: Authenticated Telegram user session for message sending
- **Key Feature**: 100% identical to manual user typing
- **Session Management**: String-based session for corruption resistance

### 2. Message Reading Tools
- **Primary**: `/home/almaz/MCP/SCRIPTS/telegram-read-manager.sh`
- **Fallback**: Python Telethon client for message retrieval
- **Function**: Read bot responses for validation

### 3. Response Validation
- **Pattern Matching**: Validate expected response content
- **Timing Validation**: Ensure responses within acceptable timeframes
- **File Delivery**: Verify EPUB files sent by bot

## IUC Test Structure

### Test Naming Convention
- **IUC01**: Basic commands (e.g., /start)
- **IUC02**: Single book search with EPUB delivery
- **IUC03**: Multi-book batch processing
- **IUC04**: Error handling scenarios
- **IUC05**: Concurrent request handling

### Standard Test Flow
```bash
1. Check user session authentication
2. Send command/message via user session
3. Wait for bot processing (typically 5-10 seconds)
4. Read bot response using telegram tools
5. Validate response content and timing
6. Generate timestamped report with Moscow timezone
```

## Implementation Details

### Core Functions Template
```bash
# Send message using authenticated session
send_user_message() {
    python3 -c "
from telethon.sync import TelegramClient
with TelegramClient('session_file', API_ID, 'API_HASH') as client:
    message = client.send_message('@bot_username', '$message')
    print(f'SUCCESS:{message.id}')
"
}

# Read bot response
read_bot_response() {
    if command -v /home/almaz/MCP/SCRIPTS/telegram-read-manager.sh &>/dev/null; then
        /home/almaz/MCP/SCRIPTS/telegram-read-manager.sh --bot "@bot" --last 1
    else
        # Python fallback
        python3 -c "..."
    fi
}

# Validate response
validate_response() {
    local response="$1"
    local expected="$2"
    if [[ "$response" == *"$expected"* ]]; then
        echo "✅ PASS"
        return 0
    else
        echo "❌ FAIL"
        return 1
    fi
}
```

### Configuration Requirements
- **Bot Username**: `epub_toc_based_sample_bot`
- **User ID**: `14835038`
- **API Credentials**: `API_ID` and `API_HASH`
- **Session File**: Authenticated user session file
- **Timezone**: Moscow (Europe/Moscow)

## Success Criteria

### IUC01 (Start Command)
- Message sent successfully via user session
- Bot response received within 10 seconds
- Response contains: "📚 Welcome to Book Search Bot!"
- Full logs with Moscow timestamps

### Future IUC Tests
- **IUC02**: EPUB file delivery validation
- **IUC03**: Batch processing reliability
- **IUC04**: Error recovery mechanisms
- **IUC05**: Performance under load

## Benefits

1. **Real-World Validation**: Tests actual user experience
2. **Complete Feedback Loop**: Validates entire pipeline
3. **No Mocking**: Tests real bot responses
4. **Automation**: Scalable for CI/CD integration
5. **Debugging**: Clear logs for troubleshooting

## Git Integration

### Branch Strategy
- **Development**: `feat/iuc-integration-tests`
- **Commits**: Atomic commits per IUC test
- **Documentation**: Memory cards updated per test

### File Organization
```
tests/
├── IUC01_start_command_feedback.sh
├── IUC02_book_search_complete_cycle.sh
├── lib/
│   ├── iuc_common.sh           # Shared functions
│   ├── telegram_reader.py      # Response reading
│   └── validate_response.sh    # Validation logic
└── run_iuc_suite.sh           # Test runner
```

## References

- **Base Test**: `telegram_bot/UC24_user_session_book_search_test.sh`
- **Session Management**: `telegram_bot/stable_unified_session.py`
- **Authentication**: `telegram_bot/authenticate_step_by_step.py`
- **Documentation**: `telegram_bot/STABLE_SESSION_SUCCESS_SUMMARY.md`

---

**Last Updated**: 2025-08-13 08:02 MSK  
**Next Action**: Implement IUC01 test for /start command validation