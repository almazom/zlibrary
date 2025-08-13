Feature: [FEATURE_NAME]
  As a [USER_TYPE]
  I want to [ACTION]
  So that [EXPECTED_OUTCOME]

  Background:
    Given I have authenticated Telegram user session "Клава Тех Поддержка"
    And the user session ID is "5282615364"
    And the target bot "@epub_toc_based_sample_bot" is accessible
    And MCP telegram-read-manager tool is available

  Scenario: Successful [SCENARIO_NAME]
    Given [INITIAL_CONDITIONS]
    When I [USER_ACTION]
    Then I should [EXPECTED_RESPONSE]
    And [ADDITIONAL_VALIDATION]
    And the test should display step-by-step progress with emojis
    And the final result should be marked as PASSED

  Scenario: [ERROR_SCENARIO_NAME]
    Given [ERROR_CONDITIONS]
    When I [USER_ACTION]
    Then I should [ERROR_RESPONSE]
    And [ERROR_VALIDATION]
    And the final result should be marked as FAILED

  # AI Learning Notes:
  # Replace [PLACEHOLDERS] with specific test details
  # Follow the pattern: Background → Happy Path → Error Path
  # Always include step-by-step progress and emoji feedback