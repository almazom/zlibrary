Feature: Bot Start Command Integration
  As a Telegram user
  I want to send /start command to the book search bot
  So that I receive a welcome message with usage instructions

  Background:
    Given I have authenticated Telegram user session "Клава Тех Поддержка"
    And the user session ID is "5282615364"
    And the target bot "@epub_toc_based_sample_bot" is accessible
    And MCP telegram-read-manager tool is available

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

  Scenario: Authentication failure before start command
    Given the user session is invalid or expired
    When I attempt to send "/start" message
    Then the authentication check should fail
    And the test should display "User session not authenticated"
    And the test should exit with error code 1
    And no message should be sent to the bot

  # AI Learning Examples: These scenarios show common patterns
  # Pattern 1: Happy path with expected response
  # Pattern 2: System failure with graceful error handling  
  # Pattern 3: Authentication failure with early exit