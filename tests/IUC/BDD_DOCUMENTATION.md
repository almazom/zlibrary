# BDD (Behavior-Driven Development) Documentation for IUC Tests

**Version**: 1.0.0  
**Created**: 2025-08-13 MSK  
**Framework**: Gherkin-style BDD with Bash implementation  
**Purpose**: Define behavior specifications for Integration User Cases

## 🎯 BDD Philosophy for IUC Tests

### Behavior-Driven Integration Testing
BDD in the context of IUC (Integration User Cases) focuses on validating real user behaviors and system responses through actual Telegram interactions. Each test scenario represents a complete user journey from message sending to response validation.

### Three Amigos Approach
- **Product Owner**: Defines expected bot behaviors and user experiences
- **Developer**: Implements bot functionality and integration points  
- **QA/Tester**: Creates IUC tests validating end-to-end behavior

## 📋 BDD Template Structure

### Standard IUC Test Scenario Format
```gherkin
Feature: [Integration Feature Name]
  As a [User Type]
  I want to [Perform Action]  
  So that [Expected Outcome]

  Background:
    Given I have an authenticated Telegram user session
    And the target bot is running and accessible
    And all required tools are available

  Scenario: [Specific Test Case]
    Given [Initial Conditions]
    When [User Actions]
    Then [Expected System Response]
    And [Additional Validations]
```

## 🧪 IUC01: Start Command BDD Specification

### Feature Definition
```gherkin
Feature: Bot Start Command Integration
  As a Telegram user
  I want to send /start command to the book search bot
  So that I receive a welcome message with usage instructions

  Background:
    Given I have an authenticated Telegram user session "Клава Тех Поддержка"
    And the user session is valid with ID "5282615364"  
    And the target bot "@epub_toc_based_sample_bot" is accessible
    And MCP telegram-read-manager tool is available
    And Python Telethon library is installed

  Scenario: Successful start command interaction
    Given the bot is running and responsive
    When I send "/start" message to "@epub_toc_based_sample_bot"
    Then I should receive a message within 10 seconds
    And the response should contain "📚 Welcome to Book Search Bot"
    And the response should include usage instructions
    And the test should display step-by-step progress with emojis
    And the final result should be marked as PASSED

  Scenario: Bot not responding to start command  
    Given the bot is not running or not responsive
    When I send "/start" message to "@epub_toc_based_sample_bot"
    Then I should wait 5 seconds for a response
    And no bot response should be detected
    And the test should display "No bot response found in recent messages"
    And the validation should fail with clear error message
    And the final result should be marked as FAILED

  Scenario: Authentication failure
    Given the user session is invalid or expired
    When I attempt to send "/start" message
    Then the authentication check should fail
    And the test should display "User session not authenticated"
    And the test should exit with error code 1
    And no message should be sent to the bot
```

### Implementation Mapping
```bash
# BDD Step Implementations in IUC01_start_command_feedback.sh

# Background: Given I have an authenticated Telegram user session
check_authentication() {
    # Validates StringSession with Telegram API
    # Confirms user identity and permissions
}

# When I send "/start" message to "@epub_toc_based_sample_bot"  
send_start_command() {
    # Sends message via authenticated user session
    # Captures message ID and timestamp
    # 100% identical to manual typing
}

# Then I should receive a message within 10 seconds
read_bot_response() {
    # Waits configurable time for bot response
    # Uses MCP telegram-read-manager tool
    # Falls back to Python Telethon if needed
}

# And the response should contain "📚 Welcome to Book Search Bot"
validate_response() {
    # Pattern matching against expected response
    # Rich reporting with expected vs actual
    # Clear pass/fail indication
}
```

## 🔄 Future IUC02: Book Search BDD Specification

### Feature Definition
```gherkin
Feature: Book Search Integration  
  As a Telegram user
  I want to search for books by title
  So that I receive EPUB files for requested books

  Background:
    Given I have an authenticated Telegram user session
    And the book search bot is running
    And the Z-Library backend is accessible
    And I have sufficient download quota

  Scenario: Successful book search and delivery
    Given I am authenticated with the book search bot
    When I send "Clean Code Robert Martin" to the bot
    Then I should receive a progress message "🔍 Searching for book..."
    And I should receive an EPUB file within 30 seconds
    And I should receive a success confirmation message
    And the test should validate file delivery

  Scenario: Book not found  
    Given I am authenticated with the book search bot
    When I send "NonExistentBookTitle123456" to the bot
    Then I should receive a progress message "🔍 Searching for book..."
    And I should receive an error message within 30 seconds
    And the error message should contain "No books found"
    And no EPUB file should be delivered

  Scenario: Rate limit exceeded
    Given I have exceeded my daily download limit
    When I send "Python Programming" to the bot
    Then I should receive a rate limit message
    And the message should include quota reset information
    And no EPUB file should be delivered
```

## 📊 BDD Implementation Patterns

### Test Structure Pattern
```bash
#!/bin/bash
# IUC Test Template following BDD principles

# Feature: [Feature Name]
# Background conditions setup
setup_background() {
    check_authentication
    verify_tools_available
    configure_test_environment
}

# Scenario: [Scenario Name]  
execute_scenario() {
    # Given: Initial conditions
    setup_given_conditions
    
    # When: User actions
    perform_user_actions
    
    # Then: Expected outcomes
    validate_expected_outcomes
    
    # And: Additional validations
    perform_additional_validations
}

# Cleanup and reporting
cleanup_and_report() {
    generate_bdd_report
    cleanup_test_artifacts
}
```

### Rich Feedback Implementation
```bash
# BDD-style logging with emojis and structured output
log_given() { echo -e "${BLUE}[GIVEN]${NC} $1"; }
log_when() { echo -e "${YELLOW}[WHEN]${NC} $1"; }  
log_then() { echo -e "${GREEN}[THEN]${NC} $1"; }
log_and() { echo -e "${CYAN}[AND]${NC} $1"; }
log_scenario() { echo -e "${PURPLE}[SCENARIO]${NC} $1"; }
```

## 🎛️ BDD Configuration Management

### Scenario-Specific Configuration
```bash
# IUC01 BDD Configuration
declare -A IUC01_CONFIG=(
    ["feature"]="Bot Start Command Integration"
    ["user_type"]="Telegram user"
    ["action"]="send /start command"
    ["outcome"]="receive welcome message"
    ["timeout"]="10"
    ["expected_pattern"]="📚 Welcome to Book Search Bot"
)

# IUC02 BDD Configuration  
declare -A IUC02_CONFIG=(
    ["feature"]="Book Search Integration"
    ["user_type"]="Book searcher"
    ["action"]="search for books"
    ["outcome"]="receive EPUB files"
    ["timeout"]="30"
    ["expected_pattern"]="EPUB file delivered"
)
```

### Test Data Management
```bash
# BDD Test Data for different scenarios
declare -A BDD_TEST_DATA=(
    # Success scenarios
    ["valid_book_title"]="Clean Code Robert Martin"
    ["expected_welcome"]="📚 Welcome to Book Search Bot"
    ["progress_message"]="🔍 Searching for book..."
    
    # Error scenarios  
    ["invalid_book"]="NonExistentBookTitle123456"
    ["rate_limit_message"]="Daily download limit exceeded"
    ["no_books_found"]="No books found for your search"
)
```

## 📈 BDD Metrics and Reporting

### Scenario Execution Metrics
```bash
# BDD execution tracking
declare -A BDD_METRICS=(
    ["total_scenarios"]=0
    ["passed_scenarios"]=0  
    ["failed_scenarios"]=0
    ["skipped_scenarios"]=0
    ["execution_time"]=0
)

# Update metrics during test execution
update_bdd_metrics() {
    local status=$1  # PASSED/FAILED/SKIPPED
    ((BDD_METRICS["total_scenarios"]++))
    ((BDD_METRICS["${status,,}_scenarios"]++))
}
```

### BDD Report Generation
```bash
generate_bdd_report() {
    cat << EOF
🎯 BDD TEST EXECUTION REPORT
============================
Feature: ${IUC_CONFIG["feature"]}
Execution Time: $(get_timestamp)

SCENARIO RESULTS:
----------------
Total Scenarios: ${BDD_METRICS["total_scenarios"]}
✅ Passed: ${BDD_METRICS["passed_scenarios"]}  
❌ Failed: ${BDD_METRICS["failed_scenarios"]}
⏭️ Skipped: ${BDD_METRICS["skipped_scenarios"]}

SUCCESS RATE: $((BDD_METRICS["passed_scenarios"] * 100 / BDD_METRICS["total_scenarios"]))%

DETAILED RESULTS:
$(format_scenario_details)
============================
EOF
}
```

## 🔄 BDD Best Practices for IUC Tests

### 1. Scenario Independence
- Each scenario should be independent and executable in isolation
- No dependencies between scenarios
- Clean setup and teardown for each test

### 2. Real-World Language  
- Use business language, not technical implementation details
- Focus on user behaviors and outcomes
- Avoid technical jargon in scenario descriptions

### 3. Comprehensive Coverage
- Include happy path scenarios (successful interactions)
- Cover error scenarios (failures, invalid inputs)
- Test edge cases (rate limits, timeouts, network issues)

### 4. Rich Feedback
- Provide step-by-step progress indication
- Use emojis and colors for visual clarity
- Include timing and performance metrics

### 5. Maintainability
- Keep scenarios focused and concise
- Use shared step definitions across tests
- Maintain clear separation between BDD specification and implementation

## 🚀 BDD Evolution Roadmap

### Phase 1: Foundation (COMPLETED ✅)
- ✅ BDD template structure established
- ✅ IUC01 BDD specification complete
- ✅ Rich feedback implementation
- ✅ Integration with bash testing framework

### Phase 2: Expansion (NEXT)
- 🔄 IUC02 BDD specification and implementation
- 🔄 Shared BDD step library development
- 🔄 Cross-scenario data management
- 🔄 Performance benchmarking integration

### Phase 3: Advanced BDD Features (FUTURE)
- 🔄 Scenario outline support for data-driven testing
- 🔄 BDD report dashboard with visual metrics
- 🔄 Integration with external BDD tools (Cucumber, SpecFlow)
- 🔄 Automated scenario generation from user stories

---

**Conclusion**: BDD implementation in IUC tests provides clear, business-focused specifications that drive real integration testing. The combination of Gherkin-style scenarios with bash implementation creates maintainable, understandable tests that validate actual user behaviors.

**Next Steps**: Implement IUC02 following the established BDD patterns, expanding the shared step library and enhancing reporting capabilities.