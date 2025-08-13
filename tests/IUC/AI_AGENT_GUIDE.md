# IUC Test Creation Guide for AI Agents

**Version**: 1.0.0  
**Target**: AI Agents creating new IUC tests  
**Pattern**: Gherkin-First BDD Development  

## 🤖 Quick Start for AI Agents

### Step 1: Analyze Requirements
```
User Request: "Create test for [FUNCTIONALITY]"
↓
Identify test type: basic | book_search | error_handling
↓
Choose appropriate template
```

### Step 2: Start with Gherkin Feature
```bash
# Copy appropriate template
cp templates/[TYPE]_template.feature features/IUC[NN]_[NAME].feature

# Customize for specific test:
# - Replace [PLACEHOLDERS] with actual values
# - Define user story (As a... I want... So that...)
# - Add scenarios (happy path + error paths)
```

### Step 3: Implement Bash Test
```bash
# Copy corresponding bash template
cp templates/[TYPE]_template.sh IUC[NN]_[NAME].sh

# Map Gherkin steps to bash functions:
# "Given I have authenticated session" → given_I_have_authenticated_session()
# "When I send book title" → when_I_send_book_title()
# "Then I should receive EPUB" → then_I_should_receive_EPUB()
```

## 📚 Shared Library Reference

### ALWAYS Use These Functions
```bash
# Step 1: Authentication (REQUIRED for all tests)
authenticate_user_session()          # Returns 0 if successful
verify_test_environment()            # Checks tools availability

# Step 2: Action (choose based on test type)
send_message_to_bot(message, bot)    # Generic message sending
send_start_command(bot)              # For /start commands
send_book_search(title, bot)         # For book searches

# Step 3: Response Reading (choose based on expected response)
read_bot_response(timeout, type)     # Generic response reading
read_progress_message(timeout)       # For "🔍 Searching..." messages  
read_epub_delivery(timeout)          # For file delivery

# Step 4: Validation (REQUIRED for all tests)
validate_response(actual, expected, type)  # Smart validation with auto-detection
validate_timing(start_time, max_sec)       # Response time validation

# Step 5: Reporting (REQUIRED for all tests)
generate_test_report(name, status, details)  # Standard test reports
```

## 🎯 Test Types and Patterns

### Type 1: Basic Command Tests (like IUC01)
```gherkin
Feature: [Command] Integration
  As a Telegram user
  I want to send [command] to bot
  So that I receive [expected response]

Scenario: Successful [command] execution
  When I send "[command]" to bot
  Then I should receive "[expected]" within [N] seconds
```

```bash
# Implementation pattern:
given_I_have_authenticated_session() { authenticate_user_session; }
when_I_send_[command]() { send_message_to_bot "[command]" "$TARGET_BOT"; }
then_I_should_receive_[response]() { 
    response=$(read_bot_response 10)
    validate_response "$response" "[expected]" "auto"
}
```

### Type 2: Book Search Tests (like IUC02)
```gherkin
Feature: Book Search Integration
  As a book reader
  I want to search for books
  So that I receive EPUB files

Scenario: Successful book search
  When I send book title "[title]"
  Then I should receive progress message within 10 seconds
  And I should receive EPUB file within 30 seconds
```

```bash
# Implementation pattern:
when_I_send_book_title() {
    send_book_search "$1" "$TARGET_BOT"
}
then_I_should_receive_progress_message() {
    response=$(read_progress_message 10)
    validate_response "$response" "🔍 Searching" "progress"
}
then_I_should_receive_EPUB_file() {
    response=$(read_epub_delivery 30)
    validate_response "$response" "file" "file"
}
```

### Type 3: Error Handling Tests
```gherkin
Feature: Error Handling
  As a user
  I want to receive clear error messages
  So that I understand what went wrong

Scenario: Invalid input handling
  When I send invalid input "[invalid]"
  Then I should receive error message within 10 seconds
```

```bash
# Implementation pattern:
when_I_send_invalid_input() {
    send_message_to_bot "$1" "$TARGET_BOT"
}
then_I_should_receive_error_message() {
    response=$(read_bot_response 10)
    validate_response "$response" "error" "error"
}
```

## 🔧 Function Naming Conventions

### Gherkin Step → Function Mapping
```
"Given I have authenticated session" → given_I_have_authenticated_session()
"Given the bot is running" → given_the_bot_is_running()
"When I send message X" → when_I_send_message_X()
"When I send book title" → when_I_send_book_title()
"Then I should receive Y" → then_I_should_receive_Y()
"Then I should receive EPUB file" → then_I_should_receive_EPUB_file()
"And the response should contain Z" → and_the_response_should_contain_Z()
```

### Parameter Handling
```bash
# Use parameters for dynamic values
when_I_send_book_title() {
    local book_title="$1"
    send_book_search "$book_title" "$TARGET_BOT"
}

# Use defaults for common cases
then_I_should_receive_response_within_N_seconds() {
    local timeout="${1:-10}"
    local response=$(read_bot_response "$timeout")
}
```

## 🎨 Rich UI Patterns (REQUIRED)

### Always Include These Logging Patterns
```bash
# Use appropriate log functions
log_given "🔐 GIVEN: Authentication setup"
log_when "📤 WHEN: Sending message to bot"  
log_then "✅ THEN: Validating response"

# Show progress with emojis
log_step "🧪 SCENARIO: Testing start command"
log_info "⏰ Timestamp: $(get_timestamp)"
log_success "✅ Message sent successfully"
log_error "❌ Validation failed"

# Always show expected vs actual
log_info "Expected: '$expected_pattern'"
log_info "Actual: '$actual_response'"
```

## ⚡ Quick Generation Commands

### For AI Agents to Bootstrap Tests
```bash
# Generate new test structure
generate_iuc_test() {
    local test_number="$1"
    local test_name="$2"
    local test_type="${3:-basic}"  # basic|book_search|error_handling
    
    # Copy appropriate templates
    cp "templates/${test_type}_template.feature" "features/IUC${test_number}_${test_name}.feature"
    cp "templates/${test_type}_template.sh" "IUC${test_number}_${test_name}.sh"
    
    # Make executable
    chmod +x "IUC${test_number}_${test_name}.sh"
    
    echo "✅ Generated IUC${test_number} skeleton - ready for customization"
}

# Usage examples:
# generate_iuc_test "02" "book_search" "book_search"
# generate_iuc_test "03" "error_handling" "error_handling"
# generate_iuc_test "04" "batch_processing" "basic"
```

## 🔍 Validation Guidelines

### Smart Validation Type Selection
```bash
# Let validate_response() auto-detect type:
validate_response "$response" "📚 Welcome" "auto"          # → welcome type
validate_response "$response" "🔍 Searching" "auto"        # → progress type  
validate_response "$response" "file delivered" "auto"      # → file type
validate_response "$response" "error occurred" "auto"      # → error type

# Or specify explicitly:
validate_response "$response" "pattern" "welcome"
validate_response "$response" "pattern" "progress"
validate_response "$response" "pattern" "file"
validate_response "$response" "pattern" "error"
```

### Timing Validation
```bash
# Always validate response timing
IUC_TEST_START_TIME=$(get_epoch)
# ... perform action ...
validate_timing "$IUC_TEST_START_TIME" 30  # Max 30 seconds
```

## 📋 Quality Checklist

### Before Submitting New IUC Test
- [ ] Gherkin feature file created with user story
- [ ] Bash implementation maps all Gherkin steps to functions  
- [ ] Uses shared library functions (authenticate_user_session, etc.)
- [ ] Includes rich UI with emoji feedback
- [ ] Has comprehensive --help documentation
- [ ] Validates both content and timing
- [ ] Generates standard test report
- [ ] Follows naming conventions
- [ ] Includes error scenarios
- [ ] Has GHERKIN_MAPPING comments in bash file

## 🚀 Example: Creating IUC02 Book Search Test

### 1. Feature File (features/IUC02_book_search.feature)
```gherkin
Feature: Book Search and EPUB Delivery
  As a book reader
  I want to search for books by title
  So that I receive EPUB files

  Background:
    Given I have authenticated Telegram user session

  Scenario: Successful book search
    When I send book title "Clean Code Robert Martin"
    Then I should receive progress message within 10 seconds
    And I should receive EPUB file within 30 seconds
```

### 2. Bash Implementation (IUC02_book_search.sh)
```bash
#!/bin/bash
# IUC02: Book Search Integration Test
# Generated from: features/IUC02_book_search.feature

source "lib/iuc_patterns.sh"

# GHERKIN_MAPPING:
# "When I send book title {string}" → when_I_send_book_title()
# "Then I should receive progress message within {int} seconds" → then_I_should_receive_progress_message_within_N_seconds()

when_I_send_book_title() {
    local book_title="$1"
    log_when "📚 WHEN: Sending book title '$book_title'"
    send_book_search "$book_title" "$TARGET_BOT"
}

then_I_should_receive_progress_message_within_N_seconds() {
    local timeout="$1"
    log_then "🔍 THEN: Expecting progress message within ${timeout}s"
    
    local response=$(read_progress_message "$timeout")
    validate_response "$response" "🔍 Searching" "progress"
}

# ... rest of implementation following patterns
```

---

**Remember**: Follow IUC01 as the golden standard. When in doubt, check how IUC01 implements authentication, validation, and reporting patterns! 🌟