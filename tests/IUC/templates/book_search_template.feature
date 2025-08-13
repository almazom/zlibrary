Feature: Book Search and EPUB Delivery
  As a book reader
  I want to search for books by title
  So that I receive EPUB files for download

  Background:
    Given I have authenticated Telegram user session "Клава Тех Поддержка"
    And the user session ID is "5282615364"
    And the target bot "@epub_toc_based_sample_bot" is accessible
    And MCP telegram-read-manager tool is available
    And the book search system is operational

  Scenario: Successful book search and delivery
    Given the bot is running and responsive
    And I have sufficient download quota
    When I send book title "[BOOK_TITLE]" to the bot
    Then I should receive a progress message "🔍 Searching for book..." within 10 seconds
    And I should receive an EPUB file within 30 seconds
    And I should receive a success confirmation message
    And the test should validate file delivery
    And the final result should be marked as PASSED

  Scenario: Book not found
    Given the bot is running and responsive
    When I send an invalid book title "[INVALID_BOOK]" to the bot
    Then I should receive a progress message within 10 seconds
    And I should receive an error message "No books found" within 30 seconds
    And no EPUB file should be delivered
    And the final result should be marked as FAILED

  Scenario: Rate limit exceeded
    Given I have exceeded my daily download limit
    When I send book title "[BOOK_TITLE]" to the bot
    Then I should receive a rate limit message within 10 seconds
    And the message should include quota reset information
    And no EPUB file should be delivered
    And the final result should be marked as FAILED

  # AI Learning Notes:
  # Book search tests follow: Send → Progress → Delivery → Confirmation
  # Always validate timing: Progress (5-10s), Delivery (15-30s)
  # Include error scenarios: Not found, Rate limits, System errors