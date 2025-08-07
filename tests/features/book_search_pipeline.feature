# BDD Feature Specification: Multi-Source Book Search Pipeline
# Using Gherkin syntax for behavior-driven development

Feature: Multi-Source Book Search with Fallback Chain
  As a book searcher
  I want to find books across multiple sources with intelligent fallback
  So that I have the highest chance of finding any book I'm looking for

  Background:
    Given the book search pipeline is initialized
    And Claude SDK normalization is available
    And Z-Library source is configured
    And Flibusta source is configured

  Scenario: Successful search with primary source
    Given the fallback chain is configured as ["zlibrary", "flibusta"]
    When I search for "1984 George Orwell"
    And Z-Library finds the book
    Then the result should be successful
    And the source should be "zlibrary"
    And Flibusta should not be queried

  Scenario: Fallback to secondary source on primary failure
    Given the fallback chain is configured as ["zlibrary", "flibusta"]
    When I search for "Маленький принц"
    And Z-Library does not find the book
    And Flibusta finds the book
    Then the result should be successful
    And the source should be "flibusta"
    And both sources should have been queried

  Scenario: All sources fail to find book
    Given the fallback chain is configured as ["zlibrary", "flibusta"]
    When I search for "NonExistentBook XYZ123"
    And Z-Library does not find the book
    And Flibusta does not find the book
    Then the result should indicate "not found"
    And both sources should have been queried
    And the response should include attempted sources

  Scenario: Claude normalization enhances fuzzy input
    Given Claude SDK is available for normalization
    When I search for "hary poter filosofer stone"
    Then Claude should normalize it to "Harry Potter and the Philosopher's Stone"
    And the normalized query should be used for all sources
    And bilingual search strings should be generated

  Scenario Outline: Language-aware source prioritization
    Given the pipeline supports language-aware routing
    When I search for "<query>"
    Then the primary source should be "<expected_primary>"
    And the fallback source should be "<expected_fallback>"

    Examples:
      | query                    | expected_primary | expected_fallback |
      | Война и мир             | flibusta         | zlibrary          |
      | 1984 Orwell             | zlibrary         | flibusta          |
      | Мастер и Маргарита      | flibusta         | zlibrary          |
      | Pride and Prejudice     | zlibrary         | flibusta          |

  Scenario: Custom fallback chain configuration
    Given I configure a custom chain as ["flibusta", "zlibrary"]
    When I search for any book
    Then Flibusta should be queried first
    And Z-Library should be queried second if needed

  Scenario: Speed-priority configuration
    Given I configure speed priority mode
    When I search for any book
    Then only fast sources should be queried
    And slow sources should be skipped
    And the response should be under 10 seconds

  Scenario: Timeout handling
    Given the pipeline has a maximum timeout of 30 seconds
    When I search for a book
    And a source takes longer than its timeout
    Then the source should be skipped
    And the next source in the chain should be tried
    And the pipeline should complete within the total timeout

  Scenario Outline: Input validation and edge cases
    When I search for "<invalid_input>"
    Then the pipeline should handle it gracefully
    And return an appropriate error message

    Examples:
      | invalid_input |
      |               |
      | a             |
      | !@#$%         |
      |     only spaces     |

Feature: Bilingual Search Capability
  As a multilingual user
  I want the system to search using both original and Russian language strings
  So that I can find books regardless of the language I use for searching

  Scenario: Bilingual search strings generation
    Given Claude normalization is available
    When I search for "malenkiy prinz"
    Then Claude should generate both original and Russian search strings
    And the original string should be "Le Petit Prince Antoine de Saint-Exupéry"
    And the Russian string should be "Маленький принц Антуан де Сент-Экзюпери"

  Scenario: Using bilingual strings for source searching
    Given bilingual search strings are available
    When querying each source
    Then both original and Russian strings should be tried
    And the best match should be returned

Feature: Performance and Reliability
  As a system user
  I want the search to be fast and reliable
  So that I have a good user experience

  Scenario: Performance SLA compliance
    When I search for a common book like "1984"
    And Z-Library finds it immediately
    Then the response should be under 5 seconds
    And the success rate should be above 90%

  Scenario: Graceful degradation
    Given one source is temporarily unavailable
    When I search for any book
    Then the pipeline should continue with available sources
    And return results if any source succeeds
    And log the failure for monitoring

  Scenario: Cache effectiveness
    Given caching is enabled
    When I search for the same book twice
    Then the second search should be faster
    And the cache should be used appropriately

Feature: Monitoring and Analytics
  As a system administrator
  I want visibility into pipeline performance
  So that I can optimize and troubleshoot the system

  Scenario: Performance metrics collection
    When searches are performed
    Then response times should be tracked per source
    And success rates should be recorded
    And failure reasons should be logged

  Scenario: Source availability monitoring
    When a source fails repeatedly
    Then alerts should be generated
    And the source should be temporarily disabled
    And automatic retry should be attempted later