Feature: Russian Bookstore URL Extraction and High-Confidence Book Search
  As a test automation system
  I want to extract book metadata from Russian bookstore URLs using Claude AI
  So that I can validate end-to-end book search with 80%+ confidence accuracy

  Background:
    Given I have authenticated Telegram user session
    And the book search system is operational
    And the Claude AI extraction service is available

  @critical @atomic
  Scenario: Successful Russian bookstore extraction and EPUB delivery
    Given I have a pool of Russian bookstore URLs
    When I select a random bookstore URL
    And I extract book metadata using Claude AI with WebFetch
    And the extracted book has not been processed today
    And the extraction confidence is above 80%
    Then I should get valid book metadata with title and author
    When I search for the extracted book using book_search.sh
    Then I should receive a progress message within 10 seconds
    And I should receive an EPUB file within 30 seconds
    And the delivered EPUB should match the extracted book metadata
    And I should save the extracted book to daily tracking file

  # Error scenarios handled by mixed resilience strategy
  @error-recovery
  Scenario: Claude extraction failure with bookstore retry
    Given I have a pool of Russian bookstore URLs
    When I select a random bookstore URL
    And Claude AI extraction fails
    Then I should retry with up to 2 different bookstore URLs
    And if any extraction succeeds with 80%+ confidence
    Then the test should continue with successful book search flow

  @validation
  Scenario: Book metadata quality validation
    Given I have extracted book metadata from Russian bookstore
    When I validate the metadata quality
    Then the title should not be empty or generic
    And the author should not be empty or generic
    And the extraction confidence should be at least 80%
    And the book should not be a duplicate from today's extractions

  # Acceptance Criteria:
  # - One book extraction per test run (atomic)
  # - Retry extraction up to 3 attempts with different stores
  # - Track duplicates by title+author per day
  # - Require 80%+ confidence for book metadata
  # - Full validation: metadata → search → EPUB delivery
  # - Mixed error handling: retry extraction, fail fast on search, retry delivery
  # - Support 10 Russian bookstores from commercial to independent